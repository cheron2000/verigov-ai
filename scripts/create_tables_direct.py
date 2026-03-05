#!/usr/bin/env python3
"""Create DynamoDB tables directly (without CloudFormation) - Cost optimized"""

import sys
import boto3
from botocore.exceptions import ClientError

def create_audit_logs_table(dynamodb, table_name):
    """Create audit logs table with minimal cost settings"""
    print(f"\n📋 Creating {table_name}...")
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'timestamp', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'event_type', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'event_type', 'AttributeType': 'S'},
                {'AttributeName': 'verification_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'verification_id-index',
                    'KeySchema': [
                        {'AttributeName': 'verification_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # Most cost-effective for low usage
            SSESpecification={'Enabled': True},  # Encryption at rest
            Tags=[
                {'Key': 'Environment', 'Value': 'dev'},
                {'Key': 'Application', 'Value': 'VeriGov-AI'},
                {'Key': 'CostCenter', 'Value': 'Development'}
            ]
        )
        
        print(f"   ✅ Table created: {table_name}")
        print(f"   💰 Billing: PAY_PER_REQUEST (only pay for actual usage)")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"   ⚠️  Table already exists: {table_name}")
            return True
        else:
            print(f"   ❌ Error: {e.response['Error']['Message']}")
            return False

def create_verifications_table(dynamodb, table_name):
    """Create verifications table with minimal cost settings"""
    print(f"\n📋 Creating {table_name}...")
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'verification_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'verification_id', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'},
                {'AttributeName': 'stored_at', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'status-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'},
                        {'AttributeName': 'stored_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            SSESpecification={'Enabled': True},
            Tags=[
                {'Key': 'Environment', 'Value': 'dev'},
                {'Key': 'Application', 'Value': 'VeriGov-AI'}
            ]
        )
        
        print(f"   ✅ Table created: {table_name}")
        print(f"   💰 Billing: PAY_PER_REQUEST")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"   ⚠️  Table already exists: {table_name}")
            return True
        else:
            print(f"   ❌ Error: {e.response['Error']['Message']}")
            return False

def create_whitelist_table(dynamodb, table_name):
    """Create whitelist table with minimal cost settings"""
    print(f"\n📋 Creating {table_name}...")
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'domain', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'domain', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST',
            SSESpecification={'Enabled': True},
            Tags=[
                {'Key': 'Environment', 'Value': 'dev'},
                {'Key': 'Application', 'Value': 'VeriGov-AI'}
            ]
        )
        
        print(f"   ✅ Table created: {table_name}")
        print(f"   💰 Billing: PAY_PER_REQUEST")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"   ⚠️  Table already exists: {table_name}")
            return True
        else:
            print(f"   ❌ Error: {e.response['Error']['Message']}")
            return False

def wait_for_tables(dynamodb, table_names):
    """Wait for tables to become active"""
    print(f"\n⏳ Waiting for tables to become ACTIVE...")
    
    for table_name in table_names:
        try:
            waiter = dynamodb.meta.client.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"   ✅ {table_name} is ACTIVE")
        except Exception as e:
            print(f"   ⚠️  {table_name}: {e}")

def main():
    print("=" * 60)
    print("🚀 CREATING DYNAMODB TABLES (COST-OPTIMIZED)")
    print("=" * 60)
    
    region = 'ap-south-1'
    env = 'dev'
    
    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=region)
    
    # Table names
    tables = {
        'audit_logs': f'verigov-{env}-audit-logs',
        'verifications': f'verigov-{env}-verifications',
        'whitelist': f'verigov-{env}-whitelist'
    }
    
    print(f"\n📍 Region: {region}")
    print(f"🏷️  Environment: {env}")
    print(f"💰 Billing Mode: PAY_PER_REQUEST (most cost-effective)")
    
    # Create tables
    success = True
    success &= create_audit_logs_table(dynamodb, tables['audit_logs'])
    success &= create_verifications_table(dynamodb, tables['verifications'])
    success &= create_whitelist_table(dynamodb, tables['whitelist'])
    
    if success:
        # Wait for tables to be active
        wait_for_tables(dynamodb, list(tables.values()))
        
        print("\n" + "=" * 60)
        print("✅ ALL TABLES CREATED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n💰 COST INFORMATION:")
        print("   • Billing Mode: PAY_PER_REQUEST (on-demand)")
        print("   • No charges when idle")
        print("   • Write: $1.25 per million requests")
        print("   • Read: $0.25 per million requests")
        print("   • Expected cost: < $1/month for development")
        
        print("\n📊 NEXT STEPS:")
        print("   1. Check status: python scripts/check_status.py")
        print("   2. Test AWS storage: python -m src.verigov.main --storage aws verify 'Test'")
        print("   3. Monitor costs: python scripts/check_aws_costs.py")
        
        print("\n⚠️  COST SAVING TIPS:")
        print("   • Use local storage for development when possible")
        print("   • Use hybrid mode only during migration")
        print("   • Delete tables when not needed: aws dynamodb delete-table --table-name <name>")
        print("   • Monitor usage regularly")
        
        print("=" * 60)
        return 0
    else:
        print("\n❌ Some tables failed to create")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)