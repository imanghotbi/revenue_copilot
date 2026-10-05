If you ran Session 1's `native_agent_loop` on the same question, the trace
should look familiar. `create_agent` did not invent a new kind of intelligence.
It compiled your loop into a **graph** with two nodes — `model` and `tools` —
and an edge that says *if there are tool_calls, go to tools, else stop*.

We are going to build that graph by hand next, because that is how you add
the things `create_agent` does not give you: a router in front, a human gate
on writes, and a path that never calls the model at all.

⚠️ **Trap — `create_agent` is not "production."** It is a very good default
ReAct loop. Production is the workflow you wrap *around* it.

---

## 4. 💻 LangGraph: state, nodes, edges

LangGraph models a system as three things:

| Piece | Meaning | In Revenue Copilot |
|---|---|---|
| **State** | The snapshot the system carries | messages, lead id, score, route, approval |
| **Node** | A function `state -> update` | `qualify`, `agent`, `approve`, `commit` |
| **Edge** | What runs next | `if grade == "D": self_serve else agent` |

Nodes can contain an LLM. They can also contain an `if` statement. Mixing the
two is the point.

We will build two graphs:

1. A **ReAct graph** that is Session 1's loop, drawn as nodes. (~15 lines)
2. A **lead-triage workflow** with a deterministic router and one agentic
   step inside it. That is the thing we ship.
