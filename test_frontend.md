# 🧪 Frontend Testing Guide

## Flask Server Status
✅ Server is running on: http://127.0.0.1:5000

## How to Test

### 1. Open the Web Interface
Open your browser and go to:
```
http://127.0.0.1:5000
```

### 2. Test Verification (Using Lambda API)
1. Enter a claim in the text box, for example:
   - "The Earth orbits the Sun"
   - "Water boils at 100 degrees Celsius"
   - "The moon landing was faked"

2. Optionally add source URLs

3. Click "Verify Claim"

4. You should see:
   - ✅ Loading indicator
   - ✅ Result with status (VERIFIED/UNVERIFIED/etc.)
   - ✅ Confidence score (0-100%)
   - ✅ Explanation from AI
   - ✅ Timestamp

**Note:** This now calls the Lambda function via API Gateway!

### 3. Check Whitelist Section
- Should show trusted sources from local config
- Located in the sidebar

### 4. Check Audit Log Section
- Should show recent verification activities
- Located in the sidebar
- Updates after each verification

## What's Working

### ✅ Verification Endpoint
- **Backend**: AWS Lambda via API Gateway
- **URL**: https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify
- **Storage**: DynamoDB (AWS)
- **AI**: Groq API (llama-3.3-70b-versatile)

### ✅ Whitelist Endpoint
- **Backend**: Local Flask server
- **URL**: http://127.0.0.1:5000/api/whitelist
- **Storage**: Local file (config/whitelist.json)

### ✅ Audit Endpoint
- **Backend**: Local Flask server
- **URL**: http://127.0.0.1:5000/api/audit
- **Storage**: AWS DynamoDB (via local Flask proxy)

## Architecture

```
Browser
  │
  ├─→ Verify Claim ──→ API Gateway ──→ Lambda ──→ Groq AI
  │                                      │
  │                                      └──→ DynamoDB
  │
  ├─→ Whitelist ──→ Flask (local) ──→ Local file
  │
  └─→ Audit Log ──→ Flask (local) ──→ DynamoDB (via AWS SDK)
```

## Test Scenarios

### Scenario 1: Scientific Fact
**Claim**: "The Earth orbits the Sun"
**Expected**: VERIFIED, 100% confidence

### Scenario 2: Common Knowledge
**Claim**: "Water boils at 100 degrees Celsius at sea level"
**Expected**: VERIFIED, high confidence

### Scenario 3: Controversial Claim
**Claim**: "The moon landing was faked"
**Expected**: UNVERIFIED or FALSE, with explanation

### Scenario 4: Ambiguous Claim
**Claim**: "Chocolate is healthy"
**Expected**: PARTIALLY_VERIFIED, medium confidence

### Scenario 5: Invalid Input
**Claim**: (empty)
**Expected**: Error message "Claim is required"

## Troubleshooting

### Issue: "Network error"
- Check if Flask server is running
- Check if Lambda API is accessible
- Check browser console for errors

### Issue: Whitelist not loading
- Check if config/whitelist.json exists
- Check Flask server logs

### Issue: Audit log not loading
- Check if DynamoDB tables are accessible
- Check AWS credentials in .env file

### Issue: Verification takes too long
- First request has "cold start" (~3-4 seconds)
- Subsequent requests are faster (~500ms)

## Browser Console Testing

Open browser console (F12) and run:

```javascript
// Test verification
fetch('https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({claim: 'Test claim', sources: []})
})
.then(r => r.json())
.then(console.log);

// Test whitelist
fetch('http://127.0.0.1:5000/api/whitelist')
.then(r => r.json())
.then(console.log);

// Test audit
fetch('http://127.0.0.1:5000/api/audit?limit=5')
.then(r => r.json())
.then(console.log);
```

## Next Steps After Testing

1. ✅ Verify all features work
2. ✅ Test with different claims
3. ✅ Check response times
4. ✅ Verify data is stored in DynamoDB
5. 📸 Take screenshots for demo
6. 🎥 Record demo video (optional)
7. 📝 Prepare presentation for judges

## Demo Tips

1. **Start with a simple fact**: "The Earth orbits the Sun"
   - Shows the system works
   - Gets VERIFIED status
   - High confidence score

2. **Show a controversial claim**: "The moon landing was faked"
   - Demonstrates AI reasoning
   - Shows how system handles misinformation

3. **Highlight the architecture**:
   - Serverless Lambda function
   - API Gateway for public access
   - DynamoDB for persistence
   - Groq AI for verification

4. **Mention the cost**: $0.02/month!
   - Within free tier
   - Scalable to millions of requests

## Success Criteria

✅ Web interface loads  
✅ Verification works and returns results  
✅ Results display correctly with status and confidence  
✅ Whitelist shows trusted sources  
✅ Audit log shows recent activity  
✅ Response time is acceptable (<5 seconds)  
✅ No errors in browser console  
✅ Data is stored in DynamoDB  

---

**Ready to test!** Open http://127.0.0.1:5000 in your browser.
