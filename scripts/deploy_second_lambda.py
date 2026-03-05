#!/usr/bin/env python3
"""Deploy second Lambda function with source fetching"""
import subprocess
import sys
import zipfile
import shutil
import boto3
import json
import os
from pathlib import Path

print("🔧 Building Lambda with source fetching...")
print("=" * 50)

region = 'ap-south-1'
environment = 'dev'
function_name = f'verigov-{environment}-verify-sources'
role_name = f'verigov-{environment}-lambda-role'

# Clean up
package_dir = Path("lambda_with_sources")
if package_dir.exists():
    shutil.rmtree(package_dir)
package_dir.mkdir()

# Copy enhanced handler
print("📄 Copying enhanced handler...")
shutil.copy("lambda/verify_handler_with_sources.py", package_dir / "verify_handler.py")

# Install dependencies
print("📦 Installing dependencies (this may take a minute)...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "-t", str(package_dir),
    "--upgrade", "--quiet",
    "requests", "boto3", "beautifulsoup4", "lxml"
])

# Create zip
zip_path = Path("lambda_with_sources.zip")
if zip_path.exists():
    zip_path.unlink()

print("📦 Creating deployment package...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(package_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if file.endswith('.pyc'):
                continue
            file_path = Path(root) / file
            arcname = file_path.relative_to(package_dir)
            zipf.write(file_path, arcname)

shutil.rmtree(package_dir)

size_mb = zip_path.stat().st_size / (1024 * 1024)
print(f"✅ Created: {zip_path} ({size_mb:.2f} MB)")

# Initialize AWS clients
lambda_client = boto3.client('lambda', region_name=region)
iam_client = boto3.client('iam', region_name=region)

# Get IAM role
print(f"\n🔐 Getting IAM role: {role_name}...")
role = iam_client.get_role(RoleName=role_name)
role_arn = role['Role']['Arn']
print(f"✅ Using role: {role_arn}")

# Get environment variables
groq_key = os.environ.get('GROQ_API_KEY', 'your-groq-api-key-here')

env_vars = {
    'GROQ_API_KEY': groq_key,
    'ENVIRONMENT': environment
}

# Read zip
with open(zip_path, 'rb') as f:
    zip_data = f.read()

# Deploy Lambda
print(f"\n🚀 Deploying Lambda: {function_name}...")

try:
    # Try to create new function
    response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.11',
        Role=role_arn,
        Handler='verify_handler.lambda_handler',
        Code={'ZipFile': zip_data},
        Description='VeriGov verification with source fetching',
        Timeout=60,  # Longer timeout for web scraping
        MemorySize=512,
        Environment={'Variables': env_vars}
    )
    print(f"✅ Created Lambda: {response['FunctionArn']}")
    function_arn = response['FunctionArn']
    
except lambda_client.exceptions.ResourceConflictException:
    # Function exists, update it
    print("Function exists, updating...")
    
    lambda_client.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_data
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName=function_name)
    
    response = lambda_client.update_function_configuration(
        FunctionName=function_name,
        Timeout=60,
        MemorySize=512,
        Environment={'Variables': env_vars}
    )
    
    print(f"✅ Updated Lambda: {response['FunctionArn']}")
    function_arn = response['FunctionArn']

# Test without sources
print("\n🧪 Test 1: Without sources (AI knowledge)...")
test_event1 = {
    'body': json.dumps({
        'claim': 'The Earth orbits the Sun',
        'sources': []
    })
}

response = lambda_client.invoke(
    FunctionName=function_name,
    Payload=json.dumps(test_event1)
)

result = json.loads(response['Payload'].read())
if result.get('statusCode') == 200:
    body = json.loads(result['body'])
    print(f"   ✅ Status: {body.get('status')}")
    print(f"   ✅ Confidence: {body.get('confidence')}%")
    print(f"   ✅ Sources Checked: {body.get('sources_checked')}")

# Test with sources
print("\n🧪 Test 2: With source URL (fetches content)...")
test_event2 = {
    'body': json.dumps({
        'claim': 'NASA has landed humans on the moon',
        'sources': ['https://www.nasa.gov/']
    })
}

response = lambda_client.invoke(
    FunctionName=function_name,
    Payload=json.dumps(test_event2)
)

result = json.loads(response['Payload'].read())
if result.get('statusCode') == 200:
    body = json.loads(result['body'])
    print(f"   ✅ Status: {body.get('status')}")
    print(f"   ✅ Confidence: {body.get('confidence')}%")
    print(f"   ✅ Sources Checked: {body.get('sources_checked')}")
    print(f"   ✅ Explanation: {body.get('explanation', '')[:100]}...")

print("\n" + "=" * 50)
print("✅ Second Lambda Deployed!")
print()
print(f"Function Name: {function_name}")
print(f"Function ARN: {function_arn}")
print()
print("📝 Next: Create API Gateway endpoint for this Lambda")
print("   Run: python scripts/deploy_second_api.py")
