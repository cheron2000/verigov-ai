#!/usr/bin/env python3
"""Monitor AWS usage and costs for VeriGov AI"""

import boto3
from datetime import datetime

def monitor_usage():
    """Monitor DynamoDB and S3 usage"""
    
    print("=" * 60)
    print("📊 VERIGOV AI - AWS USAGE MONITOR")
    print("=" * 60)
    
    region = 'ap-south-1'
    env = 'dev'
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    # DynamoDB monitoring
    print("\n🗄️  DYNAMODB TABLES")
    print("-" * 60)
    
    dynamodb = boto3.client('dynamodb', region_name=region)
    
    tables = [
        f'verigov-{env}-audit-logs',
        f'verigov-{env}-verifications',
        f'verigov-{env}-whitelist'
    ]
    
    total_size = 0
    total_items = 0
    
    for table_name in tables:
        try:
            response = dynamodb.describe_table(TableName=table_name)
            table = response['Table']
            
            size_bytes = table['TableSizeBytes']
            item_count = table['ItemCount']
            
            total_size += size_bytes
            total_items += item_count
            
            print(f"\n📋 {table_name}:")
            print(f"   Items: {item_count}")
            print(f"   Size: {size_bytes:,} bytes ({size_bytes/1024:.2f} KB)")
            print(f"   Status: {table['TableStatus']}")
            print(f"   Billing: {table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')}")
            
        except Exception as e:
            print(f"\n❌ {table_name}: {e}")
    
    print(f"\n📊 Total DynamoDB:")
    print(f"   Items: {total_items}")
    print(f"   Size: {total_size:,} bytes ({total_size/1024:.2f} KB)")
    
    # S3 monitoring
    print("\n\n🪣 S3 BUCKET")
    print("-" * 60)
    
    s3 = boto3.client('s3', region_name=region)
    bucket_name = f'verigov-{env}-data-{account_id}'
    
    try:
        # List all objects
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)
        
        file_count = 0
        total_s3_size = 0
        file_types = {}
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    file_count += 1
                    total_s3_size += obj['Size']
                    
                    # Categorize by prefix
                    key = obj['Key']
                    if key.startswith('audit/'):
                        file_types['audit'] = file_types.get('audit', 0) + 1
                    elif key.startswith('results/'):
                        file_types['results'] = file_types.get('results', 0) + 1
                    elif key.startswith('batch/'):
                        file_types['batch'] = file_types.get('batch', 0) + 1
        
        print(f"\n🪣 {bucket_name}:")
        print(f"   Total Files: {file_count}")
        print(f"   Total Size: {total_s3_size:,} bytes ({total_s3_size/1024:.2f} KB)")
        
        print(f"\n   File Breakdown:")
        for file_type, count in file_types.items():
            print(f"      {file_type}: {count} files")
        
    except Exception as e:
        print(f"\n❌ Error accessing S3: {e}")
    
    # Cost estimation
    print("\n\n💰 ESTIMATED COSTS")
    print("-" * 60)
    
    # DynamoDB costs (on-demand pricing)
    # Assuming 100 writes and 50 reads per day
    writes_per_month = 100 * 30  # 3,000 writes
    reads_per_month = 50 * 30    # 1,500 reads
    
    dynamodb_write_cost = (writes_per_month / 1_000_000) * 1.25  # $1.25 per million
    dynamodb_read_cost = (reads_per_month / 1_000_000) * 0.25    # $0.25 per million
    dynamodb_storage_cost = (total_size / 1024 / 1024 / 1024) * 0.25  # $0.25 per GB
    
    total_dynamodb_cost = dynamodb_write_cost + dynamodb_read_cost + dynamodb_storage_cost
    
    # S3 costs
    s3_storage_cost = (total_s3_size / 1024 / 1024 / 1024) * 0.023  # $0.023 per GB
    s3_request_cost = (writes_per_month / 1000) * 0.005  # $0.005 per 1,000 PUT
    
    total_s3_cost = s3_storage_cost + s3_request_cost
    
    total_cost = total_dynamodb_cost + total_s3_cost
    
    print(f"\n📊 DynamoDB (estimated monthly):")
    print(f"   Write requests: ${dynamodb_write_cost:.4f}")
    print(f"   Read requests: ${dynamodb_read_cost:.4f}")
    print(f"   Storage: ${dynamodb_storage_cost:.4f}")
    print(f"   Subtotal: ${total_dynamodb_cost:.4f}")
    
    print(f"\n🪣 S3 (estimated monthly):")
    print(f"   Storage: ${s3_storage_cost:.4f}")
    print(f"   Requests: ${s3_request_cost:.4f}")
    print(f"   Subtotal: ${total_s3_cost:.4f}")
    
    print(f"\n💵 TOTAL ESTIMATED MONTHLY COST: ${total_cost:.4f}")
    
    if total_cost < 1:
        print(f"   ✅ Well within budget! (< $1/month)")
    elif total_cost < 5:
        print(f"   ✅ Within budget (< $5/month)")
    elif total_cost < 10:
        print(f"   ⚠️  Moderate usage (< $10/month)")
    else:
        print(f"   ⚠️  High usage! Review and optimize")
    
    # Recommendations
    print("\n\n💡 COST OPTIMIZATION TIPS")
    print("-" * 60)
    print("✅ Using PAY_PER_REQUEST billing (most cost-effective)")
    print("✅ Using eventually consistent reads for audit logs")
    print("✅ Lifecycle policy: Old versions deleted after 30 days")
    print("✅ Lifecycle policy: Audit logs moved to IA after 90 days")
    
    if total_items > 1000:
        print("\n⚠️  Consider:")
        print("   • Archive old data to S3 Glacier")
        print("   • Delete unnecessary test data")
    
    if file_count > 100:
        print("\n⚠️  S3 file count is high:")
        print("   • Consider consolidating old audit logs")
        print("   • Enable lifecycle policies for automatic cleanup")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        monitor_usage()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()