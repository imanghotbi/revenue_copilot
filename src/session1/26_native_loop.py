# 💻 Native tool-calling loop. Same idea as agent_loop, different message shape.
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

def native_agent_loop(task, tools, llm, system_prompt, max_steps=12, verbose=True):
    """Run an agent that uses native tool_calls (the OpenAI/HF/Groq shape).

    tools          list of LangChain @tool functions
    llm            any LangChain chat model (mock, OpenRouter, Groq, HF, OpenAI)
    """
    if hasattr(llm, "reset"):
        llm.reset()
    bound = llm.bind_tools(tools)
    tool_map = {t.name: t for t in tools}
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=task)]

    for step in range(1, max_steps + 1):
        ai = bound.invoke(messages)
        messages.append(ai)
        calls = getattr(ai, "tool_calls", None) or []

        if not calls:                              # ← THE EXIT CONDITION, again
            if verbose:
                print(f"  step {step}: FINAL")
            return {"answer": ai.content, "messages": messages,
                    "steps": step, "status": "ok"}

        for tc in calls:
            name, args = tc["name"], tc.get("args") or {}
            tcid = tc.get("id", f"{name}_{step}")
            if name not in tool_map:
                observation = json.dumps({"error": f"unknown tool '{name}'",
                                          "available": sorted(tool_map)})
            else:
                try:
                    observation = tool_map[name].invoke(args)
                except Exception as exc:
                    observation = json.dumps({"error": f"{type(exc).__name__}: {exc}"})
            if verbose:
                preview = json.dumps(args, default=str)[:90]
                print(f"  step {step}: CALL {name}({preview})")
                print(f"           -> {str(observation)[:110]}")
            messages.append(ToolMessage(content=str(observation),
                                        tool_call_id=tcid, name=name))

    return {"answer": None, "messages": messages,
            "steps": max_steps, "status": "max_steps_exceeded"}


SYSTEM = (
    "You are Revenue Copilot, a sales analyst at Northwind Supply Co. "
    "Never invent a number: if you need a fact, call a tool. "
    "Quote policy by its KB id. You may draft email but you must never send it."
)

crm.reset_call_log()
llm = config.get_chat_model(verbose_mock=True)

print(f"model: {type(llm).__name__}")
print("=== RUN: native loop on C-1006 (Fjord Energi) ===")
native_result = native_agent_loop(
    task=("Customer C-1006 just emailed. How much revenue have they generated, "
          "should we be worried about losing them, and what does policy say we "
          "must do? Draft a recovery reply if needed."),
    tools=crm.ALL_TOOLS,
    llm=llm,
    system_prompt=SYSTEM,
    max_steps=12,
)

print("\n=== RESULT ===")
print("status:", native_result["status"], "| steps:", native_result["steps"])
print("\nFINAL ANSWER:\n")
print(native_result["answer"] or "(no final answer — hit max_steps)")
