#!/usr/bin/env python3
"""Quick update - recreate zip with fixed handler"""
import zipfile
import os
import shutil
from pathlib import Path

print("Creating fresh deployment package...")

# Remove old zip
if Path('lambda_deployment_fixed.zip').exists():
    Path('lambda_deployment_fixed.zip').unlink()

# Extract old zip to temp dir
temp_dir = Path('temp_lambda')
if temp_dir.exists():
    shutil.rmtree(temp_dir)
temp_dir.mkdir()

print("Extracting old package...")
with zipfile.ZipFile('lambda_deployment.zip', 'r') as zip_ref:
    zip_ref.extractall(temp_dir)

# Replace handler
print("Updating handler...")
shutil.copy('lambda/verify_handler.py', temp_dir / 'verify_handler.py')

# Create new zip
print("Creating new package...")
with zipfile.ZipFile('lambda_deployment_fixed.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(temp_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if file.endswith('.pyc'):
                continue
            file_path = Path(root) / file
            arcname = file_path.relative_to(temp_dir)
            zipf.write(file_path, arcname)

# Cleanup
shutil.rmtree(temp_dir)

size_mb = Path('lambda_deployment_fixed.zip').stat().st_size / (1024 * 1024)
print(f"✅ Created: lambda_deployment_fixed.zip ({size_mb:.2f} MB)")
