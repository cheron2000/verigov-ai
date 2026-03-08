#!/usr/bin/env python3
"""Test multiple random claims one by one"""
import boto3
import json
import time

function_name = 'verigov-dev-verify-sources'
region = 'ap-south-1'
lambda_client = boto3.client('lambda', region_name=region)

# List of random claims to test
claims = [
    "The Earth orbits around the Sun",
    "Water boils at 100 degrees Celsius at sea level",
    "The human body has 206 bones",
    "The Great Wall of China is visible from space",
    "Bananas are berries",
    "Sharks are mammals",
    "The Amazon River is the longest river in the world",
    "Humans use only 10% of their brain",
    "Goldfish have a 3-second memory",
    "Bats are blind"
]

print("=" * 70)
print("Testing Random Claims")
print("=" * 70)

for i, claim in enumerate(claims, 1):
    print(f"\n{'=' * 70}")
    print(f"Claim {i}/{len(claims)}")
    print(f"Claim: {claim}")
    print(f"{'=' * 70}")
    
    test_event = {'body': json.dumps({'claim': claim, 'sources': []})}
    response = lambda_client.invoke(FunctionName=function_name, Payload=json.dumps(test_event))
    result = json.loads(response['Payload'].read())
    
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        
        print(f"Status: {body.get('status')}")
        print(f"Confidence: {body.get('confidence')}%")
        print(f"Research Method: {body.get('research_method')}")
        print(f"Topics: {', '.join(body.get('topics_identified', []))}")
        print(f"Sources Checked: {body.get('sources_checked', 0)}")
        
        if body.get('sources_selected'):
            print(f"Sources Selected: {body.get('sources_selected', [])}")
        
        print(f"\nExplanation: {body.get('explanation', '')[:250]}...")
        
        # Wait between requests to avoid rate limiting
        time.sleep(3)
    else:
        print(f"Error: {result}")
        # Wait longer on error to avoid rate limiting
        time.sleep(5)

print(f"\n{'=' * 70}")
print("Test Complete")
print(f"{'=' * 70}")
