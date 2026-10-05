## 5. 🔑 A capable model: Hugging Face Inference Providers

A 0.5B model is a teaching instrument, not a production component. For the rest
of the course we need a model that can follow instructions and emit valid JSON
*reliably*. There are three ways to get one, and you should understand the
trade-off:

| Option | Cost | Latency | Data leaves your machine | Good for |
|---|---|---|---|---|
| **Local small model** (§3) | free | slow on CPU | no | learning, offline demos, sensitive data |
| **Hosted API** (this section) | free tier → cheap | fast | yes | everything else |
| **Local big model** (Ollama, llama.cpp, vLLM) | your hardware | medium | no | privacy, on-prem, no rate limits |

### Which hosted provider?

This course is built to run on **free tiers**. Set up one of these and put the key
in Colab's 🔑 **Secrets** panel (never in a cell — a shared notebook leaks it):

| Provider | Key name | Free? | Notes |
|---|---|---|---|
| **[OpenRouter](https://openrouter.ai)** | `OPENROUTER_API_KEY` | genuinely free models | one key, hundreds of models. **Recommended.** |
| **[Groq](https://console.groq.com)** | `GROQ_API_KEY` | free tier, very fast | great for live demos |
| **[Hugging Face](https://huggingface.co/settings/tokens)** | `HF_TOKEN` | $0.10/month of credit on free accounts | one token for models *and* datasets |
| **[OpenAI](https://platform.openai.com)** | `OPENAI_API_KEY` | no free tier | the default in most tutorials |

🧠 **Worth knowing:** Hugging Face's old "free Inference API" became **Inference
Providers** — your requests are routed to Cerebras, Groq, Together, Fireworks,
etc. Free accounts get **$0.10 of credit per month**, PRO accounts $2.00. That is
plenty for a class if you keep outputs short, but it is *credit*, not unlimited.

**And the safety net:** if no key is found, `config.get_chat_model()` returns the
offline `MockSalesLLM`, so every cell in both notebooks still runs. You will see
`>>> Active provider: mock` above if that is what happened. The graphs, tools and
state management are identical; only the "thinking" is scripted.
