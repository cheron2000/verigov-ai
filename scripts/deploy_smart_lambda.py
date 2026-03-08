#!/usr/bin/env python3
"""Deploy smart Lambda with automatic source selection"""
import subprocess
import sys
import zipfile
import shutil
import boto3
import json
import os
from pathlib import Path

print("🧠 Building SMART Lambda with auto source selection...")
print("=" * 50)

# Update the existing sources Lambda
function_name = 'verigov-dev-verify-sources'

# Clean up
package_dir = Path("lambda_smart")
if package_dir.exists():
    shutil.rmtree(package_dir)
package_dir.mkdir()

# Copy smart handler
print("📄 Copying smart handler...")
shutil.copy("lambda/verify_handler_smart.py", package_dir / "verify_handler.py")

# Install dependencies
print("📦 Installing dependencies...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "-t", str(package_dir),
    "--upgrade", "--quiet",
    "requests", "boto3", "beautifulsoup4", "lxml", "groq"
])

# Create zip
zip_path = Path("lambda_smart.zip")
if zip_path.exists():
    zip_path.unlink()

print("📦 Creating deployment package...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(package_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if file.endswith('.pyc'):
                continue
            file_path = Path(root) / file
            arcname = file_path.relative_to(package_dir)
            zipf.write(file_path, arcname)

shutil.rmtree(package_dir)

size_mb = zip_path.stat().st_size / (1024 * 1024)
print(f"✅ Created: {zip_path} ({size_mb:.2f} MB)")

# Upload
print(f"\n🚀 Updating Lambda: {function_name}...")
lambda_client = boto3.client('lambda', region_name='ap-south-1')

with open(zip_path, 'rb') as f:
    zip_data = f.read()

lambda_client.update_function_code(
    FunctionName=function_name,
    ZipFile=zip_data
)
print("✅ Code updated, waiting...")

waiter = lambda_client.get_waiter('function_updated')
waiter.wait(FunctionName=function_name)
print("✅ Lambda updated with SMART capabilities!")

# Test scenarios
print("\n" + "=" * 50)
print("🧪 Testing Smart Source Selection")
print("=" * 50)

test_cases = [
    {
        'name': 'Space Topic (should auto-select NASA)',
        'claim': 'NASA has landed humans on the moon',
        'sources': []
    },
    {
        'name': 'Health Topic (should auto-select WHO/CDC)',
        'claim': 'Vaccines help prevent diseases',
        'sources': []
    },
    {
        'name': 'General Topic (should use AI knowledge)',
        'claim': 'Water boils at 100 degrees Celsius',
        'sources': []
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. {test['name']}")
    print(f"   Claim: {test['claim']}")
    
    test_event = {'body': json.dumps(test)}
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(test_event)
    )
    
    result = json.loads(response['Payload'].read())
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        print(f"   ✅ Status: {body.get('status')}")
        print(f"   ✅ Research Method: {body.get('research_method')}")
        print(f"   ✅ Topics: {', '.join(body.get('topics_identified', []))}")
        print(f"   ✅ Sources Selected: {len(body.get('sources_selected', []))}")
        print(f"   ✅ Note: {body.get('research_note', '')[:80]}...")
    else:
        print(f"   ❌ Failed: {result}")

print("\n" + "=" * 50)
print("✅ Smart Lambda Deployed!")
print()
print("🧠 New Capabilities:")
print("   1. Analyzes claim to identify topics")
print("   2. Automatically selects relevant trusted sources")
print("   3. Fetches from selected sources")
print("   4. Falls back to AI knowledge if no sources found")
print("   5. Reports research method used")
print()
print("📝 The system now:")
print("   - Detects space topics → Uses NASA")
print("   - Detects health topics → Uses WHO/CDC/NIH")
print("   - Detects science topics → Uses Nature/Science journals")
print("   - Detects government topics → Uses relevant gov sites")
print("   - Falls back to AI for general knowledge")
