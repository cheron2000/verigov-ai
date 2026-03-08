#!/usr/bin/env python3
"""Test local verification with the VeriGovApp class"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.verigov.main import VeriGovApp

print("=" * 70)
print("Testing Local Verification with VeriGovApp")
print("=" * 70)

# Initialize with local storage
app = VeriGovApp(storage_mode='local')

# Test claims that are already verified by government sources
test_claims = [
    {
        'claim': 'Vaccines help prevent infectious diseases',
        'category': 'Health'
    },
    {
        'claim': 'Digital India initiative was launched in 2015',
        'category': 'Government India'
    },
    {
        'claim': 'The United Nations was founded in 1945',
        'category': 'International'
    },
    {
        'claim': 'NASA was established in 1958',
        'category': 'Space'
    },
    {
        'claim': 'The White House is the official residence of the US President',
        'category': 'Government USA'
    }
]

for i, test in enumerate(test_claims, 1):
    print(f"\n{'=' * 70}")
    print(f"Test {i}: {test['category']}")
    print(f"Claim: {test['claim']}")
    print(f"{'=' * 70}")
    
    try:
        result = app.verify_claim(test['claim'], [])
        
        print(f"\n✅ Verification Complete!")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Research Method: {result.get('research_method', 'N/A')}")
        print(f"   Sources Checked: {result.get('sources_checked', 0)}")
        
        if result.get('explanation'):
            print(f"\n   Explanation: {result.get('explanation', '')[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 70}")
print("Test Complete")
print(f"{'=' * 70}")
