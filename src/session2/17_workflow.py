# 💻 Lead-triage workflow: deterministic qualify + one agentic step + a gate.
WRITE_NAMES = {t.name for t in crm.WRITE_TOOLS}


class CopilotState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    lead_id: str
    company: str
    contact_name: str
    contact_email: str
    employees: int
    budget_eur: float
    urgency: str
    message: str
    is_existing: bool
    customer_id: str
    lead_score: int
    grade: str
    qualified: bool
    flags: list
    route: str          # "self_serve" | "agent"
    brief: str
    approved: bool
    committed: list


def load_lead(state: CopilotState) -> dict:
    payload = json.loads(crm.get_inbox_leads.invoke({"lead_id": state["lead_id"]}))
    if payload.get("error"):
        return {"brief": payload["error"], "route": "self_serve", "qualified": False}
    lead = payload["leads"][0]
    return {
        "company": lead["company"],
        "contact_name": lead["contact_name"],
        "contact_email": lead["contact_email"],
        "employees": int(lead["employees"]),
        "budget_eur": float(lead["budget_eur"]),
        "urgency": lead["urgency"],
        "message": lead["message"],
    }


def qualify(state: CopilotState) -> dict:
    found = json.loads(crm.search_customers.invoke({"query": state["company"]}))
    existing, cid = False, ""
    if found.get("customers"):
        existing = True
        cid = found["customers"][0]["customer_id"]
    scored = json.loads(crm.score_lead.invoke({
        "company": state["company"],
        "employees": state["employees"],
        "budget_eur": state["budget_eur"],
        "urgency": state["urgency"],
        "message": state["message"],
        "is_existing_customer": existing,
    }))
    qualified = bool(scored["sales_qualified"])
    return {
        "is_existing": existing,
        "customer_id": cid,
        "lead_score": int(scored["lead_score"]),
        "grade": scored["grade"],
        "qualified": qualified,
        "flags": scored.get("flags") or [],
        "route": "agent" if qualified else "self_serve",
        "brief": scored["recommended_action"],
    }


def route_after_qualify(state: CopilotState) -> Literal["self_serve", "researcher"]:
    return "researcher" if state.get("route") == "agent" else "self_serve"


def self_serve(state: CopilotState) -> dict:
    """No LLM. Policy already decided. Draft a polite redirect and stop."""
    draft = json.loads(crm.draft_email.invoke({
        "to_name": state.get("contact_name") or "there",
        "subject": f"Your enquiry — {state.get('company', '')}",
        "purpose": "nurture",
        "key_points": [
            "Our minimum order value is EUR 1,000; the self-service shop is the fastest path.",
            state.get("brief") or "We will keep you on the newsletter.",
        ],
    }))
    return {
        "brief": f"[self-serve] grade {state.get('grade')} score {state.get('lead_score')}. "
                 f"No salesperson assigned.\n\n{draft.get('draft', '')}",
        "approved": False,
        "committed": [],
    }


print("workflow nodes defined: load_lead, qualify, self_serve")
print("Pixel & Pine will take the self_serve path and never call the model.")
