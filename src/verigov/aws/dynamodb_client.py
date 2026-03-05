"""DynamoDB client for VeriGov AI with optimized queries and cost management"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal

try:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False


class DynamoDBClient:
    """DynamoDB client for audit logs, verifications, and whitelist"""
    
    def __init__(self, region: str = None):
        if not AWS_AVAILABLE:
            raise ImportError("boto3 is required for DynamoDB. Install with: pip install boto3")
        
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        
        # Get environment for table naming
        env = os.getenv('ENVIRONMENT', 'dev')
        self.audit_table_name = f"verigov-{env}-audit-logs"
        self.verifications_table_name = f"verigov-{env}-verifications"
        self.whitelist_table_name = f"verigov-{env}-whitelist"
        
        # Cache table references
        self._audit_table = None
        self._verifications_table = None
        self._whitelist_table = None
    
    @property
    def audit_table(self):
        """Lazy load audit logs table"""
        if self._audit_table is None:
            self._audit_table = self.dynamodb.Table(self.audit_table_name)
        return self._audit_table
    
    @property
    def verifications_table(self):
        """Lazy load verifications table"""
        if self._verifications_table is None:
            self._verifications_table = self.dynamodb.Table(self.verifications_table_name)
        return self._verifications_table
    
    @property
    def whitelist_table(self):
        """Lazy load whitelist table"""
        if self._whitelist_table is None:
            self._whitelist_table = self.dynamodb.Table(self.whitelist_table_name)
        return self._whitelist_table
    
    # ==================== AUDIT LOGS ====================
    
    def put_audit_log(self, entry: Dict[str, Any]) -> bool:
        """Store audit log entry in DynamoDB
        
        Table structure:
        - Partition key: timestamp (ISO8601 string)
        - Sort key: event_type (string)
        - GSI: verification_id-index for querying by verification
        - GSI: event_type-timestamp-index for querying by event type
        
        Args:
            entry: Audit log entry with timestamp, event_type, and data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure timestamp is present
            if 'timestamp' not in entry:
                entry['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            
            # Convert any float values to Decimal for DynamoDB
            entry = self._convert_floats_to_decimal(entry)
            
            # Put item in DynamoDB
            self.audit_table.put_item(Item=entry)
            
            return True
            
        except ClientError as e:
            print(f"DynamoDB error storing audit log: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"Error storing audit log to DynamoDB: {e}")
            return False
    
    def query_audit_logs(
        self,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        verification_id: Optional[str] = None,
        consistent_read: bool = False
    ) -> List[Dict[str, Any]]:
        """Query audit log entries from DynamoDB
        
        Uses eventually consistent reads by default for cost optimization.
        Can query by date range, event type, or verification ID.
        
        Args:
            limit: Maximum number of entries to return
            start_date: Filter entries after this date
            end_date: Filter entries before this date
            event_type: Filter by specific event type
            verification_id: Filter by verification ID (uses GSI)
            consistent_read: Use strongly consistent reads (costs more)
            
        Returns:
            List of audit log entries
        """
        try:
            # Query by verification_id using GSI
            if verification_id:
                response = self.audit_table.query(
                    IndexName='verification_id-index',
                    KeyConditionExpression=Key('verification_id').eq(verification_id),
                    Limit=limit,
                    ConsistentRead=False  # GSI queries are always eventually consistent
                )
                items = response.get('Items', [])
            
            # Query by event_type using GSI
            elif event_type and (start_date or end_date):
                key_condition = Key('event_type').eq(event_type)
                
                if start_date and end_date:
                    key_condition = key_condition & Key('timestamp').between(
                        start_date.isoformat() + 'Z',
                        end_date.isoformat() + 'Z'
                    )
                elif start_date:
                    key_condition = key_condition & Key('timestamp').gte(start_date.isoformat() + 'Z')
                elif end_date:
                    key_condition = key_condition & Key('timestamp').lte(end_date.isoformat() + 'Z')
                
                response = self.audit_table.query(
                    IndexName='event_type-timestamp-index',
                    KeyConditionExpression=key_condition,
                    Limit=limit,
                    ConsistentRead=False
                )
                items = response.get('Items', [])
            
            # Scan with filters (less efficient, use sparingly)
            else:
                scan_kwargs = {
                    'Limit': limit,
                    'ConsistentRead': consistent_read
                }
                
                # Build filter expression
                filter_expressions = []
                
                if event_type:
                    filter_expressions.append(Attr('event_type').eq(event_type))
                
                if start_date:
                    filter_expressions.append(Attr('timestamp').gte(start_date.isoformat() + 'Z'))
                
                if end_date:
                    filter_expressions.append(Attr('timestamp').lte(end_date.isoformat() + 'Z'))
                
                # Combine filters
                if filter_expressions:
                    filter_expr = filter_expressions[0]
                    for expr in filter_expressions[1:]:
                        filter_expr = filter_expr & expr
                    scan_kwargs['FilterExpression'] = filter_expr
                
                response = self.audit_table.scan(**scan_kwargs)
                items = response.get('Items', [])
            
            # Convert Decimal back to float
            items = [self._convert_decimals_to_float(item) for item in items]
            
            # Sort by timestamp (most recent first)
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return items[:limit]
            
        except ClientError as e:
            print(f"DynamoDB error querying audit logs: {e.response['Error']['Message']}")
            return []
        except Exception as e:
            print(f"Error querying audit logs from DynamoDB: {e}")
            return []
    
    # ==================== VERIFICATIONS ====================
    
    def put_verification(self, verification_id: str, result: Dict[str, Any]) -> bool:
        """Store verification result in DynamoDB
        
        Table structure:
        - Partition key: verification_id (string)
        - GSI: status-timestamp-index for querying by status
        
        Args:
            verification_id: Unique verification identifier
            result: Verification result data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            result['verification_id'] = verification_id
            result['stored_at'] = datetime.utcnow().isoformat() + 'Z'
            
            # Convert floats to Decimal
            result = self._convert_floats_to_decimal(result)
            
            # Put item with strongly consistent write
            self.verifications_table.put_item(Item=result)
            
            return True
            
        except ClientError as e:
            print(f"DynamoDB error storing verification: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"Error storing verification to DynamoDB: {e}")
            return False
    
    def get_verification(self, verification_id: str, consistent_read: bool = True) -> Optional[Dict[str, Any]]:
        """Get verification result from DynamoDB
        
        Uses strongly consistent reads by default for verification results.
        
        Args:
            verification_id: Unique verification identifier
            consistent_read: Use strongly consistent reads (default: True)
            
        Returns:
            Verification result or None if not found
        """
        try:
            response = self.verifications_table.get_item(
                Key={'verification_id': verification_id},
                ConsistentRead=consistent_read
            )
            
            item = response.get('Item')
            if item:
                return self._convert_decimals_to_float(item)
            return None
            
        except ClientError as e:
            print(f"DynamoDB error getting verification: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            print(f"Error getting verification from DynamoDB: {e}")
            return None
    
    def query_verifications_by_status(
        self,
        status: str,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Query verifications by status using GSI
        
        Args:
            status: Verification status (VERIFIED, UNVERIFIED, etc.)
            limit: Maximum number of results
            start_date: Filter by timestamp
            end_date: Filter by timestamp
            
        Returns:
            List of verification results
        """
        try:
            key_condition = Key('status').eq(status)
            
            if start_date and end_date:
                key_condition = key_condition & Key('stored_at').between(
                    start_date.isoformat() + 'Z',
                    end_date.isoformat() + 'Z'
                )
            elif start_date:
                key_condition = key_condition & Key('stored_at').gte(start_date.isoformat() + 'Z')
            elif end_date:
                key_condition = key_condition & Key('stored_at').lte(end_date.isoformat() + 'Z')
            
            response = self.verifications_table.query(
                IndexName='status-timestamp-index',
                KeyConditionExpression=key_condition,
                Limit=limit,
                ConsistentRead=False
            )
            
            items = response.get('Items', [])
            return [self._convert_decimals_to_float(item) for item in items]
            
        except ClientError as e:
            print(f"DynamoDB error querying verifications: {e.response['Error']['Message']}")
            return []
        except Exception as e:
            print(f"Error querying verifications from DynamoDB: {e}")
            return []
    
    # ==================== WHITELIST ====================
    
    def get_whitelist(self) -> List[str]:
        """Get all whitelist domains from DynamoDB
        
        Table structure:
        - Partition key: domain (string)
        
        Returns:
            List of approved domains
        """
        try:
            response = self.whitelist_table.scan(ConsistentRead=False)
            
            domains = []
            for item in response.get('Items', []):
                if 'domain' in item:
                    domains.append(item['domain'])
            
            return domains
            
        except ClientError as e:
            print(f"DynamoDB error getting whitelist: {e.response['Error']['Message']}")
            return []
        except Exception as e:
            print(f"Error getting whitelist from DynamoDB: {e}")
            return []
    
    def update_whitelist(self, sources: List[str]) -> bool:
        """Update whitelist in DynamoDB
        
        Replaces all existing entries with new list.
        
        Args:
            sources: List of approved domains
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear existing entries
            response = self.whitelist_table.scan()
            for item in response.get('Items', []):
                self.whitelist_table.delete_item(Key={'domain': item['domain']})
            
            # Add new entries
            timestamp = datetime.utcnow().isoformat() + 'Z'
            for source in sources:
                self.whitelist_table.put_item(Item={
                    'domain': source,
                    'updated_at': timestamp
                })
            
            return True
            
        except ClientError as e:
            print(f"DynamoDB error updating whitelist: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"Error updating whitelist in DynamoDB: {e}")
            return False
    
    # ==================== UTILITY METHODS ====================
    
    def _convert_floats_to_decimal(self, obj: Any) -> Any:
        """Convert float values to Decimal for DynamoDB compatibility"""
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        return obj
    
    def _convert_decimals_to_float(self, obj: Any) -> Any:
        """Convert Decimal values back to float for JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimals_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimals_to_float(item) for item in obj]
        return obj
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a DynamoDB table exists
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            table = self.dynamodb.Table(table_name)
            table.load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            raise
    
    def get_table_status(self, table_name: str) -> Optional[str]:
        """Get the status of a DynamoDB table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table status (ACTIVE, CREATING, etc.) or None if not found
        """
        try:
            table = self.dynamodb.Table(table_name)
            table.load()
            return table.table_status
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return None
            raise