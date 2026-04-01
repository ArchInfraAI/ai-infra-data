from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AIAuditLog(Base):
    __tablename__ = 'ai_audit_log'

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
