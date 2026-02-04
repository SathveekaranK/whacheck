from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.agents.types import ValidationStrategy, DecisionTrace

class ValidateRequest(BaseModel):
    phone_number: str
    country_code: str = "US" # Default to US if not provided
    context: Optional[Dict[str, Any]] = None

class ConfidenceBreakdown(BaseModel):
    score: float
    classification: str
    signals: Dict[str, float]
    recommendation: str

class ValidateResponse(BaseModel):
    success: bool
    phone_number: str
    formatted_number: Optional[str] = None
    country_code: str
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    
    whatsapp_available: bool
    validation_strategy: ValidationStrategy
    
    confidence_score: float
    confidence_breakdown: ConfidenceBreakdown
    
    decision_trace: Optional[DecisionTrace] = None
    retry_metadata: Optional[Dict[str, Any]] = None
    
    reasoning: str
