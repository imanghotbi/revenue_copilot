# 💻 Session 1's native_agent_loop, redrawn as a LangGraph StateGraph.
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def make_react_graph(model, tools):
    """model node <-> tools node, until the model stops calling tools."""
    if hasattr(model, "reset"):
        model.reset()
    bound = model.bind_tools(tools)

    def call_model(state: AgentState):
        return {"messages": [bound.invoke(state["messages"])]}

    g = StateGraph(AgentState)
    g.add_node("model", call_model)
    g.add_node("tools", ToolNode(tools))
    g.add_edge(START, "model")
    g.add_conditional_edges("model", tools_condition)   # -> "tools" or END
    g.add_edge("tools", "model")
    return g.compile()


react = make_react_graph(config.get_chat_model(verbose_mock=True), crm.READ_TOOLS)
print(react)

print("\n=== RUN: read-only ReAct graph on C-1011 (Kite Media, also at risk) ===")
crm.reset_call_log()
react_out = react.invoke({
    "messages": [
        SystemMessage(content=SYSTEM),
        HumanMessage(content="Give me a churn briefing on customer C-1011. Use tools."),
    ]
})
print(last_text({"messages": react_out["messages"]}))
print("\ntools used:", [r["tool"] for r in crm.CALL_LOG])
