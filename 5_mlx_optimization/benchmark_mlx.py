import time
import mlx.core as mx
from mlx_lm import load, generate

def run_performance_test(model_id):
    print(f"\n🚀 STARTING MLX INFERENCE BENCHMARK")
    print(f"Model: {model_id}")
    print("-" * 40)
    
    # 1. Load Model & Tokenizer
    start_load = time.time()
    model, tokenizer = load(model_id)
    load_time = time.time() - start_load
    print(f"✅ Model loaded in {load_time:.2f}s")

    # 2. Warm-up (Critical for GPU profiling)
    print("🔄 Warming up GPU kernels...")
    generate(model, tokenizer, prompt="Warm up", max_tokens=1)

    # 3. Benchmark Run
    prompt = "Write a technical summary of why Unified Memory architecture is superior for LLM inference."
    max_tokens = 150
    
    print(f"⚡ Generating {max_tokens} tokens...")
    start_gen = time.time()
    response = generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens)
    gen_time = time.time() - start_gen
    
    # 4. Metrics Calculation
    tps = max_tokens / gen_time
    peak_mem = mx.metal.get_active_memory() / 1024**2
    
    print("\n--- PERFORMANCE METRICS ---")
    print(f"📊 Speed: {tps:.2f} tokens/second")
    print(f"⏱️ Total Time: {gen_time:.2f}s")
    print(f"🧠 Peak Memory: {peak_mem:.2f} MB")
    print("-" * 40)
    print(f"\nSample Response Peek: {response[:100]}...")

if __name__ == "__main__":
    MODEL = "mlx-community/Llama-3.2-1B-Instruct-4bit"
    try:
        run_performance_test(MODEL)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please ensure 'mlx-lm' is installed: pip install mlx-lm")
