#!/usr/bin/env python3
"""
Deploy Lambda function for VeriGov AI verification endpoint
Creates Lambda function with dependencies packaged as a layer
"""

import boto3
import json
import os
import sys
import zipfile
import subprocess
from pathlib import Path

def create_lambda_package():
    """Create deployment package with Lambda function code"""
    print("📦 Creating Lambda deployment package...")
    
    lambda_dir = Path("lambda")
    package_path = Path("lambda_package.zip")
    
    # Remove old package if exists
    if package_path.exists():
        package_path.unlink()
    
    # Create zip with Lambda handler
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(lambda_dir / "verify_handler.py", "verify_handler.py")
    
    print(f"✅ Created {package_path}")
    return package_path


def create_lambda_layer():
    """Create Lambda layer with dependencies"""
    print("📦 Creating Lambda layer with dependencies...")
    
    layer_dir = Path("lambda_layer")
    python_dir = layer_dir / "python"
    
    # Clean up old layer
    if layer_dir.exists():
        import shutil
        shutil.rmtree(layer_dir)
    
    python_dir.mkdir(parents=True, exist_ok=True)
    
    # Install dependencies
    print("Installing dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install",
        "-r", "lambda/requirements.txt",
        "-t", str(python_dir),
        "--upgrade"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to install dependencies: {result.stderr}")
        return None
    
    # Create layer zip
    layer_zip = Path("lambda_layer.zip")
    if layer_zip.exists():
        layer_zip.unlink()
    
    print("Creating layer zip...")
    with zipfile.ZipFile(layer_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(layer_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(layer_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created {layer_zip}")
    return layer_zip


def create_iam_role(iam_client, role_name):
    """Create IAM role for Lambda function"""
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
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"✅ Role already exists: {role_arn}")
    
    # Attach policies
    policies = [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    ]
    
    for policy_arn in policies:
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print(f"✅ Attached policy: {policy_arn.split('/')[-1]}")
        except Exception as e:
            if "already attached" not in str(e).lower():
                print(f"⚠️  Policy attachment: {e}")
    
    return role_arn


def publish_lambda_layer(lambda_client, layer_zip, layer_name):
    """Publish Lambda layer"""
    print(f"📤 Publishing Lambda layer: {layer_name}...")
    
    with open(layer_zip, 'rb') as f:
        layer_content = f.read()
    
    response = lambda_client.publish_layer_version(
        LayerName=layer_name,
        Description="Dependencies for VeriGov verification Lambda",
        Content={'ZipFile': layer_content},
        CompatibleRuntimes=['python3.11', 'python3.12']
    )
    
    layer_arn = response['LayerVersionArn']
    print(f"✅ Published layer: {layer_arn}")
    return layer_arn


def deploy_lambda_function(lambda_client, function_name, role_arn, package_path, layer_arn, environment):
    """Deploy or update Lambda function"""
    print(f"🚀 Deploying Lambda function: {function_name}...")
    
    with open(package_path, 'rb') as f:
        function_code = f.read()
    
    # Get environment variables
    groq_api_key = os.environ.get('GROQ_API_KEY')
    aws_region = os.environ.get('AWS_REGION', 'ap-south-1')
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return None
    
    env_vars = {
        'GROQ_API_KEY': groq_api_key,
        'AWS_REGION': aws_region,
        'ENVIRONMENT': environment
    }
    
    try:
        # Try to create new function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='verify_handler.lambda_handler',
            Code={'ZipFile': function_code},
            Description='VeriGov AI claim verification endpoint',
            Timeout=30,
            MemorySize=512,
            Environment={'Variables': env_vars},
            Layers=[layer_arn]
        )
        print(f"✅ Created Lambda function: {response['FunctionArn']}")
        return response['FunctionArn']
        
    except lambda_client.exceptions.ResourceConflictException:
        # Function exists, update it
        print("Function exists, updating...")
        
        # Update code
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=function_code
        )
        
        # Wait for update to complete
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        # Update configuration
        response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='verify_handler.lambda_handler',
            Timeout=30,
            MemorySize=512,
            Environment={'Variables': env_vars},
            Layers=[layer_arn]
        )
        
        print(f"✅ Updated Lambda function: {response['FunctionArn']}")
        return response['FunctionArn']


def test_lambda_function(lambda_client, function_name):
    """Test Lambda function with sample payload"""
    print(f"🧪 Testing Lambda function...")
    
    test_event = {
        'body': json.dumps({
            'claim': 'The Earth orbits the Sun',
            'sources': []
        })
    }
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(test_event)
    )
    
    result = json.loads(response['Payload'].read())
    
    if response['StatusCode'] == 200:
        print(f"✅ Lambda test successful!")
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"❌ Lambda test failed: {result}")
        return False


def main():
    """Main deployment function"""
    print("🚀 VeriGov Lambda Deployment")
    print("=" * 50)
    
    # Configuration
    region = os.environ.get('AWS_REGION', 'ap-south-1')
    environment = os.environ.get('ENVIRONMENT', 'dev')
    function_name = f"verigov-{environment}-verify"
    role_name = f"verigov-{environment}-lambda-role"
    layer_name = f"verigov-{environment}-dependencies"
    
    print(f"Region: {region}")
    print(f"Environment: {environment}")
    print(f"Function: {function_name}")
    print()
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda', region_name=region)
    iam_client = boto3.client('iam', region_name=region)
    
    try:
        # Step 1: Create Lambda package
        package_path = create_lambda_package()
        
        # Step 2: Create Lambda layer
        layer_zip = create_lambda_layer()
        if not layer_zip:
            print("❌ Failed to create Lambda layer")
            return 1
        
        # Step 3: Create IAM role
        role_arn = create_iam_role(iam_client, role_name)
        
        # Wait a bit for IAM role to propagate
        print("⏳ Waiting for IAM role to propagate...")
        import time
        time.sleep(10)
        
        # Step 4: Publish Lambda layer
        layer_arn = publish_lambda_layer(lambda_client, layer_zip, layer_name)
        
        # Step 5: Deploy Lambda function
        function_arn = deploy_lambda_function(
            lambda_client, function_name, role_arn, 
            package_path, layer_arn, environment
        )
        
        if not function_arn:
            return 1
        
        # Step 6: Test Lambda function
        print()
        test_lambda_function(lambda_client, function_name)
        
        # Success!
        print()
        print("=" * 50)
        print("✅ Deployment Complete!")
        print()
        print(f"Function ARN: {function_arn}")
        print(f"Function Name: {function_name}")
        print()
        print("Next steps:")
        print("1. Create API Gateway to expose this Lambda")
        print("2. Test the API endpoint")
        print("3. Update frontend to use API Gateway URL")
        
        return 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
