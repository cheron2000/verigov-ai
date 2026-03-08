#!/usr/bin/env python3
"""Test biographical queries with improved handling"""
import boto3
import json

region = 'ap-south-1'
function_name = 'verigov-dev-verify-sources'

lambda_client = boto3.client('lambda', region_name=region)

print("=" * 70)
print("Testing Biographical Queries")
print("=" * 70)

test_cases = [
    {
        'name': 'Biographical Query - Narendra Modi',
        'claim': 'Who is Narendra Modi?'
    },
    {
        'name': 'Biographical Query - Joe Biden',
        'claim': 'Who is Joe Biden?'
    },
    {
        'name': 'Informational Query - NASA',
        'claim': 'What is NASA?'
    },
    {
        'name': 'Factual Claim - Vaccines',
        'claim': 'Vaccines help prevent diseases'
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 70}")
    print(f"Test {i}: {test['name']}")
    print(f"Query: {test['claim']}")
    print(f"{'=' * 70}")
    
    test_event = {
        'body': json.dumps({
            'claim': test['claim'],
            'sources': []
        })
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') == 200:
            body = json.loads(result['body'])
            
            print(f"✅ Status: {body.get('status')}")
            print(f"   Confidence: {body.get('confidence')}%")
            print(f"   Research Method: {body.get('research_method')}")
            print(f"   Topics: {', '.join(body.get('topics_identified', []))}")
            print(f"   Sources Selected: {body.get('sources_selected', [])}")
            print(f"   Sources Checked: {body.get('sources_checked', 0)}")
            print(f"\n   Explanation: {body.get('explanation', '')[:300]}...")
            
        else:
            print(f"❌ Failed: Status {result.get('statusCode')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n{'=' * 70}")
print("Test Complete")
print(f"{'=' * 70}")
