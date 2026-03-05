"""Change detector for monitoring government sources"""

import time
from typing import Dict, List, Callable
from ..collection.source_collector import SourceCollector
from ..infrastructure.audit_log import AuditLog


class ChangeDetector:
    """Monitors sources for changes"""
    
    def __init__(
        self,
        source_collector: SourceCollector,
        audit_log: AuditLog,
        interval: int = 3600
    ):
        self.collector = source_collector
        self.audit = audit_log
        self.interval = interval
        self.cache: Dict[str, str] = {}
    
    def monitor(
        self,
        urls: List[str],
        callback: Callable[[Dict], None] = None,
        duration: int = None
    ) -> None:
        """Monitor URLs for changes"""
        
        start_time = time.time()
        
        while True:
            for url in urls:
                try:
                    data = self.collector.collect(url)
                    if data and "content" in data:
                        self._check_for_changes(url, data["content"], callback)
                except Exception as e:
                    self.audit.log("monitoring_error", {"url": url, "error": str(e)})
            
            # Check if duration limit reached
            if duration and (time.time() - start_time) >= duration:
                break
            
            time.sleep(self.interval)
    
    def _check_for_changes(
        self,
        url: str,
        content: str,
        callback: Callable[[Dict], None] = None
    ) -> None:
        """Check if content has changed"""
        
        if url in self.cache:
            if self.cache[url] != content:
                change_event = {
                    "url": url,
                    "change_detected": True,
                    "impact": "MEDIUM"
                }
                self.audit.log("change_detected", change_event)
                
                if callback:
                    callback(change_event)
        
        self.cache[url] = content
