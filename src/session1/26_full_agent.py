# 💻 Full agent on the real CRM — via create_agent (no hand-written loop).
# Derived from SYSTEM_PROMPT each run, so re-running this cell is safe.
SYSTEM = SYSTEM_PROMPT + " You may draft email but you must never send it."

crm.reset_call_log()
llm = config.get_chat_model(verbose_mock=True)

print(f"model: {type(llm).__name__}")
print("=== RUN: framework agent on C-1006 (Fjord Energi) ===")
agent = make_agent(llm, crm.ALL_TOOLS, SYSTEM)
native_result = agent.invoke({
    "messages": [
        {"role": "user",
         "content": ("Customer C-1006 (Fjord Energi) emailed — they may churn after "
                     "a late delivery complaint. How much revenue have they generated, "
                     "are they at risk, and what does service recovery policy require? "
                     "Draft a recovery reply if needed.")},
    ]
})

print("\n=== RESULT ===")
print("messages in trace:", len(native_result.get("messages", [])))
print("\nFINAL ANSWER:\n")
print(last_text(native_result) or "(no final answer)")
