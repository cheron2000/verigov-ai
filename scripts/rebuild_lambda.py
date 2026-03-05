#!/usr/bin/env python3
"""Rebuild Lambda with correct platform dependencies"""
import subprocess
import sys
import zipfile
import shutil
from pathlib import Path

print("🔧 Rebuilding Lambda with platform-specific dependencies...")

# Clean up
package_dir = Path("lambda_package_clean")
if package_dir.exists():
    shutil.rmtree(package_dir)
package_dir.mkdir()

# Copy handler
print("📄 Copying handler...")
shutil.copy("lambda/verify_handler.py", package_dir / "verify_handler.py")

# Install dependencies for Linux (Lambda runtime)
print("📦 Installing dependencies for Linux/Lambda...")
result = subprocess.run([
    sys.executable, "-m", "pip", "install",
    "--platform", "manylinux2014_x86_64",
    "--implementation", "cp",
    "--python-version", "3.11",
    "--only-binary=:all:",
    "--upgrade",
    "-t", str(package_dir),
    "groq", "pydantic", "pydantic-core", "httpx", "httpcore", "certifi", "h11", "anyio", "sniffio"
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"⚠️  Warning: {result.stderr}")
    print("Trying without platform restrictions...")
    # Fallback: install without platform restrictions
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "-t", str(package_dir),
        "--upgrade",
        "groq", "pydantic", "pydantic-core", "boto3"
    ])

# Create zip
zip_path = Path("lambda_clean.zip")
if zip_path.exists():
    zip_path.unlink()

print("📦 Creating deployment package...")
import os
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(package_dir):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if file.endswith('.pyc'):
                continue
            file_path = Path(root) / file
            arcname = file_path.relative_to(package_dir)
            zipf.write(file_path, arcname)

# Cleanup
shutil.rmtree(package_dir)

size_mb = zip_path.stat().st_size / (1024 * 1024)
print(f"✅ Created: {zip_path} ({size_mb:.2f} MB)")

# Upload
print("\n🚀 Uploading to Lambda...")
import boto3
import os
import json

lambda_client = boto3.client('lambda', region_name='ap-south-1')

with open(zip_path, 'rb') as f:
    zip_data = f.read()

try:
    lambda_client.update_function_code(
        FunctionName='verigov-dev-verify',
        ZipFile=zip_data
    )
    print("✅ Code updated, waiting...")
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='verigov-dev-verify')
    print("✅ Lambda updated!")
    
    # Test
    print("\n🧪 Testing...")
    test_event = {'body': json.dumps({'claim': 'The Earth orbits the Sun', 'sources': []})}
    response = lambda_client.invoke(
        FunctionName='verigov-dev-verify',
        Payload=json.dumps(test_event)
    )
    
    result = json.loads(response['Payload'].read())
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        print(f"✅ SUCCESS!")
        print(f"   Status: {body.get('status')}")
        print(f"   Confidence: {body.get('confidence')}%")
        print(f"\n🎉 Lambda is working! API Gateway URL:")
        print(f"   https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify")
    else:
        print(f"❌ Still failing: {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
