"""Storage interface for VeriGov AI - supports local and AWS modes"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class StorageInterface(ABC):
    """Abstract base class for storage implementations"""
    
    @abstractmethod
    def store_audit_log(self, entry: Dict[str, Any]) -> bool:
        """Store audit log entry"""
        pass
    
    @abstractmethod
    def query_audit_logs(self, limit: int = 100, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Query audit log entries"""
        pass
    
    @abstractmethod
    def store_verification(self, verification_id: str, result: Dict[str, Any]) -> bool:
        """Store verification result"""
        pass
    
    @abstractmethod
    def get_verification(self, verification_id: str) -> Optional[Dict[str, Any]]:
        """Get verification result by ID"""
        pass
    
    @abstractmethod
    def get_whitelist(self) -> List[str]:
        """Get whitelist sources"""
        pass
    
    @abstractmethod
    def update_whitelist(self, sources: List[str]) -> bool:
        """Update whitelist sources"""
        pass
    
    @abstractmethod
    def store_batch_results(self, batch_id: str, results: List[Dict[str, Any]]) -> bool:
        """Store batch verification results"""
        pass
    
    @abstractmethod
    def get_batch_results(self, batch_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get batch verification results"""
        pass