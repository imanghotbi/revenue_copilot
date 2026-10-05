# 💻 Drive the loop with a scripted "model" to prove the orchestration works.
# The stub below is deliberately dumb: it replays a plan. That is the point -
# the LOOP does not care how clever the model is.
PLAN = [
    {"thought": "I need the real numbers, not a guess.",
     "tool": "account_metrics", "args": {"customer_id": "C-1006"}},
    {"thought": "Risk is high - I should read the open ticket before writing anything.",
     "tool": "get_support_tickets", "args": {"customer_id": "C-1006", "status": "open"}},
    {"thought": "Policy says what exactly? Check the handbook.",
     "tool": "search_knowledge_base", "args": {"query": "service recovery late delivery credit note"}},
    {"thought": "I now have the facts and the policy. I can answer.",
     "final_answer": "Fjord Energi (C-1006) has generated EUR 8,260.80 across 2 orders. "
                     "Yes, we should be worried: churn risk is 72/100 (high) because the CRM "
                     "health flag is red and ticket T-9001 has been open for 110 days. "
                     "Policy KB-03 requires a credit note of 15% (delay over 20 working days), "
                     "a named delivery coordinator for the next two orders, and an account "
                     "manager call within 5 working days."},
]

class ScriptedModel:
    """A fake model that replays PLAN, one step per call."""
    def __init__(self, plan): self.plan, self.i = plan, 0
    def __call__(self, messages):
        item = self.plan[min(self.i, len(self.plan) - 1)]
        self.i += 1
        return json.dumps(item)

# The subset of tools this agent is allowed to use, as plain callables.
TOOL_FUNCTIONS = {
    "account_metrics": lambda customer_id: crm.account_metrics.invoke({"customer_id": customer_id}),
    "get_support_tickets": lambda customer_id="", status="": crm.get_support_tickets.invoke(
        {"customer_id": customer_id, "status": status}),
    "search_knowledge_base": lambda query: crm.search_knowledge_base.invoke({"query": query}),
}
def _schema(name, description, **props):
    """A tiny helper to write a schema inline. (make_schema() above does the
    same job from type hints - this one is more explicit for teaching.)"""
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object",
                       "properties": {k: {"type": v} for k, v in props.items()},
                       "required": list(props)}}}

SCHEMAS = [
    _schema("account_metrics", "Return revenue, order count and churn risk for one customer.",
            customer_id="string"),
    _schema("get_support_tickets", "List support tickets for a customer.",
            customer_id="string", status="string"),
    _schema("search_knowledge_base", "Search the internal sales policy handbook.", query="string"),
]

SYSTEM_PROMPT = (
    "You are Revenue Copilot, a sales analyst at Northwind Supply Co. "
    "Never invent a number: if you need a fact, call a tool. "
    "Quote policy by its KB id when you rely on it."
)

print("=== RUN: scripted model, 3 tools ===")
result = agent_loop(
    task="How much revenue has C-1006 generated, and should we be worried about losing them?",
    schemas=SCHEMAS,
    tool_functions=TOOL_FUNCTIONS,
    call_model=ScriptedModel(PLAN),
    system_prompt=SYSTEM_PROMPT,
    max_steps=6,
)

print("\n=== RESULT ===")
print("status:", result["status"], "| steps used:", result["steps"])
print("\nFINAL ANSWER:\n" + result["answer"])
