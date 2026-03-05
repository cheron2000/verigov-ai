"""Audit logging for VeriGov AI with storage abstraction"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..storage import StorageFactory


class AuditLog:
    """Immutable append-only audit log with configurable storage backend"""
    
    def __init__(self, log_path: str = "logs/audit.log", storage_mode: str = None):
        # Keep legacy file path for backward compatibility
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use storage abstraction
        self.storage = StorageFactory.create_storage(storage_mode)
    
    def log(self, event_type: str, data: Dict) -> None:
        """Log an event to the audit log"""
        entry = {
            "timestamp": datetime.now().isoformat() + 'Z',
            "event_type": event_type,
            "data": data
        }
        
        # Store using storage abstraction
        success = self.storage.store_audit_log(entry)
        
        if not success:
            # Fallback to local file if storage fails
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
    
    def query(self, event_type: Optional[str] = None, limit: int = 100, 
              start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """Query the audit log"""
        try:
            # Use storage abstraction
            entries = self.storage.query_audit_logs(limit, start_date, end_date)
            
            # Filter by event type if specified
            if event_type:
                entries = [entry for entry in entries if entry.get("event_type") == event_type]
            
            return entries
            
        except Exception as e:
            print(f"Error querying audit log: {e}")
            # Fallback to local file
            return self._query_local_file(event_type, limit)
    
    def _query_local_file(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Fallback method to query local file"""
        if not self.log_path.exists():
            return []
        
        entries = []
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if event_type is None or entry.get("event_type") == event_type:
                        entries.append(entry)
        
        if limit is not None:
            return entries[-limit:]
        return entries
    
    def export(self, output_path: str) -> None:
        """Export audit log to JSON file"""
        entries = self.query(limit=None)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2)
