# 💻 Pause before the write. Approve one lead, reject another.
try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:  # older LangGraph
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver

from langgraph.types import Command


def run_gated(graph, lead_id, approve: bool):
    """Invoke until the approval interrupt, print it, then resume."""
    config = {"configurable": {"thread_id": f"approve-{lead_id}-{approve}"}}
    first = graph.invoke({"lead_id": lead_id}, config=config)
    pending = first.get("__interrupt__") if isinstance(first, dict) else None
    if not pending:
        print(f"{lead_id}: finished without a pause (route={first.get('route')})")
        return first
    payload = pending[0].value if hasattr(pending[0], "value") else pending[0]
    print(f"\n{lead_id}: PAUSED for a human")
    print(json.dumps(payload, indent=2, default=str)[:700])
    decision = "APPROVE" if approve else "REJECT"
    print(f"human says: {decision}")
    return graph.invoke(Command(resume=approve), config=config)


saver = InMemorySaver()
gated = build_triage_graph(
    config.get_chat_model(verbose_mock=True),
    with_gate=True,
    checkpointer=saver,
)

print("=" * 72)
print("L-2003 Fjord Energi — existing, angry, grade B. We APPROVE the write.")
print("=" * 72)
crm.reset_call_log()
fjord_gate = run_gated(gated, "L-2003", approve=True)
print("approved:", fjord_gate.get("approved"),
      "| pipeline:", [c.get("pipeline_id") for c in fjord_gate.get("committed") or []
                     if isinstance(c, dict)])

print("\n" + "=" * 72)
print("L-2001 Cascade Interiors — new logo. We REJECT the write.")
print("=" * 72)
cascade_gate = run_gated(gated, "L-2001", approve=False)
print("approved:", cascade_gate.get("approved"),
      "| committed rows:", len(cascade_gate.get("committed") or []))
print((cascade_gate.get("brief") or "")[-80:])
