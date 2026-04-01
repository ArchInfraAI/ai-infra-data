#!/bin/bash
# FINAL PARITY BENCHMARK: GEMMA 4 DENSE (3-BIT) VS MOE (3-BIT)
# Platform: Apple Silicon M1 Pro (16GB RAM)
# Methodology: 1000-token technical generation, isolated loading.

LOG_FILE="gemma4_comparison.log"
PROMPT="Write a detailed technical article about the future of decentralized AI infrastructure cluster management."

echo "--- STARTING PARITY BENCHMARK SESSION: $(date) ---" > $LOG_FILE
echo "Platform: Apple Silicon M1 Pro (16GB Unified Memory)" >> $LOG_FILE
echo "Quantization Parity: Both models are 3-bit (Q3_K_M / IQ3_S)" >> $LOG_FILE
echo "" >> $LOG_FILE

function run_managed_test {
    MODEL=$1
    LABEL=$2
    
    echo "Processing $LABEL..."
    echo "--- $LABEL ---" >> $LOG_FILE
    
    # 1. WARM-UP (Load into RAM)
    ollama run $MODEL "Warm up." > /dev/null 2>&1
    sleep 3
    
    # 2. CAPTURE RUNTIME MEMORY
    echo "Runtime Memory State:" >> $LOG_FILE
    ollama ps >> $LOG_FILE
    
    # 3. CORE INFERENCE (1000 Tokens)
    ollama run $MODEL --verbose "$PROMPT" 2>&1 | sed -e 's/\x1b\[[0-9;?]*[a-zA-Z]//g' | grep -E "eval count|eval rate|total duration" >> $LOG_FILE
    
    # 4. STOP
    ollama stop $MODEL
    sleep 2
    echo "" >> $LOG_FILE
}

# 1. RUN DENSE 3-BIT TEST
run_managed_test "gemma-4-e4b-it-Q3_K_M" "GEMMA 4 E4B (DENSE 3-BIT)"

# 2. RUN MOE 3-BIT TEST
run_managed_test "gemma-4-26B-A4B-it-UD-IQ3_S" "GEMMA 4 26B-A4B (MOE 3-BIT)"

echo "--- BENCHMARK SESSION COMPLETED ---" >> $LOG_FILE
