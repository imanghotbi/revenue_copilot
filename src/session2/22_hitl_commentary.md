🧠 What you should have seen:

- Fjord paused, you approved, a **pipeline record** appeared and (because they
  are already a customer) a **CRM note** was logged on C-1006.
- Cascade paused, you rejected, `committed` is empty and the brief ends with
  `[writes blocked by human]`.
- Pixel & Pine, if you ran them through this graph, would **not** pause: the
  router sent them to `self_serve` and ended. A gate you never reach is not a
  gate. That is why the router exists.

⚠️ **Trap — approving the model is not the same as approving the action.**
The interrupt payload shows a *preview* of the brief. In a real UI you would
also show the exact tool arguments (quote lines, discount, recipient) and let
the human edit them. `Command(resume=...)` can carry that edited payload; the
node decides what to do with it.

---

## 6. 🧠 Memory that survives a turn

Inside one run, memory is the message list. Across runs — "the rep closed the
laptop and opened it again" — you need the checkpointer plus the same
`thread_id`.

Short-term memory (this section) is the graph state for one thread.
Long-term memory (a vector store of every email ever) is a tool you add later,
the same way `search_knowledge_base` is a tool. Do not stuff last quarter's
CRM into the prompt.
