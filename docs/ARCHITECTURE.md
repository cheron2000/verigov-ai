# VeriGov AI - System Architecture

## Overview

VeriGov AI is built on a fully serverless AWS architecture, designed for scalability, cost-effectiveness, and reliability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                              │
│  - Web Browsers (Desktop, Mobile, Tablet)                       │
│  - Any device with internet connection                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  S3 Static Website Hosting                               │  │
│  │  Bucket: verigov-ai-frontend                             │  │
│  │  - index.html (Modern Dashboard UI)                      │  │
│  │  - style.css (Responsive Design)                         │  │
│  │  - script.js (Frontend Logic)                            │  │
│  │  Features:                                               │  │
│  │  • Light/Dark Mode                                       │  │
│  │  • Real-time Statistics                                  │  │
│  │  • Responsive Grid Layout                                │  │
│  │  • Modal Components                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API Calls
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Gateway (REST API)                                  │  │
│  │  ID: qycb40y6n6                                          │  │
│  │  Region: ap-south-1                                      │  │
│  │                                                          │  │
│  │  Endpoints:                                              │  │
│  │  • POST /api/verify-sources                             │  │
│  │    - Smart claim verification                           │  │
│  │    - Auto source selection                              │  │
│  │                                                          │  │
│  │  • GET /audit?limit=N                                   │  │
│  │    - Retrieve verification history                      │  │
│  │    - Pagination support                                 │  │
│  │                                                          │  │
│  │  • GET /whitelist                                       │  │
│  │    - Get trusted sources list                           │  │
│  │    - 20+ verified sources                               │  │
│  │                                                          │  │
│  │  Features:                                              │  │
│  │  • CORS enabled                                         │  │
│  │  • Request/Response transformation                      │  │
│  │  • Throttling & Rate limiting                           │  │
│  │  • CloudWatch logging                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Lambda Proxy Integration
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Compute Layer                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Lambda Functions (Python 3.11)                          │  │
│  │                                                          │  │
│  │  1. verigov-dev-verify-sources                          │  │
│  │     - Handler: verify_handler_smart.lambda_handler      │  │
│  │     - Memory: 512 MB                                    │  │
│  │     - Timeout: 30 seconds                               │  │
│  │     - Features:                                         │  │
│  │       • Topic detection (9 categories)                  │  │
│  │       • Auto source selection                           │  │
│  │       • Web scraping (BeautifulSoup4)                   │  │
│  │       • AI verification (Groq)                          │  │
│  │       • Confidence scoring                              │  │
│  │                                                          │  │
│  │  2. verigov-dev-audit                                   │  │
│  │     - Handler: audit_handler.lambda_handler             │  │
│  │     - Memory: 256 MB                                    │  │
│  │     - Timeout: 30 seconds                               │  │
│  │     - Features:                                         │  │
│  │       • Query DynamoDB audit logs                       │  │
│  │       • Sort by timestamp                               │  │
│  │       • Pagination support                              │  │
│  │                                                          │  │
│  │  3. verigov-dev-whitelist                               │  │
│  │     - Handler: whitelist_handler.lambda_handler         │  │
│  │     - Memory: 256 MB                                    │  │
│  │     - Timeout: 30 seconds                               │  │
│  │     - Features:                                         │  │
│  │       • Retrieve trusted sources                        │  │
│  │       • Sort alphabetically                             │  │
│  │       • Category filtering                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SDK Calls (Boto3)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DynamoDB Tables                                         │  │
│  │                                                          │  │
│  │  1. verigov-dev-verifications                           │  │
│  │     - Primary Key: verification_id (String)             │  │
│  │     - Attributes:                                       │  │
│  │       • claim, status, confidence                       │  │
│  │       • explanation, sources_checked                    │  │
│  │       • timestamp, research_method                      │  │
│  │     - Billing: PAY_PER_REQUEST                          │  │
│  │     - Encryption: AES-256                               │  │
│  │                                                          │  │
│  │  2. verigov-dev-audit-logs                              │  │
│  │     - Primary Key: timestamp (String)                   │  │
│  │     - Attributes:                                       │  │
│  │       • event_type, data                                │  │
│  │       • verification_id                                 │  │
│  │     - Billing: PAY_PER_REQUEST                          │  │
│  │     - Point-in-time Recovery: Enabled                   │  │
│  │                                                          │  │
│  │  3. verigov-dev-whitelist                               │  │
│  │     - Primary Key: domain (String)                      │  │
│  │     - Attributes:                                       │  │
│  │       • name, category                                  │  │
│  │       • approved_by, approved_date                      │  │
│  │     - Items: 20 trusted sources                         │  │
│  │     - Billing: PAY_PER_REQUEST                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  S3 Buckets                                              │  │
│  │                                                          │  │
│  │  1. verigov-dev-data-448772857627                       │  │
│  │     - Purpose: Data storage                             │  │
│  │     - Encryption: AES-256                               │  │
│  │     - Versioning: Enabled                               │  │
│  │     - Lifecycle: Delete old versions after 30 days      │  │
│  │                                                          │  │
│  │  2. verigov-ai-frontend                                 │  │
│  │     - Purpose: Static website hosting                   │  │
│  │     - Public Access: Enabled                            │  │
│  │     - Website Endpoint: Configured                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ External API Calls
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   External Services                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Groq AI                                                 │  │
│  │  - Model: llama-3.3-70b-versatile                       │  │
│  │  - Purpose: AI-powered verification                     │  │
│  │  - Fallback when no sources available                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Trusted Sources (20+)                                   │  │
│  │  - Government websites                                   │  │
│  │  - Health organizations                                  │  │
│  │  - Scientific institutions                               │  │
│  │  - International bodies                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Verification Request Flow

```
1. User submits claim via web interface
   ↓
2. Frontend sends POST request to API Gateway
   ↓
3. API Gateway triggers verify-sources Lambda
   ↓
4. Lambda analyzes claim and detects topics
   ↓
5. Lambda auto-selects relevant sources from whitelist
   ↓
6. Lambda fetches data from selected sources (web scraping)
   ↓
7. If sources found: Verify against fetched data
   If no sources: Use Groq AI for verification
   ↓
8. Lambda stores result in DynamoDB (verifications table)
   ↓
9. Lambda logs event in DynamoDB (audit-logs table)
   ↓
10. Lambda returns result to API Gateway
    ↓
11. API Gateway returns response to frontend
    ↓
12. Frontend displays result with confidence score
```

### Audit Log Retrieval Flow

```
1. Frontend requests audit logs
   ↓
2. API Gateway triggers audit Lambda
   ↓
3. Lambda queries DynamoDB audit-logs table
   ↓
4. Lambda sorts by timestamp (newest first)
   ↓
5. Lambda returns paginated results
   ↓
6. Frontend displays in audit trail panel
```

### Whitelist Retrieval Flow

```
1. Frontend requests trusted sources
   ↓
2. API Gateway triggers whitelist Lambda
   ↓
3. Lambda scans DynamoDB whitelist table
   ↓
4. Lambda sorts alphabetically
   ↓
5. Lambda returns all sources
   ↓
6. Frontend displays in modal/sidebar
```

## Security Architecture

### IAM Roles & Permissions

```
Lambda Execution Role: verigov-dev-lambda-role
├── DynamoDB Permissions
│   ├── PutItem (verifications, audit-logs)
│   ├── GetItem (whitelist)
│   ├── Query (audit-logs)
│   └── Scan (whitelist)
├── S3 Permissions
│   ├── PutObject (data bucket)
│   └── GetObject (data bucket)
└── CloudWatch Logs
    └── CreateLogGroup, CreateLogStream, PutLogEvents
```

### Network Security

- API Gateway: HTTPS only
- Lambda: VPC not required (public endpoints)
- DynamoDB: Private (accessed via AWS SDK)
- S3: Public read for frontend, private for data

### Data Security

- DynamoDB: Encryption at rest (AES-256)
- S3: Server-side encryption (AES-256)
- API Gateway: TLS 1.2+
- No sensitive data in logs

## Scalability

### Auto-Scaling Components

1. **Lambda Functions**
   - Concurrent executions: Up to 1000 (default)
   - Auto-scales based on requests
   - Cold start: ~1-2 seconds
   - Warm execution: <100ms

2. **API Gateway**
   - Handles millions of requests
   - Auto-scales automatically
   - Rate limiting: Configurable

3. **DynamoDB**
   - On-demand capacity mode
   - Auto-scales read/write units
   - No capacity planning needed

4. **S3**
   - Unlimited storage
   - Unlimited requests
   - Auto-scales automatically

### Performance Optimization

- Lambda memory: Optimized for performance/cost
- DynamoDB indexes: Efficient queries
- S3 caching: Browser caching enabled
- API Gateway caching: Can be enabled

## Monitoring & Logging

### CloudWatch Metrics

- Lambda invocations, duration, errors
- API Gateway requests, latency, 4xx/5xx errors
- DynamoDB read/write capacity, throttles
- S3 requests, bandwidth

### CloudWatch Logs

- Lambda execution logs: `/aws/lambda/verigov-dev-*`
- API Gateway access logs: Can be enabled
- Error tracking and debugging

### Alarms (Can be configured)

- Lambda errors > threshold
- API Gateway 5xx errors
- DynamoDB throttling
- High latency alerts

## Cost Optimization

### Free Tier Usage

- Lambda: 1M requests/month FREE
- API Gateway: 1M requests/month FREE
- DynamoDB: 25GB storage, 25 RCU/WCU FREE
- S3: 5GB storage, 15GB transfer FREE

### Cost-Saving Strategies

1. On-demand DynamoDB (no provisioned capacity)
2. Lambda memory optimization
3. S3 lifecycle policies
4. API Gateway caching
5. CloudWatch log retention policies

## Disaster Recovery

### Backup Strategy

- DynamoDB: Point-in-time recovery enabled
- S3: Versioning enabled
- Lambda: Code stored in S3
- Infrastructure: CloudFormation templates

### Recovery Procedures

1. DynamoDB: Restore from backup
2. S3: Restore previous version
3. Lambda: Redeploy from code
4. Full stack: Run deployment scripts

## Future Architecture Enhancements

### Phase 1: Performance
- Add CloudFront CDN
- Enable API Gateway caching
- Optimize Lambda cold starts

### Phase 2: Security
- Add AWS WAF
- Implement Cognito authentication
- Add API keys/rate limiting

### Phase 3: Scalability
- Add ElastiCache for caching
- Implement SQS for async processing
- Add Step Functions for workflows

### Phase 4: Observability
- Add X-Ray tracing
- Create CloudWatch dashboards
- Implement custom metrics

## Technology Choices

### Why Serverless?

- ✅ No server management
- ✅ Auto-scaling
- ✅ Pay per use
- ✅ High availability
- ✅ Fast deployment

### Why DynamoDB?

- ✅ Serverless database
- ✅ Single-digit millisecond latency
- ✅ Auto-scaling
- ✅ No schema management
- ✅ Built-in backup

### Why S3 for Frontend?

- ✅ Static website hosting
- ✅ High availability (99.99%)
- ✅ Low cost
- ✅ CDN integration ready
- ✅ Versioning support

### Why API Gateway?

- ✅ RESTful API management
- ✅ Request/response transformation
- ✅ Throttling & rate limiting
- ✅ CORS support
- ✅ CloudWatch integration

## Conclusion

VeriGov AI's architecture is designed for:
- **Scalability**: Handles millions of requests
- **Reliability**: 99.9% uptime SLA
- **Cost-Effectiveness**: <$1/month after free tier
- **Security**: Enterprise-grade AWS security
- **Maintainability**: Serverless, no infrastructure management

This architecture demonstrates best practices for building modern, cloud-native applications on AWS.
