#!/usr/bin/env python3
"""Test the live Lambda function with news-related claims"""
import boto3
import json

region = 'ap-south-1'
function_name = 'verigov-dev-verify-sources'

lambda_client = boto3.client('lambda', region_name=region)

print("=" * 70)
print("Testing Live Lambda with News Fetching")
print("=" * 70)

test_cases = [
    {
        'name': 'Space News (NASA)',
        'claim': 'NASA successfully landed the Perseverance rover on Mars'
    },
    {
        'name': 'Health News (WHO/CDC)',
        'claim': 'The WHO recommends vaccination against preventable diseases'
    },
    {
        'name': 'Breaking News (BBC/AP)',
        'claim': 'Recent developments in international relations'
    },
    {
        'name': 'US Government (White House)',
        'claim': 'The US government announced new climate policies'
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 70}")
    print(f"Test {i}: {test['name']}")
    print(f"Claim: {test['claim']}")
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
            print(f"   Note: {body.get('research_note', '')}")
            print(f"\n   Explanation: {body.get('explanation', '')[:200]}...")
            
            if body.get('sources_checked', 0) > 0:
                print(f"\n   🎉 Successfully fetched content from sources!")
            else:
                print(f"\n   ⚠️  No sources fetched (using AI knowledge base)")
        else:
            print(f"❌ Failed: Status {result.get('statusCode')}")
            print(f"   {result.get('body', '')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 70}")
print("Test Complete")
print(f"{'=' * 70}")
