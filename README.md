# VeriGov AI - Government Information Verification Platform

[![AWS](https://img.shields.io/badge/AWS-Deployed-orange?logo=amazon-aws)](http://verigov-ai-frontend.s3-website.ap-south-1.amazonaws.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Serverless](https://img.shields.io/badge/Architecture-Serverless-green)](https://aws.amazon.com/serverless/)

> An AI-powered platform that verifies government claims and policies against official sources, combating misinformation and promoting transparency.

## 🌐 Live Demo

**Website:** [http://verigov-ai-frontend.s3-website.ap-south-1.amazonaws.com](http://verigov-ai-frontend.s3-website.ap-south-1.amazonaws.com)

**Try it now!** Verify claims about government policies, health announcements, or scientific facts.

## 📹 Demo Video

Link:https://drive.google.com/file/d/1scEN5GrYwuAH6srUvhrwAWR7KLRxZJV_/view?usp=sharing

## 🎯 Problem Statement

In today's digital age, misinformation about government policies, schemes, and announcements spreads rapidly. Citizens struggle to verify the authenticity of claims they encounter online, leading to confusion and mistrust in government institutions.

## 💡 Solution

VeriGov AI is an intelligent verification platform that:
- **Analyzes claims** using advanced AI (Groq's Llama 3.3 70B)
- **Auto-selects relevant sources** from 20+ verified government and international organizations
- **Fetches real-time data** from official websites
- **Provides confidence scores** and detailed explanations
- **Maintains audit trails** for transparency

## ✨ Key Features

### 🧠 Smart Verification System
- **Topic Detection**: Automatically identifies claim categories (health, space, government, etc.)
- **Source Selection**: Intelligently selects relevant trusted sources
- **Dual Mode**: Web scraping for sources OR AI knowledge base
- **Research Transparency**: Shows which method was used for verification

### 🎨 Modern Dashboard UI
- **Professional Design**: Clean, government-transparency inspired interface
- **Light/Dark Mode**: User preference with localStorage persistence
- **Real-time Stats**: Live verification counts and analytics
- **Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Accessible**: WCAG-compliant color contrast and semantic HTML

### 🔒 Trusted Sources (20+)
- Government of India (gov.in, nic.in, mygov.in)
- International Governments (UK, EU, US)
- Health Organizations (WHO, CDC, NIH)
- Scientific Institutions (NASA, Nature, Science)
- International Bodies (UN, World Bank, IMF)

### 📊 Audit & Transparency
- Complete verification history
- Timestamp tracking
- Source attribution
- Downloadable reports

## 🏗️ Architecture

### Serverless AWS Infrastructure

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  S3 Static Website Hosting          │
│  - Modern React-like UI             │
│  - Light/Dark Mode                  │
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
│  Lambda Functions (Python 3.11)     │
│  - Smart Verification               │
│  - Audit Log Retrieval              │
│  - Whitelist Management             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Data Layer                         │
│  - DynamoDB (3 tables)              │
│  - S3 (Data storage)                │
│  - Groq AI (LLM)                    │
└─────────────────────────────────────┘
```

### Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Font Awesome Icons
- Responsive Grid Layout

**Backend:**
- AWS Lambda (Python 3.11)
- API Gateway (REST API)
- DynamoDB (NoSQL Database)
- S3 (Static Hosting + Storage)

**AI/ML:**
- Groq AI (Llama 3.3 70B Versatile)
- BeautifulSoup4 (Web Scraping)
- Custom Topic Detection Algorithm

**DevOps:**
- Boto3 (AWS SDK)
- Automated Deployment Scripts
- CloudWatch (Monitoring)

## 📁 Project Structure

```
verigov-ai/
├── lambda/                          # Lambda function handlers
│   ├── verify_handler_smart.py     # Smart verification with auto source selection
│   ├── audit_handler.py            # Audit log retrieval
│   └── whitelist_handler.py        # Trusted sources management
├── static/                          # Frontend files
│   ├── index.html                  # Main dashboard
│   ├── style.css                   # Modern UI styles
│   └── script.js                   # Frontend logic
├── scripts/                         # Deployment automation
│   ├── deploy_support_lambdas.py   # Deploy Lambda functions
│   ├── deploy_to_s3.py             # Deploy frontend to S3
│   └── deploy_full_stack.py        # One-click deployment
├── config/                          # Configuration files
│   └── whitelist.json              # 20 trusted sources
├── infrastructure/                  # IaC templates
│   └── cloudformation/             # CloudFormation templates
├── src/verigov/                    # Core application logic
│   ├── verification/               # Verification engine
│   ├── collection/                 # Source management
│   └── storage/                    # Storage abstraction
├── docs/                           # Documentation
│   ├── DEPLOYMENT_SUCCESS_FULL_STACK.md
│   ├── AWS_FULL_DEPLOYMENT_GUIDE.md
│   └── ARCHITECTURE.md
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- AWS Account (Free Tier eligible)
- Python 3.11+
- Groq API Key ([Get one free](https://console.groq.com))

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/verigov-ai.git
cd verigov-ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Add your GROQ_API_KEY
```

4. **Run locally**
```bash
python app.py
```

Visit: http://localhost:5000

### Deploy to AWS

**One-Click Deployment:**
```bash
python scripts/deploy_full_stack.py
```

**Manual Deployment:**
```bash
# 1. Deploy Lambda functions
python scripts/deploy_support_lambdas.py

# 2. Deploy frontend to S3
python scripts/deploy_to_s3.py
```

See [AWS_FULL_DEPLOYMENT_GUIDE.md](AWS_FULL_DEPLOYMENT_GUIDE.md) for detailed instructions.

## 💰 Cost Analysis

### Free Tier (First 12 months)
- S3: 5GB storage, 15GB transfer - **FREE**
- Lambda: 1M requests, 400K GB-seconds - **FREE**
- API Gateway: 1M requests - **FREE**
- DynamoDB: 25GB storage, 25 RCU/WCU - **FREE**

**Total: $0/month** ✅

### After Free Tier (1000 verifications/month)
- S3: $0.10
- Lambda: $0.20
- API Gateway: $0.35
- DynamoDB: $0.25

**Total: ~$0.90/month** 💰

## 🎥 Demo Scenarios

### Scenario 1: Space Claim
**Claim:** "NASA launched a new Mars mission in 2024"
- ✅ Auto-detects "space" topic
- ✅ Selects NASA and ESA as sources
- ✅ Fetches data from official websites
- ✅ Provides verification with confidence score

### Scenario 2: Health Claim
**Claim:** "WHO declared a new health emergency"
- ✅ Auto-detects "health" topic
- ✅ Selects WHO, CDC, NIH as sources
- ✅ Verifies against official health organizations
- ✅ Shows research method used

### Scenario 3: Government Policy
**Claim:** "India's new tax reform is effective from April 2026"
- ✅ Auto-detects "government_india" topic
- ✅ Selects gov.in, nic.in, mygov.in
- ✅ Checks official government portals
- ✅ Provides detailed explanation

## 📊 Performance Metrics

- **Frontend Load Time**: < 1 second
- **Verification Speed**: 1-5 seconds
  - AI mode: ~1-2 seconds
  - Source fetching: ~3-5 seconds
- **API Response Time**: < 500ms
- **Uptime**: 99.9% (AWS SLA)
- **Scalability**: Auto-scales to millions of requests

## 🔒 Security Features

- ✅ HTTPS on API Gateway
- ✅ IAM roles for Lambda functions
- ✅ DynamoDB encryption at rest
- ✅ S3 bucket policies
- ✅ CORS enabled for API access
- ✅ No hardcoded credentials
- ✅ Environment variable management

## 🧪 Testing

### Test the Live Website
```bash
# Test verification endpoint
curl -X POST https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/api/verify-sources \
  -H "Content-Type: application/json" \
  -d '{"claim": "NASA launched a new Mars mission"}'

# Test audit endpoint
curl https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/audit?limit=5

# Test whitelist endpoint
curl https://qycb40y6n6.execute-api.ap-south-1.amazonaws.com/dev/whitelist
```

## 📈 Future Enhancements

- [ ] Add CloudFront CDN for HTTPS
- [ ] Implement user authentication (AWS Cognito)
- [ ] Add rate limiting and API keys
- [ ] Create mobile app (React Native)
- [ ] Add more international sources
- [ ] Implement ML-based source reliability scoring
- [ ] Add multi-language support
- [ ] Create browser extension
- [ ] Add fact-checking API for third-party integration

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Team

- **Developer**: Shreyash
- **AWS Account**: 448772857627
- **Region**: ap-south-1 (Mumbai)

## 🏆 Hackathon Submission

### AWS Services Used
- ✅ AWS Lambda (Serverless compute)
- ✅ API Gateway (REST API)
- ✅ DynamoDB (NoSQL database)
- ✅ S3 (Static hosting + storage)
- ✅ CloudWatch (Monitoring)
- ✅ IAM (Security)
- ✅ CloudFormation (Infrastructure as Code)

### Innovation Highlights
1. **Smart Source Selection**: AI automatically picks relevant sources
2. **Dual Verification Mode**: Web scraping + AI knowledge base
3. **Cost-Effective**: $0/month on free tier, <$1/month after
4. **Serverless Architecture**: Auto-scaling, no server management
5. **Modern UI/UX**: Professional dashboard with light/dark mode

### Impact
- Combats misinformation about government policies
- Promotes transparency and trust
- Accessible to everyone (free to use)
- Scalable to millions of users
- Educational tool for fact-checking

## 📞 Contact

- **Email**: [shreyashirkar1@gmail.com]
## 🙏 Acknowledgments

- AWS for providing cloud infrastructure
- Groq for AI capabilities
- Open-source community for tools and libraries
- Government organizations for maintaining official sources

---

**Built with ❤️ for transparent governance and informed citizens**

