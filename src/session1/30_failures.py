# 💻 Three failure modes, provoked on purpose.

# --- 9.1 max_steps: a "model" that never stops calling tools ---------------
class NeverDone:
    def __call__(self, messages):
        return json.dumps({"thought": "one more lookup",
                           "tool": "account_metrics",
                           "args": {"customer_id": "C-1006"}})

print("=== 9.1  a model that never emits final_answer ===")
stuck = agent_loop(
    task="How is C-1006 doing?",
    schemas=SCHEMAS,
    tool_functions=TOOL_FUNCTIONS,
    call_model=NeverDone(),
    system_prompt=SYSTEM_PROMPT,
    max_steps=3,
)
print("status:", stuck["status"], "| steps:", stuck["steps"])
print("answer is None, as it should be:", stuck["answer"] is None)

# --- 9.2 hallucinated tool name -------------------------------------------
class InventedTool:
    def __call__(self, messages):
        n_user = sum(1 for m in messages if m["role"] == "user")
        if n_user == 1:
            return json.dumps({"thought": "I'll just query Salesforce",
                               "tool": "salesforce_query",
                               "args": {"soql": "SELECT Id FROM Account"}})
        return json.dumps({"thought": "ok, I'll use a real tool",
                           "final_answer": "Recovered: used only tools I actually have."})

print("\n=== 9.2  a model that invents a tool name ===")
recovered = agent_loop(
    task="How is C-1006 doing?",
    schemas=SCHEMAS,
    tool_functions=TOOL_FUNCTIONS,
    call_model=InventedTool(),
    system_prompt=SYSTEM_PROMPT,
    max_steps=4,
)
print("status:", recovered["status"])
print("the error the model saw:", recovered["trace"][0]["observation"][:120], "...")

# --- 9.3 context window growth --------------------------------------------
print("\n=== 9.3  every tool result stays in the prompt forever ===")
chars = sum(len(str(getattr(m, "content", ""))) for m in native_result["messages"])
print(f"messages in the C-1006 run: {len(native_result['messages'])}")
print(f"characters sitting in the prompt: {chars:,}  (~{chars // 4:,} tokens)")
print("That cost is paid AGAIN on every subsequent step. Compact tool output is not a style choice.")
