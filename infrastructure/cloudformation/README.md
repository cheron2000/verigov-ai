# VeriGov AI - DynamoDB Infrastructure

This directory contains CloudFormation templates for deploying VeriGov AI's DynamoDB tables.

## Tables Overview

### 1. Audit Logs Table
- **Purpose**: Store all system audit events
- **Partition Key**: `timestamp` (ISO8601 string)
- **Sort Key**: `event_type` (string)
- **GSIs**:
  - `verification_id-index`: Query logs by verification ID
  - `event_type-timestamp-index`: Query logs by event type and time range
- **Features**: Encryption at rest, point-in-time recovery, DynamoDB Streams

### 2. Verifications Table
- **Purpose**: Store verification results
- **Partition Key**: `verification_id` (string)
- **GSIs**:
  - `status-timestamp-index`: Query verifications by status and time
- **Features**: Encryption at rest, point-in-time recovery

### 3. Whitelist Table
- **Purpose**: Store approved government source domains
- **Partition Key**: `domain` (string)
- **Features**: Encryption at rest, point-in-time recovery

## Deployment

### Prerequisites
1. AWS CLI configured with credentials
2. Python 3.8+ with boto3 installed
3. Appropriate IAM permissions for CloudFormation and DynamoDB

### Deploy Tables

```bash
# Deploy to development environment
python scripts/deploy_dynamodb.py deploy --environment dev

# Deploy to production environment
python scripts/deploy_dynamodb.py deploy --environment prod

# Deploy to specific region
python scripts/deploy_dynamodb.py deploy --environment dev --region us-west-2
```

### Check Table Status

```bash
# Check development tables
python scripts/deploy_dynamodb.py status --environment dev

# Check production tables
python scripts/deploy_dynamodb.py status --environment prod
```

### Delete Tables

```bash
# Delete development tables (requires confirmation)
python scripts/deploy_dynamodb.py delete --environment dev

# Delete production tables (requires confirmation)
python scripts/deploy_dynamodb.py delete --environment prod
```

## Cost Optimization

All tables use **PAY_PER_REQUEST** (on-demand) billing mode to minimize costs:

- No charges when tables are idle
- Automatic scaling based on traffic
- Pay only for actual read/write requests
- No capacity planning required

### Estimated Costs (Development)
- **Audit Logs**: ~$0.25 per million writes, ~$0.25 per million reads
- **Verifications**: ~$0.25 per million writes, ~$0.25 per million reads
- **Whitelist**: Minimal (infrequent updates, cached reads)

**Expected monthly cost for development**: < $5

### Cost Monitoring
- Use AWS Cost Explorer to track DynamoDB costs
- Set up billing alarms (see `scripts/setup_billing_alerts.py`)
- Monitor request metrics in CloudWatch

## Table Structure Details

### Audit Logs Table Schema

```json
{
  "timestamp": "2024-03-05T10:30:00.000Z",
  "event_type": "VERIFICATION_COMPLETED",
  "verification_id": "uuid-here",
  "data": {
    "status": "VERIFIED",
    "confidence": 85,
    "claim": "Example claim"
  }
}
```

**Query Patterns**:
- Get all logs (scan with limit)
- Get logs by verification ID (GSI query)
- Get logs by event type and time range (GSI query)
- Get logs by date range (filter expression)

### Verifications Table Schema

```json
{
  "verification_id": "uuid-here",
  "status": "VERIFIED",
  "confidence": 85,
  "explanation": "Detailed explanation",
  "claim": "Example claim",
  "sources_checked": 3,
  "source_urls": ["url1", "url2"],
  "stored_at": "2024-03-05T10:30:00.000Z"
}
```

**Query Patterns**:
- Get verification by ID (primary key query)
- Get verifications by status (GSI query)
- Get verifications by status and time range (GSI query)

### Whitelist Table Schema

```json
{
  "domain": "example.gov",
  "updated_at": "2024-03-05T10:30:00.000Z"
}
```

**Query Patterns**:
- Get all domains (scan)
- Check if domain exists (get item)

## Security Features

1. **Encryption at Rest**: All tables use AWS KMS encryption
2. **Point-in-Time Recovery**: Enabled for data protection
3. **IAM Permissions**: Least privilege access via IAM roles
4. **VPC Endpoints**: Can be configured for private access (optional)

## Monitoring

### CloudWatch Metrics
- `ConsumedReadCapacityUnits`
- `ConsumedWriteCapacityUnits`
- `UserErrors`
- `SystemErrors`
- `ThrottledRequests`

### Alarms
Set up CloudWatch alarms for:
- High error rates
- Throttling events
- Unexpected cost increases

## Testing

Test the DynamoDB client:

```bash
# Run DynamoDB client tests (requires deployed tables)
python test_dynamodb_client.py
```

## Troubleshooting

### Table Not Found
```
Error: ResourceNotFoundException
```
**Solution**: Deploy tables using `python scripts/deploy_dynamodb.py deploy`

### Access Denied
```
Error: AccessDeniedException
```
**Solution**: Ensure your IAM user/role has DynamoDB permissions:
- `dynamodb:PutItem`
- `dynamodb:GetItem`
- `dynamodb:Query`
- `dynamodb:Scan`
- `dynamodb:UpdateItem`
- `dynamodb:DeleteItem`

### Throttling
```
Error: ProvisionedThroughputExceededException
```
**Solution**: On-demand mode should prevent this, but if it occurs:
1. Check for hot partitions
2. Implement exponential backoff retry
3. Consider batch operations

## Migration

To migrate existing local data to DynamoDB:

```bash
# Run migration script (to be implemented in Phase 7)
python scripts/migrate_to_dynamodb.py
```

## Backup and Recovery

### Automated Backups
- Point-in-time recovery enabled (35-day retention)
- Continuous backups with 5-minute granularity

### Manual Backups
```bash
# Create on-demand backup
aws dynamodb create-backup \
  --table-name verigov-dev-audit-logs \
  --backup-name verigov-dev-audit-logs-backup-$(date +%Y%m%d)
```

### Restore from Backup
```bash
# Restore table from backup
aws dynamodb restore-table-from-backup \
  --target-table-name verigov-dev-audit-logs-restored \
  --backup-arn <backup-arn>
```

## Best Practices

1. **Use Eventually Consistent Reads**: For audit logs (cost savings)
2. **Use Strongly Consistent Reads**: For verification results (accuracy)
3. **Implement Caching**: For whitelist (5-minute TTL)
4. **Batch Operations**: When possible to reduce costs
5. **Projection Expressions**: Fetch only needed attributes
6. **Monitor Costs**: Set up billing alarms and review regularly

## References

- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
- [CloudFormation DynamoDB Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)