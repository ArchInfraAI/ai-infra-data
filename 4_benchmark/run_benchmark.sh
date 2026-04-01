#!/bin/bash
echo "Starting Vector DB Benchmark Suite..."

# Ensure we start fresh
rm -f results.json
echo "[]" > results.json
chmod 777 results.json

# Build the runner
docker build -t bench_runner -f Dockerfile .

run_benchmark() {
    local service=$1
    local engine=$2
    
    echo "========================================"
    echo "Testing $engine..."
    echo "========================================"
    
    docker compose up -d $service
    echo "Waiting for $service to initialize..."
    sleep 15
    
    # Run tests for both dimensions
    docker run --rm --network module4_vector_benchmark_default -v $(pwd)/results.json:/app/results.json bench_runner python benchmark.py --engine $engine --dim 1536
    docker run --rm --network module4_vector_benchmark_default -v $(pwd)/results.json:/app/results.json bench_runner python benchmark.py --engine $engine --dim 384
    
    docker compose stop $service
    docker compose rm -f $service
    echo ""
}

# Run the sequence
run_benchmark "portfolio_pg_benchmark" "postgres-hnsw"
run_benchmark "portfolio_pg_benchmark" "postgres-ivfflat"
run_benchmark "portfolio_surreal_benchmark" "surrealdb"
run_benchmark "portfolio_qdrant_benchmark" "qdrant"

# Final Aggregated Report
echo "FINAL AGGREGATED REPORT"
docker run --rm -v $(pwd)/results.json:/app/results.json bench_runner python benchmark.py --report > test_execution_log.txt
cat test_execution_log.txt
