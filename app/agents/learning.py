from sqlalchemy.orm import Session
from app.db.models import AgentDecision, ProviderHealth
from app.agents.types import DecisionTrace, ValidationStrategy
from app.core.logger import logger
from datetime import datetime

class LearningAgent:
    """
    Agent 4: Background process to learn from decisions and outcomes.
    """
    
    def record_decision(self, db: Session, phone: str, strategy: ValidationStrategy, trace: DecisionTrace):
        """
        Stores the decision made by Agent 1 for future analysis.
        """
        try:
            decision_record = AgentDecision(
                phone_number=phone,
                strategy=strategy.value,
                reasoning_trace=trace.dict()
            )
            db.add(decision_record)
            db.commit()
            logger.info(f"Recorded decision for {phone}")
        except Exception as e:
            logger.error(f"Failed to record decision: {e}")
            db.rollback()

    def update_provider_metrics(self, db: Session, provider_name: str, success: bool, response_time: float):
        """
        Updates success/failure rates for providers (Agent 2 feedback).
        """
        try:
            provider = db.query(ProviderHealth).filter(ProviderHealth.provider_name == provider_name).first()
            if not provider:
                provider = ProviderHealth(provider_name=provider_name)
                db.add(provider)
            
            if success:
                provider.success_count += 1
            else:
                provider.failure_count += 1
                
            # Simple moving average for response time (simplified)
            current_avg = provider.avg_response_time
            total_ops = provider.success_count + provider.failure_count
            new_avg = ((current_avg * (total_ops - 1)) + response_time) / total_ops
            provider.avg_response_time = new_avg
            
            db.commit()
            logger.info(f"Updated metrics for {provider_name}")
        except Exception as e:
            logger.error(f"Failed to update provider metrics: {e}")
            db.rollback()

learning_agent = LearningAgent()
