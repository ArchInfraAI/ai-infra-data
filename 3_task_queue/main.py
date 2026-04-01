import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker, Session
from models import Base, TaskQueue
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    db_url: str = Field(default="postgresql://ai_admin:dummy_password_for_local_test@portfolio_db:5432/portfolio_vault")

settings = Settings()

engine = create_engine(settings.db_url, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Background Worker Logic using SKIP LOCKED ---
async def process_tasks():
    """
    Background worker loop that fetches tasks from PostgreSQL safely.
    It uses 'FOR UPDATE SKIP LOCKED' to ensure multiple workers can run concurrently
    without picking up the same task, eliminating the need for Redis/Celery for simple workloads.
    """
    logger.info("Background worker started.")
    while True:
        try:
            with SessionLocal() as db:
                # 1. Fetch exactly one pending task and lock it
                # SKIP LOCKED skips any rows currently locked by other workers
                stmt = (
                    select(TaskQueue)
                    .where(TaskQueue.status == 'pending')
                    .order_by(TaskQueue.created_at.asc())
                    .with_for_update(skip_locked=True)
                    .limit(1)
                )
                
                task = db.execute(stmt).scalar_one_or_none()
                
                if task:
                    # 2. Mark as processing
                    task.status = 'processing'
                    db.commit()
                    db.refresh(task)
                    
                    logger.info(f"Processing Task ID: {task.id} | Type: {task.task_type}")
                    
                    # 3. Simulate expensive AI work (e.g., PDF Parsing, Embedding Generation)
                    await asyncio.sleep(2.0)
                    
                    # 4. Mark as completed
                    task.status = 'completed'
                    db.commit()
                    logger.info(f"Completed Task ID: {task.id}")
                else:
                    # No pending tasks, wait before polling again
                    await asyncio.sleep(1.0)
        except Exception as e:
            logger.error(f"Worker encountered an error: {e}")
            await asyncio.sleep(5.0)

# --- App Lifecycle ---
worker_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_task
    # Initialize schema
    Base.metadata.create_all(bind=engine)
    
    # Start the background worker loop
    loop = asyncio.get_running_loop()
    worker_task = loop.create_task(process_tasks())
    
    yield
    
    # Graceful shutdown
    if worker_task:
        worker_task.cancel()

app = FastAPI(title="Async Task Queue (PostgreSQL SKIP LOCKED)", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Schemas ---
class TaskRequest(BaseModel):
    task_type: str
    payload: dict = {}

class TaskResponse(BaseModel):
    task_id: int
    status: str

# --- Routes ---
@app.post("/tasks", response_model=TaskResponse, summary="Enqueue a new task")
def create_task(req: TaskRequest, db: Session = Depends(get_db)):
    """
    Adds a new task to the queue table. The background worker will pick it up automatically.
    """
    new_task = TaskQueue(
        task_type=req.task_type,
        payload=req.payload,
        status='pending'
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {"task_id": new_task.id, "status": new_task.status}

@app.get("/tasks/{task_id}", response_model=TaskResponse, summary="Check task status")
def get_task_status(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(select(TaskQueue).where(TaskQueue.id == task_id)).scalar_one_or_none()
    if not task:
        return {"task_id": task_id, "status": "not_found"}
    
    return {"task_id": task.id, "status": task.status}
