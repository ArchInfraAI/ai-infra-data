from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class TaskQueue(Base):
    __tablename__ = 'task_queue'

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String, index=True, nullable=False)
    payload = Column(JSON, nullable=True)
    status = Column(String, index=True, default='pending') # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
