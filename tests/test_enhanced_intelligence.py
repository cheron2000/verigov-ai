"""Test enhanced intelligence layer with various claims"""

import requests
import json

# Lambda API endpoint
API_URL = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources"

def test_claim(claim, expected_status=None):
    """Test a single claim"""
    print(f"\n{'='*80}")
    print(f"CLAIM: {claim}")
    print(f"{'='*80}")
    
    payload = {
        "claim": claim,
        "sources": []
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=35)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"✅ Status: {result.get('status', 'N/A')}")
        print(f"📊 Confidence: {result.get('confidence', 'N/A')}%")
        print(f"🔍 Research Method: {result.get('research_method', 'N/A')}")
        print(f"📚 Topics: {', '.join(result.get('topics_identified', []))}")
        print(f"🌐 Sources Selected: {len(result.get('sources_selected', []))}")
        print(f"📖 Explanation: {result.get('explanation', 'N/A')[:200]}...")
        
        if expected_status:
            if result.get('status') == expected_status:
                print(f"✅ PASS - Got expected status: {expected_status}")
            else:
                print(f"❌ FAIL - Expected {expected_status}, got {result.get('status')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("🧪 Testing Enhanced Intelligence Layer")
    print("="*80)
    
    # Test 1: Basic scientific fact
    test_claim("The Earth orbits the Sun", expected_status="VERIFIED")
    
    # Test 2: False claim
    test_claim("Sharks are mammals", expected_status="UNVERIFIED")
    
    # Test 3: Statistical claim
    test_claim("Water boils at 100 degrees Celsius at sea level", expected_status="VERIFIED")
    
    # Test 4: Biographical query
    test_claim("Who is Narendra Modi", expected_status="VERIFIED")
    
    # Test 5: Complex scientific claim
    test_claim("Humans use only 10% of their brain", expected_status="UNVERIFIED")
    
    # Test 6: Space fact
    test_claim("The Moon is Earth's only natural satellite", expected_status="VERIFIED")
    
    print(f"\n{'='*80}")
    print("✅ Testing Complete!")
    print(f"{'='*80}")
