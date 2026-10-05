## 8. 💻 First working agent on the real CRM

The read-only run in §7 proved the *orchestrator*. Now we give it the full CRM
tool set and a real brain — or the offline mock, which speaks the same
LangChain language (`invoke(messages) -> AIMessage` with `tool_calls`).

The cell below is **not** a hand-written loop. It is LangChain's `create_agent`
(model node + `ToolNode`, exit when there are no more `tool_calls`) — the same
object Session 2 builds on for routing, approval gates and memory. Once you can
read this trace, those graphs stop being magic.

We will run it on **Fjord Energi (C-1006)** — the angry customer with the 110-day
ticket. The agent is allowed the full CRM tool set.
