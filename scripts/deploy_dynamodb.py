#!/usr/bin/env python3
"""Deploy DynamoDB tables using CloudFormation"""

import os
import sys
import time
import argparse

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("❌ boto3 is required. Install with: pip install boto3")
    sys.exit(1)


def deploy_dynamodb_tables(environment='dev', region='us-east-1'):
    """Deploy DynamoDB tables using CloudFormation
    
    Args:
        environment: Environment name (dev or prod)
        region: AWS region
    """
    print(f"🚀 Deploying DynamoDB tables for {environment} environment in {region}...")
    
    # Initialize CloudFormation client
    cf = boto3.client('cloudformation', region_name=region)
    
    # Read CloudFormation template
    template_path = 'infrastructure/cloudformation/dynamodb-tables.yaml'
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        template_body = f.read()
    
    stack_name = f'verigov-{environment}-dynamodb'
    
    try:
        # Check if stack exists
        try:
            cf.describe_stacks(StackName=stack_name)
            stack_exists = True
            print(f"📦 Stack {stack_name} exists, updating...")
        except ClientError as e:
            if 'does not exist' in str(e):
                stack_exists = False
                print(f"📦 Creating new stack {stack_name}...")
            else:
                raise
        
        # Create or update stack
        if stack_exists:
            response = cf.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'Environment',
                        'ParameterValue': environment
                    }
                ],
                Capabilities=['CAPABILITY_IAM']
            )
            print(f"⏳ Updating stack {stack_name}...")
            waiter = cf.get_waiter('stack_update_complete')
        else:
            response = cf.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'Environment',
                        'ParameterValue': environment
                    }
                ],
                Capabilities=['CAPABILITY_IAM'],
                Tags=[
                    {'Key': 'Environment', 'Value': environment},
                    {'Key': 'Application', 'Value': 'VeriGov-AI'}
                ]
            )
            print(f"⏳ Creating stack {stack_name}...")
            waiter = cf.get_waiter('stack_create_complete')
        
        # Wait for stack operation to complete
        try:
            waiter.wait(StackName=stack_name)
        except Exception as e:
            print(f"⚠️  Stack operation may have failed: {e}")
            return False
        
        # Get stack outputs
        response = cf.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        print(f"\n✅ Stack {stack_name} deployed successfully!")
        print(f"📊 Stack Status: {stack['StackStatus']}")
        
        if 'Outputs' in stack:
            print("\n📋 Stack Outputs:")
            for output in stack['Outputs']:
                print(f"  {output['OutputKey']}: {output['OutputValue']}")
        
        # Verify tables are active
        print("\n🔍 Verifying tables...")
        dynamodb = boto3.client('dynamodb', region_name=region)
        
        tables = [
            f'verigov-{environment}-audit-logs',
            f'verigov-{environment}-verifications',
            f'verigov-{environment}-whitelist'
        ]
        
        for table_name in tables:
            try:
                response = dynamodb.describe_table(TableName=table_name)
                status = response['Table']['TableStatus']
                print(f"  ✅ {table_name}: {status}")
            except ClientError as e:
                print(f"  ❌ {table_name}: {e}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        if error_code == 'ValidationError' and 'No updates are to be performed' in error_msg:
            print(f"✅ Stack {stack_name} is already up to date")
            return True
        else:
            print(f"❌ CloudFormation error: {error_msg}")
            return False
    
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False


def delete_dynamodb_tables(environment='dev', region='us-east-1'):
    """Delete DynamoDB tables by deleting CloudFormation stack
    
    Args:
        environment: Environment name (dev or prod)
        region: AWS region
    """
    stack_name = f'verigov-{environment}-dynamodb'
    
    print(f"🗑️  Deleting stack {stack_name}...")
    
    cf = boto3.client('cloudformation', region_name=region)
    
    try:
        cf.delete_stack(StackName=stack_name)
        print(f"⏳ Waiting for stack deletion...")
        
        waiter = cf.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)
        
        print(f"✅ Stack {stack_name} deleted successfully!")
        return True
        
    except ClientError as e:
        print(f"❌ Error deleting stack: {e.response['Error']['Message']}")
        return False


def check_table_status(environment='dev', region='us-east-1'):
    """Check status of DynamoDB tables
    
    Args:
        environment: Environment name (dev or prod)
        region: AWS region
    """
    print(f"🔍 Checking DynamoDB tables for {environment} environment...")
    
    dynamodb = boto3.client('dynamodb', region_name=region)
    
    tables = [
        f'verigov-{environment}-audit-logs',
        f'verigov-{environment}-verifications',
        f'verigov-{environment}-whitelist'
    ]
    
    for table_name in tables:
        try:
            response = dynamodb.describe_table(TableName=table_name)
            table = response['Table']
            
            print(f"\n📊 {table_name}:")
            print(f"  Status: {table['TableStatus']}")
            print(f"  Item Count: {table['ItemCount']}")
            print(f"  Size: {table['TableSizeBytes']} bytes")
            print(f"  Billing Mode: {table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')}")
            
            if 'GlobalSecondaryIndexes' in table:
                print(f"  GSIs: {len(table['GlobalSecondaryIndexes'])}")
                for gsi in table['GlobalSecondaryIndexes']:
                    print(f"    - {gsi['IndexName']}: {gsi['IndexStatus']}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"\n❌ {table_name}: Not found")
            else:
                print(f"\n❌ {table_name}: {e.response['Error']['Message']}")


def main():
    parser = argparse.ArgumentParser(description='Deploy DynamoDB tables for VeriGov AI')
    parser.add_argument('action', choices=['deploy', 'delete', 'status'],
                       help='Action to perform')
    parser.add_argument('--environment', '-e', default='dev', choices=['dev', 'prod'],
                       help='Environment (default: dev)')
    parser.add_argument('--region', '-r', default='us-east-1',
                       help='AWS region (default: us-east-1)')
    
    args = parser.parse_args()
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"🔐 AWS Account: {identity['Account']}")
        print(f"👤 User: {identity['Arn']}\n")
    except Exception as e:
        print(f"❌ AWS credentials not configured: {e}")
        sys.exit(1)
    
    if args.action == 'deploy':
        success = deploy_dynamodb_tables(args.environment, args.region)
        sys.exit(0 if success else 1)
    elif args.action == 'delete':
        # Confirm deletion
        confirm = input(f"⚠️  Are you sure you want to delete {args.environment} tables? (yes/no): ")
        if confirm.lower() == 'yes':
            success = delete_dynamodb_tables(args.environment, args.region)
            sys.exit(0 if success else 1)
        else:
            print("❌ Deletion cancelled")
            sys.exit(0)
    elif args.action == 'status':
        check_table_status(args.environment, args.region)
        sys.exit(0)


if __name__ == '__main__':
    main()