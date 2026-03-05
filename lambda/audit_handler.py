"""
Lambda function to retrieve audit logs from DynamoDB
"""
import json
import boto3
import os
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table_name = os.environ.get('AUDIT_TABLE', 'verigov-dev-audit-logs')
audit_table = dynamodb.Table(table_name)


def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Get recent audit log entries
    
    Query parameters:
    - limit: Number of entries to return (default: 10, max: 50)
    """
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 10))
        limit = min(limit, 50)  # Cap at 50
        
        # Scan the audit table (sorted by timestamp)
        response = audit_table.scan(
            Limit=limit
        )
        
        items = response.get('Items', [])
        
        # Sort by timestamp (newest first)
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Take only the requested limit
        items = items[:limit]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(items, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to retrieve audit logs',
                'details': str(e)
            })
        }
