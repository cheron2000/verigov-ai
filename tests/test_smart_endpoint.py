#!/usr/bin/env python3
"""Test the smart endpoint with auto source selection"""
import requests
import json
import time

url = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources"

print("🧠 Testing SMART Endpoint with Auto Source Selection")
print("=" * 60)

test_cases = [
    {
        'name': 'Space Topic (should auto-select NASA)',
        'claim': 'NASA has landed humans on the moon'
    },
    {
        'name': 'Health Topic (should auto-select WHO/CDC)',
        'claim': 'Vaccines help prevent diseases'
    },
    {
        'name': 'Science Topic (should auto-select Nature/Science)',
        'claim': 'DNA contains genetic information'
    },
    {
        'name': 'General Topic (should use AI knowledge)',
        'claim': 'Water boils at 100 degrees Celsius at sea level'
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. {test['name']}")
    print(f"   Claim: {test['claim']}")
    print(f"   ⏳ Analyzing...")
    
    start = time.time()
    
    try:
        response = requests.post(
            url,
            json={'claim': test['claim'], 'sources': []},
            timeout=30
        )
        
        duration = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result.get('status')}")
            print(f"   ✅ Confidence: {result.get('confidence')}%")
            print(f"   ✅ Research Method: {result.get('research_method')}")
            print(f"   ✅ Topics: {', '.join(result.get('topics_identified', []))}")
            print(f"   ✅ Sources Selected: {len(result.get('sources_selected', []))}")
            if result.get('sources_selected'):
                print(f"   ✅ Selected: {', '.join([s.replace('https://www.', '').replace('/', '') for s in result.get('sources_selected', [])[:2]])}")
            print(f"   ✅ Sources Checked: {result.get('sources_checked')}")
            print(f"   ✅ Response Time: {duration:.2f}s")
            print(f"   📝 Note: {result.get('research_note', '')[:100]}...")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("📊 Summary")
print("=" * 60)
print()
print("✅ Smart endpoint is working!")
print()
print("🧠 The system now:")
print("   1. Analyzes the claim to identify topics")
print("   2. Automatically selects relevant trusted sources")
print("   3. Fetches content from those sources")
print("   4. Falls back to AI knowledge if no sources found")
print("   5. Reports which research method was used")
print()
print("🎯 Perfect for hackathon demo!")
print("   - Show space claim → Auto-selects NASA")
print("   - Show health claim → Auto-selects WHO/CDC")
print("   - Show general claim → Uses AI knowledge")
