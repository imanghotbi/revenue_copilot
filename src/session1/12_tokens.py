# 💻 A 12-line generation helper. This is the whole "LLM API" at its simplest.
def local_generate(messages, max_new_tokens=128, temperature=0.0, show_prompt=False):
    """Run the local model on a list of chat messages and return its text."""
    if local_llm is None:
        return "[local model not loaded - set USE_LOCAL_MODEL = True and re-run the cells above]"
    import torch

    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_tensors="pt", return_dict=True,
    ).to(local_llm.device)

    if show_prompt:
        print("=== EXACT TEXT THE MODEL RECEIVES ===")
        print(tokenizer.decode(inputs["input_ids"][0]))
        print("=== end ===\n")

    t0 = time.time()
    with torch.no_grad():
        out = local_llm.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0,
            temperature=temperature if temperature > 0 else None,
            pad_token_id=tokenizer.eos_token_id,
        )
    dt = time.time() - t0
    new_tokens = out.shape[1] - inputs["input_ids"].shape[1]
    text = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    print(f"[{new_tokens} tokens in {dt:.1f}s = {new_tokens/dt:.1f} tok/s]")
    return text


# 🧠 Tokens are not words. This is why your API bill is measured in tokens.
sentence = "Acme Corp wants 50 ergonomic chairs for their Berlin office."
ids = tokenizer.encode(sentence) if tokenizer else list(range(14))
print(f"characters: {len(sentence)}")
print(f"tokens:     {len(ids)}")
if tokenizer:
    print("pieces:    ", [tokenizer.decode([i]) for i in ids])
print("""
Rule of thumb for English: 1 token ≈ 4 characters ≈ 0.75 words.
A 200-token tool result costs you ~200 tokens of context window every single
time it appears in the history - which is why tool outputs should be compact.""")
