#!/usr/bin/env python3
"""
Check current AWS costs for VeriGov AI project
"""

import boto3
import sys
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError


def check_aws_costs():
    """Check current AWS costs and provide budget guidance"""
    
    try:
        # Cost Explorer API
        ce = boto3.client('ce', region_name='us-east-1')
        
        print("💰 Checking AWS costs for VeriGov AI...")
        
        # Get current month costs
        now = datetime.now()
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
        
        try:
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost']
            )
            
            if response['ResultsByTime']:
                total_cost = float(response['ResultsByTime'][0]['Total']['BlendedCost']['Amount'])
                print(f"📊 Current month charges: ${total_cost:.2f}")
                
                # Budget warnings
                if total_cost > 45:
                    print("🚨 CRITICAL: You're over $45! Stop all AWS resources immediately!")
                elif total_cost > 40:
                    print("⚠️  WARNING: You're over $40! Monitor closely!")
                elif total_cost > 30:
                    print("⚠️  CAUTION: You're approaching $40 threshold")
                elif total_cost > 20:
                    print("💡 INFO: You're at ${:.2f}, still within safe limits".format(total_cost))
                else:
                    print("✅ Costs are low, safe to proceed with development")
                
                # Remaining budget
                remaining = 50 - total_cost
                print(f"💵 Remaining budget: ${remaining:.2f}")
                
            else:
                print("💰 No cost data available (normal for new accounts)")
                print("✅ Safe to proceed with development")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                print("⚠️  Cannot access Cost Explorer (permissions needed)")
                print("💡 You can check costs manually in AWS Console > Billing")
            else:
                print(f"⚠️  Error getting cost data: {e}")
        
        print("\n🛡️  Budget Protection Tips:")
        print("1. Check AWS Billing Dashboard daily")
        print("2. Use LocalStack for local testing (no AWS charges)")
        print("3. Delete unused resources immediately")
        print("4. Stop EC2 instances when not using")
        print("5. Use on-demand billing for DynamoDB")
        
        print("\n🚨 EMERGENCY: If costs exceed $45:")
        print("1. Delete all CloudFormation stacks")
        print("2. Terminate all EC2 instances")
        print("3. Delete all S3 buckets")
        print("4. Delete all DynamoDB tables")
        
    except NoCredentialsError:
        print("❌ AWS credentials not configured!")
        print("Run: aws configure")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error checking costs: {e}")
        print("💡 You can check costs manually in AWS Console > Billing")


if __name__ == "__main__":
    check_aws_costs()