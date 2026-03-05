"""Whitelist manager for approved government sources with storage abstraction"""

import json
from typing import List, Dict, Optional
from pathlib import Path

from ..storage import StorageFactory


class WhitelistManager:
    """Manages whitelist of approved government sources with configurable storage backend"""
    
    def __init__(self, whitelist_path: str = "config/whitelist.json", storage_mode: str = None):
        # Keep legacy file path for backward compatibility
        self.whitelist_path = Path(whitelist_path)
        self.sources: List[Dict] = []
        
        # Use storage abstraction
        self.storage = StorageFactory.create_storage(storage_mode)
        
        self.load_whitelist()
    
    def load_whitelist(self) -> None:
        """Load whitelist from storage backend"""
        try:
            # Try storage abstraction first
            source_domains = self.storage.get_whitelist()
            
            # Convert simple domain list to full source objects
            # For backward compatibility, try to load full source info from local file
            if self.whitelist_path.exists():
                with open(self.whitelist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    local_sources_data = data.get("sources", [])
                    
                    # Convert local sources to consistent format
                    local_sources = []
                    for source in local_sources_data:
                        if isinstance(source, str):
                            local_sources.append({
                                "domain": source,
                                "name": source,
                                "approved_by": "system",
                                "approved_date": "unknown"
                            })
                        elif isinstance(source, dict):
                            local_sources.append(source)
                    
                    # Merge with storage domains
                    self.sources = []
                    for domain in source_domains:
                        # Find matching local source info
                        source_info = next((s for s in local_sources if s.get("domain") == domain), None)
                        if source_info:
                            self.sources.append(source_info)
                        else:
                            # Create minimal source info
                            self.sources.append({
                                "domain": domain,
                                "name": domain,
                                "approved_by": "system",
                                "approved_date": "unknown"
                            })
                    
                    # If no domains from storage, use local sources
                    if not source_domains and local_sources:
                        self.sources = local_sources
            else:
                # No local file, create minimal source objects
                self.sources = [
                    {
                        "domain": domain,
                        "name": domain,
                        "approved_by": "system", 
                        "approved_date": "unknown"
                    }
                    for domain in source_domains
                ]
                
        except Exception as e:
            print(f"Error loading whitelist from storage: {e}")
            # Fallback to local file
            self._load_local_file()
    
    def _load_local_file(self) -> None:
        """Fallback method to load from local file"""
        if self.whitelist_path.exists():
            with open(self.whitelist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sources_data = data.get("sources", [])
                
                # Handle both formats: list of strings or list of objects
                self.sources = []
                for source in sources_data:
                    if isinstance(source, str):
                        # Simple string format
                        self.sources.append({
                            "domain": source,
                            "name": source,
                            "approved_by": "system",
                            "approved_date": "unknown"
                        })
                    elif isinstance(source, dict):
                        # Full object format
                        self.sources.append(source)
        else:
            self.sources = []
    
    def is_approved(self, domain: str) -> bool:
        """Check if a domain is in the whitelist"""
        return any(source["domain"] == domain for source in self.sources)
    
    def get_source_info(self, domain: str) -> Optional[Dict]:
        """Get information about a whitelisted source"""
        for source in self.sources:
            if source["domain"] == domain:
                return source
        return None
    
    def add_source(self, domain: str, name: str, approved_by: str) -> None:
        """Add a new source to the whitelist"""
        from datetime import datetime
        
        if not self.is_approved(domain):
            new_source = {
                "domain": domain,
                "name": name,
                "approved_by": approved_by,
                "approved_date": datetime.now().strftime("%Y-%m-%d")
            }
            self.sources.append(new_source)
            self.save_whitelist()
    
    def save_whitelist(self) -> None:
        """Save whitelist to storage backend"""
        try:
            # Extract domain list for storage
            domains = [source["domain"] for source in self.sources]
            
            # Update storage
            success = self.storage.update_whitelist(domains)
            
            if not success:
                raise Exception("Storage update failed")
                
            # Also save to local file for backward compatibility
            self.whitelist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.whitelist_path, 'w', encoding='utf-8') as f:
                json.dump({"sources": self.sources}, f, indent=2)
                
        except Exception as e:
            print(f"Error saving whitelist to storage: {e}")
            # Fallback to local file only
            self.whitelist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.whitelist_path, 'w', encoding='utf-8') as f:
                json.dump({"sources": self.sources}, f, indent=2)
