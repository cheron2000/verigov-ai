"""Enhanced source collector for gathering data from government and news sources"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from urllib.parse import urlparse, urljoin
import time
import logging
from .whitelist_manager import WhitelistManager

logger = logging.getLogger(__name__)


class SourceCollector:
    """Collects and extracts content from whitelisted sources with enhanced scraping"""
    
    def __init__(self, whitelist_manager: WhitelistManager, timeout: int = 15):
        self.whitelist = whitelist_manager
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def collect(self, url: str) -> Optional[Dict]:
        """
        Collect and extract content from a URL if it's whitelisted
        
        Returns:
            Dict with url, domain, content, title, and metadata
        """
        domain = self._extract_domain(url)
        
        if not self.whitelist.is_approved(domain):
            logger.warning(f"Domain {domain} is not in the whitelist")
            raise ValueError(f"Domain {domain} is not in the whitelist")
        
        try:
            logger.info(f"Fetching content from: {url}")
            
            response = self.session.get(
                url, 
                timeout=self.timeout, 
                verify=True,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Extract content based on content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'html' in content_type:
                extracted = self._extract_html_content(response.text, url)
            elif 'json' in content_type:
                extracted = self._extract_json_content(response.text)
            else:
                extracted = {'text': response.text[:5000]}
            
            return {
                "url": url,
                "domain": domain,
                "status_code": response.status_code,
                "content_type": content_type,
                "title": extracted.get('title', ''),
                "content": extracted.get('text', ''),
                "summary": extracted.get('summary', ''),
                "articles": extracted.get('articles', []),
                "metadata": {
                    "word_count": len(extracted.get('text', '').split()),
                    "has_content": bool(extracted.get('text')),
                    "fetch_time": time.time()
                }
            }
            
        except requests.Timeout:
            logger.error(f"Timeout fetching {url}")
            return {
                "url": url,
                "domain": domain,
                "error": "Request timeout",
                "error_type": "timeout"
            }
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return {
                "url": url,
                "domain": domain,
                "error": str(e),
                "error_type": "request_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return {
                "url": url,
                "domain": domain,
                "error": str(e),
                "error_type": "unknown"
            }
    
    def collect_multiple(self, urls: List[str], max_sources: int = 5) -> List[Dict]:
        """
        Collect content from multiple URLs
        
        Args:
            urls: List of URLs to fetch
            max_sources: Maximum number of sources to fetch
            
        Returns:
            List of collected content dictionaries
        """
        results = []
        
        for url in urls[:max_sources]:
            try:
                result = self.collect(url)
                if result and not result.get('error'):
                    results.append(result)
                    time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"Error collecting {url}: {e}")
                continue
        
        return results
    
    def _extract_html_content(self, html: str, base_url: str) -> Dict:
        """
        Extract meaningful content from HTML
        
        Returns:
            Dict with title, text, summary, and articles
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                            'aside', 'iframe', 'noscript', 'form']):
            element.decompose()
        
        # Extract title
        title = ''
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else ''
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        
        # Try to find main content area
        main_content = None
        
        # Look for common content containers
        content_selectors = [
            'article', 'main', '[role="main"]',
            '.content', '.main-content', '.article-content',
            '#content', '#main-content', '#article-content',
            '.post-content', '.entry-content'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body') or soup
        
        # Extract text from main content
        text = self._clean_text(main_content.get_text())
        
        # Extract summary (first paragraph or meta description)
        summary = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            summary = meta_desc['content'].strip()
        elif main_content:
            first_p = main_content.find('p')
            if first_p:
                summary = first_p.get_text().strip()[:300]
        
        # Try to extract article links (for news sites)
        articles = self._extract_articles(soup, base_url)
        
        return {
            'title': title,
            'text': text[:10000],  # Limit to 10k chars
            'summary': summary,
            'articles': articles[:10]  # Limit to 10 articles
        }
    
    def _extract_articles(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract article links and titles from a page"""
        articles = []
        
        # Look for article elements
        article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and any(
            term in str(x).lower() for term in ['article', 'post', 'news', 'story']
        ))
        
        for element in article_elements[:15]:
            link = element.find('a', href=True)
            if link:
                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                title = title_elem.get_text().strip() if title_elem else link.get_text().strip()
                
                if title and len(title) > 10:
                    url = urljoin(base_url, link['href'])
                    articles.append({
                        'title': title[:200],
                        'url': url
                    })
        
        return articles
    
    def _extract_json_content(self, json_text: str) -> Dict:
        """Extract content from JSON response"""
        import json
        
        try:
            data = json.loads(json_text)
            
            # Try to extract text from common JSON structures
            text = ''
            if isinstance(data, dict):
                # Look for common text fields
                for key in ['content', 'text', 'body', 'description', 'summary']:
                    if key in data:
                        text = str(data[key])
                        break
                
                # If still no text, stringify the whole thing
                if not text:
                    text = json.dumps(data, indent=2)
            else:
                text = json.dumps(data, indent=2)
            
            return {
                'text': text[:5000],
                'title': data.get('title', '') if isinstance(data, dict) else ''
            }
        except:
            return {'text': json_text[:5000]}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Split into lines and clean each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Remove blank lines and join
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain
    
    def search_source(self, domain: str, query: str) -> Optional[str]:
        """
        Attempt to search within a source domain
        
        Args:
            domain: Domain to search (e.g., 'nasa.gov')
            query: Search query
            
        Returns:
            URL of search results or None
        """
        # Common search URL patterns
        search_patterns = [
            f"https://{domain}/search?q={query}",
            f"https://www.{domain}/search?q={query}",
            f"https://{domain}/search?query={query}",
            f"https://www.{domain}/search?query={query}",
        ]
        
        for url in search_patterns:
            try:
                response = self.session.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return url
            except:
                continue
        
        return None
