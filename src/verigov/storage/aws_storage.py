"""AWS-based storage implementation using DynamoDB and S3"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import time

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from .interface import StorageInterface
from ..aws.dynamodb_client import DynamoDBClient


class AWSStorage(StorageInterface):
    """AWS-based storage implementation using DynamoDB and S3"""
    
    def __init__(self, region: str = None):
        if not AWS_AVAILABLE:
            raise ImportError("boto3 is required for AWS storage. Install with: pip install boto3")
        
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize DynamoDB client
        self.dynamodb_client = DynamoDBClient(region=self.region)
        
        # Initialize S3 client
        self.s3 = boto3.client('s3', region_name=self.region)
        
        # Bucket name (environment-specific)
        env = os.getenv('ENVIRONMENT', 'dev')
        self.data_bucket_name = f"verigov-{env}-data-{self._get_account_id()}"
        
        # Cache for whitelist (5-minute TTL)
        self._whitelist_cache = None
        self._whitelist_cache_time = 0
        self._whitelist_cache_ttl = 300  # 5 minutes
    
    def _get_account_id(self) -> str:
        """Get AWS account ID for bucket naming"""
        try:
            sts = boto3.client('sts')
            return sts.get_caller_identity()['Account']
        except Exception:
            return "unknown"
    
    def store_audit_log(self, entry: Dict[str, Any]) -> bool:
        """Store audit log entry to DynamoDB and S3"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in entry:
                entry['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            
            # Store in DynamoDB using client
            success = self.dynamodb_client.put_audit_log(entry)
            
            if not success:
                return False
            
            # Also store in S3 for archival
            timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
            s3_key = f"audit/{timestamp.year:04d}/{timestamp.month:02d}/{timestamp.day:02d}/{entry['timestamp']}.json"
            
            self.s3.put_object(
                Bucket=self.data_bucket_name,
                Key=s3_key,
                Body=json.dumps(entry),
                ServerSideEncryption='AES256'
            )
            
            return True
        except Exception as e:
            print(f"Error storing audit log to AWS: {e}")
            return False
    
    def query_audit_logs(self, limit: int = 100, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Query audit log entries from DynamoDB"""
        try:
            # Use DynamoDB client with eventually consistent reads
            entries = self.dynamodb_client.query_audit_logs(
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                consistent_read=False  # Eventually consistent for cost optimization
            )
            
            return entries
            
        except Exception as e:
            print(f"Error querying audit logs from AWS: {e}")
            return []
    
    def store_verification(self, verification_id: str, result: Dict[str, Any]) -> bool:
        """Store verification result to DynamoDB and S3"""
        try:
            # Store in DynamoDB using client
            success = self.dynamodb_client.put_verification(verification_id, result.copy())
            
            if not success:
                return False
            
            # Also store in S3 for archival
            s3_key = f"results/{verification_id}.json"
            self.s3.put_object(
                Bucket=self.data_bucket_name,
                Key=s3_key,
                Body=json.dumps(result),
                ServerSideEncryption='AES256'
            )
            
            return True
        except Exception as e:
            print(f"Error storing verification to AWS: {e}")
            return False
    
    def get_verification(self, verification_id: str) -> Optional[Dict[str, Any]]:
        """Get verification result from DynamoDB"""
        try:
            # Use DynamoDB client with strongly consistent reads
            return self.dynamodb_client.get_verification(
                verification_id,
                consistent_read=True
            )
            
        except Exception as e:
            print(f"Error getting verification from AWS: {e}")
            return None
    
    def get_whitelist(self) -> List[str]:
        """Get whitelist sources from DynamoDB with caching"""
        # Check cache first
        current_time = time.time()
        if (self._whitelist_cache is not None and 
            current_time - self._whitelist_cache_time < self._whitelist_cache_ttl):
            return self._whitelist_cache
        
        try:
            # Use DynamoDB client
            sources = self.dynamodb_client.get_whitelist()
            
            # Update cache
            self._whitelist_cache = sources
            self._whitelist_cache_time = current_time
            
            return sources
            
        except Exception as e:
            print(f"Error getting whitelist from AWS: {e}")
            # Return cached value if available
            return self._whitelist_cache or []
    
    def update_whitelist(self, sources: List[str]) -> bool:
        """Update whitelist sources in DynamoDB"""
        try:
            # Use DynamoDB client
            success = self.dynamodb_client.update_whitelist(sources)
            
            if success:
                # Clear cache
                self._whitelist_cache = None
            
            return success
            
        except Exception as e:
            print(f"Error updating whitelist in AWS: {e}")
            return False
    
    def store_batch_results(self, batch_id: str, results: List[Dict[str, Any]]) -> bool:
        """Store batch verification results to S3"""
        try:
            s3_key = f"batch/{batch_id}/results.json"
            
            batch_data = {
                'batch_id': batch_id,
                'results': results,
                'stored_at': datetime.utcnow().isoformat() + 'Z',
                'count': len(results)
            }
            
            self.s3.put_object(
                Bucket=self.data_bucket_name,
                Key=s3_key,
                Body=json.dumps(batch_data),
                ServerSideEncryption='AES256'
            )
            
            return True
        except Exception as e:
            print(f"Error storing batch results to AWS: {e}")
            return False
    
    def get_batch_results(self, batch_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get batch verification results from S3"""
        try:
            s3_key = f"batch/{batch_id}/results.json"
            
            response = self.s3.get_object(
                Bucket=self.data_bucket_name,
                Key=s3_key
            )
            
            data = json.loads(response['Body'].read())
            return data.get('results')
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            print(f"Error getting batch results from AWS: {e}")
            return None
        except Exception as e:
            print(f"Error getting batch results from AWS: {e}")
            return None