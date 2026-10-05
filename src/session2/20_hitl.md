## 5. 🧠 Guardrails and human-in-the-loop

The workflow above *reads* freely and *writes* nothing except the self-serve
draft (and `draft_email` never sends — look at `"sent": false` in its output).

That is not enough. A qualified lead should land in the pipeline, and an angry
account should get a logged note. Those are real CRM writes. The rule:

> **The model may propose a write. A human approves it. Python performs it.**

LangGraph's `interrupt()` pauses the graph, saves state, and waits. You resume
with `Command(resume=...)`. Three things are required:

1. a **checkpointer** (here, in-memory; in production, a database)
2. a stable **`thread_id`** so the runtime knows which run to resume
3. the call to `interrupt()` *before* the write, not after

⚠️ **Trap.** On resume, the node that called `interrupt()` **starts over from
the top**. Anything before the `interrupt()` line runs twice. Put side effects
*after* the pause.
