"""
Evaluation helpers: ground truth for the exercises, and the ROI model that
turns "we built an agent" into a number a manager can read.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from . import crm

TODAY = crm._TODAY

# --------------------------------------------------------------------------
# Ground truth - computed from the data, not hard-coded, so it can never drift
# --------------------------------------------------------------------------

def account_table() -> pd.DataFrame:
    """One row per customer with the metrics the agent is expected to use."""
    rows = []
    for c in crm.table("customers"):
        import json

        m = json.loads(crm.account_metrics.invoke({"customer_id": c["customer_id"]}))
        rows.append(
            {
                "customer_id": c["customer_id"],
                "company": c["company"],
                "segment": c["segment"],
                "region": c["region"],
                "owner": c["owner"],
                "plan": c["plan"],
                "health": c["health"],
                "revenue_eur": m["total_revenue_eur"],
                "orders": m["order_count"],
                "aov_eur": m["avg_order_value_eur"],
                "days_since_last_order": m["days_since_last_order"],
                "trend_pct": m["revenue_trend_pct"],
                "open_tickets": m["open_support_tickets"],
                "churn_risk": m["churn_risk_score"],
                "risk_band": m["churn_risk_band"],
            }
        )
    df = pd.DataFrame(rows).sort_values("churn_risk", ascending=False)
    crm.reset_call_log()          # building this table is not agent activity
    return df.reset_index(drop=True)


def lead_table() -> pd.DataFrame:
    """The five inbox leads with their deterministic scores."""
    import json

    rows = []
    for lead in crm.table("inbox_leads"):
        existing = any(
            lead["company"].lower() in c["company"].lower()
            or c["company"].lower() in lead["company"].lower()
            for c in crm.table("customers")
        )
        s = json.loads(
            crm.score_lead.invoke(
                {
                    "company": lead["company"],
                    "employees": lead["employees"],
                    "budget_eur": lead["budget_eur"],
                    "urgency": lead["urgency"],
                    "message": lead["message"],
                    "is_existing_customer": existing,
                }
            )
        )
        rows.append(
            {
                "lead_id": lead["lead_id"],
                "company": lead["company"],
                "country": lead["country"],
                "employees": lead["employees"],
                "budget_eur": lead["budget_eur"],
                "urgency": lead["urgency"],
                "existing_customer": existing,
                "score": s["lead_score"],
                "grade": s["grade"],
                "qualified": s["sales_qualified"],
                "flags": "; ".join(s["flags"]),
            }
        )
    df = pd.DataFrame(rows).sort_values("score", ascending=False)
    crm.reset_call_log()
    return df.reset_index(drop=True)


def exercise_answers() -> dict[str, Any]:
    """Solutions for the self-check quizzes in both notebooks."""
    accounts = account_table()
    leads = lead_table()
    top_risk = accounts.iloc[0]
    best_lead = leads.iloc[0]
    worst_lead = leads.iloc[-1]
    return {
        "highest_churn_risk_customer": top_risk["customer_id"],
        "highest_churn_risk_company": top_risk["company"],
        "highest_churn_risk_score": int(top_risk["churn_risk"]),
        "accounts_at_high_risk": int((accounts["churn_risk"] >= 60).sum()),
        "revenue_at_high_risk_eur": float(
            accounts.loc[accounts["churn_risk"] >= 60, "revenue_eur"].sum()
        ),
        "best_lead_id": best_lead["lead_id"],
        "best_lead_company": best_lead["company"],
        "best_lead_score": int(best_lead["score"]),
        "lead_to_self_serve": worst_lead["lead_id"],
        "leads_not_qualified": int((~leads["qualified"]).sum()),
        "total_pipeline_budget_eur": float(leads["budget_eur"].sum()),
    }


# --------------------------------------------------------------------------
# The business case
# --------------------------------------------------------------------------

# Manual effort, in minutes, measured with the sales team for each task.
# These are the numbers a manager will challenge, so they live in one place.
MANUAL_MINUTES = {
    "qualify_lead": 12,          # read email, search CRM, check policy, decide
    "prepare_quote": 20,         # find prices, apply discount rules, build PDF
    "draft_reply": 10,           # write the email, check tone and promises
    "log_crm": 4,                # the step everyone skips
    "account_review": 25,        # pull orders, tickets, compute metrics, write brief
    "churn_check": 30,           # scan every account for risk signals
}

# What the same tasks cost an LLM agent, in minutes of elapsed wall-clock time,
# plus the fully-loaded hourly cost of the human who reviews the output.
AGENT_MINUTES = {
    "qualify_lead": 0.6,
    "prepare_quote": 0.8,
    "draft_reply": 0.5,
    "log_crm": 0.1,
    "account_review": 1.5,
    "churn_check": 2.0,
}
HUMAN_REVIEW_SHARE = {           # humans still check the agent's work
    "qualify_lead": 0.3,
    "prepare_quote": 0.4,
    "draft_reply": 0.5,
    "log_crm": 0.1,
    "account_review": 0.4,
    "churn_check": 0.3,
}


def roi_table(hourly_cost_eur: float = 45.0,
              api_cost_per_task_eur: float = 0.01,
              volumes: Optional[dict[str, int]] = None) -> pd.DataFrame:
    """Monthly cost and time comparison, per task type.

    `volumes` is how many of each task happen per month.  The defaults are
    Northwind's real numbers: ~90 inbound leads a month, etc.
    """
    volumes = volumes or {
        "qualify_lead": 90,
        "prepare_quote": 55,
        "draft_reply": 90,
        "log_crm": 145,
        "account_review": 28,
        "churn_check": 28,
    }
    rows = []
    for task, n in volumes.items():
        manual_min = MANUAL_MINUTES[task] * n
        agent_min = AGENT_MINUTES[task] * n
        review_min = manual_min * HUMAN_REVIEW_SHARE[task]
        labour_manual = manual_min / 60 * hourly_cost_eur
        labour_agent = review_min / 60 * hourly_cost_eur
        api_cost = api_cost_per_task_eur * n
        rows.append(
            {
                "task": task,
                "per_month": n,
                "manual_minutes": round(manual_min, 1),
                "agent_minutes": round(agent_min + review_min, 1),
                "manual_cost_eur": round(labour_manual, 2),
                "agent_cost_eur": round(labour_agent + api_cost, 2),
                "saved_minutes": round(manual_min - (agent_min + review_min), 1),
                "saved_eur": round(labour_manual - (labour_agent + api_cost), 2),
            }
        )
    df = pd.DataFrame(rows)
    total = {
        "task": "TOTAL",
        "per_month": df["per_month"].sum(),
        "manual_minutes": df["manual_minutes"].sum(),
        "agent_minutes": df["agent_minutes"].sum(),
        "manual_cost_eur": df["manual_cost_eur"].sum(),
        "agent_cost_eur": df["agent_cost_eur"].sum(),
        "saved_minutes": df["saved_minutes"].sum(),
        "saved_eur": df["saved_eur"].sum(),
    }
    return pd.concat([df, pd.DataFrame([total])], ignore_index=True)


def actual_run_cost(call_log: Optional[pd.DataFrame] = None,
                    tokens: Optional[dict] = None,
                    price_per_mtok: float = 0.0,
                    seconds: float = 0.0) -> dict:
    """What one real agent run actually cost, measured rather than estimated."""
    log = call_log if call_log is not None else crm.call_log_frame()
    tokens = tokens or {}
    total_tokens = tokens.get("total_tokens", 0)
    api_eur = total_tokens / 1_000_000 * price_per_mtok
    return {
        "tool_calls": len(log),
        "write_operations": int(log["writes"].sum()) if len(log) else 0,
        "read_operations": int((~log["writes"].astype(bool)).sum()) if len(log) else 0,
        "tokens": total_tokens,
        "api_cost_eur": round(api_eur, 6),
        "elapsed_seconds": round(seconds, 2),
        "human_review_minutes": round(len(log) * 0.25, 2),
    }
