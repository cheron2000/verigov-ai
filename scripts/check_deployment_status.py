#!/usr/bin/env python3
"""Check if Lambda deployment is complete"""
import boto3
import json

region = 'ap-south-1'
function_name = 'verigov-dev-verify-sources'

lambda_client = boto3.client('lambda', region_name=region)

try:
    print("Checking Lambda status...")
    response = lambda_client.get_function(FunctionName=function_name)
    config = response['Configuration']
    
    print(f"\n✅ Function: {config['FunctionName']}")
    print(f"   State: {config['State']}")
    print(f"   Last Update: {config.get('LastUpdateStatus', 'Unknown')}")
    print(f"   Code Size: {config['CodeSize'] / 1024 / 1024:.2f} MB")
    print(f"   Last Modified: {config['LastModified']}")
    
    if config['State'] == 'Active' and config.get('LastUpdateStatus') == 'Successful':
        print("\n✅ Lambda is ready!")
    elif config.get('LastUpdateStatus') == 'InProgress':
        print("\n⏳ Update in progress...")
    else:
        print(f"\n⚠️  State: {config['State']}, Update: {config.get('LastUpdateStatus')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
