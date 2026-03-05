"""
One-click deployment script for VeriGov AI to AWS
Deploys Lambda functions, creates API endpoints, and hosts frontend on S3
"""
import subprocess
import sys
import time

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print("\n" + "="*60)
    print(f"🚀 {description}")
    print("="*60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    print("="*60)
    print("VeriGov AI - Full Stack AWS Deployment")
    print("="*60)
    print("\nThis script will:")
    print("  1. Deploy audit and whitelist Lambda functions")
    print("  2. Create API Gateway endpoints")
    print("  3. Deploy frontend to S3")
    print("  4. Provide you with the website URL")
    print("\n⏱️  Estimated time: 3-5 minutes")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    # Step 1: Deploy support Lambda functions
    if not run_script(
        'scripts/deploy_support_lambdas.py',
        'Step 1/3: Deploying Lambda Functions'
    ):
        print("\n❌ Deployment failed at Step 1")
        return
    
    print("\n⏳ Waiting 10 seconds for Lambda functions to be ready...")
    time.sleep(10)
    
    # Step 2: Sync whitelist data
    print("\n" + "="*60)
    print("🚀 Step 2/3: Syncing Whitelist Data")
    print("="*60)
    
    if not run_script(
        'scripts/sync_whitelist.py',
        'Syncing trusted sources to DynamoDB'
    ):
        print("\n⚠️  Warning: Whitelist sync failed, but continuing...")
    
    # Step 3: Deploy frontend to S3
    if not run_script(
        'scripts/deploy_to_s3.py',
        'Step 3/3: Deploying Frontend to S3'
    ):
        print("\n❌ Deployment failed at Step 3")
        return
    
    # Success!
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)
    
    print("\n🎉 Your VeriGov AI application is now live on AWS!")
    print("\n📝 Important Notes:")
    print("  1. Check the output above for your website URL")
    print("  2. Update API endpoints in static/script.js if needed")
    print("  3. Test all features before sharing")
    
    print("\n🔗 Quick Links:")
    print("  - Website: http://verigov-ai-frontend.s3-website.ap-south-1.amazonaws.com")
    print("  - API Gateway: https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev")
    print("  - DynamoDB Tables: AWS Console > DynamoDB")
    
    print("\n📚 For detailed information, see:")
    print("  - AWS_FULL_DEPLOYMENT_GUIDE.md")
    print("  - AWS_FRONTEND_HOSTING_PLAN.md")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
