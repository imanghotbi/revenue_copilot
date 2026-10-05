# 💻 One client interface, two back-ends: hosted HF model, or offline mock.
#
# `InferenceClient` speaks the OpenAI-compatible chat API, and the SAME code
# works whichever provider HF routes you to (Groq, Cerebras, Together, ...).
# When there is no HF_TOKEN we build a mock object with the identical surface,
# so the rest of the notebook is unchanged.

class _MockMessage:
    def __init__(self, content): self.content, self.role, self.tool_calls = content, "assistant", None

class _MockChoice:
    def __init__(self, content): self.message, self.finish_reason = _MockMessage(content), "stop"

class _MockUsage:
    prompt_tokens, completion_tokens, total_tokens = 120, 60, 180

class _MockResponse:
    def __init__(self, content):
        self.choices = [_MockChoice(content)]
        self.usage = _MockUsage()
        self.model = "mock-sales-analyst-v1"

class MockInferenceClient:
    """Stand-in for huggingface_hub.InferenceClient with the same .chat() shape."""
    def __init__(self, model="mock"): self.model = model
    def chat(self, messages, **kwargs):
        last = messages[-1]["content"] if messages else ""
        return _MockResponse(
            "[OFFLINE MOCK - no HF_TOKEN was found, so no real model was called.]\n"
            f"You asked: {last[:180]!r}\n\n"
            "With a real model you would get a fluent answer here. Add a free "
            "OPENROUTER_API_KEY or HF_TOKEN in Colab's Secrets panel and re-run "
            "the setup cell to switch this notebook to a live model. Everything "
            "that follows - tools, the agent loop, state, graphs - works "
            "identically in mock mode, which is the point of having it."
        )

hf_token = config.get_secret("HF_TOKEN")
if hf_token:
    from huggingface_hub import InferenceClient
    client = InferenceClient(model=config.HF_MODEL, provider=config.HF_PROVIDER, token=hf_token)
    print(f"Using Hugging Face Inference Providers -> model '{config.HF_MODEL}'")
else:
    client = MockInferenceClient()
    print("No HF_TOKEN -> using MockInferenceClient (offline). Add a key to go live.")


def ask(prompt, system="You are a concise sales analyst at Northwind Supply Co.", max_tokens=400):
    """The simplest possible 'call a model' function. We will replace this with
    a LangChain chat model in Session 2 - notice how much this hides."""
    t0 = time.time()
    resp = client.chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    dt = time.time() - t0
    text = resp.choices[0].message.content
    print(f"[{dt:.1f}s | {getattr(resp, 'model', '?')}]")
    return text


print()
print(ask("In two sentences, what does a sales operations team do all day that a computer could do instead?"))
