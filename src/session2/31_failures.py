# 💻 Three limits, demonstrated rather than described.
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
try:
    loop.compile().invoke({"n": 0}, {"recursion_limit": 4})
    print("unexpected: the loop was allowed to finish")
except GraphRecursionError as exc:
    print("9.1 recursion_limit stopped a runaway graph:", type(exc).__name__)

# 9.2 A rule the model must not talk its way around.
print("\n9.2 credit hold — the agent must not promise delivery")
print(crm.get_customer.invoke({"customer_id": "C-1028"}))
print(crm.search_knowledge_base.invoke({"query": "credit hold overdue payment"}))

# 9.3 The ROI number moves when the review assumption moves.
published = evaluation.roi_table(hourly_cost_eur=45.0)
original_share = dict(evaluation.HUMAN_REVIEW_SHARE)
evaluation.HUMAN_REVIEW_SHARE["draft_reply"] = 1.0   # humans rewrite every email
pessimistic = evaluation.roi_table(hourly_cost_eur=45.0)
evaluation.HUMAN_REVIEW_SHARE.clear()
evaluation.HUMAN_REVIEW_SHARE.update(original_share)

pub = published.loc[published.task == "TOTAL", "saved_eur"].item()
pess = pessimistic.loc[pessimistic.task == "TOTAL", "saved_eur"].item()
print(f"\n9.3 published monthly saving (draft review share 0.5): EUR {pub:,.0f}")
print(f"    if every draft is rewritten by a human:              EUR {pess:,.0f}")
print("    Quote the second number until the team measures the first.")
