#!/usr/bin/env python3
"""Quick Lambda upload using existing zip"""
import boto3
import json
import os
import sys

region = os.environ.get('AWS_REGION', 'ap-south-1')
environment = os.environ.get('ENVIRONMENT', 'dev')
function_name = f"verigov-{environment}-verify"
role_name = f"verigov-{environment}-lambda-role"

print(f"Uploading Lambda: {function_name}")

lambda_client = boto3.client('lambda', region_name=region)
iam_client = boto3.client('iam', region_name=region)

# Get role ARN
try:
    role = iam_client.get_role(RoleName=role_name)
    role_arn = role['Role']['Arn']
    print(f"Using role: {role_arn}")
except:
    print(f"ERROR: Role {role_name} not found. Creating...")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    role = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy)
    )
    role_arn = role['Role']['Arn']
    
    # Attach policies
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    )
    print("Created role, waiting 10 seconds...")
    import time
    time.sleep(10)

# Read zip
with open('lambda_deployment_fixed.zip', 'rb') as f:
    zip_data = f.read()

print(f"Zip size: {len(zip_data) / 1024 / 1024:.2f} MB")

# Get env vars
groq_key = os.environ.get('GROQ_API_KEY')
if not groq_key:
    print("ERROR: GROQ_API_KEY not set")
    sys.exit(1)

env_vars = {
    'GROQ_API_KEY': groq_key,
    'ENVIRONMENT': environment
}

# Deploy
try:
    print("Creating function...")
    response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.11',
        Role=role_arn,
        Handler='verify_handler.lambda_handler',
        Code={'ZipFile': zip_data},
        Timeout=30,
        MemorySize=512,
        Environment={'Variables': env_vars}
    )
    print(f"✅ Created: {response['FunctionArn']}")
except lambda_client.exceptions.ResourceConflictException:
    print("Function exists, updating...")
    lambda_client.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_data
    )
    print("✅ Updated code")
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName=function_name)
    
    lambda_client.update_function_configuration(
        FunctionName=function_name,
        Environment={'Variables': env_vars}
    )
    print("✅ Updated config")

# Test
print("\nTesting...")
test_event = {'body': json.dumps({'claim': 'Test', 'sources': []})}
response = lambda_client.invoke(
    FunctionName=function_name,
    Payload=json.dumps(test_event)
)
result = json.loads(response['Payload'].read())
print(f"Status: {response['StatusCode']}")
print(f"Result: {result}")

print("\n✅ Done! Run: python scripts/deploy_api_gateway.py")
