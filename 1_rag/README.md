# Module 1: Advanced RAG with PostgreSQL pgvector and HNSW Index

This module demonstrates a production-ready approach to building a Retrieval-Augmented Generation (RAG) backend utilizing FastAPI, SQLAlchemy, and PostgreSQL with the pgvector extension.

## Architectural Highlights (Senior Level)

HNSW Indexing: Unlike basic tutorials that default to IVFFlat indexes, this implementation provisions an HNSW (Hierarchical Navigable Small World) index upon initialization. HNSW provides superior recall and querying speed for high-dimensional spaces (like OpenAI 1536-dim vectors), which is a critical requirement for scaling RAG applications.

Infrastructure as Code: The extension activation (CREATE EXTENSION vector) and index creation are handled automatically via FastAPI asynchronous lifespan events, ensuring the database is instantly ready upon deployment without manual SQL intervention.

Pydantic Settings and Safety: Demonstrates modern 12-factor app principles. Configuration is loaded via pydantic-settings. 
Note on Security: Dummy credentials are deliberately hardcoded in the docker-compose.yml and defaults to provide a frictionless 1-click testing experience for reviewers. In a live production CI/CD pipeline, these are injected dynamically via a secrets manager.

Cost-Aware Testing: The OpenAI client wrapper contains a fallback mechanism. If the OPENAI_API_KEY is left as dummy, it generates a mock vector. This allows infrastructure logic testing (routing, DB inserts, HNSW indexing) without incurring unnecessary LLM API costs.

## How to Run Locally

You can launch this entire module with one command. Docker will automatically pull Postgres 17 (with pgvector), build the Python API, and handle the migrations.

    cd module1_advanced_rag
    docker compose up --build

## Testing the Endpoints

Once the containers are running (portfolio_api and portfolio_pgvector), the API will be available at http://localhost:8000.

### Automated Integration Test

To verify the entire workflow (ingestion, similarity search, and edge-cases) with a single command, run the included integration test suite:

    python3 integration_test.py

This script will programmatically execute API calls and assert the expected JSON responses. You can view a sample of its output in `test_execution_log.txt`.

### Manual Testing via cURL

#### 1. Ingest a Document

    curl -X POST http://localhost:8000/ingest \
    -H 'Content-Type: application/json' \
    -d '{
      "content": "This is a document about machine learning and vector databases.", 
      "doc_metadata": {"author": "AI Engineer"}
    }'

### 2. Perform a Semantic Search

    curl -X POST http://localhost:8000/search \
    -H 'Content-Type: application/json' \
    -d '{
      "query": "machine learning architecture", 
      "limit": 1
    }'

You can also explore the auto-generated Swagger documentation at: http://localhost:8000/docs
