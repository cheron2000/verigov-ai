#!/usr/bin/env python3
"""Create S3 bucket for VeriGov AI - Cost optimized"""

import sys
import boto3
from botocore.exceptions import ClientError

def create_s3_bucket(region='ap-south-1', env='dev'):
    """Create S3 bucket with cost-optimized settings"""
    
    print("=" * 60)
    print("🪣 CREATING S3 BUCKET ")
    print("=" * 60)
    
    # Initialize S3 client
    s3 = boto3.client('s3', region_name=region)
    sts = boto3.client('sts')
    
    # Get account ID
    account_id = sts.get_caller_identity()['Account']
    
    # Bucket name (must be globally unique)
    bucket_name = f"verigov-{env}-data-{account_id}"
    
    print(f"\n📍 Region: {region}")
    print(f"🏷️  Environment: {env}")
    print(f"🪣 Bucket Name: {bucket_name}")
    
    try:
        # Create bucket
        print(f"\n📦 Creating bucket...")
        
        if region == 'us-east-1':
            # us-east-1 doesn't need LocationConstraint
            s3.create_bucket(Bucket=bucket_name)
        else:
            # Other regions need LocationConstraint
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"   ✅ Bucket created: {bucket_name}")
        
        # Enable encryption (no extra cost)
        print(f"\n🔒 Enabling encryption...")
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        )
        print(f"   ✅ Encryption enabled (AES256)")
        
        # Enable versioning (minimal cost, good for safety)
        print(f"\n📚 Enabling versioning...")
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"   ✅ Versioning enabled")
        
        # Add lifecycle policy to minimize costs
        print(f"\n♻️  Setting up lifecycle policy...")
        s3.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID': 'DeleteOldVersions',
                        'Status': 'Enabled',
                        'NoncurrentVersionExpiration': {
                            'NoncurrentDays': 30  # Delete old versions after 30 days
                        },
                        'Filter': {'Prefix': ''}
                    },
                    {
                        'ID': 'TransitionToIA',
                        'Status': 'Enabled',
                        'Transitions': [
                            {
                                'Days': 90,  # Move to cheaper storage after 90 days
                                'StorageClass': 'STANDARD_IA'
                            }
                        ],
                        'Filter': {'Prefix': 'audit/'}  # Only for audit logs
                    }
                ]
            }
        )
        print(f"   ✅ Lifecycle policy set (cost optimization)")
        
        # Block public access (security best practice)
        print(f"\n🔐 Blocking public access...")
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"   ✅ Public access blocked")
        
        # Add tags
        print(f"\n🏷️  Adding tags...")
        s3.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {'Key': 'Environment', 'Value': env},
                    {'Key': 'Application', 'Value': 'VeriGov-AI'},
                    {'Key': 'CostCenter', 'Value': 'Development'},
                    {'Key': 'ManagedBy', 'Value': 'Script'}
                ]
            }
        )
        print(f"   ✅ Tags added")
        
        print("\n" + "=" * 60)
        print("✅ S3 BUCKET CREATED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n💰 COST INFORMATION:")
        print("   • Storage: $0.023 per GB per month")
        print("   • PUT requests: $0.005 per 1,000 requests")
        print("   • GET requests: $0.0004 per 1,000 requests")
        print("   • Expected cost: < $0.10/month for development")
        
        print("\n📊 COST OPTIMIZATION FEATURES:")
        print("   ✅ Lifecycle policy: Old versions deleted after 30 days")
        print("   ✅ Transition to IA: Audit logs moved to cheaper storage after 90 days")
        print("   ✅ Encryption: Enabled (no extra cost)")
        print("   ✅ Versioning: Enabled (minimal cost)")
        
        print("\n📋 NEXT STEPS:")
        print("   1. Test AWS storage: python -m src.verigov.main --storage aws verify 'Test'")
        print("   2. Check status: python scripts/check_status.py")
        print("   3. Monitor costs: python scripts/check_aws_costs.py")
        
        print("\n⚠️  COST SAVING TIPS:")
        print("   • Use local storage for development when possible")
        print("   • AWS storage is for testing and production")
        print("   • Monitor bucket size regularly")
        print("   • Delete bucket when not needed: aws s3 rb s3://{bucket_name} --force")
        
        print("=" * 60)
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"\n✅ Bucket already exists: {bucket_name}")
            return True
        elif error_code == 'BucketAlreadyExists':
            print(f"\n❌ Bucket name taken globally: {bucket_name}")
            print(f"   Try a different environment or account ID")
            return False
        else:
            print(f"\n❌ Error: {e.response['Error']['Message']}")
            return False
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    try:
        success = create_s3_bucket(region='ap-south-1', env='dev')
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()