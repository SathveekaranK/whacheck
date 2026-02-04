from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ValidationStrategy(str, Enum):
    IMMEDIATE = "immediate"
    DEFERRED = "deferred"
    SKIP = "skip"

class DecisionSignal(BaseModel):
    rule_name: str
    passed: bool
    details: str

class DecisionTrace(BaseModel):
    steps: List[DecisionSignal]
    final_decision: ValidationStrategy
    reasoning: str

class ValidationResult(BaseModel):
    phone_number: str
    is_valid: bool
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    whatsapp_available: bool = False
    confidence_score: float = 0.0
    strategy_used: ValidationStrategy
    trace: Optional[DecisionTrace] = None
