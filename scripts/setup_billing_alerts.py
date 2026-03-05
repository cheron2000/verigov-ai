#!/usr/bin/env python3
"""
Setup AWS billing alerts for VeriGov AI project
CRITICAL: Run this FIRST to avoid exceeding $50 budget
"""

import boto3
import sys
import os
from botocore.exceptions import ClientError, NoCredentialsError


def setup_billing_alerts():
    """Set up billing alerts at $40 and $45 thresholds"""
    
    try:
        # CloudWatch must be in us-east-1 for billing metrics
        cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
        sns = boto3.client('sns', region_name='us-east-1')
        
        print("🔧 Setting up AWS billing alerts...")
        
        # Create SNS topic for billing alerts
        print("📧 Creating SNS topic for billing alerts...")
        try:
            topic_response = sns.create_topic(Name='verigov-billing-alerts')
            topic_arn = topic_response['TopicArn']
            print(f"✅ Created SNS topic: {topic_arn}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'TopicAlreadyExists':
                # Get existing topic ARN
                topics = sns.list_topics()
                topic_arn = None
                for topic in topics['Topics']:
                    if 'verigov-billing-alerts' in topic['TopicArn']:
                        topic_arn = topic['TopicArn']
                        break
                print(f"✅ Using existing SNS topic: {topic_arn}")
            else:
                raise
        
        # Subscribe email to topic (you'll need to confirm via email)
        email = input("📧 Enter your email for billing alerts: ").strip()
        if email:
            try:
                sns.subscribe(
                    TopicArn=topic_arn,
                    Protocol='email',
                    Endpoint=email
                )
                print(f"✅ Subscribed {email} to billing alerts")
                print("📬 Check your email and confirm the subscription!")
            except ClientError as e:
                print(f"⚠️  Warning: Could not subscribe email: {e}")
        
        # Create billing alarms
        thresholds = [40, 45]
        for threshold in thresholds:
            alarm_name = f'verigov-billing-{threshold}'
            
            try:
                cloudwatch.put_metric_alarm(
                    AlarmName=alarm_name,
                    AlarmDescription=f'VeriGov AI: Alert when charges exceed ${threshold}',
                    ActionsEnabled=True,
                    AlarmActions=[topic_arn],
                    MetricName='EstimatedCharges',
                    Namespace='AWS/Billing',
                    Statistic='Maximum',
                    Dimensions=[
                        {'Name': 'Currency', 'Value': 'USD'}
                    ],
                    Period=21600,  # 6 hours
                    EvaluationPeriods=1,
                    Threshold=threshold,
                    ComparisonOperator='GreaterThanThreshold',
                    TreatMissingData='notBreaching'
                )
                print(f"✅ Created billing alarm for ${threshold}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'AlarmAlreadyExists':
                    print(f"✅ Billing alarm for ${threshold} already exists")
                else:
                    print(f"❌ Error creating alarm for ${threshold}: {e}")
        
        print("\n🎉 Billing alerts setup complete!")
        print("💡 You will receive email alerts when costs exceed $40 and $45")
        print("🚨 IMPORTANT: Monitor your AWS costs regularly!")
        
        # Show current estimated charges
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/Billing',
                MetricName='EstimatedCharges',
                Dimensions=[{'Name': 'Currency', 'Value': 'USD'}],
                StartTime='2024-01-01T00:00:00Z',
                EndTime='2024-12-31T23:59:59Z',
                Period=86400,  # 1 day
                Statistics=['Maximum']
            )
            
            if response['Datapoints']:
                latest = max(response['Datapoints'], key=lambda x: x['Timestamp'])
                current_charges = latest['Maximum']
                print(f"\n💰 Current estimated charges: ${current_charges:.2f}")
                
                if current_charges > 40:
                    print("🚨 WARNING: You're already over $40!")
                elif current_charges > 30:
                    print("⚠️  CAUTION: You're approaching the $40 threshold")
                else:
                    print("✅ Current charges are within safe limits")
            else:
                print("💰 No billing data available yet (normal for new accounts)")
                
        except Exception as e:
            print(f"⚠️  Could not retrieve current charges: {e}")
    
    except NoCredentialsError:
        print("❌ AWS credentials not configured!")
        print("Run: aws configure")
        print("Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error setting up billing alerts: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_billing_alerts()