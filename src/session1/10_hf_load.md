## 3. 💻 Loading a model from Hugging Face

Before we let a model act on a business, let us look at what a model actually
*is*. We will download a real one — `Qwen/Qwen2.5-0.5B-Instruct`, about
**494 million parameters, ~1 GB on disk** — and run it on this machine.

Why start tiny and local?

1. It is **free** and it is **yours**: no key, no rate limit, no bill, no data
   leaving the machine.
2. It is **small enough to see**. You can print the whole prompt the model
   receives, which is exactly what you need to understand tool calling later.
3. It is **deliberately too weak for the job**, and that failure is the most
   useful thing in this session. A 0.5B model will happily invent a customer's
   revenue. Watching it do that teaches you why agents need tools.

⚠️ **Trap:** `Instruct` / `Chat` models are not the same as their base versions.
`Qwen2.5-0.5B` answers by *continuing* your text. `Qwen2.5-0.5B-Instruct` has
been fine-tuned to follow the chat format and obey instructions. For agents you
always want the instruct/chat variant, and ideally one whose model card says it
supports **function calling**.

The next cell downloads the model on first run (~1 GB, a minute or two), then
caches it in `~/.cache/huggingface` so later runs are instant.
