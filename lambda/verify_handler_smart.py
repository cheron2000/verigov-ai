"""
Smart Lambda handler with automatic source selection
Analyzes claim -> Selects relevant sources -> Fetches -> Verifies
"""

import json
import os
import re
from datetime import datetime

# Trusted sources by category
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
    'news': ['bbc.com', 'apnews.com', 'reuters.com'],
    'reference': ['britannica.com', 'loc.gov'],
    'data': ['statista.com', 'ourworldindata.org']
}


def lambda_handler(event, context):
    """Main handler"""
    print(f"Event: {json.dumps(event)}")
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        claim = body.get('claim', '').strip()
        user_sources = body.get('sources', [])
        
        if not claim:
            return error_response(400, 'Claim required')
        
        verification_id = generate_id()
        
        try:
            # Detect topics
            topics = detect_topics(claim)
            print(f"Topics: {topics}")
            
            # Select sources
            if user_sources:
                sources = user_sources
                method = 'user_provided_sources'
            elif 'biography' in topics:
                sources = []
                method = 'ai_knowledge_base'
            else:
                sources = select_sources(topics)
                method = 'auto_selected_sources' if sources else 'ai_knowledge_base'
            
            # Fetch content
            contents = fetch_sources(sources) if sources else []
            print(f"Fetched {len(contents)} sources")
            
            # Verify with AI
            result = verify_claim(claim, contents, topics)
            
            # Add metadata
            result.update({
                'verification_id': verification_id,
                'claim': claim,
                'research_method': method,
                'topics_identified': topics,
                'sources_selected': sources,
                'sources_checked': len(contents),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'research_note': f"Auto-selected {len(sources)} sources for {', '.join(topics)}" if method == 'auto_selected_sources' else f"AI knowledge base ({', '.join(topics)})"
            })
            
            store_result(verification_id, result)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(result)
            }
            
        except Exception as e:
            print(f"Verification error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    'verification_id': verification_id,
                    'claim': claim,
                    'status': 'ERROR',
                    'confidence': 0,
                    'explanation': f'Error: {str(e)}',
                    'research_method': 'error',
                    'topics_identified': [],
                    'sources_selected': [],
                    'sources_checked': 0,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
            }
    
    except Exception as e:
        print(f"Handler error: {e}")
        import traceback
        traceback.print_exc()
        return error_response(500, str(e))


def detect_topics(claim):
    """Simple keyword-based topic detection"""
    claim_lower = claim.lower()
    topics = []
    
    # Check each category
    if any(w in claim_lower for w in ['who is', 'who are', 'biography']):
        topics.append('biography')
    if any(w in claim_lower for w in ['space', 'nasa', 'moon', 'mars', 'planet', 'satellite', 'astronaut', 'artemis', 'esa']):
        topics.append('space')
    if any(w in claim_lower for w in ['health', 'disease', 'vaccine', 'medical', 'brain', 'body']):
        topics.append('health')
    if any(w in claim_lower for w in ['science', 'research', 'study', 'scientific']):
        topics.append('science')
    
    return topics[:2] if topics else ['general']


def select_sources(topics):
    """Select sources for topics"""
    sources = []
    for topic in topics:
        if topic in TRUSTED_SOURCES:
            sources.extend(TRUSTED_SOURCES[topic][:2])
    
    # Remove duplicates, limit to 3
    unique = list(dict.fromkeys(sources))[:3]
    return [f"https://www.{d}/" if not d.startswith('http') else d for d in unique]


def fetch_sources(urls):
    """Fetch content from URLs"""
    import requests
    from bs4 import BeautifulSoup
    
    contents = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in urls[:3]:
        try:
            r = requests.get(url, timeout=10, headers=headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                    tag.decompose()
                
                text = soup.get_text()
                text = re.sub(r'\s+', ' ', text)[:4000]
                
                contents.append({'url': url, 'content': text})
                print(f"Fetched {len(text)} chars from {url}")
        except Exception as e:
            print(f"Fetch error {url}: {e}")
    
    return contents


def verify_claim(claim, sources, topics):
    """Verify claim with Groq AI"""
    import requests
    
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise Exception("GROQ_API_KEY missing")
    
    # Build context
    if sources:
        context = "\n\n".join([f"Source {i+1}:\n{s['content'][:1500]}" for i, s in enumerate(sources)])
        instruction = "Use the provided sources to verify the claim."
    else:
        context = "No sources available."
        instruction = "Use your knowledge base to verify the claim."
    
    prompt = f"""Verify this claim: {claim}

{context}

{instruction}

Respond with JSON only:
{{"status": "VERIFIED", "confidence": 90, "explanation": "...", "evidence": ["fact1"]}}"""
    
    # Call Groq
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Fact-checker. JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 600
    }
    
    r = requests.post(url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload, timeout=25)
    r.raise_for_status()
    
    response_text = r.json()['choices'][0]['message']['content']
    print(f"AI response: {response_text[:100]}")
    
    # Parse response - BULLETPROOF
    return parse_response(response_text)


def parse_response(text):
    """Bulletproof JSON parser"""
    
    # Remove ALL markdown
    text = text.replace('```json', '').replace('```', '').strip()
    
    # Try direct parse
    try:
        return validate(json.loads(text))
    except:
        pass
    
    # Find JSON by counting braces
    depth = 0
    start = None
    
    for i, c in enumerate(text):
        if c == '{':
            if depth == 0:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    obj = json.loads(text[start:i+1])
                    if 'status' in obj:
                        return validate(obj)
                except:
                    pass
    
    # Extract fields manually
    return extract_fields(text)


def extract_fields(text):
    """Extract fields from text"""
    result = {'status': 'UNVERIFIED', 'confidence': 50, 'explanation': text[:400], 'evidence': []}
    
    # Status
    m = re.search(r'"status"\s*:\s*"(VERIFIED|UNVERIFIED|PARTIALLY_VERIFIED)"', text, re.I)
    if m:
        result['status'] = m.group(1).upper()
    
    # Confidence
    m = re.search(r'"confidence"\s*:\s*(\d+)', text)
    if m:
        result['confidence'] = int(m.group(1))
    
    # Explanation
    m = re.search(r'"explanation"\s*:\s*"([^"]{30,600})"', text, re.DOTALL)
    if m:
        result['explanation'] = m.group(1)[:500]
    
    # Evidence
    m = re.search(r'"evidence"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if m:
        items = re.findall(r'"([^"]+)"', m.group(1))
        result['evidence'] = items[:5]
    
    return result


def validate(obj):
    """Validate result object"""
    if 'status' not in obj:
        obj['status'] = 'UNVERIFIED'
    if 'confidence' not in obj:
        obj['confidence'] = 50
    if 'explanation' not in obj:
        obj['explanation'] = 'No explanation'
    if 'evidence' not in obj:
        obj['evidence'] = []
    
    obj['status'] = str(obj['status']).upper()
    if obj['status'] not in ['VERIFIED', 'UNVERIFIED', 'PARTIALLY_VERIFIED']:
        obj['status'] = 'UNVERIFIED'
    
    try:
        obj['confidence'] = max(0, min(100, int(obj['confidence'])))
    except:
        obj['confidence'] = 50
    
    return obj


def generate_id():
    """Generate UUID"""
    import uuid
    return str(uuid.uuid4())


def store_result(vid, result):
    """Store in DynamoDB"""
    try:
        import boto3
        from decimal import Decimal
        
        def to_decimal(obj):
            if isinstance(obj, float):
                return Decimal(str(obj))
            elif isinstance(obj, dict):
                return {k: to_decimal(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [to_decimal(x) for x in obj]
            return obj
        
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        table = dynamodb.Table(f"verigov-{os.environ.get('ENVIRONMENT', 'dev')}-verifications")
        
        item = to_decimal(result)
        item['stored_at'] = datetime.utcnow().isoformat() + 'Z'
        table.put_item(Item=item)
        print(f"Stored {vid}")
    except Exception as e:
        print(f"Storage error: {e}")


def cors_headers():
    """CORS headers"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }


def error_response(code, msg):
    """Error response"""
    return {
        'statusCode': code,
        'headers': cors_headers(),
        'body': json.dumps({'error': 'Failed', 'message': str(msg)})
    }
