# VeriGov AI - AWS Frontend Hosting Plan

## Overview
Deploy the complete VeriGov AI application to AWS using serverless architecture for minimal cost and maximum scalability.

## Architecture

### Current State
- Flask app running locally (app.py)
- Frontend: HTML/CSS/JS in templates/ and static/
- Backend: Lambda functions already deployed
- Database: DynamoDB tables already created
- Storage: S3 bucket already configured

### Target Architecture
```
User Browser
    ↓
CloudFront CDN (Optional - for better performance)
    ↓
S3 Static Website Hosting
    ↓
API Gateway (Already deployed)
    ↓
Lambda Functions (Already deployed)
    ↓
DynamoDB + S3 (Already deployed)
```

## Deployment Options

### Option 1: S3 Static Hosting (Recommended - FREE TIER)
**Cost**: FREE (within free tier limits)
**Pros**:
- Simplest setup
- No server management
- Fast deployment
- Free tier: 5GB storage, 15GB transfer/month
- Perfect for hackathon demo

**Cons**:
- HTTP only (unless using CloudFront)
- No server-side rendering

### Option 2: S3 + CloudFront (Better Performance)
**Cost**: ~$0.50-1/month (after free tier)
**Pros**:
- HTTPS support
- Global CDN
- Better performance
- Custom domain support
- Free tier: 50GB transfer, 2M requests/month

**Cons**:
- Slightly more complex setup
- Takes 15-20 minutes to deploy

### Option 3: Elastic Beanstalk (Full Flask App)
**Cost**: ~$15-20/month (EC2 instance)
**Pros**:
- Keep Flask app as-is
- Server-side rendering
- Easy deployment

**Cons**:
- More expensive
- Overkill for static frontend

## Recommended Approach: S3 Static Hosting

Since your backend is already on Lambda/API Gateway, we'll:
1. Convert Flask templates to static HTML
2. Update API endpoints to use Lambda URLs
3. Upload to S3 with static website hosting
4. (Optional) Add CloudFront for HTTPS

## Implementation Steps

### Step 1: Create Static HTML Files
- Convert `templates/index.html` to standalone HTML
- Update API endpoints in `static/script.js` to use Lambda URLs
- Keep all CSS and JS files as-is

### Step 2: Create Lambda Functions for Missing APIs
Currently deployed:
- ✅ `/api/verify-sources` - Smart verification Lambda

Need to create:
- ❌ `/api/audit` - Get audit logs from DynamoDB
- ❌ `/api/whitelist` - Get trusted sources from DynamoDB

### Step 3: Deploy to S3
- Create S3 bucket for website hosting
- Enable static website hosting
- Upload HTML, CSS, JS files
- Set bucket policy for public read access

### Step 4: (Optional) Add CloudFront
- Create CloudFront distribution
- Point to S3 bucket
- Enable HTTPS
- Get CloudFront URL

## Files to Modify

### 1. templates/index.html
- Remove Flask template syntax: `{{ url_for() }}`
- Use direct paths: `/static/style.css` → `style.css`

### 2. static/script.js
- Update API endpoints to Lambda URLs
- Add new Lambda endpoints for audit and whitelist

### 3. New Lambda Functions
- `lambda/audit_handler.py` - Query DynamoDB audit logs
- `lambda/whitelist_handler.py` - Get whitelist from DynamoDB

## Cost Estimate (Monthly)

### Free Tier (First 12 months)
- S3: 5GB storage, 15GB transfer - FREE
- Lambda: 1M requests, 400K GB-seconds - FREE
- API Gateway: 1M requests - FREE
- DynamoDB: 25GB storage, 25 RCU/WCU - FREE
- CloudFront: 50GB transfer, 2M requests - FREE

**Total: $0/month** (within free tier)

### After Free Tier
- S3: ~$0.10/month (assuming 1GB storage, 10GB transfer)
- Lambda: ~$0.20/month (assuming 10K requests)
- API Gateway: ~$0.35/month (assuming 10K requests)
- DynamoDB: ~$0.25/month (on-demand pricing)
- CloudFront: ~$0.50/month (assuming 10GB transfer)

**Total: ~$1.40/month** (very affordable!)

## Timeline

- Step 1: Create static files - 15 minutes
- Step 2: Create Lambda functions - 20 minutes
- Step 3: Deploy to S3 - 10 minutes
- Step 4: (Optional) CloudFront - 20 minutes

**Total: 45-65 minutes**

## Next Steps

1. Create the two missing Lambda functions (audit, whitelist)
2. Convert Flask template to static HTML
3. Create S3 bucket and deploy
4. Test the hosted application
5. (Optional) Add CloudFront for HTTPS

Ready to proceed?
