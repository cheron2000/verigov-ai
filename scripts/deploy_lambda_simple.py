#!/usr/bin/env python3
"""
Simple Lambda deployment - packages everything in one zip
"""

import boto3
import json
import os
import sys
import zipfile
import subprocess
import shutil
from pathlib import Path

def create_deployment_package():
    """Create single deployment package with all dependencies"""
    print("📦 Creating deployment package...")
    
    # Create temp directory
    package_dir = Path("lambda_package_temp")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy Lambda handler
    shutil.copy("lambda/verify_handler.py", package_dir / "verify_handler.py")
    
    # Install dependencies directly into package
    print("Installing dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install",
        "groq", "boto3",
        "-t", str(package_dir),
        "--upgrade", "--quiet"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Warning: {result.stderr}")
    
    # Create zip file
    zip_path = Path("lambda_deployment.zip")
    if zip_path.exists():
        zip_path.unlink()
    
    print("Creating zip file...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Cleanup
    shutil.rmtree(package_dir)
    
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✅ Created deployment package: {zip_path} ({size_mb:.2f} MB)")
    
    if size_mb > 50:
        print("⚠️  Warning: Package is large, may take time to upload")
    
    return zip_path


def create_iam_role(iam_client, role_name):
    """Create IAM role for Lambda"""
    print(f"🔐 Creating IAM role: {role_name}...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Execution role for VeriGov verification Lambda"
        )
        role_arn = response['Role']['Arn']
        print(f"✅ Created role: {role_arn}")
        is_new = True
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"✅ Role already exists: {role_arn}")
        is_new = False
    
    # Attach policies
    policies = [
        ("arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "Basic Execution"),
        ("arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess", "DynamoDB Access")
    ]
    
    for policy_arn, policy_name in policies:
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print(f"✅ Attached: {policy_name}")
        except Exception as e:
            if "already attached" not in str(e).lower():
                print(f"⚠️  {policy_name}: {e}")
    
    return role_arn, is_new


def deploy_lambda(lambda_client, function_name, role_arn, zip_path, environment):
    """Deploy Lambda function"""
    print(f"🚀 Deploying Lambda: {function_name}...")
    
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    groq_api_key = os.environ.get('GROQ_API_KEY')
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return None
    
    # Note: AWS_REGION is reserved by Lambda, it's automatically set
    env_vars = {
        'GROQ_API_KEY': groq_api_key,
        'ENVIRONMENT': environment
    }
    
    try:
        # Create new function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='verify_handler.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='VeriGov AI claim verification',
            Timeout=30,
            MemorySize=512,
            Environment={'Variables': env_vars}
        )
        print(f"✅ Created Lambda: {response['FunctionArn']}")
        return response['FunctionArn']
        
    except lambda_client.exceptions.ResourceConflictException:
        # Update existing function
        print("Function exists, updating...")
        
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        # Wait for update
        print("⏳ Waiting for update...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='verify_handler.lambda_handler',
            Timeout=30,
            MemorySize=512,
            Environment={'Variables': env_vars}
        )
        
        print(f"✅ Updated Lambda: {response['FunctionArn']}")
        return response['FunctionArn']


def test_lambda(lambda_client, function_name):
    """Test Lambda function"""
    print(f"🧪 Testing Lambda...")
    
    test_event = {
        'body': json.dumps({
            'claim': 'The Earth orbits the Sun',
            'sources': []
        })
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            body = json.loads(result.get('body', '{}'))
            print(f"✅ Test successful!")
            print(f"   Status: {body.get('status', 'N/A')}")
            print(f"   Confidence: {body.get('confidence', 'N/A')}%")
            return True
        else:
            print(f"❌ Test failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def main():
    print("🚀 VeriGov Lambda Deployment (Simple)")
    print("=" * 50)
    
    region = os.environ.get('AWS_REGION', 'ap-south-1')
    environment = os.environ.get('ENVIRONMENT', 'dev')
    function_name = f"verigov-{environment}-verify"
    role_name = f"verigov-{environment}-lambda-role"
    
    print(f"Region: {region}")
    print(f"Environment: {environment}")
    print(f"Function: {function_name}")
    print()
    
    lambda_client = boto3.client('lambda', region_name=region)
    iam_client = boto3.client('iam', region_name=region)
    
    try:
        # Step 1: Create deployment package
        zip_path = create_deployment_package()
        print()
        
        # Step 2: Create IAM role
        role_arn, is_new_role = create_iam_role(iam_client, role_name)
        print()
        
        # Wait for IAM role to propagate
        if is_new_role:
            print("⏳ Waiting for IAM role to propagate (10 seconds)...")
            import time
            time.sleep(10)
        
        # Step 3: Deploy Lambda
        function_arn = deploy_lambda(lambda_client, function_name, role_arn, zip_path, environment)
        if not function_arn:
            return 1
        print()
        
        # Step 4: Test Lambda
        test_lambda(lambda_client, function_name)
        
        # Success!
        print()
        print("=" * 50)
        print("✅ Lambda Deployment Complete!")
        print()
        print(f"Function ARN: {function_arn}")
        print(f"Function Name: {function_name}")
        print()
        print("Next step:")
        print("  python scripts/deploy_api_gateway.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
