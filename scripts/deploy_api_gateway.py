#!/usr/bin/env python3
"""
Deploy API Gateway for VeriGov AI Lambda function
Creates REST API with CORS support
"""

import boto3
import json
import os
import sys
import time

def get_lambda_arn(lambda_client, function_name, region):
    """Get Lambda function ARN"""
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        return response['Configuration']['FunctionArn']
    except Exception as e:
        print(f"❌ Lambda function not found: {function_name}")
        print(f"   Error: {e}")
        print(f"\n   Please deploy Lambda first:")
        print(f"   python scripts/deploy_lambda.py")
        return None


def create_rest_api(apigateway_client, api_name):
    """Create or get REST API"""
    print(f"🌐 Creating REST API: {api_name}...")
    
    # Check if API already exists
    response = apigateway_client.get_rest_apis()
    for api in response.get('items', []):
        if api['name'] == api_name:
            print(f"✅ API already exists: {api['id']}")
            return api['id']
    
    # Create new API
    response = apigateway_client.create_rest_api(
        name=api_name,
        description='VeriGov AI Verification API',
        endpointConfiguration={'types': ['REGIONAL']}
    )
    
    api_id = response['id']
    print(f"✅ Created API: {api_id}")
    return api_id


def get_root_resource(apigateway_client, api_id):
    """Get root resource ID"""
    response = apigateway_client.get_resources(restApiId=api_id)
    for resource in response['items']:
        if resource['path'] == '/':
            return resource['id']
    return None


def create_resource(apigateway_client, api_id, parent_id, path_part):
    """Create API resource"""
    # Check if resource exists
    response = apigateway_client.get_resources(restApiId=api_id)
    for resource in response['items']:
        if resource.get('pathPart') == path_part:
            print(f"✅ Resource exists: /{path_part}")
            return resource['id']
    
    # Create new resource
    response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=parent_id,
        pathPart=path_part
    )
    print(f"✅ Created resource: /{path_part}")
    return response['id']


def create_method(apigateway_client, api_id, resource_id, http_method):
    """Create API method"""
    try:
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            authorizationType='NONE'
        )
        print(f"✅ Created method: {http_method}")
    except apigateway_client.exceptions.ConflictException:
        print(f"✅ Method exists: {http_method}")


def create_integration(apigateway_client, api_id, resource_id, http_method, lambda_arn, region, account_id):
    """Create Lambda integration"""
    lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
    
    try:
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        print(f"✅ Created Lambda integration")
    except apigateway_client.exceptions.ConflictException:
        print(f"✅ Integration exists")


def enable_cors(apigateway_client, api_id, resource_id):
    """Enable CORS for resource"""
    print("🔓 Enabling CORS...")
    
    # Create OPTIONS method
    try:
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
    except apigateway_client.exceptions.ConflictException:
        pass
    
    # Create mock integration for OPTIONS
    try:
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
    except apigateway_client.exceptions.ConflictException:
        pass
    
    # Set up OPTIONS method response
    try:
        apigateway_client.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
    except apigateway_client.exceptions.ConflictException:
        pass
    
    # Set up OPTIONS integration response
    try:
        apigateway_client.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
    except apigateway_client.exceptions.ConflictException:
        pass
    
    print("✅ CORS enabled")


def add_lambda_permission(lambda_client, function_name, api_id, region, account_id):
    """Add permission for API Gateway to invoke Lambda"""
    print("🔐 Adding Lambda invoke permission...")
    
    source_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*"
    
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'apigateway-invoke-{api_id}',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn
        )
        print("✅ Permission added")
    except lambda_client.exceptions.ResourceConflictException:
        print("✅ Permission already exists")


def deploy_api(apigateway_client, api_id, stage_name):
    """Deploy API to stage"""
    print(f"🚀 Deploying API to stage: {stage_name}...")
    
    response = apigateway_client.create_deployment(
        restApiId=api_id,
        stageName=stage_name,
        description=f'Deployment to {stage_name}'
    )
    
    print(f"✅ Deployed to {stage_name}")
    return response['id']


def test_api_endpoint(url):
    """Test API endpoint"""
    print(f"🧪 Testing API endpoint...")
    
    import requests
    
    test_payload = {
        'claim': 'The Earth orbits the Sun',
        'sources': []
    }
    
    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ API test successful!")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Confidence: {result.get('confidence')}%")
            return True
        else:
            print(f"❌ API test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False


def main():
    """Main deployment function"""
    print("🌐 VeriGov API Gateway Deployment")
    print("=" * 50)
    
    # Configuration
    region = os.environ.get('AWS_REGION', 'ap-south-1')
    environment = os.environ.get('ENVIRONMENT', 'dev')
    function_name = f"verigov-{environment}-verify"
    api_name = f"verigov-{environment}-api"
    stage_name = environment
    
    print(f"Region: {region}")
    print(f"Environment: {environment}")
    print(f"API Name: {api_name}")
    print()
    
    # Initialize AWS clients
    apigateway_client = boto3.client('apigateway', region_name=region)
    lambda_client = boto3.client('lambda', region_name=region)
    sts_client = boto3.client('sts', region_name=region)
    
    # Get account ID
    account_id = sts_client.get_caller_identity()['Account']
    
    try:
        # Step 1: Get Lambda ARN
        lambda_arn = get_lambda_arn(lambda_client, function_name, region)
        if not lambda_arn:
            return 1
        
        print(f"Lambda ARN: {lambda_arn}")
        print()
        
        # Step 2: Create REST API
        api_id = create_rest_api(apigateway_client, api_name)
        
        # Step 3: Get root resource
        root_id = get_root_resource(apigateway_client, api_id)
        
        # Step 4: Create /api resource
        api_resource_id = create_resource(apigateway_client, api_id, root_id, 'api')
        
        # Step 5: Create /api/verify resource
        verify_resource_id = create_resource(apigateway_client, api_id, api_resource_id, 'verify')
        
        # Step 6: Create POST method
        create_method(apigateway_client, api_id, verify_resource_id, 'POST')
        
        # Step 7: Create Lambda integration
        create_integration(apigateway_client, api_id, verify_resource_id, 'POST', lambda_arn, region, account_id)
        
        # Step 8: Enable CORS
        enable_cors(apigateway_client, api_id, verify_resource_id)
        
        # Step 9: Add Lambda permission
        add_lambda_permission(lambda_client, function_name, api_id, region, account_id)
        
        # Step 10: Deploy API
        deployment_id = deploy_api(apigateway_client, api_id, stage_name)
        
        # Construct API URL
        api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage_name}/api/verify"
        
        # Success!
        print()
        print("=" * 50)
        print("✅ API Gateway Deployment Complete!")
        print()
        print(f"🌐 API Endpoint URL:")
        print(f"   {api_url}")
        print()
        print("📋 API Details:")
        print(f"   API ID: {api_id}")
        print(f"   Stage: {stage_name}")
        print(f"   Region: {region}")
        print()
        
        # Test the endpoint
        print("Testing endpoint...")
        test_api_endpoint(api_url)
        
        print()
        print("📝 Next Steps:")
        print(f"1. Update static/script.js to use this URL:")
        print(f"   const API_ENDPOINT = '{api_url}';")
        print()
        print(f"2. Test with curl:")
        print(f"   curl -X POST {api_url} \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"claim\": \"Test claim\"}}'")
        print()
        print(f"3. Share this URL with hackathon judges!")
        
        # Save URL to file
        with open('API_ENDPOINT.txt', 'w') as f:
            f.write(api_url)
        print()
        print("✅ API URL saved to API_ENDPOINT.txt")
        
        return 0
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
