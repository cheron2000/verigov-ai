"""
Enhanced Smart Lambda Handler for VeriGov
Analyzes claim -> Selects relevant sources -> Fetches -> Verifies with AI
Dependency-light version for AWS Lambda
"""

import json
import os
import re
import uuid
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import requests


TRUSTED_SOURCES = {
    'space': ['nasa.gov', 'esa.int'],
    'health': ['who.int', 'cdc.gov', 'nih.gov', 'fda.gov', 'nhs.uk', 'pubmed.ncbi.nlm.nih.gov'],
    'science': ['nature.com', 'ncbi.nlm.nih.gov', 'usgs.gov', 'sciencedaily.com', 'arxiv.org'],
    'biography': ['britannica.com', 'bbc.com', 'theguardian.com'],
    'government_india': ['pib.gov.in', 'data.gov.in', 'indiabudget.gov.in'],
    'government_us': ['whitehouse.gov', 'state.gov', 'census.gov', 'bls.gov'],
    'government_uk': ['gov.uk', 'parliament.uk'],
    'government_eu': ['europa.eu', 'ec.europa.eu'],
    'international': ['un.org', 'worldbank.org', 'imf.org', 'oecd.org'],
    'weather': ['noaa.gov', 'wmo.int'],
    'environment': ['epa.gov', 'climate.nasa.gov', 'ipcc.ch'],
    'news': ['bbc.com', 'apnews.com', 'reuters.com', 'aljazeera.com'],
    'reference': ['britannica.com', 'loc.gov'],
    'data': ['ourworldindata.org', 'gapminder.org']
}

TOPIC_KEYWORDS = {
    'biography': {
        'keywords': ['who is', 'who are', 'who was', 'biography of', 'born in', 'life of'],
        'priority': 1,
        'use_ai_only': True
    },
    'space': {
        'keywords': ['space', 'nasa', 'moon', 'mars', 'planet', 'satellite', 'astronaut', 'rocket', 'orbit', 'asteroid', 'galaxy', 'artemis', 'esa'],
        'priority': 1,
        'use_ai_only': False
    },
    'health': {
        'keywords': ['health', 'disease', 'vaccine', 'medical', 'hospital', 'doctor', 'covid', 'virus', 'pandemic', 'brain', 'body', 'organ'],
        'priority': 1,
        'use_ai_only': False
    },
    'science': {
        'keywords': ['science', 'research', 'study', 'experiment', 'scientific', 'biology', 'chemistry', 'physics'],
        'priority': 2,
        'use_ai_only': False
    },
    'government_india': {
        'keywords': ['india', 'indian government', 'modi', 'lok sabha', 'rajya sabha', 'prime minister of india', 'pib'],
        'priority': 1,
        'use_ai_only': False
    }
}


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event, default=str)}")

    try:
        http_method = event.get("httpMethod", "")
        if http_method == "OPTIONS":
            return success_response({"message": "CORS preflight OK"})

        body = parse_request_body(event)
        claim = str(body.get('claim', '')).strip()
        user_sources = body.get('sources', [])

        if not isinstance(user_sources, list):
            user_sources = []

        if not claim:
            return error_response(400, 'Claim is required')

        verification_id = generate_id()

        try:
            result = process_verification(claim, user_sources)
            result['verification_id'] = verification_id
            result['claim'] = claim
            result['timestamp'] = utc_now()

            store_verification(verification_id, result)
            return success_response(result)

        except Exception as e:
            print(f"Verification error: {e}")
            import traceback
            traceback.print_exc()

            return success_response({
                'verification_id': verification_id,
                'claim': claim,
                'status': 'ERROR',
                'confidence': 0,
                'explanation': f'Error: {str(e)}',
                'evidence': [],
                'research_method': 'error',
                'topics_identified': [],
                'sources_selected': [],
                'sources_checked': 0,
                'timestamp': utc_now()
            })

    except Exception as e:
        print(f"Lambda error: {e}")
        import traceback
        traceback.print_exc()
        return error_response(500, str(e))


def process_verification(claim: str, user_sources: List[str]) -> Dict:
    topics, use_ai_only = analyze_claim_topics(claim)
    print(f"Topics: {topics}, AI only: {use_ai_only}")

    if user_sources:
        selected_sources = user_sources[:3]
        research_method = 'user_provided_sources'
        source_contents = fetch_sources(selected_sources)
    elif use_ai_only:
        selected_sources = []
        research_method = 'ai_knowledge_base'
        source_contents = []
    else:
        selected_sources = select_sources_for_topics(topics)
        if selected_sources:
            research_method = 'auto_selected_sources'
            source_contents = fetch_sources(selected_sources)
        else:
            research_method = 'ai_knowledge_base'
            source_contents = []

    print(f"Research: {research_method}, Sources fetched: {len(source_contents)}")

    verification_result = verify_with_ai(claim, source_contents, topics)
    verification_result['research_method'] = research_method
    verification_result['topics_identified'] = topics
    verification_result['sources_selected'] = selected_sources
    verification_result['sources_checked'] = len(source_contents)
    verification_result['research_note'] = generate_research_note(research_method, len(selected_sources), topics)

    return verification_result


def analyze_claim_topics(claim: str) -> Tuple[List[str], bool]:
    claim_lower = claim.lower()
    topic_scores = {}
    use_ai_only = False

    for topic, config in TOPIC_KEYWORDS.items():
        matches = sum(1 for keyword in config['keywords'] if keyword in claim_lower)
        if matches > 0:
            topic_scores[topic] = matches / max(config['priority'], 1)
            if config.get('use_ai_only', False):
                use_ai_only = True

    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    topics = [topic for topic, _ in sorted_topics[:3]]

    return topics if topics else ['general'], use_ai_only


def select_sources_for_topics(topics: List[str]) -> List[str]:
    sources = []
    for topic in topics:
        sources.extend(TRUSTED_SOURCES.get(topic, []))

    unique = []
    seen = set()
    for s in sources:
        if s not in seen:
            seen.add(s)
            unique.append(s)

    unique = unique[:3]
    return [f"https://www.{d}/" if not d.startswith('http') else d for d in unique]


def fetch_url_text(url: str, timeout: int = 10) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    req = Request(url, headers=headers)

    with urlopen(req, timeout=timeout) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or 'utf-8'
        return raw.decode(charset, errors='replace')


def strip_html(html: str) -> Tuple[str, str]:
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ''

    html = re.sub(r'<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<style\b[^<]*(?:(?!</style>)<[^<]*)*</style>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<nav\b[^<]*(?:(?!</nav>)<[^<]*)*</nav>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<footer\b[^<]*(?:(?!</footer>)<[^<]*)*</footer>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<header\b[^<]*(?:(?!</header>)<[^<]*)*</header>', ' ', html, flags=re.IGNORECASE | re.DOTALL)

    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&nbsp;|&#160;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return title, text[:5000]


def fetch_sources(source_urls: List[str]) -> List[Dict]:
    contents = []

    for url in source_urls[:3]:
        try:
            html = fetch_url_text(url, timeout=10)
            title, text = strip_html(html)

            if text:
                contents.append({
                    'url': url,
                    'title': title,
                    'content': text,
                    'status': 'success'
                })
                print(f"Fetched {len(text)} chars from {url}")

        except HTTPError as e:
            print(f"HTTP error fetching {url}: {e}")
        except URLError as e:
            print(f"URL error fetching {url}: {e}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    return contents


def verify_with_ai(claim: str, source_contents: List[Dict], topics: List[str]) -> Dict:
    # Try Groq first, then Bedrock
    api_key = os.environ.get('GROQ_API_KEY', '').strip()
    use_bedrock = os.environ.get('USE_BEDROCK', 'false').lower() == 'true'
    
    if use_bedrock and os.environ.get('BEDROCK_API_KEY', '').strip():
        return verify_with_bedrock(claim, source_contents, topics)
    elif api_key:
        return verify_with_groq(claim, source_contents, topics)
    else:
        raise Exception("No AI provider configured (GROQ_API_KEY or USE_BEDROCK)")


def verify_with_groq(claim: str, source_contents: List[Dict], topics: List[str]) -> Dict:
    api_key = os.environ.get('GROQ_API_KEY', '').strip()
    if not api_key:
        raise Exception("GROQ_API_KEY not configured")

    sources_text = ""
    if source_contents:
        parts = []
        for i, src in enumerate(source_contents, 1):
            if src.get('content'):
                parts.append(f"Source {i} ({src.get('url')}):\n{src['content'][:2000]}")
        sources_text = "\n\n".join(parts)

    context_line = f"Trusted Sources:\n{sources_text}" if source_contents else "No sources available. Use your knowledge base."

    prompt = f"""Verify this claim:

Claim: {claim}

{context_line}

Respond with valid JSON only. No markdown. No code block.

{{
  "status": "VERIFIED or UNVERIFIED or PARTIALLY_VERIFIED",
  "confidence": 0,
  "explanation": "your explanation",
  "evidence": ["fact1", "fact2"]
}}"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a fact-checker. Return JSON only, with no markdown."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Groq API error: {response.status_code} - {response.text}")
            if response.status_code == 429:
                raise Exception("Groq API rate limit exceeded. Please wait a few minutes and try again.")
            raise Exception(f"Groq API error: {response.status_code}")
        
        response_data = response.json()
        
        if 'choices' not in response_data:
            print(f"Groq API unexpected response: {response_data}")
            raise Exception("Groq API returned unexpected response format")
        
        ai_response = response_data['choices'][0]['message']['content'].strip()
        print(f"Groq AI response (first 200): {ai_response[:200]}")
        return parse_ai_response(ai_response)
    except requests.exceptions.RequestException as e:
        print(f"Groq API request error: {e}")
        raise Exception(f"Groq API error: {str(e)}")


def verify_with_bedrock(claim: str, source_contents: List[Dict], topics: List[str]) -> Dict:
    import boto3
    import os
    
    sources_text = ""
    if source_contents:
        parts = []
        for i, src in enumerate(source_contents, 1):
            if src.get('content'):
                parts.append(f"Source {i} ({src.get('url')}):\n{src['content'][:2000]}")
        sources_text = "\n\n".join(parts)

    context_line = f"Trusted Sources:\n{sources_text}" if source_contents else "No sources available. Use your knowledge base."

    prompt = f"""Verify this claim:

Claim: {claim}

{context_line}

Respond with valid JSON only. No markdown. No code block.

{{
  "status": "VERIFIED or UNVERIFIED or PARTIALLY_VERIFIED",
  "confidence": 0,
  "explanation": "your explanation",
  "evidence": ["fact1", "fact2"]
}}"""

    try:
        # Get Bedrock API key from environment variable
        bedrock_api_key = os.environ.get('BEDROCK_API_KEY', '').strip()
        if not bedrock_api_key:
            raise Exception("BEDROCK_API_KEY not configured")
        
        # Use Claude Haiku model (faster approval, lower cost)
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": f"""You are a fact-checker. Return JSON only, with no markdown.

{prompt}"""
                }
            ],
            "temperature": 0.1
        })
        
        # Call Bedrock API using requests with API key
        import requests
        response = requests.post(
            f"https://bedrock-runtime.us-east-1.amazonaws.com/model/{model_id}/invoke",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Amz-Content-Sha256": body,
                "Authorization": f"Bearer {bedrock_api_key}"
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Bedrock API error: {response.status_code} - {response.text}")
            raise Exception(f"Bedrock API error: {response.status_code}")
        
        response_body = json.loads(response.text)
        ai_response = response_body['content'][0]['text'].strip()
        print(f"Bedrock AI response (first 200): {ai_response[:200]}")
        return parse_ai_response(ai_response)
    except Exception as e:
        print(f"Bedrock error: {e}")
        raise Exception(f"Bedrock error: {str(e)}")


def parse_ai_response(text: str) -> Dict:
    print(f"Raw AI response length: {len(text)} chars")

    cleaned = text.strip()
    cleaned = re.sub(r'^```(?:json)?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'```$', '', cleaned)
    cleaned = cleaned.replace('```', '').strip()

    try:
        result = json.loads(cleaned)
        return validate_result(result)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(0))
            return validate_result(result)
        except json.JSONDecodeError:
            pass

    return manual_extract(text)


def manual_extract(text: str) -> Dict:
    result = {
        'status': 'UNVERIFIED',
        'confidence': 50,
        'explanation': 'Failed to parse AI response',
        'evidence': []
    }

    status_match = re.search(r'"status"\s*:\s*"(VERIFIED|UNVERIFIED|PARTIALLY_VERIFIED)"', text, re.IGNORECASE)
    if status_match:
        result['status'] = status_match.group(1).upper()

    conf_match = re.search(r'"confidence"\s*:\s*(\d+)', text)
    if conf_match:
        result['confidence'] = int(conf_match.group(1))

    exp_match = re.search(r'"explanation"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
    if exp_match:
        explanation = exp_match.group(1).replace('\\"', '"').replace('\\n', ' ').strip()
        if explanation:
            result['explanation'] = explanation[:1000]

    evidence_match = re.search(r'"evidence"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if evidence_match:
        result['evidence'] = re.findall(r'"([^"]+)"', evidence_match.group(1))[:5]

    return validate_result(result)


def validate_result(result: Dict) -> Dict:
    status = str(result.get('status', 'UNVERIFIED')).upper()
    if status not in ['VERIFIED', 'UNVERIFIED', 'PARTIALLY_VERIFIED']:
        status = 'UNVERIFIED'

    try:
        confidence = int(result.get('confidence', 50))
    except Exception:
        confidence = 50
    confidence = max(0, min(100, confidence))

    explanation = str(result.get('explanation', 'No explanation')).strip() or 'No explanation'
    evidence = result.get('evidence', [])
    if not isinstance(evidence, list):
        evidence = []

    return {
        'status': status,
        'confidence': confidence,
        'explanation': explanation,
        'evidence': evidence[:5]
    }


def generate_research_note(method: str, count: int, topics: List[str]) -> str:
    if method == 'user_provided_sources':
        return f"Verified using {count} user-provided source(s)"
    if method == 'auto_selected_sources':
        return f"Auto-selected {count} source(s) for topics: {', '.join(topics)}"
    return f"AI knowledge base (topics: {', '.join(topics)})"


def parse_request_body(event: Dict) -> Dict:
    body = event.get('body', {})
    if isinstance(body, str):
        body = body.strip()
        if not body:
            return {}
        return json.loads(body)
    return body if isinstance(body, dict) else {}


def generate_id() -> str:
    return str(uuid.uuid4())


def store_verification(vid: str, result: Dict):
    try:
        import boto3
        from decimal import Decimal

        def convert_numbers(obj):
            if isinstance(obj, float):
                return Decimal(str(obj))
            if isinstance(obj, dict):
                return {k: convert_numbers(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_numbers(i) for i in obj]
            return obj

        region = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'ap-south-1'))
        environment = os.environ.get('ENVIRONMENT', 'dev')

        dynamodb = boto3.resource('dynamodb', region_name=region)
        table = dynamodb.Table(f"verigov-{environment}-verifications")

        item = convert_numbers(result)
        item['verification_id'] = vid
        item['stored_at'] = utc_now()

        table.put_item(Item=item)
        print(f"Stored verification {vid}")

    except Exception as e:
        print(f"Storage error: {e}")


def utc_now() -> str:
    return datetime.utcnow().isoformat() + 'Z'


def success_response(data: Dict) -> Dict:
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(data)
    }


def error_response(code: int, msg: str) -> Dict:
    return {
        'statusCode': code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({
            'error': 'Request failed' if code < 500 else 'Server error',
            'message': str(msg)
        })
    }