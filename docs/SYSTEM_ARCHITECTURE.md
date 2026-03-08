# VeriGov AI - System Architecture

## Overview

VeriGov AI is a serverless web application that verifies government claims using AI and official sources.

## Simple Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Web Browser (S3 Static Hosting)                              │  │
│  │  - Modern Dashboard UI                                        │  │
│  │  - Light/Dark Mode                                            │  │
│  │  - Claim Input Form                                           │  │
│  │  - Results Display                                            │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  REST API (API Gateway)                                       │  │
│  │  - POST /api/verify-sources  (Claim Verification)            │  │
│  │  - GET  /audit               (Verification History)          │  │
│  │  - GET  /whitelist           (Trusted Sources)               │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Lambda Trigger
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LAMBDA FUNCTIONS                               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  1. verify-sources (Main Verification)                       │  │
│  │     - Analyzes claim text                                     │  │
│  │     - Detects topics (space, health, government, etc.)       │  │
│  │     - Selects relevant sources                                │  │
│  │     - Fetches data from sources (web scraping)               │  │
│  │     - Verifies with AI (Groq/Bedrock)                        │  │
│  │     - Returns confidence score & explanation                 │  │
│  │                                                                 │  │
│  │  2. audit (History)                                          │  │
│  │     - Retrieves verification history                         │  │
│  │     - Returns sorted results                                 │  │
│  │                                                                 │  │
│  │  3. whitelist (Sources)                                      │  │
│  │     - Returns list of trusted sources                        │  │
│  │     - 50+ verified organizations                             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SDK Calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  DynamoDB Tables                                              │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐            │  │
│  │  │ verifications       │  │ audit-logs          │            │  │
│  │  │ - verification_id   │  │ - timestamp         │            │  │
│  │  │ - claim, status     │  │ - event_type        │            │  │
│  │  │ - confidence        │  │ - data              │            │  │
│  │  │ - sources_checked   │  │ - verification_id   │            │  │
│  │  │ - timestamp         │  │                   │            │  │
│  │  └─────────────────────┘  └─────────────────────┘            │  │
│  │                                                                 │  │
│  │  ┌─────────────────────┐                                      │  │
│  │  │ whitelist           │                                      │  │
│  │  │ - domain            │                                      │  │
│  │  │ - name              │                                      │  │
│  │  │ - category          │                                      │  │
│  │  └─────────────────────┘                                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ External API Calls
                                    ▼
┌──────────���──────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Groq AI / AWS Bedrock                                        │  │
│  │  - Llama 3.3 70B / Claude Sonnet                             │  │
│  │  - AI-powered verification                                    │  │
│  │  - Confidence scoring                                         │  │
│  │                                                                 │  │
│  │  Trusted Sources (50+)                                        │  │
│  │  - Government websites (gov.in, nic.in, pib.gov.in)          │  │
│  │  - Health (who.int, cdc.gov, nih.gov)                        │  │
│  │  - Science (nasa.gov, nature.com, science.org)               │  │
│  │  - International (un.org, worldbank.org)                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## How It Works

### Step 1: User Submits a Claim
```
User types: "NASA launched a new Mars mission"
         ↓
Sends to API Gateway
```

### Step 2: Lambda Analyzes the Claim
```
Lambda receives claim
         ↓
Analyzes text to detect topics
         ↓
Identifies: "space", "NASA", "Mars"
```

### Step 3: Selects Relevant Sources
```
Based on topics, selects sources:
- nasa.gov (NASA)
- esa.int (European Space Agency)
         ↓
Fetches content from these websites
```

### Step 4: Verifies with AI
```
Sends claim + source content to AI
         ↓
AI analyzes and returns:
- Status: VERIFIED / UNVERIFIED / PARTIALLY_VERIFIED
- Confidence: 0-100%
- Explanation: Detailed reasoning
- Evidence: Supporting facts
```

### Step 5: Returns Results
```
Returns JSON response to user
         ↓
User sees verification result in browser
```

## Data Flow Example

```
User Input: "The Moon is Earth's only natural satellite"
         ↓
API Gateway → Lambda: verify-sources
         ↓
Lambda analyzes: Topics = ['space']
         ↓
Lambda selects: nasa.gov, esa.int
         ↓
Lambda fetches: Content from both sites
         ↓
Lambda calls AI: "Is this claim true based on these sources?"
         ↓
AI Response: {"status": "VERIFIED", "confidence": 100, ...}
         ↓
Store in DynamoDB: verifications table
         ↓
Log to DynamoDB: audit-logs table
         ↓
Return to User: Success!
```

## Technologies Used

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Font Awesome Icons
- Responsive Design

### Backend
- AWS Lambda (Python 3.11)
- API Gateway (REST API)
- DynamoDB (NoSQL Database)
- S3 (Static Website Hosting)

### AI/ML
- Groq AI (Llama 3.3 70B)
- AWS Bedrock (Claude Sonnet) - Optional

### Libraries
- requests (HTTP requests)
- beautifulsoup4 (Web scraping)
- boto3 (AWS SDK)
- python-dotenv (Environment variables)

## Cost Structure

### Free Tier (12 months)
- S3: 5GB storage, 15GB transfer - **FREE**
- Lambda: 1M requests, 400K GB-seconds - **FREE**
- API Gateway: 1M requests - **FREE**
- DynamoDB: 25GB storage, 25 RCU/WCU - **FREE**
- **Total: $0/month**

### After Free Tier
- S3: $0.10
- Lambda: $0.20
- API Gateway: $0.35
- DynamoDB: $0.25
- **Total: ~$0.90/month**

## Security Features

- ✅ HTTPS on all endpoints
- ✅ IAM roles with least privilege
- ✅ DynamoDB encryption at rest
- ✅ S3 server-side encryption
- ✅ No hardcoded credentials
- ✅ CORS properly configured

## Scalability

- **Auto-scaling**: Lambda scales automatically
- **Concurrent users**: Unlimited
- **Requests**: Millions per month
- **Uptime**: 99.9% (AWS SLA)

## Deployment

### One-Command Deployment
```bash
python scripts/deploy_full_stack.py
```

### What Gets Deployed
1. 3 Lambda functions
2. API Gateway with 3 endpoints
3. DynamoDB tables
4. S3 static website
5. IAM roles and policies

### Deployment Time: 3-5 minutes

## Monitoring

### CloudWatch Metrics
- Lambda invocations
- API Gateway requests
- DynamoDB read/write capacity
- Error rates

### Logs
- Lambda execution logs
- API Gateway access logs
- Error tracking

## Future Enhancements

- [ ] CloudFront CDN for HTTPS
- [ ] User authentication (Cognito)
- [ ] Rate limiting and API keys
- [ ] Mobile app (React Native)
- [ ] More international sources
- [ ] ML-based source reliability scoring
- [ ] Multi-language support
- [ ] Browser extension

---

**Built for transparent governance and informed citizens**

**Live Demo:** http://verigov-ai-frontend.s3-website.ap-south-1.amazonaws.com
