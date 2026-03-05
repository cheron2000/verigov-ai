#!/usr/bin/env python3
"""Sync whitelist from local file to DynamoDB"""

import json
import boto3
from pathlib import Path

print("📋 Syncing Whitelist to DynamoDB")
print("=" * 50)

# Load local whitelist
whitelist_path = Path("config/whitelist.json")
with open(whitelist_path, 'r') as f:
    data = json.load(f)
    sources = data.get('sources', [])

print(f"✅ Loaded {len(sources)} sources from local file")

# Connect to DynamoDB
region = 'ap-south-1'
environment = 'dev'
table_name = f'verigov-{environment}-whitelist'

dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(table_name)

print(f"📤 Uploading to DynamoDB table: {table_name}")

# Upload each source
success_count = 0
for source in sources:
    try:
        # Store in DynamoDB
        table.put_item(Item={
            'domain': source['domain'],
            'name': source['name'],
            'approved_by': source['approved_by'],
            'approved_date': source['approved_date']
        })
        print(f"   ✅ {source['domain']} - {source['name']}")
        success_count += 1
    except Exception as e:
        print(f"   ❌ {source['domain']} - Error: {e}")

print()
print("=" * 50)
print(f"✅ Sync Complete!")
print(f"   Uploaded: {success_count}/{len(sources)} sources")
print()
print("🧪 Test the whitelist:")
print("   python -c \"from src.verigov.collection.whitelist_manager import WhitelistManager; wm = WhitelistManager(); print(f'Sources: {len(wm.sources)}'); [print(f'  - {s[\\\"domain\\\"]}') for s in wm.sources[:5]]\"")
