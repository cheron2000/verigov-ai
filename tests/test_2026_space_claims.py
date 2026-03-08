"""Test 2026 space claims with enhanced intelligence layer"""

import requests
import json
import time

API_URL = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources"

# 5 space claims for 2026
CLAIMS = [
    "NASA Artemis II will send astronauts around the Moon in 2026",
    "The Moon is Earth's only natural satellite",
    "Mars is the fourth planet from the Sun",
    "NASA operates the International Space Station",
    "SpaceX Starship is being developed for Moon missions"
]

def test_claim(claim):
    """Test a single claim"""
    try:
        response = requests.post(API_URL, json={'claim': claim, 'sources': []}, timeout=35)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}


if __name__ == "__main__":
    print("="*80)
    print("Testing 5 Space Claims with Enhanced Intelligence Layer")
    print("="*80)
    
    for i, claim in enumerate(CLAIMS, 1):
        print(f"\n{i}. CLAIM: {claim}")
        print("-"*80)
        
        result = test_claim(claim)
        
        if 'error' in result:
            print(f"   ERROR: {result['error']}")
        else:
            print(f"   Status: {result.get('status')}")
            print(f"   Confidence: {result.get('confidence')}%")
            print(f"   Topics: {result.get('topics_identified')}")
            print(f"   Sources Checked: {result.get('sources_checked')}")
            explanation = result.get('explanation', '')
            print(f"   Explanation ({len(explanation)} chars):")
            print(f"   {explanation}")
        
        time.sleep(2)  # Rate limiting
    
    print("\n" + "="*80)
    print("Testing Complete!")
    print("="*80)
