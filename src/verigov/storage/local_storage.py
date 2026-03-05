"""Local file-based storage implementation"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

from .interface import StorageInterface


class LocalStorage(StorageInterface):
    """Local file-based storage implementation"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.audit_log_path = self.base_path / "logs" / "audit.log"
        self.whitelist_path = self.base_path / "config" / "whitelist.json"
        self.verifications_path = self.base_path / "data" / "verifications"
        self.batch_results_path = self.base_path / "data" / "batch_results"
        
        # Ensure directories exist
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.whitelist_path.parent.mkdir(parents=True, exist_ok=True)
        self.verifications_path.mkdir(parents=True, exist_ok=True)
        self.batch_results_path.mkdir(parents=True, exist_ok=True)
    
    def store_audit_log(self, entry: Dict[str, Any]) -> bool:
        """Store audit log entry to file"""
        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            return True
        except Exception as e:
            print(f"Error storing audit log: {e}")
            return False
    
    def query_audit_logs(self, limit: int = 100, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Query audit log entries from file"""
        entries = []
        
        if not self.audit_log_path.exists():
            return entries
        
        try:
            with open(self.audit_log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        
                        # Filter by date range if specified
                        if start_date or end_date:
                            entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                            if start_date and entry_time < start_date:
                                continue
                            if end_date and entry_time > end_date:
                                continue
                        
                        entries.append(entry)
            
            # Return most recent entries up to limit
            return entries[-limit:] if len(entries) > limit else entries
            
        except Exception as e:
            print(f"Error querying audit logs: {e}")
            return []
    
    def store_verification(self, verification_id: str, result: Dict[str, Any]) -> bool:
        """Store verification result to file"""
        try:
            file_path = self.verifications_path / f"{verification_id}.json"
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2)
            return True
        except Exception as e:
            print(f"Error storing verification: {e}")
            return False
    
    def get_verification(self, verification_id: str) -> Optional[Dict[str, Any]]:
        """Get verification result from file"""
        try:
            file_path = self.verifications_path / f"{verification_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error getting verification: {e}")
            return None
    
    def get_whitelist(self) -> List[str]:
        """Get whitelist sources from file"""
        try:
            if self.whitelist_path.exists():
                with open(self.whitelist_path, 'r') as f:
                    data = json.load(f)
                    return data.get('sources', [])
            return []
        except Exception as e:
            print(f"Error getting whitelist: {e}")
            return []
    
    def update_whitelist(self, sources: List[str]) -> bool:
        """Update whitelist sources in file"""
        try:
            data = {'sources': sources}
            with open(self.whitelist_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating whitelist: {e}")
            return False
    
    def store_batch_results(self, batch_id: str, results: List[Dict[str, Any]]) -> bool:
        """Store batch verification results to file"""
        try:
            file_path = self.batch_results_path / f"{batch_id}.json"
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            return True
        except Exception as e:
            print(f"Error storing batch results: {e}")
            return False
    
    def get_batch_results(self, batch_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get batch verification results from file"""
        try:
            file_path = self.batch_results_path / f"{batch_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error getting batch results: {e}")
            return None