"""Enhanced Intelligence layer using Groq AI for semantic analysis"""

from typing import Dict, List
import json
import re
from groq import Groq
from ..config.api_config import APIConfig


class IntelligenceLayer:
    """AI-powered semantic analysis using Groq with enhanced reasoning"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.config.validate()
        self.client = Groq(api_key=self.config.api_key)
    
    def analyze_claim(self, claim: str, sources: List[Dict]) -> Dict:
        """Analyze a claim against source data using enhanced multi-step reasoning"""
        
        # Step 1: Classify the claim type
        claim_type = self._classify_claim_type(claim)
        
        # Step 2: Prepare context from sources
        context = self._prepare_context(sources)
        
        # Step 3: Analyze based on claim type
        if claim_type == 'biographical':
            return self._analyze_biographical(claim, context, sources)
        elif claim_type == 'factual':
            return self._analyze_factual(claim, context, sources)
        elif claim_type == 'statistical':
            return self._analyze_statistical(claim, context, sources)
        else:
            return self._analyze_general(claim, context, sources)
    
    def _classify_claim_type(self, claim: str) -> str:
        """Classify the type of claim for appropriate analysis"""
        claim_lower = claim.lower()
        
        # Biographical queries
        if any(keyword in claim_lower for keyword in ['who is', 'who are', 'biography', 'born in', 'life of']):
            return 'biographical'
        
        # Statistical claims
        if any(keyword in claim_lower for keyword in ['percent', '%', 'statistics', 'number of', 'how many', 'rate of']):
            return 'statistical'
        
        # Factual claims (scientific, historical, etc.)
        if any(keyword in claim_lower for keyword in ['is', 'are', 'was', 'were', 'does', 'do', 'can', 'will']):
            return 'factual'
        
        return 'general'
    
    def _analyze_biographical(self, claim: str, context: str, sources: List[Dict]) -> Dict:
        """Analyze biographical queries with appropriate handling"""
        
        if not sources or not context.strip():
            # Use AI knowledge base for biographical info
            prompt = f"""You are a biographical information assistant. Answer this query using your knowledge base.

Query: {claim}

Instructions:
1. Provide accurate biographical information if you have it
2. Be specific and factual
3. If you don't have reliable information, say so clearly
4. Format your response as JSON with these exact fields:
   - status: "VERIFIED" (if you have reliable info), "PARTIALLY_VERIFIED" (if limited info), or "UNVERIFIED" (if no reliable info)
   - confidence: number from 0-100 (your confidence in the information)
   - explanation: the biographical information or explanation why you can't provide it
   - evidence: list of key facts (empty list if no reliable info)

Respond ONLY with valid JSON, no other text."""
            
            return self._call_groq_json(prompt, fallback_confidence=85)
        
        else:
            # Analyze with provided sources
            prompt = f"""You are a biographical information assistant. Analyze this query using the provided sources.

Query: {claim}

Sources:
{context}

Instructions:
1. Check if the sources contain relevant biographical information
2. Extract and summarize the information found
3. If sources don't contain the information, state that clearly
4. Format your response as JSON with these exact fields:
   - status: "VERIFIED" (if sources confirm), "PARTIALLY_VERIFIED" (if partial info), or "UNVERIFIED" (if sources don't contain info)
   - confidence: number from 0-100 (based on source quality and relevance)
   - explanation: the information found or explanation of what's missing
   - evidence: list of key facts from sources (empty list if not found)

Respond ONLY with valid JSON, no other text."""
            
            return self._call_groq_json(prompt, fallback_confidence=70)
    
    def _analyze_factual(self, claim: str, context: str, sources: List[Dict]) -> Dict:
        """Analyze factual claims with rigorous verification"""
        
        if not sources or not context.strip():
            # Use AI knowledge base
            prompt = f"""You are a fact-checking assistant. Verify this claim using your knowledge base.

Claim: {claim}

Instructions:
1. Assess if the claim is factually correct based on your knowledge
2. Consider scientific consensus and established facts
3. Be conservative - if uncertain, lower confidence
4. Format your response as JSON with these exact fields:
   - status: "VERIFIED" (if definitely true), "UNVERIFIED" (if false or uncertain), or "PARTIALLY_VERIFIED" (if partially true)
   - confidence: number from 0-100 (your confidence level)
   - explanation: clear explanation of why the claim is true/false/uncertain
   - evidence: list of key supporting facts (empty list if unverified)

Respond ONLY with valid JSON, no other text."""
            
            return self._call_groq_json(prompt, fallback_confidence=75)
        
        else:
            # Analyze with sources
            prompt = f"""You are a fact-checking assistant. Verify this claim using the provided trusted sources.

Claim: {claim}

Trusted Sources:
{context}

Instructions:
1. Check if the sources support, contradict, or don't mention the claim
2. Look for specific evidence in the source content
3. If sources are irrelevant to the claim, state that clearly
4. Be precise about what the sources actually say
5. Format your response as JSON with these exact fields:
   - status: "VERIFIED" (if sources confirm), "UNVERIFIED" (if sources contradict or are irrelevant), or "PARTIALLY_VERIFIED" (if sources partially support)
   - confidence: number from 0-100 (based on source relevance and clarity)
   - explanation: clear explanation citing what sources say
   - evidence: list of specific quotes or facts from sources (empty list if sources are irrelevant)

Respond ONLY with valid JSON, no other text."""
            
            return self._call_groq_json(prompt, fallback_confidence=80)
    
    def _analyze_statistical(self, claim: str, context: str, sources: List[Dict]) -> Dict:
        """Analyze statistical claims with numerical verification"""
        
        prompt = f"""You are a statistical fact-checker. Verify this statistical claim.

Claim: {claim}

{"Trusted Sources:\n" + context if context.strip() else "Note: No specific sources provided. Use your knowledge base."}

Instructions:
1. Check if the numbers/statistics in the claim are accurate
2. Look for exact matches or close approximations in sources
3. Consider the date/context of statistics (they may change over time)
4. If sources don't contain the statistics, check your knowledge base
5. Format your response as JSON with these exact fields:
   - status: "VERIFIED" (if numbers match), "UNVERIFIED" (if numbers don't match or can't verify), or "PARTIALLY_VERIFIED" (if approximately correct)
   - confidence: number from 0-100 (based on precision of match)
   - explanation: clear explanation of the statistical verification
   - evidence: list of specific numbers/statistics found (empty list if not found)

Respond ONLY with valid JSON, no other text."""
        
        return self._call_groq_json(prompt, fallback_confidence=70)
    
    def _analyze_general(self, claim: str, context: str, sources: List[Dict]) -> Dict:
        """Analyze general claims"""
        
        prompt = f"""You are a fact-checking assistant. Analyze this claim.

Claim: {claim}

{"Trusted Sources:\n" + context if context.strip() else "Note: No specific sources provided. Use your knowledge base."}

Instructions:
1. Assess the claim's validity based on available information
2. Be thorough but concise
3. If sources are provided but irrelevant, state that clearly
4. Format your response as JSON with these exact fields:
   - status: "VERIFIED", "UNVERIFIED", or "PARTIALLY_VERIFIED"
   - confidence: number from 0-100
   - explanation: clear explanation of your assessment
   - evidence: list of supporting facts (empty list if none)

Respond ONLY with valid JSON, no other text."""
        
        return self._call_groq_json(prompt, fallback_confidence=70)
    
    def _call_groq_json(self, prompt: str, fallback_confidence: int = 50) -> Dict:
        """Call Groq API and parse JSON response with robust error handling"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise fact-checking assistant. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Lower temperature for more consistent output
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            result = self._parse_json_response(result_text)
            
            # Validate and normalize the result
            result = self._validate_result(result, fallback_confidence)
            
            return result
            
        except Exception as e:
            print(f"Error in Groq API call: {e}")
            return {
                "status": "ERROR",
                "confidence": 0,
                "explanation": f"Error during analysis: {str(e)}",
                "evidence": []
            }
    
    def _parse_json_response(self, text: str) -> Dict:
        """Parse JSON from response text with multiple fallback strategies"""
        
        # Strategy 1: Direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Find first JSON object in text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Manual parsing from text
        return self._manual_parse(text)
    
    def _manual_parse(self, text: str) -> Dict:
        """Manually parse response when JSON parsing fails"""
        
        result = {
            "status": "UNVERIFIED",
            "confidence": 50,
            "explanation": text[:500],
            "evidence": []
        }
        
        # Extract status
        status_match = re.search(r'status["\s:]+([A-Z_]+)', text, re.IGNORECASE)
        if status_match:
            status = status_match.group(1).upper()
            if status in ["VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "FALSE"]:
                result["status"] = status
        
        # Extract confidence
        conf_match = re.search(r'confidence["\s:]+(\d+)', text, re.IGNORECASE)
        if conf_match:
            try:
                result["confidence"] = int(conf_match.group(1))
            except ValueError:
                pass
        
        # Extract explanation
        exp_match = re.search(r'explanation["\s:]+["\']([^"\']+)["\']', text, re.IGNORECASE | re.DOTALL)
        if exp_match:
            result["explanation"] = exp_match.group(1)[:500]
        
        return result
    
    def _validate_result(self, result: Dict, fallback_confidence: int) -> Dict:
        """Validate and normalize the result"""
        
        # Ensure required fields exist
        if "status" not in result:
            result["status"] = "UNVERIFIED"
        
        if "confidence" not in result:
            result["confidence"] = fallback_confidence
        
        if "explanation" not in result:
            result["explanation"] = "Analysis completed but explanation not provided"
        
        if "evidence" not in result:
            result["evidence"] = []
        
        # Normalize status
        status = str(result["status"]).upper()
        if status not in ["VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "FALSE", "ERROR"]:
            result["status"] = "UNVERIFIED"
        else:
            result["status"] = status
        
        # Normalize confidence
        try:
            confidence = int(result["confidence"])
            result["confidence"] = max(0, min(100, confidence))
        except (ValueError, TypeError):
            result["confidence"] = fallback_confidence
        
        # Ensure evidence is a list
        if not isinstance(result["evidence"], list):
            result["evidence"] = []
        
        return result
    
    def _prepare_context(self, sources: List[Dict]) -> str:
        """Prepare source context for analysis with better formatting"""
        
        if not sources:
            return ""
        
        context_parts = []
        for i, source in enumerate(sources, 1):
            if "content" in source and source["content"]:
                # Get domain from URL
                domain = source.get('domain', source.get('url', 'unknown'))
                
                # Truncate content intelligently (keep first 3000 chars)
                content = source["content"][:3000]
                
                # Add source with clear formatting
                context_parts.append(
                    f"=== Source {i}: {domain} ===\n"
                    f"{content}\n"
                    f"{'=' * 50}\n"
                )
        
        return "\n".join(context_parts) if context_parts else ""
