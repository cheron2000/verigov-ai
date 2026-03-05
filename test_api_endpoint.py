#!/usr/bin/env python3
"""Test the deployed API Gateway endpoint"""
import requests
import json

url = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify"

print(f"🧪 Testing API endpoint:")
print(f"   {url}")
print()

payload = {
    "claim": "The Earth orbits the Sun",
    "sources": []
}

print(f"📤 Sending request...")
print(f"   Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"📥 Response:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS!")
        print(f"   Verification ID: {result.get('verification_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Explanation: {result.get('explanation')}")
        print(f"   Timestamp: {result.get('timestamp')}")
        print()
        print(f"🎉 API is working! Share this URL with hackathon judges!")
    else:
        print(f"❌ Error:")
        print(f"   {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
    import traceback
    traceback.print_exc()
