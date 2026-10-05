🧠 **Read that output twice.** `bind_tools` did not run `account_metrics`. It
told the model the tool *existed*. The model then *requested* a call. Your code
still has to execute it and feed the result back — which is exactly the loop
from Session 1.

That request/execute split is the whole security model. The weights cannot
touch the CRM. Only the Python you write after `tool_calls` can.

---

## 3. 💻 `create_agent`: the loop, packaged

LangChain 1.0's `create_agent(model, tools, system_prompt=...)` is Session 1's
`native_agent_loop`, with retries, tracing hooks and a LangGraph runtime
underneath.

If an older LangChain is installed, the cell falls back to
`langgraph.prebuilt.create_react_agent`. Same idea, slightly different
argument names. You should not have to care: `make_agent()` hides it.
