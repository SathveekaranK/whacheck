from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class ValidationHistory(Base):
    __tablename__ = "validation_history"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True, unique=True)
    country_code = Column(String)
    is_valid = Column(Boolean)
    carrier = Column(String, nullable=True)
    line_type = Column(String, nullable=True)
    whatsapp_available = Column(Boolean)
    confidence_score = Column(Float)
    last_validated = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, nullable=True)

class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    strategy = Column(String)  # IMMEDIATE, DEFERRED, SKIP
    reasoning_trace = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ProviderHealth(Base):
    __tablename__ = "provider_health"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, unique=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
