"""
Smart Lambda handler with automatic source selection
Analyzes claim → Selects relevant sources → Fetches → Verifies
"""

import json
import os
import sys
from datetime import datetime
import re

# Trusted sources mapping by category
TRUSTED_SOURCES = {
    'space': ['nasa.gov', 'esa.int'],
    'health': ['who.int', 'cdc.gov', 'nih.gov'],
    'science': ['nature.com', 'science.org', 'ncbi.nlm.nih.gov'],
    'government_india': ['gov.in', 'nic.in', 'pib.gov.in', 'mygov.in', 'data.gov.in'],
    'government_us': ['census.gov', 'bls.gov'],
    'government_uk': ['gov.uk'],
    'government_eu': ['europa.eu'],
    'international': ['un.org', 'worldbank.org', 'imf.org'],
    'weather': ['noaa.gov']
}

def lambda_handler(event, context):
    """Smart verification with automatic source selection"""
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        claim = body.get('claim', '').strip()
        user_sources = body.get('sources', [])  # User can still provide sources
        
        # Validate input
        if not claim:
            return error_response(400, 'Claim is required')
        
        verification_id = generate_verification_id()
        
        try:
            # Step 1: Analyze claim to determine topic and select sources
            analysis = analyze_claim_topic(claim)
            
            # Step 2: Select relevant sources (user sources take priority)
            if user_sources:
                selected_sources = user_sources
                research_method = 'user_provided_sources'
            elif analysis['relevant_sources']:
                selected_sources = analysis['relevant_sources']
                research_method = 'auto_selected_sources'
            else:
                selected_sources = []
                research_method = 'ai_knowledge_base'
            
            # Step 3: Fetch from sources if available
            source_contents = []
            if selected_sources:
                source_contents = fetch_sources(selected_sources)
            
            # Step 4: Verify with AI
            result = analyze_with_sources(claim, source_contents, analysis['topics'])
            
            # Add metadata
            result['verification_id'] = verification_id
            result['claim'] = claim
            result['research_method'] = research_method
            result['topics_identified'] = analysis['topics']
            result['sources_selected'] = selected_sources
            result['sources_checked'] = len(source_contents)
            result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            
            # Add research method explanation
            if research_method == 'user_provided_sources':
                result['research_note'] = f"Verified using {len(selected_sources)} user-provided source(s)"
            elif research_method == 'auto_selected_sources':
                result['research_note'] = f"Automatically selected {len(selected_sources)} relevant source(s) based on topics: {', '.join(analysis['topics'])}"
            else:
                result['research_note'] = f"Verified using AI knowledge base (topics: {', '.join(analysis['topics'])}). No specific trusted sources found for this claim."
            
        except Exception as e:
            print(f"Verification error: {e}")
            import traceback
            traceback.print_exc()
            result = {
                'status': 'ERROR',
                'confidence': 0,
                'explanation': f'Verification error: {str(e)}',
                'research_method': 'error',
                'research_note': 'An error occurred during verification'
            }
        
        # Store in DynamoDB
        try:
            store_verification(verification_id, result)
        except Exception as e:
            print(f"Storage error: {e}")
        
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


def analyze_claim_topic(claim):
    """Analyze claim to identify topics and select relevant sources"""
    import requests
    
    claim_lower = claim.lower()
    topics = []
    relevant_sources = []
    
    # Keyword-based topic detection
    topic_keywords = {
        'space': ['space', 'nasa', 'moon', 'mars', 'planet', 'satellite', 'astronaut', 'rocket', 'orbit'],
        'health': ['health', 'disease', 'vaccine', 'medical', 'hospital', 'doctor', 'covid', 'virus', 'pandemic'],
        'science': ['science', 'research', 'study', 'experiment', 'scientific', 'biology', 'chemistry', 'physics'],
        'government_india': ['india', 'indian government', 'delhi', 'mumbai', 'modi', 'parliament'],
        'government_us': ['united states', 'america', 'us government', 'washington', 'congress', 'census'],
        'government_uk': ['uk', 'britain', 'british', 'london', 'parliament'],
        'government_eu': ['europe', 'european union', 'eu', 'brussels'],
        'international': ['united nations', 'un', 'world bank', 'imf', 'international'],
        'weather': ['weather', 'climate', 'temperature', 'rain', 'storm', 'hurricane', 'forecast']
    }
    
    # Detect topics
    for topic, keywords in topic_keywords.items():
        if any(keyword in claim_lower for keyword in keywords):
            topics.append(topic)
            # Add sources for this topic
            if topic in TRUSTED_SOURCES:
                relevant_sources.extend(TRUSTED_SOURCES[topic])
    
    # Remove duplicates and limit to top 3 sources
    relevant_sources = list(dict.fromkeys(relevant_sources))[:3]
    
    # Convert domains to full URLs
    relevant_sources = [f"https://www.{domain}/" if not domain.startswith('http') else domain 
                       for domain in relevant_sources]
    
    print(f"Topics identified: {topics}")
    print(f"Relevant sources: {relevant_sources}")
    
    return {
        'topics': topics if topics else ['general'],
        'relevant_sources': relevant_sources
    }


def fetch_sources(source_urls):
    """Fetch content from source URLs"""
    import requests
    from bs4 import BeautifulSoup
    
    contents = []
    
    for url in source_urls[:3]:  # Limit to 3 sources
        try:
            print(f"Fetching: {url}")
            
            response = requests.get(
                url,
                timeout=8,
                headers={'User-Agent': 'VeriGov-Bot/1.0'}
            )
            
            if response.status_code == 200:
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
                text = text[:3000]  # First 3000 chars
                
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
    
    return contents


def analyze_with_sources(claim, source_contents, topics):
    """Analyze claim with AI using source content or knowledge base"""
    import requests
    
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise Exception("GROQ_API_KEY not configured")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Build prompt based on available sources
    if source_contents:
        sources_text = "\n\n".join([
            f"Source {i+1} ({src['url']}):\n{src['content'][:800]}"
            for i, src in enumerate(source_contents)
            if src.get('content')
        ])
        
        prompt = f"""Analyze this claim using the provided source content from trusted sources:

Claim: {claim}

Topics: {', '.join(topics)}

Trusted Source Content:
{sources_text}

Based on the source content above, provide a JSON response with:
- status: VERIFIED (if sources confirm), UNVERIFIED (if sources contradict), or PARTIALLY_VERIFIED (if sources partially support)
- confidence: 0-100 (based on source reliability and clarity)
- explanation: Brief explanation citing the sources and mentioning that content was fetched from trusted sources
- evidence: Key quotes or facts from sources

Response:"""
    else:
        prompt = f"""Analyze this claim using your knowledge base:

Claim: {claim}

Topics: {', '.join(topics)}

Note: No specific trusted sources were found for this claim. Use your general knowledge to assess it.

Provide a JSON response with:
- status: VERIFIED, UNVERIFIED, or PARTIALLY_VERIFIED
- confidence: 0-100
- explanation: Brief explanation mentioning that this is based on AI knowledge base since no specific trusted sources were available
- evidence: Key facts supporting your assessment

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
        json_match = re.search(r'\{[^}]+\}', ai_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(ai_response)
    except:
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
