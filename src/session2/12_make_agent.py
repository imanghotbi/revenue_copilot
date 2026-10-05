# 💻 One factory that works on LangChain 1.x and on the older prebuilt helper.
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


SYSTEM = (
    "You are Revenue Copilot at Northwind Supply Co. "
    "Never invent a number or a delivery date: call a tool. "
    "Cite policy by KB id. Draft email, never send it."
)

print("make_agent and last_text defined.")
