#!/usr/bin/env python3
"""Check VeriGov AI system status"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def check_local_storage():
    """Check local storage status"""
    print("\n📁 LOCAL STORAGE STATUS")
    print("-" * 50)
    
    files = {
        'Audit Log': 'logs/audit.log',
        'Whitelist': 'config/whitelist.json',
        'Verifications': 'data/verifications',
        'Batch Results': 'data/batch_results'
    }
    
    for name, path in files.items():
        if os.path.exists(path):
            if os.path.isfile(path):
                size = os.path.getsize(path)
                print(f"✅ {name}: {path} ({size} bytes)")
            else:
                count = len(os.listdir(path)) if os.path.isdir(path) else 0
                print(f"✅ {name}: {path} ({count} files)")
        else:
            print(f"⚠️  {name}: {path} (not found)")

def check_aws_credentials():
    """Check AWS credentials"""
    print("\n🔐 AWS CREDENTIALS")
    print("-" * 50)
    
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Account: {identity['Account']}")
        print(f"✅ AWS User: {identity['Arn'].split('/')[-1]}")
        print(f"✅ Region: {os.getenv('AWS_REGION', 'Not set')}")
        return True
    except ImportError:
        print("⚠️  boto3 not installed")
        print("   Install with: pip install -r requirements-aws.txt")
        return False
    except Exception as e:
        print(f"❌ AWS credentials not configured: {e}")
        return False

def check_aws_permissions():
    """Check AWS permissions"""
    print("\n🔑 AWS PERMISSIONS")
    print("-" * 50)
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        region = os.getenv('AWS_REGION', 'ap-south-1')
        
        # Check DynamoDB
        try:
            dynamodb = boto3.client('dynamodb', region_name=region)
            dynamodb.list_tables()
            print("✅ DynamoDB: Access granted")
        except ClientError as e:
            if 'AccessDenied' in str(e):
                print("❌ DynamoDB: Access denied")
                print("   Request permissions from AWS admin")
            else:
                print(f"⚠️  DynamoDB: {e}")
        
        # Check CloudFormation
        try:
            cf = boto3.client('cloudformation', region_name=region)
            cf.list_stacks(StackStatusFilter=['CREATE_COMPLETE'])
            print("✅ CloudFormation: Access granted")
        except ClientError as e:
            if 'AccessDenied' in str(e):
                print("❌ CloudFormation: Access denied")
            else:
                print(f"⚠️  CloudFormation: {e}")
        
        # Check S3
        try:
            s3 = boto3.client('s3', region_name=region)
            s3.list_buckets()
            print("✅ S3: Access granted")
        except ClientError as e:
            if 'AccessDenied' in str(e):
                print("❌ S3: Access denied")
            else:
                print(f"⚠️  S3: {e}")
                
    except ImportError:
        print("⚠️  boto3 not installed")

def check_dynamodb_tables():
    """Check DynamoDB tables"""
    print("\n🗄️  DYNAMODB TABLES")
    print("-" * 50)
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        region = os.getenv('AWS_REGION', 'ap-south-1')
        env = os.getenv('ENVIRONMENT', 'dev')
        dynamodb = boto3.client('dynamodb', region_name=region)
        
        tables = [
            f'verigov-{env}-audit-logs',
            f'verigov-{env}-verifications',
            f'verigov-{env}-whitelist'
        ]
        
        for table_name in tables:
            try:
                response = dynamodb.describe_table(TableName=table_name)
                status = response['Table']['TableStatus']
                item_count = response['Table']['ItemCount']
                print(f"✅ {table_name}: {status} ({item_count} items)")
            except ClientError as e:
                if 'ResourceNotFoundException' in str(e):
                    print(f"⚠️  {table_name}: Not deployed")
                    print(f"   Deploy with: python scripts/deploy_dynamodb.py deploy")
                else:
                    print(f"❌ {table_name}: {e}")
                    
    except ImportError:
        print("⚠️  boto3 not installed")
    except Exception as e:
        print(f"❌ Cannot check tables: {e}")

def check_environment():
    """Check environment configuration"""
    print("\n⚙️  ENVIRONMENT CONFIGURATION")
    print("-" * 50)
    
    env_vars = {
        'STORAGE_MODE': os.getenv('STORAGE_MODE', 'Not set'),
        'AWS_REGION': os.getenv('AWS_REGION', 'Not set'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'Not set'),
        'AI_PROVIDER': os.getenv('AI_PROVIDER', 'Not set'),
        'GROQ_API_KEY': '***' if os.getenv('GROQ_API_KEY') else 'Not set'
    }
    
    for key, value in env_vars.items():
        if value == 'Not set':
            print(f"⚠️  {key}: {value}")
        else:
            print(f"✅ {key}: {value}")

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 PYTHON DEPENDENCIES")
    print("-" * 50)
    
    dependencies = {
        'flask': 'Web framework',
        'requests': 'HTTP client',
        'groq': 'Groq AI client',
        'boto3': 'AWS SDK (optional)',
        'python-dotenv': 'Environment variables'
    }
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"✅ {package}: Installed ({description})")
        except ImportError:
            if package == 'boto3':
                print(f"⚠️  {package}: Not installed ({description})")
                print(f"   Install with: pip install -r requirements-aws.txt")
            else:
                print(f"❌ {package}: Not installed ({description})")
                print(f"   Install with: pip install {package}")

def main():
    """Main status check"""
    print("=" * 50)
    print("🏛️  VERIGOV AI - SYSTEM STATUS")
    print("=" * 50)
    
    # Check local storage
    check_local_storage()
    
    # Check environment
    check_environment()
    
    # Check dependencies
    check_dependencies()
    
    # Check AWS credentials
    has_aws = check_aws_credentials()
    
    # Check AWS permissions (if credentials exist)
    if has_aws:
        check_aws_permissions()
        check_dynamodb_tables()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    storage_mode = os.getenv('STORAGE_MODE', 'local')
    print(f"\n✅ Current Storage Mode: {storage_mode}")
    
    if storage_mode == 'local':
        print("✅ Local storage is fully functional")
        print("\n💡 To use AWS storage:")
        print("   1. Request DynamoDB permissions (see AWS_SETUP_GUIDE.md)")
        print("   2. Deploy tables: python scripts/deploy_dynamodb.py deploy")
        print("   3. Update .env: STORAGE_MODE=aws")
    elif storage_mode == 'aws':
        print("⚠️  AWS storage mode selected")
        print("   Make sure DynamoDB tables are deployed")
    elif storage_mode == 'hybrid':
        print("⚠️  Hybrid storage mode selected")
        print("   Writes to both local and AWS")
    
    print("\n📚 Documentation:")
    print("   • AWS_SETUP_GUIDE.md - AWS setup instructions")
    print("   • DYNAMODB_GUIDE.md - DynamoDB usage guide")
    print("   • AWS_PROGRESS.md - Implementation progress")
    
    print("\n🧪 Test Commands:")
    print("   • python test_local_integration.py - Test local storage")
    print("   • python -m src.verigov.main verify 'Test' - Quick test")
    print("   • python app.py - Start web interface")
    
    print("=" * 50)

if __name__ == '__main__':
    main()