from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class RagDocument(Base):
    __tablename__ = 'rag_documents'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    metadata_ = Column(JSON, nullable=True) 
    embedding = Column(Vector(1536)) # OpenAI text-embedding-3-small dimension
