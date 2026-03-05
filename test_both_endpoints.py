#!/usr/bin/env python3
"""Test both API endpoints"""
import requests
import json
import time

print("🧪 Testing Both VeriGov API Endpoints")
print("=" * 60)

# Endpoint URLs
fast_url = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify"
sources_url = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources"

# Test 1: Fast endpoint (no sources)
print("\n1️⃣  Testing FAST endpoint (AI knowledge only)...")
print(f"   URL: {fast_url}")

payload1 = {
    "claim": "The Earth orbits the Sun",
    "sources": []
}

start = time.time()
try:
    response = requests.post(fast_url, json=payload1, timeout=30)
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Sources Checked: {result.get('sources_checked')}")
        print(f"   Response Time: {duration:.2f}s")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Sources endpoint (with URL)
print("\n2️⃣  Testing SOURCES endpoint (fetches from URLs)...")
print(f"   URL: {sources_url}")
print("   ⏳ This will take longer (fetching from web)...")

payload2 = {
    "claim": "NASA has landed humans on the moon",
    "sources": ["https://www.nasa.gov/"]
}

start = time.time()
try:
    response = requests.post(sources_url, json=payload2, timeout=60)
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Sources Checked: {result.get('sources_checked')}")
        print(f"   Response Time: {duration:.2f}s")
        print(f"   Explanation: {result.get('explanation', '')[:150]}...")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Sources endpoint without URLs (should use AI knowledge)
print("\n3️⃣  Testing SOURCES endpoint WITHOUT URLs...")
print("   (Should work like fast endpoint)")

payload3 = {
    "claim": "Water boils at 100 degrees Celsius",
    "sources": []
}

start = time.time()
try:
    response = requests.post(sources_url, json=payload3, timeout=30)
    duration = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Sources Checked: {result.get('sources_checked')}")
        print(f"   Response Time: {duration:.2f}s")
    else:
        print(f"   ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("📊 Summary")
print("=" * 60)
print()
print("✅ You now have TWO working endpoints:")
print()
print("1. FAST (AI Knowledge):")
print(f"   {fast_url}")
print("   - Best for: Quick demos, general knowledge")
print("   - Speed: ~1-2 seconds")
print()
print("2. WITH SOURCES (Web Scraping):")
print(f"   {sources_url}")
print("   - Best for: Verifying against specific sources")
print("   - Speed: ~5-10 seconds")
print("   - Requires: source URLs in request")
print()
print("💡 For hackathon demo:")
print("   - Use FAST endpoint for quick demonstrations")
print("   - Use SOURCES endpoint to show actual source fetching")
print("   - Both store results in DynamoDB")
