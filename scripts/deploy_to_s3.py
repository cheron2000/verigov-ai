"""
Deploy VeriGov AI frontend to AWS S3 for static website hosting
"""
import boto3
import os
import mimetypes
from pathlib import Path

# Configuration
REGION = 'ap-south-1'
BUCKET_NAME = 'verigov-ai-frontend'  # Will be created if doesn't exist
ACCOUNT_ID = '448772857627'

s3_client = boto3.client('s3', region_name=REGION)

# Files to upload
FILES_TO_UPLOAD = [
    ('static/index.html', 'index.html'),
    ('static/style.css', 'style.css'),
    ('static/script.js', 'script.js'),
]


def create_bucket():
    """Create S3 bucket if it doesn't exist"""
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"✅ Bucket '{BUCKET_NAME}' already exists")
        return True
    except:
        print(f"Creating bucket '{BUCKET_NAME}'...")
        
        try:
            # Create bucket
            if REGION == 'us-east-1':
                s3_client.create_bucket(Bucket=BUCKET_NAME)
            else:
                s3_client.create_bucket(
                    Bucket=BUCKET_NAME,
                    CreateBucketConfiguration={'LocationConstraint': REGION}
                )
            
            print(f"✅ Bucket created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating bucket: {str(e)}")
            return False


def enable_static_website():
    """Enable static website hosting on the bucket"""
    try:
        s3_client.put_bucket_website(
            Bucket=BUCKET_NAME,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'index.html'}
            }
        )
        print(f"✅ Static website hosting enabled")
        return True
    except Exception as e:
        print(f"❌ Error enabling static website: {str(e)}")
        return False


def set_bucket_policy():
    """Set bucket policy to allow public read access"""
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
            }
        ]
    }
    
    try:
        import json
        s3_client.put_bucket_policy(
            Bucket=BUCKET_NAME,
            Policy=json.dumps(policy)
        )
        print(f"✅ Bucket policy set for public access")
        return True
    except Exception as e:
        print(f"❌ Error setting bucket policy: {str(e)}")
        return False


def disable_block_public_access():
    """Disable block public access settings"""
    try:
        s3_client.delete_public_access_block(Bucket=BUCKET_NAME)
        print(f"✅ Public access block disabled")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not disable public access block: {str(e)}")
        return False


def upload_file(local_path, s3_key):
    """Upload a file to S3"""
    try:
        # Determine content type
        content_type, _ = mimetypes.guess_type(local_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Upload file
        with open(local_path, 'rb') as f:
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=f,
                ContentType=content_type,
                CacheControl='max-age=300'  # 5 minutes cache
            )
        
        print(f"  ✅ {s3_key}")
        return True
        
    except Exception as e:
        print(f"  ❌ {s3_key}: {str(e)}")
        return False


def upload_files():
    """Upload all files to S3"""
    print("\nUploading files...")
    success_count = 0
    
    for local_path, s3_key in FILES_TO_UPLOAD:
        if os.path.exists(local_path):
            if upload_file(local_path, s3_key):
                success_count += 1
        else:
            print(f"  ⚠️  File not found: {local_path}")
    
    print(f"\n✅ Uploaded {success_count}/{len(FILES_TO_UPLOAD)} files")
    return success_count == len(FILES_TO_UPLOAD)


def get_website_url():
    """Get the website URL"""
    return f"http://{BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"


def main():
    print("="*60)
    print("VeriGov AI - Deploy Frontend to S3")
    print("="*60)
    
    # Step 1: Create bucket
    print("\n[1/5] Creating S3 bucket...")
    if not create_bucket():
        print("❌ Failed to create bucket")
        return
    
    # Step 2: Disable block public access
    print("\n[2/5] Configuring public access...")
    disable_block_public_access()
    
    # Step 3: Set bucket policy
    print("\n[3/5] Setting bucket policy...")
    if not set_bucket_policy():
        print("❌ Failed to set bucket policy")
        return
    
    # Step 4: Enable static website hosting
    print("\n[4/5] Enabling static website hosting...")
    if not enable_static_website():
        print("❌ Failed to enable static website hosting")
        return
    
    # Step 5: Upload files
    print("\n[5/5] Uploading files...")
    if not upload_files():
        print("⚠️  Some files failed to upload")
    
    # Print summary
    website_url = get_website_url()
    
    print("\n" + "="*60)
    print("DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"\n🌐 Website URL: {website_url}")
    print(f"\n📝 Next Steps:")
    print(f"  1. Update API endpoints in script.js")
    print(f"  2. Test the website")
    print(f"  3. (Optional) Set up CloudFront for HTTPS")
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
