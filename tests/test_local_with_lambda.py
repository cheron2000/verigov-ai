#!/usr/bin/env python3
"""Test local claims using the deployed Lambda endpoint"""
import boto3
import json

# Deployed Lambda endpoint
function_name = 'verigov-dev-verify-sources'
region = 'ap-south-1'

lambda_client = boto3.client('lambda', region_name=region)

print("=" * 70)
print("Testing Local Claims with Deployed Lambda")
print("=" * 70)
print("\nThis script tests verified government claims using the deployed Lambda.")
print("Run this manually to see the verification results.\n")

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
        test_event = {
            'body': json.dumps({
                'claim': test['claim'],
                'sources': []
            })
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') == 200:
            body = json.loads(result['body'])
            
            print(f"\n✅ Verification Complete!")
            print(f"   Status: {body.get('status')}")
            print(f"   Confidence: {body.get('confidence')}%")
            print(f"   Research Method: {body.get('research_method')}")
            print(f"   Topics: {', '.join(body.get('topics_identified', []))}")
            print(f"   Sources Checked: {body.get('sources_checked', 0)}")
            
            if body.get('sources_selected'):
                print(f"   Sources Selected: {body.get('sources_selected', [])}")
            
            if body.get('explanation'):
                explanation = body.get('explanation', '')[:300]
                print(f"\n   Explanation: {explanation}...")
                
        else:
            print(f"❌ Error: {result.get('statusCode')}")
            print(f"   {result.get('body', '')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 70}")
print("Test Complete")
print(f"{'=' * 70}")
print("\n💡 Tip: The Lambda is already deployed with all the smart features.")
print("   This test uses the deployed Lambda to verify claims.")
