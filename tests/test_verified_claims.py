#!/usr/bin/env python3
"""Test with verified government claims - run manually"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.verigov.main import VeriGovApp

print("=" * 70)
print("VeriGov AI - Verified Claims Test")
print("=" * 70)
print("\nThis script tests with claims that are already verified by governments.")
print("Run this manually to see the verification results.\n")

# Initialize with local storage
try:
    app = VeriGovApp(storage_mode='local')
    print("✅ VeriGov AI initialized with local storage\n")
except Exception as e:
    print(f"❌ Error initializing: {e}")
    sys.exit(1)

# Predefined verified claims
verified_claims = [
    {
        'claim': 'Vaccines help prevent infectious diseases',
        'category': 'Health',
        'note': 'WHO and CDC recommend vaccines'
    },
    {
        'claim': 'Digital India initiative was launched in 2015',
        'category': 'Government India',
        'note': 'Official government initiative'
    },
    {
        'claim': 'The United Nations was founded in 1945',
        'category': 'International',
        'note': 'UN official history'
    },
    {
        'claim': 'NASA was established in 1958',
        'category': 'Space',
        'note': 'NASA official history'
    },
    {
        'claim': 'The White House is the official residence of the US President',
        'category': 'Government USA',
        'note': 'White House official information'
    },
    {
        'claim': 'The Paris Agreement on climate change was signed in 2015',
        'category': 'Environment',
        'note': 'UNFCCC official agreement'
    },
    {
        'claim': 'World Health Organization recommends vaccination',
        'category': 'Health',
        'note': 'WHO official position'
    },
    {
        'claim': 'The Census Bureau conducts the US population count every 10 years',
        'category': 'Government USA',
        'note': 'US Census Bureau official information'
    }
]

print(f"Testing {len(verified_claims)} verified claims...\n")

for i, test in enumerate(verified_claims, 1):
    print(f"\n{'=' * 70}")
    print(f"Test {i}/{len(verified_claims)}: {test['category']}")
    print(f"Claim: {test['claim']}")
    print(f"Note: {test['note']}")
    print(f"{'=' * 70}")
    
    try:
        result = app.verify_claim(test['claim'], [])
        
        print(f"\n✅ Verification Complete!")
        print(f"   Status: {result.get('status')}")
        print(f"   Confidence: {result.get('confidence')}%")
        print(f"   Research Method: {result.get('research_method')}")
        print(f"   Sources Checked: {result.get('sources_checked')}")
        
        if result.get('explanation'):
            explanation = result.get('explanation', '')[:300]
            print(f"\n   Explanation: {explanation}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 70}")
print("Test Complete")
print(f"{'=' * 70}")
print("\n💡 Tip: Run this script manually to see the full verification results.")
print("   The verification process may take a few seconds per claim.")
