import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker, Session
from models import Base, RagDocument
from openai import OpenAI
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # NOTE: Default dummy credentials are provided strictly to enable 1-click local testing 
    # via docker-compose for recruiters/reviewers. In a production environment, 
    # these MUST be injected via secure CI/CD secrets manager and a .env file.
    db_url: str = Field(default="postgresql://ai_admin:dummy_password_for_local_test@portfolio_db:5432/portfolio_vault")
    openai_api_key: str = Field(default="dummy")

settings = Settings()

# --- Database Setup ---
engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- OpenAI Client ---
client = OpenAI(api_key=settings.openai_api_key)

def get_embedding(text: str) -> list[float]:
    if settings.openai_api_key == "dummy":
        # Fallback mechanism: Return a mock 1536-dimensional vector for local logic testing
        # without requiring reviewers to provide a real OpenAI API key.
        return [0.01] * 1536 
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure pgvector extension is activated
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    
    # 2. Initialize schema
    Base.metadata.create_all(bind=engine)
    
    # 3. Create HNSW (Hierarchical Navigable Small World) Index.
    # Why HNSW over IVFFlat? HNSW provides significantly better recall and performance 
    # for high-dimensional semantic search, crucial for production-grade RAG systems.
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS rag_documents_embedding_hnsw_idx 
            ON rag_documents 
            USING hnsw (embedding vector_cosine_ops) 
            WITH (m = 16, ef_construction = 64);
        """))
        conn.commit()
    yield

app = FastAPI(title="Advanced RAG with pgvector (HNSW)", lifespan=lifespan)

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Schemas ---
class DocumentCreate(BaseModel):
    content: str
    doc_metadata: dict = {}

class SearchQuery(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    id: int
    content: str
    similarity: float

# --- Routes ---
@app.post("/ingest", summary="Ingest Document", description="Generates embeddings and stores the document.")
def ingest_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    vector = get_embedding(doc.content)
    
    db_doc = RagDocument(
        content=doc.content,
        metadata_=doc.doc_metadata,
        embedding=vector
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return {"status": "success", "doc_id": db_doc.id}

@app.post("/search", response_model=list[SearchResult], summary="Semantic Search", description="Uses pgvector HNSW index for fast cosine similarity search.")
def search_documents(query: SearchQuery, db: Session = Depends(get_db)):
    query_vector = get_embedding(query.query)
    
    # Perform cosine similarity search utilizing the PostgreSQL pgvector HNSW index
    results = db.execute(
        select(
            RagDocument, 
            RagDocument.embedding.cosine_distance(query_vector).label('distance')
        )
        .order_by(RagDocument.embedding.cosine_distance(query_vector))
        .limit(query.limit)
    ).all()
    
    response = []
    for doc, distance in results:
        response.append(SearchResult(
            id=doc.id,
            content=doc.content,
            # Convert cosine distance to cosine similarity score
            similarity=1.0 - distance
        ))
        
    return response
