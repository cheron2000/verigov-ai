# VeriGov AI - Complete AWS Deployment Guide

## Overview
This guide will help you deploy the entire VeriGov AI application to AWS, making it fully accessible via a public URL.

## Current Status
✅ Backend Lambda functions deployed
✅ DynamoDB tables created
✅ S3 bucket for data storage created
✅ API Gateway endpoints configured
❌ Frontend not yet hosted on AWS

## Deployment Steps

### Step 1: Deploy Support Lambda Functions (Audit & Whitelist)

These Lambda functions provide the `/api/audit` and `/api/whitelist` endpoints needed by the frontend.

```bash
python scripts/deploy_support_lambdas.py
```

This will:
- Create `verigov-dev-audit` Lambda function
- Create `verigov-dev-whitelist` Lambda function
- Create API Gateway endpoints for both
- Print the endpoint URLs

**Expected Output:**
```
✅ API Endpoints:
  audit: https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/audit
  whitelist: https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/whitelist
```

### Step 2: Update Frontend API Endpoints

Edit `static/script.js` and update the API endpoints at the top of the file:

```javascript
// API Configuration
const API_ENDPOINT_SMART = 'https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources';
const API_ENDPOINT_AUDIT = 'https://YOUR-API-ID.execute-api.ap-south-1.amazonaws.com/dev/audit';
const API_ENDPOINT_WHITELIST = 'https://YOUR-API-ID.execute-api.ap-south-1.amazonaws.com/dev/whitelist';
```

Replace the URLs with the ones from Step 1.

Then update the fetch calls in the script:

**Find this:**
```javascript
const response = await fetch('/api/audit?limit=10');
```

**Replace with:**
```javascript
const response = await fetch(`${API_ENDPOINT_AUDIT}?limit=10`);
```

**Find this:**
```javascript
const response = await fetch('/api/whitelist');
```

**Replace with:**
```javascript
const response = await fetch(API_ENDPOINT_WHITELIST);
```

### Step 3: Deploy Frontend to S3

```bash
python scripts/deploy_to_s3.py
```

This will:
- Create S3 bucket: `verigov-ai-frontend`
- Enable static website hosting
- Set public access policy
- Upload HTML, CSS, and JS files

**Expected Output:**
```
🌐 Website URL: http://verigov-ai-frontend.s3-website.ap-south-1.amazonaws.com
```

### Step 4: Test Your Deployment

1. Open the website URL in your browser
2. Try verifying a claim
3. Check if sources load
4. Verify the audit trail works

### Step 5 (Optional): Add CloudFront for HTTPS

If you want HTTPS and better performance:

```bash
python scripts/deploy_cloudfront.py
```

This will:
- Create CloudFront distribution
- Point to S3 bucket
- Enable HTTPS
- Provide CloudFront URL

## Architecture Diagram

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  S3 Static Website Hosting          │
│  - index.html                       │
│  - style.css                        │
│  - script.js                        │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  API Gateway (REST API)             │
│  - /api/verify-sources (POST)       │
│  - /audit (GET)                     │
│  - /whitelist (GET)                 │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Lambda Functions                   │
│  - verigov-dev-verify-sources       │
│  - verigov-dev-audit                │
│  - verigov-dev-whitelist            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  DynamoDB Tables                    │
│  - verigov-dev-verifications        │
│  - verigov-dev-audit-logs           │
│  - verigov-dev-whitelist            │
└─────────────────────────────────────┘
```

## Cost Estimate

### Free Tier (First 12 months)
- S3: 5GB storage, 15GB transfer - **FREE**
- Lambda: 1M requests, 400K GB-seconds - **FREE**
- API Gateway: 1M requests - **FREE**
- DynamoDB: 25GB storage, 25 RCU/WCU - **FREE**

**Total: $0/month** ✅

### After Free Tier (Estimated for 1000 verifications/month)
- S3: ~$0.10/month
- Lambda: ~$0.20/month
- API Gateway: ~$0.35/month
- DynamoDB: ~$0.25/month

**Total: ~$0.90/month** 💰

## Troubleshooting

### Issue: "Access Denied" when accessing S3 website

**Solution:**
1. Check bucket policy is set correctly
2. Ensure public access block is disabled
3. Verify files are uploaded

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket verigov-ai-frontend

# Check public access block
aws s3api get-public-access-block --bucket verigov-ai-frontend
```

### Issue: API endpoints return CORS errors

**Solution:**
Lambda functions already include CORS headers. If you still see errors:

1. Check API Gateway CORS settings
2. Verify Lambda function has correct headers in response
3. Test endpoints directly with curl:

```bash
curl https://YOUR-API-ID.execute-api.ap-south-1.amazonaws.com/dev/audit
```

### Issue: Whitelist or audit data not loading

**Solution:**
1. Check DynamoDB tables have data:

```bash
python scripts/sync_whitelist.py
```

2. Verify Lambda functions have correct table names in environment variables
3. Check Lambda execution role has DynamoDB permissions

### Issue: Website loads but verification doesn't work

**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify API endpoints are correct in script.js
4. Test Lambda function directly:

```bash
curl -X POST https://YOUR-API-ID.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources \
  -H "Content-Type: application/json" \
  -d '{"claim": "Test claim"}'
```

## Security Considerations

### Current Setup (Development)
- ✅ S3 bucket is public (required for static hosting)
- ✅ API Gateway endpoints are public (no authentication)
- ✅ Lambda functions use IAM roles
- ✅ DynamoDB tables are private

### Production Recommendations
- Add CloudFront with custom domain
- Implement API authentication (API keys or Cognito)
- Add rate limiting on API Gateway
- Enable CloudWatch logging
- Set up AWS WAF for DDoS protection

## Monitoring

### CloudWatch Logs
- Lambda logs: `/aws/lambda/verigov-dev-*`
- API Gateway logs: Enable in API Gateway settings

### Metrics to Monitor
- Lambda invocations
- API Gateway requests
- DynamoDB read/write capacity
- S3 bandwidth usage

## Backup and Recovery

### DynamoDB Backups
Enable point-in-time recovery (already enabled):
```bash
aws dynamodb update-continuous-backups \
  --table-name verigov-dev-verifications \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
```

### S3 Versioning
Enable versioning on frontend bucket:
```bash
aws s3api put-bucket-versioning \
  --bucket verigov-ai-frontend \
  --versioning-configuration Status=Enabled
```

## Updating the Application

### Update Frontend
1. Make changes to files in `static/`
2. Run deployment script:
```bash
python scripts/deploy_to_s3.py
```

### Update Lambda Functions
1. Make changes to files in `lambda/`
2. Run deployment script:
```bash
python scripts/deploy_support_lambdas.py
```

### Update DynamoDB Data
```bash
python scripts/sync_whitelist.py
```

## Next Steps

1. ✅ Deploy support Lambda functions
2. ✅ Update API endpoints in script.js
3. ✅ Deploy frontend to S3
4. ✅ Test the application
5. ⬜ (Optional) Add CloudFront
6. ⬜ (Optional) Set up custom domain
7. ⬜ (Optional) Add authentication

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review this guide
3. Test individual components
4. Check AWS service status

## Conclusion

Once deployed, your VeriGov AI application will be:
- ✅ Fully hosted on AWS
- ✅ Accessible via public URL
- ✅ Scalable and reliable
- ✅ Cost-effective (free tier eligible)
- ✅ Production-ready for hackathon demo

Good luck with your hackathon! 🚀
