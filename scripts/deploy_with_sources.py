#!/usr/bin/env python3
"""Deploy Lambda with source fetching capability"""
import subprocess
import sys
import zipfile
import shutil
import boto3
import json
import os
from pathlib import Path

print("🔧 Building Lambda with source fetching...")

# Clean up
package_dir = Path("lambda_with_sources")
if package_dir.exists():
    shutil.rmtree(package_dir)
package_dir.mkdir()

# Copy enhanced handler as verify_handler.py
print("📄 Copying enhanced handler...")
shutil.copy("lambda/verify_handler_with_sources.py", package_dir / "verify_handler.py")

# Install dependencies (requests + beautifulsoup4 for web scraping)
print("📦 Installing dependencies...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "-t", str(package_dir),
    "--upgrade", "--quiet",
    "requests", "boto3", "beautifulsoup4"
])

# Create zip
zip_path = Path("lambda_with_sources.zip")
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
print("\n🚀 Uploading to Lambda...")
lambda_client = boto3.client('lambda', region_name='ap-south-1')

with open(zip_path, 'rb') as f:
    zip_data = f.read()

lambda_client.update_function_code(
    FunctionName='verigov-dev-verify',
    ZipFile=zip_data
)
print("✅ Code updated, waiting...")

waiter = lambda_client.get_waiter('function_updated')
waiter.wait(FunctionName='verigov-dev-verify')
print("✅ Lambda updated with source fetching capability!")

# Test
print("\n🧪 Testing with source URL...")
test_event = {
    'body': json.dumps({
        'claim': 'NASA landed humans on the moon',
        'sources': ['https://www.nasa.gov/']
    })
}

response = lambda_client.invoke(
    FunctionName='verigov-dev-verify',
    Payload=json.dumps(test_event)
)

result = json.loads(response['Payload'].read())
print(f"Status Code: {response['StatusCode']}")

if result.get('statusCode') == 200:
    body = json.loads(result['body'])
    print(f"✅ SUCCESS!")
    print(f"   Status: {body.get('status')}")
    print(f"   Confidence: {body.get('confidence')}%")
    print(f"   Sources Checked: {body.get('sources_checked')}")
    print(f"   Explanation: {body.get('explanation', '')[:150]}...")
    print(f"\n🎉 Lambda now fetches and analyzes from source URLs!")
else:
    print(f"❌ Failed: {result}")

print("\n📝 Note: Now when you provide source URLs, Lambda will:")
print("   1. Fetch content from those URLs")
print("   2. Extract text from the web pages")
print("   3. Pass the content to AI for analysis")
print("   4. Return verification based on actual source content")
