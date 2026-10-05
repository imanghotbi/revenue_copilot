# 💻 Three failure modes, provoked on purpose — all through the framework.
import json

# --- 9.1 recursion_limit: a graph that never stops -------------------------
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.errors import GraphRecursionError

class LoopState(TypedDict):
    n: int

def bump(state: LoopState):
    return {"n": state["n"] + 1}

def keep_going(state: LoopState):
    return "bump" if state["n"] < 100 else END

loop = StateGraph(LoopState)
loop.add_node("bump", bump)
loop.add_edge(START, "bump")
loop.add_conditional_edges("bump", keep_going)

print("=== 9.1  a graph that never emits a final answer ===")
try:
    loop.compile().invoke({"n": 0}, {"recursion_limit": 4})
    print("unexpected: the loop was allowed to finish")
except GraphRecursionError as exc:
    print("stopped by recursion_limit (the framework max_steps):", type(exc).__name__)

# --- 9.2 hallucinated tool name: the framework refuses it -------------------
print("\n=== 9.2  a model that invents a tool name ===")
tool_map = {t.name: t for t in crm.ALL_TOOLS}
bad_name = "salesforce_query"
if bad_name not in tool_map:
    observation = json.dumps({"error": f"unknown tool '{bad_name}'",
                              "available": sorted(tool_map)})
    print("the error the model would see:", observation[:160], "...")
print("ToolNode / create_agent feed this back as an observation instead of crashing.")

# --- 9.3 context window growth ------------------------------------------------
print("\n=== 9.3  every tool result stays in the prompt forever ===")
msgs = native_result.get("messages", [])
chars = sum(len(str(getattr(m, "content", ""))) for m in msgs)
print(f"messages in the C-1006 run: {len(msgs)}")
print(f"characters sitting in the prompt: {chars:,}  (~{chars // 4:,} tokens)")
print("That cost is paid AGAIN on every subsequent step. Compact tool output is not a style choice.")
