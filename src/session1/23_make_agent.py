# 💻 THE AGENT LOOP, via the framework.
# LangChain's create_agent IS the loop from §2 — model node <-> tools node,
# with retries, tracing hooks and a LangGraph runtime underneath.
# Everything else in this course is a hardened version of THIS call.

def make_agent(model, tools, system_prompt, checkpointer=None):
    """Return a compiled agent graph. Prefer LangChain 1.0 create_agent."""
    try:
        from langchain.agents import create_agent
        kwargs = dict(model=model, tools=tools, system_prompt=system_prompt)
        if checkpointer is not None:
            kwargs["checkpointer"] = checkpointer
        agent = create_agent(**kwargs)
        print("using langchain.agents.create_agent")
        return agent
    except ImportError:
        from langgraph.prebuilt import create_react_agent
        kwargs = dict(model=model, tools=tools, prompt=system_prompt)
        if checkpointer is not None:
            kwargs["checkpointer"] = checkpointer
        agent = create_react_agent(**kwargs)
        print("using langgraph.prebuilt.create_react_agent (older install)")
        return agent


def last_text(result) -> str:
    """Pull the final assistant text out of an agent result dict."""
    messages = result.get("messages", []) if isinstance(result, dict) else []
    for m in reversed(messages):
        content = getattr(m, "content", None)
        if content and getattr(m, "type", "") == "ai" and not getattr(m, "tool_calls", None):
            return content
    if messages:
        return str(getattr(messages[-1], "content", messages[-1]))
    return str(result)


SYSTEM_PROMPT = (
    "You are Revenue Copilot, a sales analyst at Northwind Supply Co. "
    "Never invent a number: if you need a fact, call a tool. "
    "Quote policy by its KB id when you rely on it."
)
SYSTEM = SYSTEM_PROMPT  # alias so later cells can use either name

print("make_agent + last_text defined.")
print("Three exits in framework terms: no tool_calls (END), "
      "unparsable/invalid call (error fed back, retry), recursion_limit exceeded.")
