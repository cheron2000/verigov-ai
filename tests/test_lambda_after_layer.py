"""Test Lambda after layer attachment"""

import requests
import json
import time

API_URL = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources"

def test_simple_claim():
    """Test with a simple claim"""
    
    claim = "The Moon orbits Earth"
    
    print(f"Testing claim: {claim}")
    print("="*60)
    
    try:
        response = requests.post(
            API_URL,
            json={'claim': claim, 'sources': []},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ SUCCESS!")
            print(f"Status: {result.get('status')}")
            print(f"Confidence: {result.get('confidence')}%")
            print(f"Explanation: {result.get('explanation')}")
            
            # Check if explanation contains JSON or error
            explanation = result.get('explanation', '')
            if 'No module named' in explanation:
                print(f"\n❌ ERROR: Still missing dependencies!")
                print(f"Full explanation: {explanation}")
            elif explanation.startswith('```json'):
                print(f"\n⚠️  WARNING: Explanation contains raw JSON")
                print(f"First 200 chars: {explanation[:200]}")
            else:
                print(f"\n✅ Explanation looks good!")
                
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")


if __name__ == '__main__':
    # Wait a bit for Lambda to be ready
    print("Waiting 5 seconds for Lambda to be ready...")
    time.sleep(5)
    test_simple_claim()
