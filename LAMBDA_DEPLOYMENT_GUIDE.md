# Lambda Deployment Guide

## Required AWS Permissions

To deploy the Lambda function, you need to add these permissions to your IAM user:

### 1. Lambda Permissions
```
AWSLambda_FullAccess
```
OR create a custom policy with:
- `lambda:CreateFunction`
- `lambda:UpdateFunctionCode`
- `lambda:UpdateFunctionConfiguration`
- `lambda:PublishLayerVersion`
- `lambda:GetFunction`
- `lambda:InvokeFunction`

### 2. IAM Permissions (for creating Lambda execution role)
```
IAMFullAccess
```
OR create a custom policy with:
- `iam:CreateRole`
- `iam:GetRole`
- `iam:AttachRolePolicy`
- `iam:PassRole`

### 3. API Gateway Permissions (for next step)
```
AmazonAPIGatewayAdministrator
```

## How to Add Permissions

1. Go to AWS Console → IAM → Users
2. Click on your user: `shreyash`
3. Click "Add permissions" → "Attach policies directly"
4. Search and select:
   - `AWSLambda_FullAccess`
   - `IAMFullAccess`
   - `AmazonAPIGatewayAdministrator`
5. Click "Add permissions"

## Deployment Steps

Once permissions are added:

### Step 1: Deploy Lambda Function
```bash
python scripts/deploy_lambda.py
```

This will:
- ✅ Create Lambda deployment package
- ✅ Install dependencies (groq, boto3)
- ✅ Create IAM role for Lambda
- ✅ Publish Lambda layer with dependencies
- ✅ Deploy Lambda function
- ✅ Test the function

### Step 2: Create API Gateway (next script)
```bash
python scripts/deploy_api_gateway.py
```

This will:
- ✅ Create REST API
- ✅ Create /api/verify endpoint
- ✅ Connect to Lambda function
- ✅ Enable CORS
- ✅ Deploy API
- ✅ Get public URL

### Step 3: Update Frontend
The script will give you an API Gateway URL like:
```
https://abc123.execute-api.ap-south-1.amazonaws.com/dev/api/verify
```

Update `static/script.js` to use this URL instead of `/api/verify`

## Cost Estimate

### Lambda
- **Free Tier**: 1 million requests/month FREE
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Estimated cost**: $0/month (within free tier)

### API Gateway
- **Free Tier**: 1 million requests/month FREE (first 12 months)
- **After free tier**: $3.50 per million requests
- **Estimated cost**: $0/month (within free tier)

### Total Estimated Cost: $0/month

## What Gets Created

### Lambda Function
- **Name**: `verigov-dev-verify`
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Handler**: `verify_handler.lambda_handler`

### Lambda Layer
- **Name**: `verigov-dev-dependencies`
- **Contents**: groq, boto3 libraries

### IAM Role
- **Name**: `verigov-dev-lambda-role`
- **Permissions**:
  - CloudWatch Logs (for logging)
  - DynamoDB Full Access (for storing results)

### API Gateway (next step)
- **Name**: `verigov-dev-api`
- **Type**: REST API
- **Endpoint**: `/api/verify` (POST)
- **CORS**: Enabled

## Testing

After deployment, you can test the Lambda directly:

```bash
# Test Lambda function
aws lambda invoke \
  --function-name verigov-dev-verify \
  --payload '{"body": "{\"claim\": \"Test claim\"}"}' \
  --region ap-south-1 \
  response.json

cat response.json
```

Or test via API Gateway URL (after Step 2):

```bash
curl -X POST https://YOUR-API-ID.execute-api.ap-south-1.amazonaws.com/dev/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth orbits the Sun"}'
```

## Troubleshooting

### "AccessDenied" errors
- Add the required IAM permissions listed above
- Wait 1-2 minutes for permissions to propagate

### "Role not found" errors
- The IAM role takes 10-15 seconds to propagate
- The script waits automatically, but you can retry if needed

### "Module not found" errors in Lambda
- The Lambda layer should include all dependencies
- Check that `lambda/requirements.txt` is correct
- Redeploy with: `python scripts/deploy_lambda.py`

### Lambda timeout errors
- Increase timeout in deployment script (currently 30s)
- Check Groq API key is valid
- Check DynamoDB tables exist

## Cleanup (if needed)

To remove Lambda resources:

```bash
# Delete Lambda function
aws lambda delete-function --function-name verigov-dev-verify --region ap-south-1

# Delete Lambda layer (get version from console)
aws lambda delete-layer-version \
  --layer-name verigov-dev-dependencies \
  --version-number 1 \
  --region ap-south-1

# Delete IAM role (detach policies first)
aws iam detach-role-policy \
  --role-name verigov-dev-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam detach-role-policy \
  --role-name verigov-dev-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam delete-role --role-name verigov-dev-lambda-role
```

## Next Steps After Deployment

1. ✅ Lambda function deployed
2. ⏭️ Create API Gateway (run `scripts/deploy_api_gateway.py`)
3. ⏭️ Update frontend with API Gateway URL
4. ⏭️ Test end-to-end from browser
5. ⏭️ Share API URL with hackathon judges

## Benefits for Hackathon

✅ **24/7 Availability**: Lambda runs continuously  
✅ **Public API**: Judges can test from anywhere  
✅ **Professional**: AWS infrastructure shows technical skill  
✅ **Scalable**: Handles multiple requests automatically  
✅ **Cost-effective**: $0/month within free tier  
✅ **Monitored**: CloudWatch logs all requests
