"""Example: Batch verification with report generation"""

import sys
import json
sys.path.insert(0, 'src')

from verigov.main import VeriGovApp


def main():
    """Generate verification report for multiple claims"""
    app = VeriGovApp()
    
    # Multiple claims to verify
    claims = [
        "The voting age in the United States is 18",
        "Social Security benefits are adjusted annually for inflation",
        "Medicare covers prescription drugs"
    ]
    
    print("Verifying multiple claims...")
    results = app.verify_batch(claims)
    
    # Generate report
    report = {
        "total_claims": len(claims),
        "verified": sum(1 for r in results if r["status"] == "VERIFIED"),
        "results": results
    }
    
    # Save to file
    with open("verification_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report generated: verification_report.json")
    print(f"Total claims: {report['total_claims']}")
    print(f"Verified: {report['verified']}")


if __name__ == "__main__":
    main()
