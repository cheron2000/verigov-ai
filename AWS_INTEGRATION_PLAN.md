# 🚀 VeriGov AI - AWS Integration Plan

## Overview
This plan integrates VeriGov AI with AWS services to create a scalable, production-ready government information verification platform for the AWS Hackathon.

---

## 🏗️ Architecture Design

### Current State
- ✅ Flask web app running locally
- ✅ Groq AI for verification
- ✅ File-based audit logging
- ✅ JSON whitelist configuration

### Target AWS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     VeriGov AI on AWS                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │    │   Backend    │    │   Storage    │
│   (S3 +      │    │   (Lambda +  │    │   (S3 +      │
│   CloudFront)│    │   API GW)    │    │   DynamoDB)  │
└──────────────┘    └──────────────┘    └──────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                    ▼               ▼
            ┌──────────┐    ┌──────────┐
            │  Bedrock │    │SageMaker │
            │  (AI)    │    │ (ML)     │
            └──────────┘    └──────────┘
```

---

## 📋 Phase-by-Phase Implementation

### Phase 1: Storage & Database (Priority: HIGH)
**Goal**: Replace file-based storage with AWS services

#### 1.1 Amazon S3 - File Storage
**Use Cases:**
- Store audit logs (replace `logs/audit.log`)
- Store verification results history
- Host static assets (CSS, JS, images)
- Backup whitelist configurations

**Implementation:**
```python
# Store audit logs in S3
import boto3

s3 = boto3.client('s3')
bucket_name = 'verigov-audit-logs'

# Upload audit entry
s3.put_object(
    Bucket=bucket_name,
    Key=f'audit/{timestamp}.json',
    Body=json.dumps(audit_entry)
)
```

**Benefits:**
- Unlimited scalability
- Automatic backups
- Cost-effective ($0.023/GB)
- No server management

#### 1.2 Amazon DynamoDB - Database
**Use Cases:**
- Store verification results
- User sessions (future)
- Whitelist management
- Real-time audit queries

**Tables to Create:**
1. **VerificationResults**
   - PK: verification_id
   - Attributes: claim, status, confidence, timestamp, sources
   
2. **AuditLog**
   - PK: timestamp
   - SK: event_type
   - Attributes: data, user_id
   
3. **Whitelist**
   - PK: domain
   - Attributes: name, approved_by, approved_date

**Benefits:**
- Fast queries (single-digit millisecond latency)
- Auto-scaling
- Free tier: 25GB storage
- Serverless (no management)

---

### Phase 2: Serverless Backend (Priority: HIGH)
**Goal**: Convert Flask app to AWS Lambda for cost efficiency

#### 2.1 AWS Lambda Functions
**Functions to Create:**

1. **verify_claim_lambda**
   - Trigger: API Gateway POST /verify
   - Runtime: Python 3.11
   - Memory: 512MB
   - Timeout: 30s
   - Purpose: Handle claim verification

2. **get_audit_lambda**
   - Trigger: API Gateway GET /audit
   - Runtime: Python 3.11
   - Memory: 256MB
   - Timeout: 10s
   - Purpose: Retrieve audit logs

3. **get_whitelist_lambda**
   - Trigger: API Gateway GET /whitelist
   - Runtime: Python 3.11
   - Memory: 128MB
   - Timeout: 5s
   - Purpose: Return approved sources

**Benefits:**
- Pay only when code runs
- Auto-scales to zero when idle
- Free tier: 1M requests/month
- No server management
- **HUGE credit savings** (mentioned in AWS guide)

#### 2.2 Amazon API Gateway
**Setup:**
- REST API endpoint
- CORS enabled
- Rate limiting (1000 req/min)
- API key authentication (optional)

**Endpoints:**
```
POST   /api/verify
GET    /api/audit
GET    /api/whitelist
POST   /api/batch
```

---

### Phase 3: AI Enhancement (Priority: MEDIUM)
**Goal**: Leverage AWS AI services alongside Groq

#### 3.1 Amazon Bedrock - Foundation Models
**Use Cases:**
- Backup AI when Groq is unavailable
- Multi-model verification (consensus)
- Enhanced semantic analysis
- Generate verification reports

**Models to Use:**
- Claude 3 (Anthropic) - Best for reasoning
- Titan Text (Amazon) - Cost-effective
- Llama 2 (Meta) - Open source

**Implementation:**
```python
import boto3

bedrock = boto3.client('bedrock-runtime')

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    body=json.dumps({
        "prompt": f"Verify this claim: {claim}",
        "max_tokens": 1000
    })
)
```

**Benefits:**
- Multiple AI models
- No API key management
- AWS security
- Included in free credits

#### 3.2 Amazon SageMaker (Optional - Advanced)
**Use Cases:**
- Train custom fact-checking model
- Fine-tune on government data
- Build confidence scoring model

**When to Use:**
- If you have training data
- For custom ML requirements
- Advanced hackathon projects

---

### Phase 4: Frontend Hosting (Priority: MEDIUM)
**Goal**: Host web app on AWS

#### 4.1 Amazon S3 Static Website
**Setup:**
- Upload HTML, CSS, JS to S3
- Enable static website hosting
- Configure bucket policy for public access

**Files to Upload:**
- `templates/index.html`
- `static/style.css`
- `static/script.js`

#### 4.2 Amazon CloudFront (Optional)
**Benefits:**
- CDN for faster loading
- HTTPS support
- Global distribution
- DDoS protection

---

### Phase 5: Monitoring & Security (Priority: LOW)
**Goal**: Production-ready monitoring

#### 5.1 Amazon CloudWatch
**Setup:**
- Lambda function logs
- API Gateway metrics
- Custom dashboards
- Billing alarms (CRITICAL!)

**Alarms to Set:**
```
- Estimated charges > $40 (80% of credits)
- Lambda errors > 10/hour
- API Gateway 5xx errors > 5/min
```

#### 5.2 AWS IAM
**Security:**
- Least privilege access
- Separate roles for each Lambda
- API key rotation
- Encryption at rest (S3, DynamoDB)

---

## 💰 Cost Optimization Strategy

### Free Tier Usage (Within $50 Credits)

| Service | Free Tier | Estimated Usage | Cost |
|---------|-----------|-----------------|------|
| Lambda | 1M requests/month | 10K requests | $0 |
| API Gateway | 1M requests/month | 10K requests | $0 |
| DynamoDB | 25GB storage | 1GB | $0 |
| S3 | 5GB storage | 2GB | $0 |
| Bedrock | Pay per use | 1000 requests | ~$5 |
| CloudWatch | 10 metrics | 5 metrics | $0 |
| **Total** | | | **~$5** |

### Credit Conservation Tips (from AWS Guide)
1. ✅ **Stop EC2 instances when not using** (if you use them)
2. ✅ **Use Lambda instead of EC2** (scales to zero)
3. ✅ **Set billing alerts at $40** (80% threshold)
4. ✅ **Delete unused resources daily**
5. ✅ **Use S3 lifecycle policies** (auto-delete old logs)

---

## 🎯 Implementation Priority

### Week 1: Core Infrastructure
- [ ] Set up AWS account with credits
- [ ] Create S3 buckets (audit logs, static site)
- [ ] Create DynamoDB tables
- [ ] Set up billing alerts

### Week 2: Serverless Backend
- [ ] Convert Flask routes to Lambda functions
- [ ] Set up API Gateway
- [ ] Test Lambda + DynamoDB integration
- [ ] Deploy and test

### Week 3: AI Enhancement
- [ ] Integrate Amazon Bedrock
- [ ] Implement multi-model verification
- [ ] Add fallback logic (Groq → Bedrock)
- [ ] Test AI accuracy

### Week 4: Polish & Demo
- [ ] Deploy frontend to S3
- [ ] Set up CloudFront (optional)
- [ ] Create demo video
- [ ] Prepare presentation

---

## 🚀 Quick Start Commands

### 1. Install AWS CLI
```bash
pip install awscli boto3
aws configure
```

### 2. Create S3 Bucket
```bash
aws s3 mb s3://verigov-audit-logs
aws s3 mb s3://verigov-frontend
```

### 3. Create DynamoDB Tables
```bash
aws dynamodb create-table \
  --table-name VerificationResults \
  --attribute-definitions AttributeName=verification_id,AttributeType=S \
  --key-schema AttributeName=verification_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### 4. Deploy Lambda Function
```bash
# Package dependencies
pip install -r requirements.txt -t package/
cd package && zip -r ../lambda.zip . && cd ..
zip -g lambda.zip app.py

# Upload to Lambda
aws lambda create-function \
  --function-name verigov-verify \
  --runtime python3.11 \
  --handler app.lambda_handler \
  --zip-file fileb://lambda.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role
```

---

## 📊 Hackathon Judging Criteria Alignment

### Innovation (25%)
- ✅ AI-powered fact verification
- ✅ Multi-source validation
- ✅ Real-time monitoring
- ✅ Serverless architecture

### Technical Implementation (25%)
- ✅ AWS services integration
- ✅ Scalable architecture
- ✅ Security best practices
- ✅ Cost optimization

### Impact (25%)
- ✅ Combats misinformation
- ✅ Government transparency
- ✅ Public benefit
- ✅ Audit trail for accountability

### Presentation (25%)
- ✅ Working demo
- ✅ Clear use case
- ✅ Architecture diagram
- ✅ Live deployment

---

## 🎬 Next Steps

1. **Review this plan** - Understand the architecture
2. **Set up AWS account** - Apply hackathon credits
3. **Start with Phase 1** - Storage & Database
4. **Test incrementally** - Don't break existing functionality
5. **Monitor costs** - Set alerts immediately

Ready to start implementation? Let me know which phase you want to tackle first!
