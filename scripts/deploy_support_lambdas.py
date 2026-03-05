"""
Deploy audit and whitelist Lambda functions
"""
import boto3
import zipfile
import os
from io import BytesIO

# Configuration
REGION = 'ap-south-1'
ROLE_ARN = 'arn:aws:iam::448772857627:role/verigov-dev-lambda-role'

lambda_client = boto3.client('lambda', region_name=REGION)
apigateway = boto3.client('apigateway', region_name=REGION)

# Lambda configurations
LAMBDAS = [
    {
        'name': 'verigov-dev-audit',
        'handler': 'audit_handler.lambda_handler',
        'file': 'lambda/audit_handler.py',
        'env_vars': {
            'AUDIT_TABLE': 'verigov-dev-audit-logs'
        }
    },
    {
        'name': 'verigov-dev-whitelist',
        'handler': 'whitelist_handler.lambda_handler',
        'file': 'lambda/whitelist_handler.py',
        'env_vars': {
            'WHITELIST_TABLE': 'verigov-dev-whitelist'
        }
    }
]


def create_lambda_zip(handler_file):
    """Create a zip file for Lambda deployment"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the handler file
        handler_name = os.path.basename(handler_file)
        zip_file.write(handler_file, handler_name)
    
    zip_buffer.seek(0)
    return zip_buffer.read()


def deploy_lambda(config):
    """Deploy or update a Lambda function"""
    function_name = config['name']
    handler = config['handler']
    handler_file = config['file']
    env_vars = config['env_vars']
    
    print(f"\n{'='*60}")
    print(f"Deploying Lambda: {function_name}")
    print(f"{'='*60}")
    
    # Create zip file
    print("Creating deployment package...")
    zip_content = create_lambda_zip(handler_file)
    print(f"Package size: {len(zip_content) / 1024:.2f} KB")
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            function_exists = True
            print(f"Function exists, updating...")
        except lambda_client.exceptions.ResourceNotFoundException:
            function_exists = False
            print(f"Function doesn't exist, creating...")
        
        if function_exists:
            # Update existing function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ Code updated successfully")
            
            # Update environment variables
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                Environment={'Variables': env_vars}
            )
            print(f"✅ Configuration updated")
            
        else:
            # Create new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=ROLE_ARN,
                Handler=handler,
                Code={'ZipFile': zip_content},
                Timeout=30,
                MemorySize=256,
                Environment={'Variables': env_vars}
            )
            print(f"✅ Function created successfully")
        
        function_arn = response['FunctionArn']
        print(f"Function ARN: {function_arn}")
        
        return function_arn
        
    except Exception as e:
        print(f"❌ Error deploying {function_name}: {str(e)}")
        return None


def create_api_endpoint(function_name, function_arn, path):
    """Create API Gateway endpoint for Lambda"""
    try:
        # Get existing API
        apis = apigateway.get_rest_apis()
        api_id = None
        
        for api in apis['items']:
            if api['name'] == 'verigov-dev-api':
                api_id = api['id']
                break
        
        if not api_id:
            print(f"❌ API Gateway 'verigov-dev-api' not found")
            return None
        
        print(f"\nCreating API endpoint: {path}")
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_id = resource['id']
                break
        
        # Create resource for the path
        try:
            resource = apigateway.create_resource(
                restApiId=api_id,
                parentId=root_id,
                pathPart=path
            )
            resource_id = resource['id']
            print(f"✅ Resource created: {path}")
        except apigateway.exceptions.ConflictException:
            # Resource already exists, get it
            for resource in resources['items']:
                if resource['path'] == f'/{path}':
                    resource_id = resource['id']
                    print(f"Resource already exists: {path}")
                    break
        
        # Create GET method
        try:
            apigateway.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='GET',
                authorizationType='NONE'
            )
            print(f"✅ GET method created")
        except apigateway.exceptions.ConflictException:
            print(f"GET method already exists")
        
        # Set up Lambda integration
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='GET',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{function_arn}/invocations'
        )
        print(f"✅ Lambda integration configured")
        
        # Add Lambda permission
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'apigateway-{path}-get',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:{REGION}:448772857627:{api_id}/*/*/{path}'
            )
            print(f"✅ Lambda permission added")
        except lambda_client.exceptions.ResourceConflictException:
            print(f"Lambda permission already exists")
        
        # Deploy API
        apigateway.create_deployment(
            restApiId=api_id,
            stageName='dev'
        )
        print(f"✅ API deployed")
        
        endpoint = f"https://{api_id}.execute-api.{REGION}.amazonaws.com/dev/{path}"
        print(f"Endpoint: {endpoint}")
        
        return endpoint
        
    except Exception as e:
        print(f"❌ Error creating API endpoint: {str(e)}")
        return None


def main():
    print("="*60)
    print("VeriGov AI - Deploy Support Lambda Functions")
    print("="*60)
    
    endpoints = {}
    
    # Deploy Lambda functions
    for config in LAMBDAS:
        function_arn = deploy_lambda(config)
        
        if function_arn:
            # Create API endpoint
            path = config['name'].split('-')[-1]  # Extract 'audit' or 'whitelist'
            endpoint = create_api_endpoint(config['name'], function_arn, path)
            
            if endpoint:
                endpoints[path] = endpoint
    
    # Print summary
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    
    if endpoints:
        print("\n✅ API Endpoints:")
        for path, endpoint in endpoints.items():
            print(f"  {path}: {endpoint}")
        
        print("\n📝 Update these endpoints in static/script.js:")
        print(f"  const API_ENDPOINT_AUDIT = '{endpoints.get('audit', 'NOT_DEPLOYED')}';")
        print(f"  const API_ENDPOINT_WHITELIST = '{endpoints.get('whitelist', 'NOT_DEPLOYED')}';")
    else:
        print("\n❌ No endpoints deployed")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
