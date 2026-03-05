# DynamoDB Integration Guide for VeriGov AI

## Quick Start

### 1. Install AWS Dependencies

```bash
pip install -r requirements-aws.txt
```

### 2. Configure AWS Credentials

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### 3. Deploy DynamoDB Tables

```bash
python scripts/deploy_dynamodb.py deploy --environment dev
```

### 4. Configure Application

Update your `.env` file:

```bash
STORAGE_MODE=aws
AWS_REGION=us-east-1
ENVIRONMENT=dev
```

### 5. Test the Integration

```bash
# Test DynamoDB client
python test_dynamodb_client.py

# Test application with AWS storage
python -m src.verigov.main --storage aws verify "Test claim"
```

## Using DynamoDB Client Directly

### Initialize Client

```python
from src.verigov.aws import DynamoDBClient

client = DynamoDBClient(region='us-east-1')
```

### Audit Log Operations

```python
# Store audit log
entry = {
    'timestamp': '2024-03-05T10:30:00.000Z',
    'event_type': 'VERIFICATION_COMPLETED',
    'verification_id': 'uuid-123',
    'data': {'status': 'VERIFIED'}
}
client.put_audit_log(entry)

# Query all audit logs
logs = client.query_audit_logs(limit=100)

# Query by verification ID
logs = client.query_audit_logs(
    verification_id='uuid-123',
    limit=50
)

# Query by event type and date range
from datetime import datetime, timedelta
logs = client.query_audit_logs(
    event_type='VERIFICATION_COMPLETED',
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    limit=100
)
```

### Verification Operations

```python
# Store verification result
result = {
    'status': 'VERIFIED',
    'confidence': 85,
    'explanation': 'Claim verified',
    'claim': 'Example claim'
}
client.put_verification('verification-id', result)

# Get verification by ID
result = client.get_verification('verification-id')

# Query by status
verifications = client.query_verifications_by_status(
    status='VERIFIED',
    limit=50
)
```

### Whitelist Operations

```python
# Update whitelist
sources = ['example.gov', 'test.gov']
client.update_whitelist(sources)

# Get whitelist
sources = client.get_whitelist()
```

## Using Storage Abstraction

The recommended way to use DynamoDB is through the storage abstraction layer:

```python
from src.verigov.storage import StorageFactory

# Create AWS storage instance
storage = StorageFactory.create_storage('aws')

# Or use environment variable
import os
os.environ['STORAGE_MODE'] = 'aws'
storage = StorageFactory.create_storage()

# Use storage interface
storage.store_audit_log(entry)
logs = storage.query_audit_logs(limit=100)
```

## Hybrid Mode (Local + AWS)

Write to both local files and AWS for gradual migration:

```python
# Set hybrid mode
os.environ['STORAGE_MODE'] = 'hybrid'

# Initialize app
from src.verigov.main import VeriGovApp
app = VeriGovApp()

# All operations now write to both local and AWS
result = app.verify_claim("Test claim")
```

## Cost Optimization Tips

### 1. Use Eventually Consistent Reads

```python
# For audit logs (saves ~50% on read costs)
logs = client.query_audit_logs(
    limit=100,
    consistent_read=False  # Default
)
```

### 2. Use Strongly Consistent Reads Only When Needed

```python
# For verification results (ensures latest data)
result = client.get_verification(
    'verification-id',
    consistent_read=True  # Default for verifications
)
```

### 3. Implement Caching

```python
# Whitelist is automatically cached for 5 minutes
sources = storage.get_whitelist()  # First call hits DynamoDB
sources = storage.get_whitelist()  # Subsequent calls use cache
```

### 4. Use Batch Operations

```python
# Batch verify claims
claims = ["Claim 1", "Claim 2", "Claim 3"]
batch_result = app.verify_batch(claims)
```

### 5. Limit Query Results

```python
# Always specify a reasonable limit
logs = client.query_audit_logs(limit=100)  # Good
logs = client.query_audit_logs()  # Uses default limit
```

## Monitoring

### Check Table Status

```bash
python scripts/deploy_dynamodb.py status --environment dev
```

### View CloudWatch Metrics

```bash
# Using AWS CLI
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=verigov-dev-audit-logs \
  --start-time 2024-03-05T00:00:00Z \
  --end-time 2024-03-05T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

### Monitor Costs

```bash
# Check current costs
python scripts/check_aws_costs.py

# Set up billing alerts
python scripts/setup_billing_alerts.py
```

## Troubleshooting

### Issue: "Table does not exist"

**Solution**: Deploy tables first
```bash
python scripts/deploy_dynamodb.py deploy --environment dev
```

### Issue: "Access Denied"

**Solution**: Check IAM permissions
```bash
# Test AWS credentials
aws sts get-caller-identity

# Check DynamoDB access
aws dynamodb list-tables
```

### Issue: "Throttling errors"

**Solution**: Implement exponential backoff (already built-in)
```python
# The client automatically retries with backoff
# No action needed - just be aware of rate limits
```

### Issue: "High costs"

**Solution**: Review usage patterns
```bash
# Check table metrics
python scripts/deploy_dynamodb.py status --environment dev

# Review CloudWatch metrics
# Look for unexpected scan operations
# Ensure queries use indexes (GSIs)
```

## Migration from Local to AWS

### Step 1: Test AWS Storage

```bash
# Test with AWS storage mode
STORAGE_MODE=aws python -m src.verigov.main verify "Test claim"
```

### Step 2: Use Hybrid Mode

```bash
# Write to both local and AWS
STORAGE_MODE=hybrid python -m src.verigov.main verify "Test claim"
```

### Step 3: Migrate Existing Data

```bash
# Run migration script (Phase 7)
python scripts/migrate_to_dynamodb.py
```

### Step 4: Switch to AWS Only

```bash
# Update .env
STORAGE_MODE=aws

# Restart application
python app.py
```

## Best Practices

1. **Always set ENVIRONMENT variable** to avoid mixing dev/prod data
2. **Use hybrid mode during migration** for safety
3. **Monitor costs regularly** with billing alerts
4. **Test in dev environment first** before deploying to prod
5. **Implement proper error handling** for AWS service failures
6. **Use caching** for frequently accessed data (whitelist)
7. **Limit query results** to avoid excessive costs
8. **Use GSIs** for efficient queries (already configured)

## API Reference

### DynamoDBClient Methods

- `put_audit_log(entry)` - Store audit log entry
- `query_audit_logs(limit, start_date, end_date, event_type, verification_id, consistent_read)` - Query audit logs
- `put_verification(verification_id, result)` - Store verification result
- `get_verification(verification_id, consistent_read)` - Get verification by ID
- `query_verifications_by_status(status, limit, start_date, end_date)` - Query verifications by status
- `get_whitelist()` - Get all whitelist domains
- `update_whitelist(sources)` - Update whitelist domains
- `table_exists(table_name)` - Check if table exists
- `get_table_status(table_name)` - Get table status

### StorageInterface Methods

- `store_audit_log(entry)` - Store audit log
- `query_audit_logs(limit, start_date, end_date)` - Query audit logs
- `store_verification(verification_id, result)` - Store verification
- `get_verification(verification_id)` - Get verification
- `get_whitelist()` - Get whitelist
- `update_whitelist(sources)` - Update whitelist
- `store_batch_results(batch_id, results)` - Store batch results
- `get_batch_results(batch_id)` - Get batch results

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review CloudWatch logs for error details
3. Check AWS service health dashboard
4. Review DynamoDB best practices documentation