#!/usr/bin/env python3
"""
Create demo verifications for presentation
"""

import requests
import json
import time

API_URL = "https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources"

# Demo claims that should verify well
DEMO_CLAIMS = [
    # Space facts
    "The Moon is Earth's only natural satellite",
    "Mars is the fourth planet from the Sun",
    "The International Space Station orbits Earth",
    
    # Health facts
    "The human heart pumps blood throughout the body",
    "Vaccines help prevent infectious diseases",
    "The human body has 206 bones",
    
    # Science facts
    "Water boils at 100 degrees Celsius at sea level",
    "DNA carries genetic information",
    "Photosynthesis converts sunlight into energy",
    
    # Government facts
    "The United Nations was founded in 1945",
    "The US Census is conducted every 10 years",
    "The World Health Organization is a UN agency",
    
    # Environment facts
    "Carbon dioxide is a greenhouse gas",
    "The Paris Agreement addresses climate change",
    "Renewable energy includes solar and wind power",
]

def verify_claim(claim):
    """Verify a single claim"""
    print(f"\n{'='*70}")
    print(f"Claim: {claim}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            API_URL,
            json={'claim': claim, 'sources': []},
            timeout=35
        )
        response.raise_for_status()
        
        result = response.json()
        
        print(f"✅ Status: {result.get('status')}")
        print(f"📊 Confidence: {result.get('confidence')}%")
        print(f"📚 Topics: {', '.join(result.get('topics_identified', []))}")
        print(f"🌐 Sources: {len(result.get('sources_selected', []))}")
        print(f"📝 ID: {result.get('verification_id')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎯 Creating Demo Verifications")
    print("="*70)
    print(f"Total claims to verify: {len(DEMO_CLAIMS)}")
    print()
    
    success = 0
    failed = 0
    
    for i, claim in enumerate(DEMO_CLAIMS, 1):
        print(f"\n[{i}/{len(DEMO_CLAIMS)}]")
        
        if verify_claim(claim):
            success += 1
        else:
            failed += 1
        
        # Rate limiting
        if i < len(DEMO_CLAIMS):
            time.sleep(2)
    
    print(f"\n{'='*70}")
    print(f"✅ Success: {success}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(DEMO_CLAIMS)}")
    print()
    print("🎉 Demo verifications created!")

if __name__ == "__main__":
    main()
