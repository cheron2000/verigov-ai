"""Test the source collector with verified working sources"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.verigov.collection.source_collector import SourceCollector
from src.verigov.collection.whitelist_manager import WhitelistManager


def test_working_sources():
    """Test with sources we know are working"""
    
    print("=" * 70)
    print("Testing Source Collector with Verified Working Sources")
    print("=" * 70)
    
    # Initialize
    whitelist = WhitelistManager(
        whitelist_path="config/whitelist.json",
        storage_mode='local'
    )
    
    print(f"\nLoaded {len(whitelist.sources)} whitelisted sources")
    
    collector = SourceCollector(whitelist, timeout=10)
    
    # Test with verified working sources
    test_cases = [
        ("https://www.nasa.gov/", "NASA - Space News"),
        ("https://www.who.int/", "WHO - Health Information"),
        ("https://www.bbc.com/news", "BBC News"),
        ("https://www.cdc.gov/", "CDC - Health Guidelines"),
        ("https://apnews.com/", "Associated Press News"),
    ]
    
    successful = 0
    failed = 0
    
    for url, description in test_cases:
        print(f"\n{'=' * 70}")
        print(f"Testing: {description}")
        print(f"URL: {url}")
        print(f"{'=' * 70}")
        
        try:
            result = collector.collect(url)
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
                failed += 1
            else:
                print(f"✅ Success!")
                print(f"   Domain: {result['domain']}")
                print(f"   Title: {result.get('title', 'N/A')[:70]}")
                print(f"   Content: {len(result.get('content', ''))} chars")
                print(f"   Words: {result['metadata']['word_count']}")
                
                if result.get('articles'):
                    print(f"   Articles: {len(result['articles'])}")
                    for i, article in enumerate(result['articles'][:3], 1):
                        print(f"      {i}. {article['title'][:65]}")
                
                # Show content preview
                content = result.get('content', '')[:250]
                print(f"\n   Preview: {content}...")
                
                successful += 1
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            failed += 1
    
    print(f"\n{'=' * 70}")
    print(f"RESULTS: {successful} successful, {failed} failed")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    test_working_sources()
