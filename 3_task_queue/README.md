# Module 3: Async Task Queue (PostgreSQL SKIP LOCKED)

This module demonstrates how to build a highly concurrent background task processing system using standard PostgreSQL capabilities, specifically the `SELECT ... FOR UPDATE SKIP LOCKED` pattern, eliminating the need for heavyweight external dependencies like Redis or Celery for moderately scaled workloads.

## Architectural Highlights (Senior Level)

SKIP LOCKED Concurrency: When multiple worker containers attempt to fetch the next pending task, row-level locking causes contention. Adding `SKIP LOCKED` ensures that if Worker A locks Row 1, Worker B instantly skips Row 1 and locks Row 2. This guarantees zero race conditions and maximum throughput across distributed workers.

Resource Efficiency: For AI startups or smaller microservices, introducing Redis + Celery adds significant DevOps overhead and points of failure. Utilizing the primary transactional database for task queues reduces infrastructure costs and complexity while maintaining ACID compliance.

Graceful Background Processing: The background worker loop is spawned as an `asyncio.Task` tied to the FastAPI application lifespan, ensuring it starts when the API boots and cleanly shuts down on exit.

## How to Run Locally

Launch the module using Docker Compose:

    cd module3_async_task_queue
    docker compose up --build

## Testing the Endpoints

### Automated Integration Test

To verify the workflow, run the integration script. This script submits multiple tasks concurrently and periodically polls their status until all are completed.

    python3 integration_test.py

You can view the execution trace in `test_execution_log.txt`.

### Manual Testing via cURL

#### 1. Enqueue a Task

    curl -X POST http://localhost:8000/tasks \
    -H 'Content-Type: application/json' \
    -d '{
      "task_type": "process_pdf", 
      "payload": {"file_url": "s3://bucket/doc.pdf"}
    }'

#### 2. Check Task Status

    curl -X GET http://localhost:8000/tasks/1
