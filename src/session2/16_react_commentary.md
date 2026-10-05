🧠 `tools_condition` is the exit condition from Session 1, as a library
function: *if the last message has `tool_calls`, go to the tools node,
otherwise END.*

`add_messages` is a **reducer**: when a node returns `{"messages": [new]}`,
LangGraph *appends* instead of replacing. That is how the conversation
accumulates. Keys without a reducer are overwritten.

Read-only tools on purpose. C-1011 (Kite Media) is a briefing, not a write.
The next graph is where we let the system act — behind a gate.

---

### 4.1 The workflow we actually ship

```
                    ┌─ grade D / not qualified ──► self_serve ──► END
                    │
 START ► load_lead ► qualify ► route
                    │
                    └─ otherwise ──► researcher (agent, READ tools)
                                          │
                                          ▼
                                     approve  ← human interrupt
                                          │
                          ┌── yes ──► commit writes ──► END
                          └── no ───► reject ────────► END
```

`qualify` is Python calling `score_lead`. Pixel & Pine never reaches the
model. That is not a fallback. That is the design.
