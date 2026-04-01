#!/bin/bash
# RESTORED WORKING BENCHMARK SCRIPT
LOG_FILE="benchmark_results.log"
PROMPT="Write a comprehensive technical article about the evolution of Large Language Models from BERT to Llama 3.2, focusing on architectural breakthroughs and hardware optimization."

echo "--- STARTING REAL-TIME BENCHMARK SESSION: $(date) ---" > $LOG_FILE
echo "Architecture: $(uname -m)" >> $LOG_FILE
echo "" >> $LOG_FILE

# 1. OLLAMA TEST (Capturing raw verbose output)
echo "--- TEST 1: OLLAMA (GGUF) ---" >> $LOG_FILE
ollama run llama3.2:1b --verbose "$PROMPT" 2>&1 | sed -e 's/\x1b\[[0-9;?]*[a-zA-Z]//g' | grep -E "total duration|load duration|prompt eval rate|eval rate|eval count" >> $LOG_FILE
echo "" >> $LOG_FILE

# 2. MLX NATIVE TEST
echo "--- TEST 2: MLX NATIVE (MLX-FORMAT) ---" >> $LOG_FILE
source ~/AI_MLX/.venv/bin/activate
python3 benchmark_mlx_native.py >> $LOG_FILE

echo "" >> $LOG_FILE
echo "--- BENCHMARK SESSION COMPLETED ---" >> $LOG_FILE
