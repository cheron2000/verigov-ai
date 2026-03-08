#!/usr/bin/env python3
"""Test a single random claim"""
import boto3
import json

function_name = 'verigov-dev-verify-sources'
region = 'ap-south-1'
lambda_client = boto3.client('lambda', region_name=region)

# Test claim: 'The Earth orbits around the Sun'
print("=" * 70)
print("Testing Random Fact: The Earth orbits around the Sun")
print("=" * 70)

test_event = {'body': json.dumps({'claim': 'The Earth orbits around the Sun', 'sources': []})}
response = lambda_client.invoke(FunctionName=function_name, Payload=json.dumps(test_event))
result = json.loads(response['Payload'].read())

if result.get('statusCode') == 200:
    body = json.loads(result['body'])
    print(json.dumps(body, indent=2))
else:
    print(f"Error: {result}")
