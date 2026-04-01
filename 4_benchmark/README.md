# Module 4: Vector Engine Benchmark: PostgreSQL vs Qdrant vs SurrealDB

This module provides a fully automated, orchestrated benchmarking suite to evaluate the performance characteristics of PostgreSQL (pgvector) against prominent specialized vector databases: Qdrant and SurrealDB.

**Benchmark Date:** March 31, 2026  
**Environment:** GCP e2-micro (2 vCPUs, 1GB RAM, 2GB Swap)  
**Target Engine Versions:**
- PostgreSQL 18.3 (pgvector v0.8.0+)
- Qdrant v1.17.1
- SurrealDB v3.0.5

## Architectural Highlights (Senior Level)

### 1. Isolated Sequential Orchestration (OOM Prevention)
To ensure a fair test and prevent out-of-memory (OOM) errors on constrained cloud environments, the benchmark utilizes an orchestrator script (`run_benchmark.sh`). It starts one database container, runs the ingestion and search benchmarks, stops the container, and proceeds to the next. This ensures zero resource contention between database engines.

### 2. The Data Locality and Network Joins Argument
While specialized vector databases often demonstrate low raw search latencies, they introduce critical architectural overhead for complex enterprise systems: Network Joins and Data Fragmentation.

When utilizing a specialized Vector DB alongside a primary relational database:
1. The system must query the Vector DB for similar vectors (e.g., "Find top 100 similar profiles").
2. The system receives a list of IDs.
3. The system then queries the primary Relational DB: `SELECT * FROM profiles WHERE id IN (...) AND status = 'active' AND location = 'NY'`.
4. If the relational filters exclude most of the candidates, the system must repeat the loop, fetching more candidates from the Vector DB. This iterative process introduces significant network latency and logic complexity.

With pgvector, relational filtering and vector search are executed simultaneously within a single database process. This eliminates data fragmentation and network overhead.

## Benchmarking Methodology
- **Dataset:** 500 vectors generated with a fixed random seed to ensure consistent testing across engines.
- **Dimensions:** Tests both 1536d (High-density) and 384d (Optimized local) embeddings.
- **Metrics:** Measures Ping Latency (Active Conn), Batch Insert Time, Index Build Time, and KNN Search Latency.

## How to Run Locally

Execute the orchestrator script. It manages Docker container lifecycles and generates a final aggregated report.

    cd module4_vector_benchmark
    chmod +x run_benchmark.sh
    ./run_benchmark.sh

## Benchmark Results
Refer to `test_execution_log.txt` for the real-world execution output generated on the cloud infrastructure.

## Conclusion: Why PostgreSQL was Selected

Based on the benchmark results conducted on March 31, 2026, PostgreSQL with pgvector was selected as the primary vector engine for the following reasons:

1. **Superior Search Latency:** At 384 dimensions, PostgreSQL (HNSW/IVFFlat) achieved search latencies of 1.90ms - 2.70ms, outperforming Qdrant (3.36ms) and SurrealDB (49.53ms) on identical hardware.
2. **Protocol Efficiency:** PostgreSQL utilizes a persistent binary TCP connection, resulting in sub-millisecond ping latencies (~0.2ms). Specialized databases evaluated via REST/HTTP interfaces inherently suffer from significant serialization and HTTP header overhead.
3. **Operational Simplicity:** Specialized vector databases do not support full relational models or complex JOIN operations. Adopting a specialized engine necessitates managing two distinct database systems and resolving data consistency issues across them.
4. **Data Locality:** By keeping vector embeddings within the primary transactional database, the system avoids costly network hops and allows the database engine to optimize relational filters and vector searches in a single execution plan.

PostgreSQL provides the optimal balance of performance, architectural integrity, and reduced infrastructure complexity for enterprise-grade matching and social networking applications.
