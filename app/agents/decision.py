from typing import Optional, Dict, Any
from app.agents.types import ValidationStrategy, DecisionTrace, DecisionSignal
from app.db.models import ValidationHistory
from app.core.logger import logger

class DecisionAgent:
    """
    Agent 1: Determines the validation strategy based on signals.
    """
    
    def decide(
        self, 
        phone_number: str, 
        country_code: str, 
        history: Optional[ValidationHistory], 
        numverify_data: Optional[Dict[str, Any]] = None
    ) -> DecisionTrace:
        
        steps = []
        
        # Step 1: Check History (Cache)
        if history and history.is_valid and history.whatsapp_available:
            # If recently validated successfully (logic to check recency can be added here)
            # For now, if we have a valid history, we skip re-validation to save cost
            steps.append(DecisionSignal(
                rule_name="History Check",
                passed=True,
                details="Found recent successful validation in history"
            ))
            return DecisionTrace(
                steps=steps,
                final_decision=ValidationStrategy.SKIP,
                reasoning="Information already known and valid."
            )
        
        steps.append(DecisionSignal(
            rule_name="History Check",
            passed=False,
            details="No valid recent history found"
        ))

        # Step 2: NumVerify Signals (Format & Line Type)
        if numverify_data:
            is_valid_format = numverify_data.get("valid", False)
            line_type = numverify_data.get("line_type", "")
            
            steps.append(DecisionSignal(
                rule_name="NumVerify Format",
                passed=is_valid_format,
                details=f"Format Valid: {is_valid_format}, Type: {line_type}"
            ))
            
            if not is_valid_format:
                return DecisionTrace(
                    steps=steps,
                    final_decision=ValidationStrategy.SKIP,
                    reasoning="Number format is invalid according to NumVerify."
                )
        
        # Step 3: Country / Market Logic (Placeholder for penetration rates)
        # e.g., Brazil/India have high WhatsApp usage -> Immediate
        high_priority_countries = ["BR", "IN", "ID", "US"]
        is_priority = country_code.upper() in high_priority_countries
        
        steps.append(DecisionSignal(
            rule_name="Country Priority",
            passed=is_priority,
            details=f"Country {country_code} is {'High' if is_priority else 'Standard'} priority"
        ))

        # Final Decision Logic
        if is_priority:
            decision = ValidationStrategy.IMMEDIATE
            reasoning = "High priority market, proceed with immediate validation."
        else:
            # Default to Deferred for others if we want to save resources, 
            # but for this MVP we might default to Immediate or Deferred based on requirements.
            # Let's say we fallback to Immediate for now to ensure we get results, 
            # or Deferred if we had a queue.
            decision = ValidationStrategy.IMMEDIATE 
            reasoning = "Standard priority, proceeding with validation."

        return DecisionTrace(
            steps=steps,
            final_decision=decision,
            reasoning=reasoning
        )

decision_agent = DecisionAgent()
