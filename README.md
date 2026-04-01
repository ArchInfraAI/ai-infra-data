# Applied AI & Data Systems Architecture

This technical portfolio showcases production-grade implementations of core AI Infrastructure and Backend patterns. The focus extends beyond writing simple scripts, encompassing the construction of resilient, highly concurrent, and cost-observable architectures designed for enterprise scale.

## 🏗️ Technical Architecture & Implementations

### 1. [Advanced RAG with PostgreSQL pgvector](./1_rag)
A FastAPI microservice designed for high-precision document ingestion and semantic search. It utilizes **PostgreSQL 17** with the **pgvector** extension to bridge structured metadata with unstructured vector embeddings.
* **Technical Highlights:** pgvector integration, **HNSW Indexing** for sub-millisecond retrieval, FastAPI lifespan management, and cost-aware local testing strategies.

### 2. [AI Observability and Monitoring](./2_observability)
A comprehensive telemetry layer for intercepting LLM requests, performing dynamic calculation of operational costs, and persisting performance metrics to PostgreSQL.
* **Technical Highlights:** Middleware-level interception, real-time token/cost tracking, and the use of **SQL Views** for business intelligence and infrastructure analytics.

### 3. [Async Task Queue (Postgres-based)](./3_task_queue)
A highly concurrent background task processing system that eliminates the need for external dependencies like Redis or Celery. It leverages the **SELECT ... FOR UPDATE SKIP LOCKED** pattern for maximum reliability.
* **Technical Highlights:** Orchestrating graceful background processes within FastAPI, preventing race conditions via row-level locking, and maintaining architectural simplicity for moderate-to-high workloads.

### 4. [Vector Engine Benchmark: PostgreSQL vs Qdrant vs SurrealDB](./4_benchmark)
An automated, orchestrated benchmarking suite to evaluate raw performance and architectural trade-offs between general-purpose and specialized vector databases.
* **Technical Highlights:** Performance testing (insertion speed, KNN latency), multi-database orchestration via Docker, and objective evaluation of **Data Locality vs. Network Join** overhead.

### 5. [Local LLM Inference Optimization: MLX vs Ollama](./5_mlx_optimization)
A deep-dive performance analysis of LLM inference on Apple Silicon. This module evaluates the throughput and efficiency of the native **Apple MLX** framework against industry-standard wrappers.
* **Technical Highlights:** Hardware-aware optimization, **Apple Silicon Unified Memory (UMA)** mastery, and sustained throughput (TPS) profiling for high-volume data processing.

### 6. [LLM Fine-Tuning (SFT) on NVIDIA T4](./6_llm_finetuning_nvidia_t4)
A professional Supervised Fine-Tuning pipeline for domain-specific model adaptation. It demonstrates the ability to transform general LLMs into high-precision technical assistants on constrained hardware.
* **Technical Highlights:** **Unsloth** framework utilization for 2x training speedup, 4-bit NF4 quantization, and LoRA (Low-Rank Adaptation) methodology.

### 7. [Architecture Comparison: Gemma 4 Dense (4B) vs. MoE (26B)](./7_gemma4_benchmark)
Immediate benchmarking and performance profiling of the Gemma 4 Mixture of Experts architecture on 16GB RAM hardware.
* **Technical Highlights:** Day-zero integration, kernel-level memory tuning (14GB VRAM unlock), and MoE efficiency verification.

---
**Note on Security:** To ensure a seamless review experience, explicit dummy passwords are provided in the demonstration files. In production environments, strict secret injection via environment variables and vault systems is mandated.
