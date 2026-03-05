"""Source collector for gathering data from government sources"""

import requests
from typing import Dict, Optional
from urllib.parse import urlparse
from .whitelist_manager import WhitelistManager


class SourceCollector:
    """Collects data from whitelisted government sources"""
    
    def __init__(self, whitelist_manager: WhitelistManager, timeout: int = 30):
        self.whitelist = whitelist_manager
        self.timeout = timeout
    
    def collect(self, url: str) -> Optional[Dict]:
        """Collect data from a URL if it's whitelisted"""
        domain = self._extract_domain(url)
        
        if not self.whitelist.is_approved(domain):
            raise ValueError(f"Domain {domain} is not in the whitelist")
        
        try:
            response = requests.get(url, timeout=self.timeout, verify=True)
            response.raise_for_status()
            
            return {
                "url": url,
                "domain": domain,
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers)
            }
        except requests.RequestException as e:
            return {
                "url": url,
                "domain": domain,
                "error": str(e)
            }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
