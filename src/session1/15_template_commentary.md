🧠 **Read the output above carefully — this is the most important observation in
Session 1.**

**In (A)** the model had no way to know anything about customer `C-1006`. It does
not exist in its training data. So what did it do? It answered *confidently
anyway*, with a plausible-sounding revenue figure. That is a hallucination, and
in a business setting it is not a curiosity — it is a number a colleague might
put in a forecast.

**In (B)** the same model was shown a `<tools>` block. Now it has an escape hatch
from its own ignorance: instead of inventing a figure it can emit a
`<tool_call>` asking for the real one.

> **This is the entire value proposition of an agent, in one picture:**
> tools convert *confident invention* into *verifiable lookup*.

Two more things worth noticing:

- The tool schema is **just text in the prompt**. "Function calling" sounds like a
  special capability; at the bottom it is the model being trained to emit a
  predictable JSON shape when it sees a `<tools>` block.
- A 0.5B model is often **too weak to do this reliably**. It may ignore the tools,
  emit malformed JSON, or invent arguments. That is not a bug in your code, it is
  a property of small models — and it is exactly why, in section 5, we move to a
  bigger model for the real work, and why, in Session 2, frameworks add parsing,
  retries and validation around the loop.
