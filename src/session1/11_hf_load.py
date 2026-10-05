# 💻 Download and load a small model locally.
# First run: ~1 GB download. Later runs: loads from cache in seconds.
import time

local_llm = None
tokenizer = None

if USE_LOCAL_MODEL:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        print(f"Could not import torch/transformers ({exc}). Skipping the local model.")
        print("Install with:  pip install 'transformers>=4.51' accelerate torch")
        USE_LOCAL_MODEL = False

if USE_LOCAL_MODEL:
    MODEL_ID = config.LOCAL_MODEL_ID          # "Qwen/Qwen2.5-0.5B-Instruct"

    # A GPU is a luxury here, not a requirement. Colab free tier = CPU is fine.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    print(f"device: {device}   dtype: {dtype}   model: {MODEL_ID}")

    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    local_llm = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=dtype).to(device)
    local_llm.eval()
    print(f"loaded in {time.time() - t0:.1f}s")

    n_params = sum(p.numel() for p in local_llm.parameters())
    bytes_per_param = next(local_llm.parameters()).element_size()   # 4 = float32, 2 = bfloat16
    print(f"parameters:    {n_params/1e6:.1f}M")
    print(f"RAM for weights: ~{n_params * bytes_per_param / 1e6:.0f} MB")
    # Note the two different numbers below - this trips people up.
    print(f"vocab_size:    {tokenizer.vocab_size:,}   (words/pieces the model was trained on)")
    print(f"len(tokenizer): {len(tokenizer):,}   (+ special tokens like <|im_start|>)")
    print(f"embedding rows: {local_llm.get_input_embeddings().weight.shape[0]:,}   "
          f"<- must match len(tokenizer), not vocab_size")
else:
    print("USE_LOCAL_MODEL is False - skipping the local model. "
          "Everything below has an offline fallback.")
