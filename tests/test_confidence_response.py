#!/usr/bin/env python3
"""Test to verify confidence score format from backend"""
import boto3
import json

region = 'ap-south-1'
function_name = 'verigov-dev-verify-sources'

lambda_client = boto3.client('lambda', region_name=region)

print("Testing Confidence Score Format")
print("=" * 70)

test_event = {
    'body': json.dumps({
        'claim': 'Who is Narendra Modi?',
        'sources': []
    })
}

response = lambda_client.invoke(
    FunctionName=function_name,
    Payload=json.dumps(test_event)
)

result = json.loads(response['Payload'].read())

if result.get('statusCode') == 200:
    body = json.loads(result['body'])
    
    print(f"Raw Response:")
    print(json.dumps(body, indent=2))
    
    print(f"\n\nConfidence Analysis:")
    print(f"  Type: {type(body.get('confidence'))}")
    print(f"  Value: {body.get('confidence')}")
    print(f"  Repr: {repr(body.get('confidence'))}")
    
    # Check if it's a number
    confidence = body.get('confidence')
    if isinstance(confidence, (int, float)):
        print(f"  ✅ Confidence is a number: {confidence}")
        print(f"  Display: {confidence}%")
    elif isinstance(confidence, str):
        print(f"  ⚠️  Confidence is a string: '{confidence}'")
        try:
            num_conf = float(confidence)
            print(f"  Can convert to: {num_conf}")
        except:
            print(f"  ❌ Cannot convert to number")
    else:
        print(f"  ❌ Unexpected type: {type(confidence)}")
        
else:
    print(f"Error: {result}")
