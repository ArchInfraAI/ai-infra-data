import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from models import Base, AIAuditLog
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = Field(default="postgresql://ai_admin:dummy_password_for_local_test@portfolio_db:5432/portfolio_vault")

settings = Settings()

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize schema
    Base.metadata.create_all(bind=engine)
    
    # Create an analytical SQL View for Business Intelligence
    # This demonstrates the ability to push analytical workloads to the database.
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE OR REPLACE VIEW ai_metrics_summary AS
            SELECT 
                model_name,
                COUNT(*) as total_requests,
                AVG(latency_ms) as avg_latency_ms,
                SUM(total_cost) as total_spend,
                (SUM(total_cost) / NULLIF(COUNT(*), 0)) * 1000 as cost_per_1k_requests
            FROM ai_audit_log
            GROUP BY model_name;
        """))
        conn.commit()
    yield

app = FastAPI(title="AI Observability & Monitoring", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pricing Configuration ---
MODEL_PRICING = {
    "gpt-4-turbo": {"prompt": 0.01 / 1000, "completion": 0.03 / 1000},
    "gpt-3.5-turbo": {"prompt": 0.0005 / 1000, "completion": 0.0015 / 1000},
}

class PromptRequest(BaseModel):
    model: str
    prompt: str

class GenerationResponse(BaseModel):
    response: str
    usage: dict

@app.post("/generate", response_model=GenerationResponse, summary="Mock LLM Generation with Telemetry")
async def generate_text(req: PromptRequest, request: Request, db: Session = Depends(get_db)):
    """
    Simulates an LLM call. The heavy lifting of observability is handled by tracking the latency
    and token usage, calculating the exact cost, and asynchronously persisting it to PostgreSQL.
    """
    start_time = time.time()
    
    # Simulate network latency based on model
    await asyncio.sleep(0.5 if req.model == "gpt-3.5-turbo" else 1.2)
    
    # Mock token calculation (1 word ~= 1.3 tokens)
    prompt_tokens = int(len(req.prompt.split()) * 1.3)
    completion_tokens = 50 # Mock fixed completion size
    
    # Calculate Cost
    rates = MODEL_PRICING.get(req.model, {"prompt": 0.0, "completion": 0.0})
    cost = (prompt_tokens * rates["prompt"]) + (completion_tokens * rates["completion"])
    
    latency_ms = (time.time() - start_time) * 1000
    
    # Log Telemetry to DB
    audit_log = AIAuditLog(
        model_name=req.model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        total_cost=cost
    )
    db.add(audit_log)
    db.commit()
    
    return GenerationResponse(
        response=f"This is a simulated response from {req.model}.",
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_cost": cost,
            "latency_ms": latency_ms
        }
    )

@app.get("/metrics", summary="Get Business Intelligence Metrics")
def get_metrics(db: Session = Depends(get_db)):
    """
    Fetches the aggregated analytics directly from the PostgreSQL View.
    """
    result = db.execute(text("SELECT * FROM ai_metrics_summary")).mappings().all()
    return [dict(row) for row in result]
