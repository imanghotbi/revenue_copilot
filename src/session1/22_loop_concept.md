## 7. 💻 Building the agent loop by hand — no framework

This is the section that makes the rest of the course make sense. We are going to
write an orchestrator in ~50 lines. Read the loop first; the code follows.

### 7.1 The loop, in pseudo-code

```
messages   = [system prompt, user task]
for step in 1..MAX_STEPS:                     # ← a limit. Always.
    response = model(messages, tool_schemas)  # the model reasons
    if response has no tool_calls:
        return response.text                  # ← done, this is the exit
    for call in response.tool_calls:          # the model acts
        result = run(call.name, call.args)    # YOUR python runs
        messages += [assistant(tool_calls), tool(result)]   # the model observes
raise RanOutOfSteps                            # ← never loop forever
```

Four things to notice:

1. **The exit condition is "the model stopped asking for tools."** That is what
   "done" means in an agent. There is no other signal.
2. **`messages` is the state.** Everything the agent knows is in that list. Every
   step appends to it, which is why long agent runs get expensive and eventually
   hit the context window.
3. **Your code executes the tools, not the model.** The model only *requests*.
   That is where you insert permission checks, validation and logging — Session 2.
4. **`MAX_STEPS` is not optional.** A model that keeps calling tools forever is a
   real failure mode. So is a model that calls a tool, misreads the result, calls
   it again with the same arguments, and loops. We will build both in §9.

### 7.2 Native tool calling vs. JSON prompting

There are two ways to get tool calls out of a model:

| | **Native tool calling** | **JSON prompting** |
|---|---|---|
| How | Pass `tools=` in the API request | Describe the tools in the prompt text, ask for JSON |
| Reliability | High — output is schema-constrained | Depends on the model; small models break JSON |
| Needs | A model that supports it | Nothing |
| Returned as | `message.tool_calls` | A string you must parse and validate |

Our `agent_loop` below implements **JSON prompting**, because it works with *any*
model — including the 0.5B one you loaded — and because seeing the parse step
makes the abstraction honest. In Session 2, LangChain uses native tool calling
when the provider supports it.

🧠 To prove that the *loop* is independent of the *model*, we will first drive it
with a scripted stub, then with a real API. Same orchestrator, different brain.
