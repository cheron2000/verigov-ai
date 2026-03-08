"""Quick test of the enhanced source collector with a single source"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.verigov.collection.source_collector import SourceCollector
from src.verigov.collection.whitelist_manager import WhitelistManager


def test_quick():
    """Quick test with NASA"""
    
    print("Testing Source Collector with NASA...")
    
    # Initialize
    whitelist = WhitelistManager(
        whitelist_path="config/whitelist.json",
        storage_mode='local'
    )
    
    print(f"Loaded {len(whitelist.sources)} whitelisted sources\n")
    
    collector = SourceCollector(whitelist, timeout=10)
    
    # Test NASA
    url = "https://www.nasa.gov/"
    print(f"Fetching: {url}")
    
    result = collector.collect(url)
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success!")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Content: {len(result.get('content', ''))} chars")
        print(f"   Articles: {len(result.get('articles', []))}")
        
        if result.get('articles'):
            print(f"\n   Found Articles:")
            for i, article in enumerate(result['articles'][:5], 1):
                print(f"   {i}. {article['title']}")
        
        print(f"\n   Content Preview:")
        print(f"   {result.get('content', '')[:300]}...")


if __name__ == '__main__':
    test_quick()
