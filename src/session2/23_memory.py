# 💻 Same thread_id = the second turn can see the first. A new id starts blank.
mem_model = config.get_chat_model(verbose_mock=False)
mem_model.bind_tools(crm.READ_TOOLS)

def _call(state):
    return {"messages": [mem_model.bind_tools(crm.READ_TOOLS).invoke(state["messages"])]}

mg = StateGraph(AgentState)
mg.add_node("model", _call)
mg.add_node("tools", ToolNode(crm.READ_TOOLS))
mg.add_edge(START, "model")
mg.add_conditional_edges("model", tools_condition)
mg.add_edge("tools", "model")
mem_graph = mg.compile(checkpointer=InMemorySaver())

thread = {"configurable": {"thread_id": "rep-sofia-fjord"}}
crm.reset_call_log()
mem_graph.invoke({
    "messages": [
        SystemMessage(content=SYSTEM),
        HumanMessage(content="Brief me on customer C-1006. Use tools. Mention the open ticket."),
    ]
}, config=thread)

turn2 = mem_graph.invoke({
    "messages": [HumanMessage(content="What was the open ticket id you just found?")],
}, config=thread)

snapshot = mem_graph.get_state(thread)
stored = snapshot.values["messages"]
blob = " ".join(str(getattr(m, "content", "")) for m in stored)
print(f"messages stored on thread 'rep-sofia-fjord': {len(stored)}")
print("roles:", [getattr(m, "type", "?") for m in stored])
print("ticket T-9001 still in the thread:", "T-9001" in blob)
print("\nsecond-turn answer:\n")
print(last_text(turn2)[:800])
print("\nA new thread_id would start from zero. The checkpointer is the memory.")
