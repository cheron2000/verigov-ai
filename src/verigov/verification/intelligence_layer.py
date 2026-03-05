"""Intelligence layer using Groq AI for semantic analysis"""

from typing import Dict, List
from groq import Groq
from ..config.api_config import APIConfig


class IntelligenceLayer:
    """AI-powered semantic analysis using Groq"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.config.validate()
        self.client = Groq(api_key=self.config.api_key)
    
    def analyze_claim(self, claim: str, sources: List[Dict]) -> Dict:
        """Analyze a claim against source data using Groq AI"""
        
        # Prepare context from sources
        context = self._prepare_context(sources)
        
        # Create prompt for Groq
        prompt = f"""You are a fact-checking AI. Analyze the following claim against official government sources.

Claim: {claim}

Sources:
{context}

Provide your analysis in the following format:
1. Status: VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED, or FALSE
2. Confidence: A score from 0-100
3. Explanation: A clear explanation of your reasoning
4. Supporting Evidence: Key quotes or facts from the sources

Be precise and cite specific sources."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a precise fact-checking assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return self._parse_response(result)
            
        except Exception as e:
            return {
                "status": "ERROR",
                "confidence": 0,
                "explanation": f"Error during analysis: {str(e)}",
                "evidence": []
            }
    
    def _prepare_context(self, sources: List[Dict]) -> str:
        """Prepare source context for analysis"""
        context_parts = []
        for i, source in enumerate(sources, 1):
            if "content" in source:
                # Truncate content to avoid token limits
                content = source["content"][:2000]
                context_parts.append(f"Source {i} ({source.get('domain', 'unknown')}):\n{content}\n")
        return "\n".join(context_parts)
    
    def _parse_response(self, response: str) -> Dict:
        """Parse Groq's response into structured format"""
        lines = response.strip().split('\n')
        
        result = {
            "status": "UNVERIFIED",
            "confidence": 50,
            "explanation": response,
            "evidence": []
        }
        
        for line in lines:
            if "Status:" in line or "status:" in line.lower():
                status = line.split(":", 1)[1].strip().upper()
                if status in ["VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "FALSE"]:
                    result["status"] = status
            elif "Confidence:" in line or "confidence:" in line.lower():
                try:
                    conf_str = line.split(":", 1)[1].strip().replace("%", "")
                    result["confidence"] = int(conf_str)
                except ValueError:
                    pass
        
        return result
