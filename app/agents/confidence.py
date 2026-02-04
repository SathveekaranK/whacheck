from typing import Dict, Any, Optional
from app.agents.types import ValidationStrategy

class ConfidenceAgent:
    """
    Agent 3: Calculates a confidence score (0-100) for the validation result.
    """
    
    def calculate_score(
        self, 
        is_valid_format: bool, 
        whatsapp_exists: bool, 
        provider_used: str,
        history_present: bool
    ) -> Dict[str, Any]:
        
        score = 0.0
        breakdown = {}
        
        # 1. Format Validation (Max 20)
        if is_valid_format:
            score += 20
            breakdown["format"] = 20
        else:
            breakdown["format"] = 0
            
        # 2. Provider Reliability (Max 25)
        # Whapi = High reliability. Mock = Low.
        if provider_used == "whapi":
            score += 25
            breakdown["provider_reliability"] = 25
        elif provider_used == "mock":
            score += 10 # Mock is less reliable
            breakdown["provider_reliability"] = 10
        else:
            breakdown["provider_reliability"] = 0
            
        # 3. WhatsApp Detection (Max 30)
        if whatsapp_exists:
            score += 30
            breakdown["whatsapp_detection"] = 30
        else:
            # If we confirmed it DOESN'T exist, that's also a high confidence result 
            # (we are confident it's invalid). But purely for "validity confidence":
            breakdown["whatsapp_detection"] = 0
            
        # 4. History (Max 10)
        if history_present:
            score += 10
            breakdown["history"] = 10
        else:
            breakdown["history"] = 0
            
        # 5. Base Connectivity / Consistency (Max 15)
        score += 15
        breakdown["consistency"] = 15
        
        # Normalize/Cap
        final_score = min(max(score, 0), 100)
        
        # Classification
        if final_score >= 80:
            classification = "HIGH"
        elif final_score >= 60:
            classification = "MEDIUM"
        else:
            classification = "LOW"
            
        return {
            "score": final_score,
            "classification": classification,
            "breakdown": breakdown
        }

confidence_agent = ConfidenceAgent()
