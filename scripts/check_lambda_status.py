#!/usr/bin/env python3
import boto3
import json

region = 'ap-south-1'
function_name = 'verigov-dev-verify'

lambda_client = boto3.client('lambda', region_name=region)

try:
    response = lambda_client.get_function(FunctionName=function_name)
    config = response['Configuration']
    
    print(f"✅ Lambda Function: {config['FunctionName']}")
    print(f"   State: {config['State']}")
    print(f"   Runtime: {config['Runtime']}")
    print(f"   Memory: {config['MemorySize']} MB")
    print(f"   Timeout: {config['Timeout']}s")
    print(f"   Last Modified: {config['LastModified']}")
    print(f"   Code Size: {config['CodeSize'] / 1024 / 1024:.2f} MB")
    
    # Test invoke
    print("\n🧪 Testing Lambda...")
    test_event = {'body': json.dumps({'claim': 'Test', 'sources': []})}
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(test_event)
    )
    
    result = json.loads(response['Payload'].read())
    print(f"   Status Code: {response['StatusCode']}")
    
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        print(f"   ✅ Test passed!")
        print(f"   Verification Status: {body.get('status')}")
        print(f"   Confidence: {body.get('confidence')}%")
    else:
        print(f"   ❌ Test failed:")
        print(f"   {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
