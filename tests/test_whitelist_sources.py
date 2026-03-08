"""Test which whitelist sources are actually working"""

import requests
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_url(url, timeout=10):
    """Test if a URL is accessible"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        return {
            'url': url,
            'status': response.status_code,
            'working': response.status_code == 200,
            'content_length': len(response.text)
        }
    except requests.Timeout:
        return {'url': url, 'working': False, 'error': 'Timeout'}
    except Exception as e:
        return {'url': url, 'working': False, 'error': str(e)[:100]}


def main():
    """Test all sources"""
    
    # Current whitelist sources
    test_sources = [
        ("https://www.gov.in/", "Government of India"),
        ("https://www.nasa.gov/", "NASA"),
        ("https://www.who.int/", "WHO"),
        ("https://www.cdc.gov/", "CDC"),
        ("https://www.nih.gov/", "NIH"),
        ("https://www.gov.uk/", "UK Government"),
        ("https://www.un.org/", "United Nations"),
        ("https://www.worldbank.org/", "World Bank"),
        ("https://www.imf.org/", "IMF"),
        ("https://www.census.gov/", "US Census"),
        ("https://www.bls.gov/", "Bureau of Labor Statistics"),
        ("https://www.noaa.gov/", "NOAA"),
        ("https://www.pib.gov.in/", "Press Information Bureau India"),
        ("https://www.mygov.in/", "MyGov India"),
        ("https://www.nic.in/", "National Informatics Centre"),
        ("https://www.data.gov.in/", "Open Government Data India"),
        ("https://www.europa.eu/", "European Union"),
        ("https://www.nature.com/", "Nature"),
        ("https://www.science.org/", "Science Magazine"),
        ("https://www.ncbi.nlm.nih.gov/", "NCBI"),
    ]
    
    # Additional reliable sources to consider
    additional_sources = [
        ("https://www.bbc.com/news", "BBC News"),
        ("https://www.reuters.com/", "Reuters"),
        ("https://apnews.com/", "Associated Press"),
        ("https://www.theguardian.com/", "The Guardian"),
        ("https://www.nytimes.com/", "New York Times"),
        ("https://www.whitehouse.gov/", "White House"),
        ("https://www.state.gov/", "US State Department"),
        ("https://www.fda.gov/", "FDA"),
        ("https://www.epa.gov/", "EPA"),
        ("https://www.usgs.gov/", "USGS"),
    ]
    
    print("=" * 70)
    print("Testing Current Whitelist Sources")
    print("=" * 70)
    
    working = []
    not_working = []
    
    for url, name in test_sources:
        print(f"\nTesting: {name}")
        print(f"  URL: {url}")
        result = test_url(url)
        
        if result['working']:
            print(f"  ✅ Working (Status: {result['status']}, Content: {result['content_length']} chars)")
            working.append((url, name))
        else:
            error = result.get('error', 'Unknown error')
            print(f"  ❌ Not working ({error})")
            not_working.append((url, name, error))
    
    print("\n" + "=" * 70)
    print("Testing Additional Reliable Sources")
    print("=" * 70)
    
    additional_working = []
    
    for url, name in additional_sources:
        print(f"\nTesting: {name}")
        print(f"  URL: {url}")
        result = test_url(url)
        
        if result['working']:
            print(f"  ✅ Working (Status: {result['status']}, Content: {result['content_length']} chars)")
            additional_working.append((url, name))
        else:
            error = result.get('error', 'Unknown error')
            print(f"  ❌ Not working ({error})")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nCurrent Whitelist:")
    print(f"  ✅ Working: {len(working)}/{len(test_sources)}")
    print(f"  ❌ Not Working: {len(not_working)}/{len(test_sources)}")
    
    print(f"\nAdditional Sources:")
    print(f"  ✅ Working: {len(additional_working)}/{len(additional_sources)}")
    
    if not_working:
        print(f"\n❌ Sources to Replace:")
        for url, name, error in not_working:
            print(f"  - {name}: {error}")
    
    if additional_working:
        print(f"\n✅ Recommended Additions:")
        for url, name in additional_working[:5]:
            print(f"  - {name}: {url}")


if __name__ == '__main__':
    main()
