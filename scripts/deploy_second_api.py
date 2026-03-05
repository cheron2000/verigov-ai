#!/usr/bin/env python3
"""Add second endpoint to API Gateway for source-fetching Lambda"""
import boto3
import json
import os

region = 'ap-south-1'
environment = 'dev'
api_id = 'qycb40y6n6'  # Existing API
function_name = f'verigov-{environment}-verify-sources'

print("🌐 Adding /api/verify-sources endpoint to API Gateway")
print("=" * 50)

apigateway = boto3.client('apigateway', region_name=region)
lambda_client = boto3.client('lambda', region_name=region)
sts = boto3.client('sts', region_name=region)

account_id = sts.get_caller_identity()['Account']

# Get Lambda ARN
lambda_response = lambda_client.get_function(FunctionName=function_name)
lambda_arn = lambda_response['Configuration']['FunctionArn']
print(f"Lambda ARN: {lambda_arn}")

# Get API resources
resources = apigateway.get_resources(restApiId=api_id)

# Find /api resource
api_resource = None
for resource in resources['items']:
    if resource.get('pathPart') == 'api':
        api_resource = resource
        break

if not api_resource:
    print("❌ /api resource not found")
    exit(1)

api_resource_id = api_resource['id']
print(f"✅ Found /api resource: {api_resource_id}")

# Create /verify-sources resource
print("📝 Creating /verify-sources resource...")
try:
    verify_sources_resource = apigateway.create_resource(
        restApiId=api_id,
        parentId=api_resource_id,
        pathPart='verify-sources'
    )
    verify_sources_id = verify_sources_resource['id']
    print(f"✅ Created resource: {verify_sources_id}")
except apigateway.exceptions.ConflictException:
    # Resource exists, find it
    for resource in resources['items']:
        if resource.get('pathPart') == 'verify-sources':
            verify_sources_id = resource['id']
            print(f"✅ Resource exists: {verify_sources_id}")
            break

# Create POST method
print("📝 Creating POST method...")
try:
    apigateway.put_method(
        restApiId=api_id,
        resourceId=verify_sources_id,
        httpMethod='POST',
        authorizationType='NONE'
    )
    print("✅ Created POST method")
except apigateway.exceptions.ConflictException:
    print("✅ POST method exists")

# Create Lambda integration
print("📝 Creating Lambda integration...")
lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"

try:
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=verify_sources_id,
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=lambda_uri
    )
    print("✅ Created integration")
except apigateway.exceptions.ConflictException:
    print("✅ Integration exists")

# Enable CORS
print("🔓 Enabling CORS...")
try:
    apigateway.put_method(
        restApiId=api_id,
        resourceId=verify_sources_id,
        httpMethod='OPTIONS',
        authorizationType='NONE'
    )
    
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=verify_sources_id,
        httpMethod='OPTIONS',
        type='MOCK',
        requestTemplates={'application/json': '{"statusCode": 200}'}
    )
    
    apigateway.put_method_response(
        restApiId=api_id,
        resourceId=verify_sources_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': False,
            'method.response.header.Access-Control-Allow-Methods': False,
            'method.response.header.Access-Control-Allow-Origin': False
        }
    )
    
    apigateway.put_integration_response(
        restApiId=api_id,
        resourceId=verify_sources_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'",
            'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'",
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        }
    )
    print("✅ CORS enabled")
except:
    print("✅ CORS already configured")

# Add Lambda permission
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
    print("✅ Permission exists")

# Deploy API
print("🚀 Deploying API...")
apigateway.create_deployment(
    restApiId=api_id,
    stageName=environment,
    description='Added verify-sources endpoint'
)
print("✅ Deployed")

# Construct URLs
fast_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{environment}/api/verify"
sources_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{environment}/api/verify-sources"

print("\n" + "=" * 50)
print("✅ API Gateway Updated!")
print()
print("📋 You now have TWO endpoints:")
print()
print("1️⃣  FAST (AI Knowledge Only):")
print(f"   {fast_url}")
print("   - Response time: ~1-2 seconds")
print("   - Uses AI's built-in knowledge")
print("   - No web scraping")
print()
print("2️⃣  WITH SOURCES (Fetches from URLs):")
print(f"   {sources_url}")
print("   - Response time: ~5-10 seconds")
print("   - Fetches content from provided URLs")
print("   - Analyzes actual source content")
print()
print("🧪 Test commands:")
print()
print("# Fast endpoint (no sources):")
print(f"curl -X POST {fast_url} \\")
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"claim": "The Earth orbits the Sun"}\'')
print()
print("# Sources endpoint (with URL):")
print(f"curl -X POST {sources_url} \\")
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"claim": "NASA landed on the moon", "sources": ["https://www.nasa.gov/"]}\'')
