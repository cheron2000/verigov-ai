"""
Lambda handler for VeriGov AI verification endpoint
Optimized for AWS Hackathon demonstration
"""

import json
import os
import sys
from datetime import datetime

# Add the parent directory to path for imports
sys.path.insert(0, '/opt/python')

def lambda_handler(event, context):
    """
    AWS Lambda handler for claim verification
    
    Event structure (API Gateway):
    {
        "body": "{\"claim\": \"...\", \"sources\": [...]}"
        "headers": {...}
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        claim = body.get('claim', '').strip()
        sources = body.get('sources', [])
        
        # Validate input
        if not claim:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Claim is required',
                    'message': 'Please provide a claim to verify'
                })
            }
        
        # Import VeriGov components
        try:
            import boto3
            from groq import Groq
        except ImportError as e:
            print(f"Import error: {e}")
            return error_response(f"Missing dependencies: {e}")
        
        # Initialize services
        groq_api_key = os.environ.get('GROQ_API_KEY')
        if not groq_api_key:
            return error_response("GROQ_API_KEY not configured")
        
        # Perform verification using Groq
        verification_id = generate_verification_id()
        
        try:
            # Call Groq AI for verification
            client = Groq(api_key=groq_api_key)
            
            prompt = f"""Analyze this claim and determine if it's verifiable:

Claim: {claim}

Provide a JSON response with:
- status: VERIFIED, UNVERIFIED, or PARTIALLY_VERIFIED
- confidence: 0-100
- explanation: Brief explanation of your assessment

Response:"""
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse AI response
            try:
                result = json.loads(ai_response)
            except:
                # Fallback if AI doesn't return JSON
                result = {
                    'status': 'UNVERIFIED',
                    'confidence': 50,
                    'explanation': ai_response[:200]
                }
            
        except Exception as e:
            print(f"Groq API error: {e}")
            result = {
                'status': 'ERROR',
                'confidence': 0,
                'explanation': f'AI service error: {str(e)}'
            }
        
        # Add metadata
        result['verification_id'] = verification_id
        result['claim'] = claim
        result['sources_checked'] = len(sources)
        result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Store in DynamoDB
        try:
            store_verification(verification_id, result)
        except Exception as e:
            print(f"Storage error: {e}")
            # Continue even if storage fails
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Lambda error: {e}")
        import traceback
        traceback.print_exc()
        return error_response(str(e))


def generate_verification_id():
    """Generate unique verification ID"""
    import uuid
    return str(uuid.uuid4())


def store_verification(verification_id, result):
    """Store verification result in DynamoDB"""
    import boto3
    from decimal import Decimal
    
    # AWS Lambda automatically sets AWS_REGION, use it or default
    region = os.environ.get('AWS_DEFAULT_REGION', os.environ.get('AWS_REGION', 'ap-south-1'))
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table_name = f"verigov-{os.environ.get('ENVIRONMENT', 'dev')}-verifications"
    table = dynamodb.Table(table_name)
    
    # Convert floats to Decimal for DynamoDB
    def convert_floats(obj):
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: convert_floats(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_floats(item) for item in obj]
        return obj
    
    item = convert_floats(result)
    item['stored_at'] = datetime.utcnow().isoformat() + 'Z'
    
    table.put_item(Item=item)
    print(f"Stored verification {verification_id} in DynamoDB")


def error_response(message):
    """Return error response"""
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({
            'error': 'Internal server error',
            'message': str(message)
        })
    }
