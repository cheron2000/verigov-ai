"""
Lambda function to retrieve trusted sources from DynamoDB
"""
import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table_name = os.environ.get('WHITELIST_TABLE', 'verigov-dev-whitelist')
whitelist_table = dynamodb.Table(table_name)


def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Get all trusted sources from whitelist
    
    Returns:
    {
        "sources": [
            {
                "domain": "india.gov.in",
                "name": "Government of India",
                "category": "government"
            },
            ...
        ]
    }
    """
    try:
        # Scan the whitelist table
        response = whitelist_table.scan()
        
        items = response.get('Items', [])
        
        # Sort by name
        items.sort(key=lambda x: x.get('name', ''))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({
                'sources': items
            }, default=decimal_default)
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
                'error': 'Failed to retrieve whitelist',
                'details': str(e),
                'sources': []
            })
        }
