"""
Lambda handler for VeriGov AI verification endpoint
Cleaned and hardened version for AWS Lambda + API Gateway
"""

import json
import os
import re
import sys
import uuid
import traceback
from datetime import datetime
from decimal import Decimal

# Add Lambda layer path for dependencies
sys.path.insert(0, "/opt/python")


CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
}


def lambda_handler(event, context):
    """
    AWS Lambda handler for claim verification.

    Expected API Gateway event:
    {
        "httpMethod": "POST",
        "body": "{\"claim\": \"...\", \"sources\": [...]}"
    }
    """

    print("Received event:")
    print(json.dumps(event, default=str))

    try:
        http_method = event.get("httpMethod", "")

        # Handle CORS preflight
        if http_method == "OPTIONS":
            return response(200, {"message": "CORS preflight OK"})

        # Parse request body
        body = parse_request_body(event)
        claim = str(body.get("claim", "")).strip()
        sources = body.get("sources", [])

        if not isinstance(sources, list):
            sources = []

        # Validate input
        if not claim:
            return response(
                400,
                {
                    "error": "Claim is required",
                    "message": "Please provide a claim to verify.",
                },
            )

        # Import external dependencies
        try:
            from groq import Groq
        except ImportError as e:
            print(f"Import error: {e}")
            return error_response(f"Missing dependency: {e}")

        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return error_response("GROQ_API_KEY not configured in environment variables.")

        verification_id = generate_verification_id()

        # Run AI verification
        result = run_verification(
            claim=claim,
            sources=sources,
            groq_api_key=groq_api_key,
        )

        # Add metadata
        result["verification_id"] = verification_id
        result["claim"] = claim
        result["sources_checked"] = len(sources)
        result["timestamp"] = utc_now()

        # Store in DynamoDB
        try:
            store_verification(verification_id, result)
        except Exception as e:
            print(f"DynamoDB storage error: {e}")
            traceback.print_exc()
            result["storage_warning"] = "Verification completed, but result could not be stored."

        return response(200, result)

    except Exception as e:
        print(f"Unhandled Lambda error: {e}")
        traceback.print_exc()
        return error_response(str(e))


def parse_request_body(event):
    """Safely parse request body from API Gateway event."""
    body = event.get("body", {})

    if isinstance(body, str):
        body = body.strip()
        if not body:
            return {}
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            raise ValueError("Request body is not valid JSON.")

    if isinstance(body, dict):
        return body

    return {}


def run_verification(claim, sources, groq_api_key):
    """Call Groq API and return normalized verification result."""
    from groq import Groq

    client = Groq(api_key=groq_api_key)

    prompt = build_verification_prompt(claim, sources)

    try:
        api_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict claim verification assistant. "
                        "Return only valid JSON. Do not use markdown. "
                        "Do not wrap the response in code fences. "
                        "Do not include any text outside the JSON object."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=400,
        )

        ai_response = api_response.choices[0].message.content.strip()
        print(f"Raw AI response: {ai_response}")

        parsed = parse_ai_json(ai_response)
        normalized = normalize_result(parsed)
        return normalized

    except Exception as e:
        print(f"Groq API error: {e}")
        traceback.print_exc()
        return {
            "status": "ERROR",
            "confidence": 0,
            "explanation": f"AI service error: {str(e)}",
        }


def build_verification_prompt(claim, sources):
    """Build a strict prompt for structured JSON output."""
    sources_text = ""
    if sources:
        joined_sources = "\n".join(f"- {str(src)}" for src in sources[:10])
        sources_text = f"""
Use these provided sources if relevant:
{joined_sources}
"""
    else:
        sources_text = """
No explicit sources were provided.
Assess whether the claim appears verifiable and explain briefly.
"""

    return f"""
Analyze this claim and determine its verification status.

Claim:
{claim}

{sources_text}

Return ONLY a valid JSON object with exactly these fields:
{{
  "status": "VERIFIED | UNVERIFIED | PARTIALLY_VERIFIED",
  "confidence": 0,
  "explanation": "Brief explanation"
}}

Rules:
- confidence must be an integer between 0 and 100
- explanation must be concise and factual
- do not include markdown
- do not include code fences
- do not include any extra text
""".strip()


def parse_ai_json(ai_response):
    """
    Robustly parse model output into JSON.
    Handles:
    - raw JSON
    - ```json ... ```
    - extra text before/after JSON
    """
    text = ai_response.strip()

    # Remove markdown code fences if present
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("Could not parse AI response as valid JSON.")


def normalize_result(parsed):
    """Normalize and validate result schema."""
    if not isinstance(parsed, dict):
        raise ValueError("Parsed AI response is not a JSON object.")

    allowed_statuses = {"VERIFIED", "UNVERIFIED", "PARTIALLY_VERIFIED"}

    status = str(parsed.get("status", "UNVERIFIED")).strip().upper()
    if status not in allowed_statuses:
        status = "UNVERIFIED"

    confidence = parsed.get("confidence", 50)
    try:
        confidence = int(confidence)
    except (ValueError, TypeError):
        confidence = 50
    confidence = max(0, min(100, confidence))

    explanation = str(parsed.get("explanation", "")).strip()
    if not explanation:
        explanation = "No explanation provided by AI."

    return {
        "status": status,
        "confidence": confidence,
        "explanation": explanation,
    }


def store_verification(verification_id, result):
    """Store verification result in DynamoDB."""
    import boto3

    region = os.environ.get(
        "AWS_DEFAULT_REGION",
        os.environ.get("AWS_REGION", "ap-south-1"),
    )
    environment = os.environ.get("ENVIRONMENT", "dev")
    table_name = f"verigov-{environment}-verifications"

    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)

    item = convert_numbers_for_dynamodb(result)
    item["verification_id"] = verification_id
    item["stored_at"] = utc_now()

    table.put_item(Item=item)
    print(f"Stored verification {verification_id} in DynamoDB table {table_name}")


def convert_numbers_for_dynamodb(obj):
    """Convert Python numeric values for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, int):
        return obj
    if isinstance(obj, dict):
        return {k: convert_numbers_for_dynamodb(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_numbers_for_dynamodb(v) for v in obj]
    return obj


def generate_verification_id():
    """Generate unique verification ID."""
    return str(uuid.uuid4())


def utc_now():
    """UTC timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat() + "Z"


def response(status_code, body):
    """Return API Gateway compatible JSON response."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body),
    }


def error_response(message):
    """Return standardized error response."""
    return response(
        500,
        {
            "error": "Internal server error",
            "message": str(message),
        },
    )