#!/usr/bin/env python3
"""Test all frontend endpoints"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"
API_URL = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify"

print("🧪 Testing VeriGov Frontend Endpoints")
print("=" * 50)

# Test 1: Homepage
print("\n1️⃣  Testing Homepage...")
try:
    response = requests.get(BASE_URL, timeout=5)
    if response.status_code == 200:
        print("   ✅ Homepage loads successfully")
        print(f"   Status: {response.status_code}")
    else:
        print(f"   ❌ Homepage failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Whitelist endpoint
print("\n2️⃣  Testing Whitelist Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/whitelist", timeout=5)
    if response.status_code == 200:
        data = response.json()
        sources = data.get('sources', [])
        print(f"   ✅ Whitelist endpoint working")
        print(f"   Sources: {len(sources)} configured")
        if sources:
            print(f"   Example: {sources[0].get('domain', 'N/A')}")
    else:
        print(f"   ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Audit endpoint
print("\n3️⃣  Testing Audit Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/audit?limit=5", timeout=5)
    if response.status_code == 200:
        entries = response.json()
        print(f"   ✅ Audit endpoint working")
        print(f"   Entries: {len(entries)} recent activities")
        if entries:
            print(f"   Latest: {entries[0].get('event_type', 'N/A')}")
    else:
        print(f"   ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Verification via Lambda (API Gateway)
print("\n4️⃣  Testing Verification (Lambda API)...")
try:
    payload = {
        "claim": "The Earth orbits the Sun",
        "sources": []
    }
    
    print("   📤 Sending request to Lambda...")
    start_time = time.time()
    
    response = requests.post(
        API_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Verification successful!")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Response time: {duration:.2f}s")
        print(f"   Verification ID: {result.get('verification_id')}")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Local Flask verify endpoint (should still work)
print("\n5️⃣  Testing Local Flask Verify Endpoint...")
try:
    payload = {
        "claim": "Water boils at 100 degrees Celsius",
        "sources": []
    }
    
    response = requests.post(
        f"{BASE_URL}/api/verify",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Local verification working")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
    else:
        print(f"   ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "=" * 50)
print("📊 Test Summary")
print("=" * 50)
print("\n✅ All endpoints tested!")
print("\n🌐 Frontend URL: http://127.0.0.1:5000")
print("🚀 Lambda API: https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify")
print("\n💡 Next: Open http://127.0.0.1:5000 in your browser to test the UI")
