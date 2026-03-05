"""Fact verification engine with storage abstraction"""

import uuid
from typing import Dict, List, Optional
from ..collection.source_collector import SourceCollector
from ..infrastructure.audit_log import AuditLog
from ..storage import StorageFactory
from .intelligence_layer import IntelligenceLayer


class FactVerificationEngine:
    """Main engine for verifying claims with result storage"""
    
    def __init__(
        self,
        source_collector: SourceCollector,
        intelligence_layer: IntelligenceLayer,
        audit_log: AuditLog,
        storage_mode: str = None
    ):
        self.collector = source_collector
        self.intelligence = intelligence_layer
        self.audit = audit_log
        
        # Use storage abstraction for verification results
        self.storage = StorageFactory.create_storage(storage_mode)
    
    def verify(self, claim: str, source_urls: Optional[List[str]] = None) -> Dict:
        """Verify a claim against sources and store the result"""
        
        # Generate unique verification ID
        verification_id = str(uuid.uuid4())
        
        # Log verification attempt
        self.audit.log("verification_started", {
            "verification_id": verification_id,
            "claim": claim,
            "source_urls": source_urls or []
        })
        
        # Collect data from sources
        sources = []
        if source_urls:
            for url in source_urls:
                try:
                    data = self.collector.collect(url)
                    if data and "content" in data:
                        sources.append(data)
                except Exception as e:
                    self.audit.log("collection_error", {
                        "verification_id": verification_id,
                        "url": url, 
                        "error": str(e)
                    })
        
        # Analyze claim using AI
        if sources:
            result = self.intelligence.analyze_claim(claim, sources)
        else:
            result = {
                "status": "NO_SOURCES",
                "confidence": 0,
                "explanation": "No valid sources provided for verification",
                "evidence": []
            }
        
        # Add metadata
        result["verification_id"] = verification_id
        result["claim"] = claim
        result["sources_checked"] = len(sources)
        result["source_urls"] = source_urls or []
        
        # Store verification result
        try:
            self.storage.store_verification(verification_id, result)
        except Exception as e:
            self.audit.log("storage_error", {
                "verification_id": verification_id,
                "error": str(e)
            })
        
        # Log completion
        self.audit.log("verification_completed", {
            "verification_id": verification_id,
            "status": result["status"],
            "confidence": result["confidence"]
        })
        
        return result
    
    def get_verification(self, verification_id: str) -> Optional[Dict]:
        """Retrieve a stored verification result"""
        try:
            return self.storage.get_verification(verification_id)
        except Exception as e:
            self.audit.log("retrieval_error", {
                "verification_id": verification_id,
                "error": str(e)
            })
            return None
    
    def verify_batch(self, claims: List[str], source_urls: Optional[List[str]] = None) -> Dict:
        """Verify multiple claims and store batch results"""
        
        # Generate unique batch ID
        batch_id = str(uuid.uuid4())
        
        # Log batch verification attempt
        self.audit.log("batch_verification_started", {
            "batch_id": batch_id,
            "claim_count": len(claims),
            "source_urls": source_urls or []
        })
        
        # Verify each claim
        results = []
        for claim in claims:
            result = self.verify(claim, source_urls)
            results.append(result)
        
        # Store batch results
        try:
            self.storage.store_batch_results(batch_id, results)
        except Exception as e:
            self.audit.log("batch_storage_error", {
                "batch_id": batch_id,
                "error": str(e)
            })
        
        # Log batch completion
        self.audit.log("batch_verification_completed", {
            "batch_id": batch_id,
            "results_count": len(results)
        })
        
        return {
            "batch_id": batch_id,
            "results": results,
            "summary": {
                "total": len(results),
                "verified": len([r for r in results if r["status"] == "VERIFIED"]),
                "unverified": len([r for r in results if r["status"] == "UNVERIFIED"]),
                "errors": len([r for r in results if r["status"] == "ERROR"])
            }
        }
    
    def get_batch_results(self, batch_id: str) -> Optional[List[Dict]]:
        """Retrieve stored batch results"""
        try:
            return self.storage.get_batch_results(batch_id)
        except Exception as e:
            self.audit.log("batch_retrieval_error", {
                "batch_id": batch_id,
                "error": str(e)
            })
            return None
