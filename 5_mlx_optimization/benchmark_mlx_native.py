import time
import mlx.core as mx
from mlx_lm import load, generate

def run_mlx_professional_test():
    model_id = "mlx-community/Llama-3.2-1B-Instruct-4bit"
    print(f"--- MLX Professional Profiling (Llama 3.2 1B) ---")
    
    model, tokenizer = load(model_id)
    prompt = "Write a comprehensive technical article about the evolution of Large Language Models from BERT to Llama 3.2, focusing on architectural breakthroughs and hardware optimization."
    
    # Target 1000 tokens for precise throughput measurement
    target_tokens = 1000
    
    # Warm-up run
    generate(model, tokenizer, prompt="Hi", max_tokens=1)
    
    # Actual measurement
    start_gen = time.time()
    response = generate(model, tokenizer, prompt=prompt, max_tokens=target_tokens)
    total_duration = time.time() - start_gen
    
    # Token count calculation
    tokens = len(tokenizer.encode(response))
    tps = tokens / total_duration
    
    # OUTPUT FORMAT MATCHING OLLAMA LOGS
    print(f"eval count:           {tokens} tokens")
    print(f"eval rate:            {tps:.2f} tokens/s")
    print(f"total duration:       {total_duration:.3f}s")
    print(f"Peak Memory:          {mx.get_active_memory() / 1024**2:.2f} MB")
    print("-" * 50)

if __name__ == "__main__":
    run_mlx_professional_test()
