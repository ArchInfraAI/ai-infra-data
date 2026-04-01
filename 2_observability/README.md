# Module 2: AI Observability and Monitoring

This module demonstrates a production-grade approach to tracking, logging, and analyzing LLM usage (tokens, latency, and cost) using FastAPI and PostgreSQL.

## Architectural Highlights (Senior Level)

Telemetry Interception: Implements a pattern to intercept LLM generation requests and asynchronously log crucial telemetry (Prompt/Completion tokens, Model name, execution time).

Dynamic Cost Calculation: Calculates exact USD cost dynamically based on model pricing tiers before committing the log to the database.

Database-Level Analytics (SQL Views): Demonstrates an understanding of moving analytical workloads to the database. Instead of calculating averages in Python, an ai_metrics_summary View is created to instantly provide Business Intelligence metrics like avg_latency_ms and cost_per_1k_requests.

Clean Database Schema: Stores audit logs efficiently, allowing simple scaling to tools like Grafana, Metabase, or Looker.

## How to Run Locally

You can launch this module with one command. Docker will automatically pull Postgres, build the Python API, and handle the migrations and views.

    cd module2_ai_observability
    docker compose up --build

## Testing the Endpoints

### Automated Integration Test

To verify the entire observability pipeline (request simulation, DB insertion, Analytics View aggregation), run the included integration test suite:

    python3 integration_test.py

This script will programmatically execute API calls and assert the expected analytics data. You can view a sample of its output in test_execution_log.txt.

### Manual Testing via cURL

#### 1. Simulate an LLM Request

    curl -X POST http://localhost:8000/generate \
    -H 'Content-Type: application/json' \
    -d '{
      "model": "gpt-4-turbo", 
      "prompt": "Write a SQL view."
    }'

#### 2. View Aggregated Business Intelligence

    curl -X GET http://localhost:8000/metrics
