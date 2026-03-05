"""Storage factory for creating storage instances based on configuration"""

import os
from typing import Optional

from .interface import StorageInterface
from .local_storage import LocalStorage
from .aws_storage import AWSStorage


class StorageFactory:
    """Factory for creating storage instances"""
    
    @staticmethod
    def create_storage(mode: Optional[str] = None) -> StorageInterface:
        """Create storage instance based on mode
        
        Args:
            mode: Storage mode ('local', 'aws', 'hybrid'). If None, uses STORAGE_MODE env var.
        
        Returns:
            StorageInterface instance
        """
        if mode is None:
            mode = os.getenv('STORAGE_MODE', 'local').lower()
        
        if mode == 'local':
            return LocalStorage()
        elif mode == 'aws':
            return AWSStorage()
        elif mode == 'hybrid':
            return HybridStorage()
        else:
            raise ValueError(f"Unknown storage mode: {mode}. Use 'local', 'aws', or 'hybrid'")


class HybridStorage(StorageInterface):
    """Hybrid storage that writes to both local and AWS"""
    
    def __init__(self):
        self.local_storage = LocalStorage()
        self.aws_storage = AWSStorage()
    
    def store_audit_log(self, entry) -> bool:
        """Store to both local and AWS"""
        local_success = self.local_storage.store_audit_log(entry)
        aws_success = self.aws_storage.store_audit_log(entry)
        return local_success and aws_success
    
    def query_audit_logs(self, limit=100, start_date=None, end_date=None):
        """Query from AWS first, fallback to local"""
        try:
            return self.aws_storage.query_audit_logs(limit, start_date, end_date)
        except Exception:
            return self.local_storage.query_audit_logs(limit, start_date, end_date)
    
    def store_verification(self, verification_id: str, result) -> bool:
        """Store to both local and AWS"""
        local_success = self.local_storage.store_verification(verification_id, result)
        aws_success = self.aws_storage.store_verification(verification_id, result)
        return local_success and aws_success
    
    def get_verification(self, verification_id: str):
        """Get from AWS first, fallback to local"""
        try:
            result = self.aws_storage.get_verification(verification_id)
            if result is not None:
                return result
        except Exception:
            pass
        return self.local_storage.get_verification(verification_id)
    
    def get_whitelist(self):
        """Get from AWS first, fallback to local"""
        try:
            return self.aws_storage.get_whitelist()
        except Exception:
            return self.local_storage.get_whitelist()
    
    def update_whitelist(self, sources) -> bool:
        """Update both local and AWS"""
        local_success = self.local_storage.update_whitelist(sources)
        aws_success = self.aws_storage.update_whitelist(sources)
        return local_success and aws_success
    
    def store_batch_results(self, batch_id: str, results) -> bool:
        """Store to both local and AWS"""
        local_success = self.local_storage.store_batch_results(batch_id, results)
        aws_success = self.aws_storage.store_batch_results(batch_id, results)
        return local_success and aws_success
    
    def get_batch_results(self, batch_id: str):
        """Get from AWS first, fallback to local"""
        try:
            result = self.aws_storage.get_batch_results(batch_id)
            if result is not None:
                return result
        except Exception:
            pass
        return self.local_storage.get_batch_results(batch_id)