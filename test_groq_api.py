#!/usr/bin/env python3
"""Test Groq API connection"""

import os
from groq import Groq

# Get API key from .env
api_key = os.environ.get('GROQ_API_KEY', 'your-groq-api-key-here')

print("🧪 Testing Groq API...")
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print()

try:
    # Initialize client
    client = Groq(api_key=api_key)
    print("✅ Client initialized")
    
    # Make a simple test call
    print("📡 Calling Groq API...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say 'Hello, I am working!' in exactly those words."}
        ],
        temperature=0.1,
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"✅ API Response: {result}")
    print()
    
    # Test with verification prompt
    print("📡 Testing verification prompt...")
    verification_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user", 
            "content": """Analyze this claim and determine if it's verifiable:

Claim: The Earth orbits the Sun

Provide a JSON response with:
- status: VERIFIED, UNVERIFIED, or PARTIALLY_VERIFIED
- confidence: 0-100
- explanation: Brief explanation of your assessment

Response:"""
        }],
        temperature=0.3,
        max_tokens=500
    )
    
    verification_result = verification_response.choices[0].message.content
    print(f"✅ Verification Response:")
    print(verification_result)
    print()
    
    print("🎉 Groq API is working perfectly!")
    print()
    print("Token usage:")
    print(f"  Prompt tokens: {response.usage.prompt_tokens}")
    print(f"  Completion tokens: {response.usage.completion_tokens}")
    print(f"  Total tokens: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
