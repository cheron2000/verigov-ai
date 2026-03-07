# 🌐 VeriGov AI - Web Application Guide

## ✅ Web App Successfully Deployed!

The VeriGov AI web interface is now running at:

**http://127.0.0.1:5000**

Open this URL in your browser to access the web interface.

## 🎨 Features

### Main Interface
- **Clean, modern UI** with gradient design
- **Claim verification form** with textarea input
- **Multiple source inputs** (up to 3 government URLs)
- **Real-time verification** with loading animation
- **Visual results display** with confidence bars and status badges

### API Endpoints

#### 1. Verify Claim
```
POST /api/verify
Content-Type: application/json

{
  "claim": "The federal minimum wage is $7.25 per hour",
  "sources": ["https://www.dol.gov/agencies/whd/minimum-wage"]
}
```

#### 2. Get Audit Log
```
GET /api/audit?limit=10
```

#### 3. Get Whitelist
```
GET /api/whitelist
```

## 🚀 How to Use

### Starting the Server
```bash
# Make sure you're in the virtual environment
python app.py
```

The server will start on http://127.0.0.1:5000

### Using the Web Interface

1. **Enter a Claim**: Type any government-related claim in the text area
2. **Add Sources (Optional)**: Paste government URLs in the source fields
3. **Click "Verify Claim"**: The AI will analyze the claim
4. **View Results**: See the verification status, confidence score, and explanation

### Example Claims to Test

- "The federal minimum wage is $7.25 per hour"
- "Social Security benefits are adjusted annually for inflation"
- "The voting age in the United States is 18"
- "Medicare covers prescription drugs"

## 📊 Dashboard Features

### Verification Results
- ✅ **VERIFIED**: Claim is confirmed by sources
- ⚠️ **PARTIALLY_VERIFIED**: Some evidence supports the claim
- ❓ **UNVERIFIED**: Cannot confirm from provided sources
- ❌ **FALSE**: Claim contradicts official sources
- 🚫 **NO_SOURCES**: No sources provided for verification

### Confidence Score
- Visual progress bar showing 0-100% confidence
- Color-coded based on verification status

### Approved Sources
- Live display of whitelisted government domains
- Shows domain name and official title

### Recent Activity
- Last 5 verification attempts
- Timestamps and event types
- Auto-refreshes after each verification

## 🛠️ Technical Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: Custom CSS with gradient design
- **AI**: Groq API (llama-3.3-70b-versatile)
- **Data**: JSON-based audit logging

## 📱 Responsive Design

The interface is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices

## 🔒 Security Features

- HTTPS-only source collection
- Whitelist validation for all domains
- SSL certificate verification
- Input sanitization
- CORS protection

## 🎯 Next Steps

### Enhancements You Can Add:

1. **User Authentication**: Add login/signup
2. **History Page**: View all past verifications
3. **Export Results**: Download as PDF/CSV
4. **Batch Upload**: Upload CSV of claims
5. **Real-time Monitoring**: WebSocket for live updates
6. **Charts & Analytics**: Visualization of verification trends
7. **API Keys**: Rate limiting and authentication
8. **Dark Mode**: Theme toggle

### Deployment Options:

1. **Local Development**: Current setup (Flask dev server)
2. **Production**: Use Gunicorn or uWSGI
3. **Cloud**: Deploy to AWS, Heroku, or DigitalOcean
4. **Docker**: Containerize the application

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Use a different port
python app.py --port 8000
```

### API errors
- Check `.env` file has valid `GROQ_API_KEY`
- Verify internet connection for API calls
- Check logs in `logs/audit.log`

### Styling issues
- Clear browser cache (Ctrl+Shift+R)
- Check browser console for errors
- Verify static files are loading

## 📞 Support

For issues or questions:
1. Check the audit log: `logs/audit.log`
2. Review the testing summary: `TESTING_SUMMARY.md`
3. Check the main README: `README.md`

---

**Status**: ✅ Running  
**URL**: http://127.0.0.1:5000  
**Port**: 5000  
**Debug Mode**: Enabled
