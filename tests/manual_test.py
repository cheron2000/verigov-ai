#!/usr/bin/env python3
"""Manual test script for VeriGov AI - Enter claims to verify"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.verigov.main import VeriGovApp

print("=" * 70)
print("VeriGov AI - Manual Testing")
print("=" * 70)
print("\nThis script allows you to manually test claims.")
print("Type 'quit' to exit.\n")

# Initialize with local storage
try:
    app = VeriGovApp(storage_mode='local')
    print("✅ VeriGov AI initialized with local storage\n")
except Exception as e:
    print(f"❌ Error initializing: {e}")
    sys.exit(1)

print("Enter a claim to verify (or 'quit' to exit):")
print("-" * 70)

while True:
    try:
        claim = input("\n📝 Claim: ").strip()
        
        if claim.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not claim:
            print("⚠️  Please enter a claim")
            continue
        
        print(f"\n🔍 Verifying: {claim}")
        print("-" * 70)
        
        result = app.verify_claim(claim, [])
        
        print(f"\n{'=' * 70}")
        print("VERIFICATION RESULTS")
        print(f"{'=' * 70}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 'N/A')}%")
        print(f"Research Method: {result.get('research_method', 'N/A')}")
        print(f"Topics: {', '.join(result.get('topics_identified', []))}")
        print(f"Sources Checked: {result.get('sources_checked', 0)}")
        
        if result.get('sources_selected'):
            print(f"Sources Selected: {result.get('sources_selected', [])}")
        
        print(f"\nExplanation:")
        print(result.get('explanation', 'N/A'))
        
        print(f"\n{'=' * 70}")
        print("Enter another claim (or 'quit' to exit):")
        print("-" * 70)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
