"""
Lambda handler with source fetching capability
Fetches data from provided URLs and analyzes with AI
"""

import json
import os
import sys
from datetime import datetime
import re

def lambda_handler(event, context):
    """AWS Lambda handler for claim verification with source fetching"""
    
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
            return error_response(400, 'Claim is required')
        
        # Perform verification
        verification_id = generate_verification_id()
        
        try:
            # Fetch content from sources if provided
            source_contents = []
            if sources:
                source_contents = fetch_sources(sources)
            
            # Analyze with AI
            result = analyze_with_sources(claim, source_contents)
            
        except Exception as e:
            print(f"Verification error: {e}")
            result = {
                'status': 'ERROR',
                'confidence': 0,
                'explanation': f'Verification error: {str(e)}'
            }
        
        # Add metadata
        result['verification_id'] = verification_id
        result['claim'] = claim
        result['sources_checked'] = len(source_contents)
        result['source_urls'] = sources
        result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Store in DynamoDB
        try:
            store_verification(verification_id, result)
        except Exception as e:
            print(f"Storage error: {e}")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Lambda error: {e}")
        import traceback
        traceback.print_exc()
        return error_response(500, str(e))


def fetch_sources(source_urls):
    """Fetch content from source URLs"""
    import requests
    from bs4 import BeautifulSoup
    
    contents = []
    
    for url in source_urls[:5]:  # Limit to 5 sources
        try:
            print(f"Fetching: {url}")
            
            # Fetch with timeout
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'VeriGov-Bot/1.0'}
            )
            
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit text length
                text = text[:5000]  # First 5000 chars
                
                contents.append({
                    'url': url,
                    'content': text,
                    'status': 'success'
                })
                
                print(f"✅ Fetched {len(text)} chars from {url}")
            else:
                print(f"❌ Failed to fetch {url}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            contents.append({
                'url': url,
                'content': '',
                'status': 'error',
                'error': str(e)
            })
    
    return contents


def analyze_with_sources(claim, source_contents):
    """Analyze claim with AI using source content"""
    import requests
    
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise Exception("GROQ_API_KEY not configured")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Build prompt with source content
    if source_contents:
        sources_text = "\n\n".join([
            f"Source {i+1} ({src['url']}):\n{src['content'][:1000]}"
            for i, src in enumerate(source_contents)
            if src.get('content')
        ])
        
        prompt = f"""Analyze this claim using the provided source content:

Claim: {claim}

Source Content:
{sources_text}

Based on the source content above, provide a JSON response with:
- status: VERIFIED (if sources confirm), UNVERIFIED (if sources contradict), or PARTIALLY_VERIFIED (if sources partially support)
- confidence: 0-100 (based on source reliability and clarity)
- explanation: Brief explanation citing the sources
- evidence: Key quotes or facts from sources that support your assessment

Response:"""
    else:
        # No sources provided, use AI knowledge
        prompt = f"""Analyze this claim and determine if it's verifiable:

Claim: {claim}

Provide a JSON response with:
- status: VERIFIED, UNVERIFIED, or PARTIALLY_VERIFIED
- confidence: 0-100
- explanation: Brief explanation of your assessment

Response:"""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 800
    }
    
    print(f"Calling Groq API...")
    response = requests.post(url, headers=headers, json=payload, timeout=25)
    response.raise_for_status()
    
    data = response.json()
    ai_response = data['choices'][0]['message']['content']
    
    # Parse AI response
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{[^}]+\}', ai_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(ai_response)
    except:
        # Fallback if AI doesn't return JSON
        result = {
            'status': 'UNVERIFIED',
            'confidence': 50,
            'explanation': ai_response[:300]
        }
    
    return result


def generate_verification_id():
    """Generate unique verification ID"""
    import uuid
    return str(uuid.uuid4())


def store_verification(verification_id, result):
    """Store verification result in DynamoDB"""
    import boto3
    from decimal import Decimal
    
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


def get_cors_headers():
    """Get CORS headers"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }


def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'error': 'Request failed' if status_code < 500 else 'Internal server error',
            'message': str(message)
        })
    }
