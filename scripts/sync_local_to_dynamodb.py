#!/usr/bin/env python3
"""
Sync local verification data to DynamoDB
"""

import boto3
import json
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime

def convert_floats(obj):
    """Convert floats to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats(item) for item in obj]
    return obj

def sync_verifications():
    """Sync all local verifications to DynamoDB"""
    
    region = os.environ.get('AWS_REGION', 'ap-south-1')
    environment = os.environ.get('ENVIRONMENT', 'dev')
    table_name = f"verigov-{environment}-verifications"
    
    print(f"🔄 Syncing Local Verifications to DynamoDB")
    print(f"{'='*60}")
    print(f"Region: {region}")
    print(f"Table: {table_name}")
    print()
    
    # Connect to DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    # Get all local verification files
    verifications_dir = Path('data/verifications')
    verification_files = list(verifications_dir.glob('*.json'))
    
    print(f"📁 Found {len(verification_files)} local verification files")
    print()
    
    success_count = 0
    error_count = 0
    
    for file_path in verification_files:
        try:
            # Read verification data
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            verification_id = file_path.stem
            claim = data.get('claim', 'Unknown')
            
            # Add metadata
            item = convert_floats(data)
            if 'stored_at' not in item:
                item['stored_at'] = datetime.utcnow().isoformat() + 'Z'
            if 'verification_id' not in item:
                item['verification_id'] = verification_id
            
            # Upload to DynamoDB
            table.put_item(Item=item)
            
            print(f"✅ {verification_id[:8]}... - {claim[:50]}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {file_path.name} - Error: {e}")
            error_count += 1
    
    print()
    print(f"{'='*60}")
    print(f"✅ Synced: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total: {len(verification_files)}")
    print()
    
    if success_count > 0:
        print(f"🎉 Successfully synced {success_count} verifications to DynamoDB!")

if __name__ == "__main__":
    sync_verifications()
