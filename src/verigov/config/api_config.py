"""API Configuration for Groq AI"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class APIConfig:
    """Configuration for Groq API"""
    
    def __init__(self):
        self.api_key: Optional[str] = os.getenv("GROQ_API_KEY")
        self.api_url: str = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1")
        self.timeout: int = int(os.getenv("COLLECTION_TIMEOUT", "30"))
        self.max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_backoff: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "2"))
        
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required in .env file")
        return True
