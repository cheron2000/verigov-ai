"""Example: Verify a single claim using the Python API"""

from verigov.main import VeriGovApp

def main():
    # Initialize the app
    app = VeriGovApp()
    
    # Verify a claim with sources
    result = app.verify_claim(
        claim="The federal minimum wage is $7.25 per hour",
        sources=["https://www.dol.gov/agencies/whd/minimum-wage"]
    )
    
    print(f"\nResult:")
    print(f"  Status: {result['status']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"  Explanation: {result['explanation'][:200]}...")

if __name__ == "__main__":
    main()
