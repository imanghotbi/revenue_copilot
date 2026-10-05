# 💻 bind_tools does not call anything. It only advertises the schema.
crm.reset_call_log()

bound = llm.bind_tools(crm.READ_TOOLS)
print("bound model:", type(bound).__name__)
print("the model has been shown", len(crm.READ_TOOLS), "read tools")
print("first tool schema the model sees:")
print(json.dumps(crm.READ_TOOLS[0].args, indent=2)[:400])

print("\n=== invoke WITH tools bound, asking about C-1006 ===")
ai = bound.invoke([
    SystemMessage(content="You are Revenue Copilot. Never invent a number; call a tool."),
    HumanMessage(content="What is the churn risk of customer C-1006?"),
])
print("content:   ", (ai.content or "")[:180] or "(empty — the model asked for a tool instead of talking)")
print("tool_calls:", json.dumps(getattr(ai, "tool_calls", None) or [], default=str)[:400])
