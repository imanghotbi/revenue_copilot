# 💻 Same Fjord Energi question as Session 1, now through create_agent.
if hasattr(llm, "reset"):
    llm.reset()
crm.reset_call_log()

analyst = make_agent(llm, crm.ALL_TOOLS, SYSTEM)

fjord = analyst.invoke({
    "messages": [
        {"role": "user",
         "content": ("Customer C-1006 (Fjord Energi) emailed. Are they at risk of "
                     "churn, what does policy require, and draft a recovery reply.")}
    ]
})

print("\n=== FINAL ANSWER ===\n")
print(last_text(fjord))
print("\n=== tool-call log ===")
log = crm.call_log_frame()
if len(log):
    print(log[["n", "tool", "writes"]].to_string(index=False))
else:
    print("(no tools recorded)")
