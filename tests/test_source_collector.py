"""Test the enhanced source collector"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.verigov.collection.source_collector import SourceCollector
from src.verigov.collection.whitelist_manager import WhitelistManager


def test_source_collector():
    """Test fetching from a trusted source"""
    
    print("=" * 60)
    print("Testing Enhanced Source Collector")
    print("=" * 60)
    
    # Initialize with local storage mode
    whitelist = WhitelistManager(
        whitelist_path="config/whitelist.json",
        storage_mode='local'
    )
    
    print(f"\nLoaded {len(whitelist.sources)} whitelisted sources")
    print("Sample sources:")
    for source in whitelist.sources[:5]:
        print(f"  - {source['domain']}: {source['name']}")
    
    collector = SourceCollector(whitelist, timeout=15)
    
    # Test URLs from different categories
    test_urls = [
        "https://www.nasa.gov/",
        "https://www.who.int/",
        "https://www.gov.in/",
    ]
    
    for url in test_urls:
        print(f"\n{'=' * 60}")
        print(f"Testing: {url}")
        print(f"{'=' * 60}")
        
        try:
            result = collector.collect(url)
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
                print(f"   Error Type: {result.get('error_type', 'unknown')}")
            else:
                print(f"✅ Success!")
                print(f"   Domain: {result['domain']}")
                print(f"   Status: {result['status_code']}")
                print(f"   Title: {result.get('title', 'N/A')[:80]}")
                print(f"   Content Length: {len(result.get('content', ''))} chars")
                print(f"   Word Count: {result['metadata']['word_count']}")
                print(f"   Has Content: {result['metadata']['has_content']}")
                
                if result.get('articles'):
                    print(f"   Articles Found: {len(result['articles'])}")
                    for i, article in enumerate(result['articles'][:3], 1):
                        print(f"      {i}. {article['title'][:60]}")
                
                # Show first 200 chars of content
                content_preview = result.get('content', '')[:200]
                print(f"\n   Content Preview:")
                print(f"   {content_preview}...")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("Test Complete")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    test_source_collector()
