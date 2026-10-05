## 7. 💻 The agent loop, via the framework

This is the section that makes the rest of the course make sense. The loop is
the same one from §2 — model reasons, tools act, results feed back — but we run
it with **LangChain / LangGraph**, not with hand-written JSON parsing.

### 7.1 The loop, in pseudo-code

```
messages   = [system prompt, user task]          # the state
for step in 1..MAX_STEPS:                       # ← a limit. Always.
    response = bound_model.invoke(messages)     # the model reasons (bind_tools)
    if response has no tool_calls:
        return response.text                    # ← done, this is the exit
    for call in response.tool_calls:            # the model acts
        result = run_tool(call.name, call.args)   # ToolNode executes it
        messages += [assistant(tool_calls), tool(result)]  # the model observes
raise recursion_limit exceeded                  # ← never loop forever
```

Four things to notice:

1. **The exit condition is "the model stopped asking for tools."** That is what
   "done" means in an agent. There is no other signal. In LangGraph this is
   `tools_condition`: tool calls → tools node, otherwise END.
2. **`messages` is the state.** Everything the agent knows is in that list. Every
   step appends to it, which is why long agent runs get expensive and eventually
   hit the context window. LangGraph stores it with the `add_messages` reducer.
3. **Your code executes the tools, not the model.** The model only *requests*.
   `bind_tools` advertises the schemas; `ToolNode` (or `create_agent`) runs
   them. That is where you insert permission checks, validation and logging —
   Session 2.
4. **`MAX_STEPS` / `recursion_limit` is not optional.** A model that keeps calling
   tools forever is a real failure mode. So is a model that calls a tool,
   misreads the result, calls it again with the same arguments, and loops. We
   will provoke both in §9.

### 7.2 Native tool calling (the only path in this course)

Production APIs return tool requests as a structured `tool_calls` list on the
message — not as a JSON string you parse. LangChain's `bind_tools` sends the
schemas with the request, and the provider does the parsing for you.

🧠 `create_agent(model, tools, system_prompt=...)` below *is* the loop above,
with retries, tracing hooks and a LangGraph runtime underneath. Same
orchestrator, different brain: swap the mock model for a hosted one and nothing
else changes.
