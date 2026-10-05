# 💻 Researcher node (read-only agent) + compile the graph WITHOUT the gate yet.
def make_researcher(model):
    """A ReAct agent that can READ the CRM but cannot write to it."""
    if hasattr(model, "reset"):
        model.reset()
    bound = model.bind_tools(crm.READ_TOOLS)

    def researcher(state: CopilotState) -> dict:
        task = (
            f"Qualify and brief the sales owner on lead {state.get('lead_id')} "
            f"({state.get('company')}). Existing customer: {state.get('is_existing')} "
            f"(id={state.get('customer_id') or 'n/a'}). "
            f"Grade {state.get('grade')} score {state.get('lead_score')}. "
            f"Flags: {state.get('flags')}. Original message:\n{state.get('message')}\n"
            "Use tools for every number and every policy claim. End with a short brief."
        )
        messages = [SystemMessage(content=SYSTEM), HumanMessage(content=task)]
        # Reuse the ReAct graph so we do not reimplement the loop.
        sub = make_react_graph(model, crm.READ_TOOLS)
        out = sub.invoke({"messages": messages})
        text = last_text(out)
        return {"messages": out["messages"], "brief": text}

    return researcher


def build_triage_graph(model, with_gate: bool = False, checkpointer=None):
    """Qualify -> (self_serve | researcher) -> optional approval -> END."""
    g = StateGraph(CopilotState)
    g.add_node("load_lead", load_lead)
    g.add_node("qualify", qualify)
    g.add_node("self_serve", self_serve)
    g.add_node("researcher", make_researcher(model))
    g.add_edge(START, "load_lead")
    g.add_edge("load_lead", "qualify")
    g.add_conditional_edges("qualify", route_after_qualify)
    g.add_edge("self_serve", END)

    if with_gate:
        from langgraph.types import interrupt

        def approve(state: CopilotState) -> dict:
            decision = interrupt({
                "question": "Approve CRM writes for this brief?",
                "lead_id": state.get("lead_id"),
                "company": state.get("company"),
                "grade": state.get("grade"),
                "brief_preview": (state.get("brief") or "")[:500],
            })
            return {"approved": bool(decision)}

        def commit(state: CopilotState) -> dict:
            if not state.get("approved"):
                return {"committed": [],
                        "brief": (state.get("brief") or "") + "\n\n[writes blocked by human]"}
            done = []
            cid = (state.get("customer_id") or "").strip()
            summary = (f"Copilot brief for {state.get('lead_id')} "
                       f"grade {state.get('grade')}: {(state.get('brief') or '')[:180]}")
            # Only an existing account has a CRM timeline. New logos go to the pipeline.
            if cid:
                done.append(json.loads(crm.log_activity.invoke({
                    "customer_id": cid,
                    "activity_type": "note",
                    "summary": summary,
                })))
            done.append(json.loads(crm.create_pipeline_record.invoke({
                "company": state.get("company") or "",
                "contact_name": state.get("contact_name") or "",
                "contact_email": state.get("contact_email") or "",
                "estimated_value_eur": float(state.get("budget_eur") or 0),
                "stage": "Qualified",
                "owner": "Revenue Copilot",
                "notes": f"grade {state.get('grade')} score {state.get('lead_score')}",
            })))
            return {"committed": done}

        g.add_node("approve", approve)
        g.add_node("commit", commit)
        g.add_edge("researcher", "approve")
        g.add_edge("approve", "commit")
        g.add_edge("commit", END)
    else:
        g.add_edge("researcher", END)

    return g.compile(checkpointer=checkpointer)


triage = build_triage_graph(config.get_chat_model(verbose_mock=True), with_gate=False)
print(triage)
