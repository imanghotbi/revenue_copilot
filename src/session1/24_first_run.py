# 💻 Drive the framework loop with the offline mock to prove it works.
# The mock is deterministic: metrics -> tickets -> policy -> answer.
# The LOOP does not care how clever the model is — swap in a hosted model
# later and the graph is unchanged.

# Read-only tools: this agent can look, but it cannot write to the CRM.
# (§8 gets the full tool set, including writes.)
DEMO_TOOLS = [crm.account_metrics, crm.get_support_tickets, crm.search_knowledge_base]

llm_demo = config.get_chat_model(verbose_mock=True)
if hasattr(llm_demo, "reset"):
    llm_demo.reset()
crm.reset_call_log()

print("=== RUN: framework agent, 3 read tools (C-1006) ===")
demo_agent = make_agent(llm_demo, DEMO_TOOLS, SYSTEM_PROMPT)
result = demo_agent.invoke({
    "messages": [
        {"role": "user",
         "content": "How much revenue has C-1006 generated, and should we be worried about losing them?"},
    ]
})

print("\n=== RESULT ===")
print("messages in trace:", len(result.get("messages", [])))
print("\nFINAL ANSWER:\n" + last_text(result))
