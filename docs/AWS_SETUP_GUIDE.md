# AWS Setup Guide for VeriGov AI

## Current Status ✅

- ✅ AWS credentials configured (user: shreyash, account: 448772857627)
- ✅ AWS region set to ap-south-1 (Mumbai)
- ✅ Local storage fully tested and working
- ✅ Storage abstraction layer implemented
- ✅ DynamoDB client code ready
- ✅ CloudFormation templates prepared
- ⏳ Waiting for DynamoDB permissions

## What You Need: IAM Permissions

To deploy and use DynamoDB tables, you need the following IAM permissions:

### Required Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:DescribeTable",
                "dynamodb:ListTables",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:BatchGetItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:ap-south-1:448772857627:table/verigov-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:UpdateStack",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents",
                "cloudformation:GetTemplate"
            ],
            "Resource": [
                "arn:aws:cloudformation:ap-south-1:448772857627:stack/verigov-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:PutBucketEncryption",
                "s3:PutBucketVersioning"
            ],
            "Resource": [
                "arn:aws:s3:::verigov-*",
                "arn:aws:s3:::verigov-*/*"
            ]
        }
    ]
}
```

### How to Request Permissions

**Option 1: Ask Your AWS Administrator**

Send this message to your AWS admin:

```
Hi,

I need IAM permissions to deploy DynamoDB tables and S3 buckets for the VeriGov AI project.

Please attach the following managed policies to my IAM user (shreyash):
- AmazonDynamoDBFullAccess
- AWSCloudFormationFullAccess
- AmazonS3FullAccess

Or create a custom policy with the permissions listed in AWS_SETUP_GUIDE.md

Account: 448772857627
Region: ap-south-1
User: shreyash

Thank you!
```

**Option 2: If You Have Console Access**

1. Go to AWS Console → IAM → Users → shreyash
2. Click "Add permissions"
3. Attach these managed policies:
   - `AmazonDynamoDBFullAccess`
   - `AWSCloudFormationFullAccess`
   - `AmazonS3FullAccess`

## Once You Have Permissions

### Step 1: Verify Permissions

```bash
# Test DynamoDB access
aws dynamodb list-tables --region ap-south-1

# Test CloudFormation access
aws cloudformation list-stacks --region ap-south-1

# Test S3 access
aws s3 ls
```

### Step 2: Deploy DynamoDB Tables

```bash
# Deploy to development environment
python scripts/deploy_dynamodb.py deploy --environment dev --region ap-south-1

# This will create:
# - verigov-dev-audit-logs (table)
# - verigov-dev-verifications (table)
# - verigov-dev-whitelist (table)
```

### Step 3: Verify Tables Are Created

```bash
# Check table status
python scripts/deploy_dynamodb.py status --environment dev --region ap-south-1

# Or use AWS CLI
aws dynamodb describe-table --table-name verigov-dev-audit-logs --region ap-south-1
```

### Step 4: Test AWS Storage Mode

```bash
# Update .env file
# Change: STORAGE_MODE=local
# To:     STORAGE_MODE=aws

# Test verification with AWS storage
python -m src.verigov.main --storage aws verify "Test claim with AWS storage"

# Check if data is in DynamoDB
aws dynamodb scan --table-name verigov-dev-audit-logs --region ap-south-1 --limit 5
```

### Step 5: Test Hybrid Mode (Optional)

```bash
# Use hybrid mode for safe migration
python -m src.verigov.main --storage hybrid verify "Test claim with hybrid storage"

# This writes to both local files AND DynamoDB
```

## Cost Monitoring

### Set Up Billing Alerts

Once you have permissions, set up billing alerts:

```bash
# This requires SNS permissions (you may need to request these too)
python scripts/setup_billing_alerts.py
```

### Monitor Costs Manually

```bash
# Check current costs
python scripts/check_aws_costs.py

# Or use AWS Console
# Go to: Billing Dashboard → Cost Explorer
```

### Expected Costs

- **DynamoDB (on-demand)**: ~$0.25 per million reads/writes
- **S3 Storage**: ~$0.023 per GB per month
- **Expected monthly cost**: < $5 for development

## Troubleshooting

### Error: "User is not authorized to perform: dynamodb:ListTables"

**Solution**: You need DynamoDB permissions. Request them from your AWS admin.

### Error: "User is not authorized to perform: cloudformation:CreateStack"

**Solution**: You need CloudFormation permissions. Request them from your AWS admin.

### Error: "Table already exists"

**Solution**: Tables are already deployed. Check status:
```bash
python scripts/deploy_dynamodb.py status --environment dev --region ap-south-1
```

### Error: "Access Denied" when writing to DynamoDB

**Solution**: Check your IAM permissions include `dynamodb:PutItem`

## Testing Checklist

Once you have permissions, test these features:

- [ ] Deploy DynamoDB tables
- [ ] Verify tables are ACTIVE
- [ ] Test AWS storage mode
- [ ] Test hybrid storage mode
- [ ] Verify data in DynamoDB
- [ ] Test verification retrieval
- [ ] Test batch operations
- [ ] Check CloudWatch metrics
- [ ] Monitor costs

## Current Working Features (No AWS Needed)

While waiting for permissions, you can use:

✅ **Local Storage Mode**
```bash
python -m src.verigov.main --storage local verify "Test claim"
```

✅ **Web Application**
```bash
python app.py
# Visit: http://127.0.0.1:5000
```

✅ **CLI Commands**
```bash
# Verify single claim
python -m src.verigov.main verify "Test claim"

# Batch verification
python -m src.verigov.main batch test_claims.txt

# Interactive mode
python -m src.verigov.main interactive

# Export audit log
python -m src.verigov.main audit --output audit_export.json
```

✅ **All Core Features**
- Claim verification
- Batch processing
- Audit logging
- Whitelist management
- Source collection
- Change detection

## Next Steps After AWS Setup

1. **Deploy DynamoDB Tables** ✅
2. **Test AWS Storage** ✅
3. **Implement S3 Integration** (Tasks 1.9-1.12)
4. **Create Lambda Functions** (Phase 2)
5. **Set Up API Gateway** (Phase 3)
6. **Integrate Bedrock AI** (Phase 4)
7. **Deploy Frontend to S3** (Phase 5)
8. **Configure Monitoring** (Phase 6)

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review `DYNAMODB_GUIDE.md` for detailed usage
3. Check `AWS_PROGRESS.md` for implementation status
4. Review CloudFormation template: `infrastructure/cloudformation/dynamodb-tables.yaml`

## Quick Reference

### Environment Variables (.env)
```bash
STORAGE_MODE=local          # or 'aws' or 'hybrid'
AWS_REGION=ap-south-1
ENVIRONMENT=dev
```

### Important Files
- `scripts/deploy_dynamodb.py` - Deploy tables
- `infrastructure/cloudformation/dynamodb-tables.yaml` - Table definitions
- `src/verigov/aws/dynamodb_client.py` - DynamoDB client
- `DYNAMODB_GUIDE.md` - Detailed usage guide

### Useful Commands
```bash
# Check AWS identity
aws sts get-caller-identity

# List DynamoDB tables
aws dynamodb list-tables --region ap-south-1

# Check CloudFormation stacks
aws cloudformation list-stacks --region ap-south-1

# Test local storage
python test_local_integration.py
```

---

**Last Updated**: March 5, 2026  
**Your AWS Account**: 448772857627  
**Your AWS User**: shreyash  
**Your AWS Region**: ap-south-1 (Mumbai)