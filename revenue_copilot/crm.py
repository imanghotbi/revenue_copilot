"""
CRM tools for the Revenue Copilot scenario.

These are ordinary Python functions decorated with LangChain's `@tool`.
Two things make them good teaching material:

1. They are *deterministic*.  Same input -> same output, always.  So an
   exercise can have a checkable answer even though an LLM is in the loop.
2. Anything involving arithmetic or business rules lives in a tool, not in a
   prompt.  The model decides *what* to do; the tool decides *what is true*.

Every tool returns a JSON string.  Tool outputs go back into the model's
context window as text, so they should be compact and unambiguous - and when
something goes wrong they should say so in a way that lets the model recover
("no customer matches 'acmee'; did you mean 'Acme Logistik GmbH'?").
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta
from difflib import get_close_matches
from typing import Any, Optional

from langchain_core.tools import tool

# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

_TODAY = date(2026, 9, 30)          # fixed "today" so results are reproducible
_cache: dict[str, list[dict]] = {}
_DATA_DIR: Optional[str] = None


def find_data_dir(explicit: Optional[str] = None) -> str:
    """Locate the folder holding the CRM CSVs, creating it if necessary."""
    candidates = []
    if explicit:
        candidates.append(explicit)
    here = os.path.dirname(os.path.abspath(__file__))
    candidates += [
        os.path.join(os.path.dirname(here), "data"),   # repo layout: revenue_copilot/data
        os.path.join(os.getcwd(), "data"),             # Colab layout: /content/data
        os.path.join(here, "data"),
    ]
    for cand in candidates:
        if os.path.isfile(os.path.join(cand, "customers.csv")):
            return cand

    # Nothing found: generate the dataset.  Deterministic, no network needed.
    target = candidates[1] if os.access(os.path.dirname(candidates[1]) or ".", os.W_OK) else candidates[2]
    from . import data as _data

    _data.write_all(target)
    return target


def data_dir() -> str:
    global _DATA_DIR
    if _DATA_DIR is None:
        _DATA_DIR = find_data_dir()
    return _DATA_DIR


def table(name: str) -> list[dict]:
    """Read (and cache) one CSV table as a list of dicts."""
    import pandas as pd

    if name not in _cache:
        path = os.path.join(data_dir(), f"{name}.csv")
        if not os.path.exists(path):
            # regenerate everything once, then retry
            find_data_dir()
            path = os.path.join(data_dir(), f"{name}.csv")
        df = pd.read_csv(path)
        df = df.where(pd.notna(df), None)
        _cache[name] = df.to_dict("records")
    return _cache[name]


def reset_cache() -> None:
    _cache.clear()


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def _err(msg: str, **extra: Any) -> str:
    return _json({"error": msg, **extra})


# --------------------------------------------------------------------------
# Tool-call recorder: lets us show the agent's trace and compute ROI later
# --------------------------------------------------------------------------

CALL_LOG: list[dict] = []


def reset_call_log() -> None:
    CALL_LOG.clear()


def _record(name: str, args: dict, result: str, writes: bool) -> None:
    CALL_LOG.append(
        {
            "n": len(CALL_LOG) + 1,
            "tool": name,
            "args": args,
            "writes": writes,
            "result_preview": result[:180],
            "ts": datetime.now().isoformat(timespec="seconds"),
        }
    )


def call_log_frame():
    """The recorded tool calls as a DataFrame (for display and ROI maths)."""
    import pandas as pd

    return pd.DataFrame(CALL_LOG)


# --------------------------------------------------------------------------
# Read tools
# --------------------------------------------------------------------------

@tool
def search_customers(query: str = "", segment: str = "", region: str = "",
                     owner: str = "", health: str = "") -> str:
    """Search the customer database. All arguments are optional filters; use an
    empty string to skip a filter. `query` matches the company name or contact
    name (partial matches allowed). `segment` is one of Enterprise, Mid-Market,
    SMB, Public Sector. `health` is one of green, amber, red. Returns a compact
    list of matching customers."""
    args = {"query": query, "segment": segment, "region": region, "owner": owner, "health": health}
    rows = table("customers")
    out = []
    q = (query or "").strip().lower()
    for r in rows:
        if q and q not in r["company"].lower() and q not in str(r["contact_name"]).lower():
            continue
        if segment and r["segment"].lower() != segment.strip().lower():
            continue
        if region and r["region"].lower() != region.strip().lower():
            continue
        if owner and owner.strip().lower() not in r["owner"].lower():
            continue
        if health and r["health"].lower() != health.strip().lower():
            continue
        out.append(r)
    if not out:
        _record("search_customers", args, "[]", False)
        names = [r["company"] for r in rows]
        hint = get_close_matches(query, names, n=3, cutoff=0.4) if q else []
        return _err("no customer matches those filters", did_you_mean=hint)
    result = _json(
        {
            "count": len(out),
            "customers": [
                {k: r[k] for k in ("customer_id", "company", "segment", "region",
                                   "owner", "plan", "health", "employee_count")}
                for r in out[:25]
            ],
        }
    )
    _record("search_customers", args, result, False)
    return result


@tool
def get_customer(customer_id: str) -> str:
    """Look up one customer by exact id (e.g. 'C-1006'). Returns the full CRM
    record: company, contacts, segment, region, owner, plan, employee count,
    signup date, health flag and free-text notes. If the id is not found it
    returns suggestions for similarly named accounts."""
    args = {"customer_id": customer_id}
    key = (customer_id or "").strip().upper()
    for r in table("customers"):
        if r["customer_id"].upper() == key:
            result = _json(r)
            _record("get_customer", args, result, False)
            return result
    # be helpful: maybe they passed a company name
    names = [r["company"] for r in table("customers")]
    hint = get_close_matches(customer_id or "", names, n=3, cutoff=0.4)
    ids = [{"customer_id": r["customer_id"], "company": r["company"]}
           for r in table("customers") if r["company"] in hint]
    result = _err(f"no customer with id '{customer_id}'", did_you_mean=ids)
    _record("get_customer", args, result, False)
    return result


@tool
def get_order_history(customer_id: str, last_n_days: int = 730) -> str:
    """Return a customer's orders, newest first, limited to the last
    `last_n_days` (default 730 = two years). Includes order id, date, items,
    total in EUR and status. Use this before commenting on what a customer buys."""
    args = {"customer_id": customer_id, "last_n_days": last_n_days}
    key = (customer_id or "").strip().upper()
    cutoff = _TODAY - timedelta(days=int(last_n_days))
    rows = [
        r for r in table("orders")
        if r["customer_id"].upper() == key
        and date.fromisoformat(str(r["date"])[:10]) >= cutoff
    ]
    rows.sort(key=lambda r: str(r["date"]), reverse=True)
    result = _json(
        {
            "customer_id": key,
            "window_days": int(last_n_days),
            "order_count": len(rows),
            "orders": rows[:30],
        }
    )
    _record("get_order_history", args, result, False)
    return result


@tool
def account_metrics(customer_id: str) -> str:
    """Compute the objective business metrics for one account: total revenue
    (excluding cancelled orders), order count, average order value, days since
    last order, revenue in the last 180 days vs the 180 days before that, the
    trend in percent, open support tickets, and a rule-based churn risk score
    from 0 to 100 with the reasons for that score. ALWAYS use this tool for
    numbers - never calculate revenue or risk yourself."""
    args = {"customer_id": customer_id}
    key = (customer_id or "").strip().upper()
    cust = next((r for r in table("customers") if r["customer_id"].upper() == key), None)
    if cust is None:
        result = _err(f"no customer with id '{customer_id}'")
        _record("account_metrics", args, result, False)
        return result

    orders = [r for r in table("orders") if r["customer_id"].upper() == key]
    live = [r for r in orders if r["status"] != "cancelled"]
    for r in live:
        r["_d"] = date.fromisoformat(str(r["date"])[:10])

    total = round(sum(float(r["total_eur"]) for r in live), 2)
    aov = round(total / len(live), 2) if live else 0.0
    last = max((r["_d"] for r in live), default=None)
    days_since = (_TODAY - last).days if last else None

    recent = sum(float(r["total_eur"]) for r in live if (_TODAY - r["_d"]).days <= 180)
    prior = sum(float(r["total_eur"]) for r in live if 180 < (_TODAY - r["_d"]).days <= 360)
    trend_pct = round((recent - prior) / prior * 100, 1) if prior else (100.0 if recent else 0.0)

    tickets = [t for t in table("support_cases") if t["customer_id"].upper() == key]
    open_tickets = [t for t in tickets if t["status"] == "open"]
    oldest_open = min((date.fromisoformat(str(t["opened"])) for t in open_tickets), default=None)
    oldest_open_days = (_TODAY - oldest_open).days if oldest_open else None

    # ---- rule-based churn risk (transparent and reproducible) ----
    score = 0
    reasons: list[str] = []
    if cust["health"] == "red":
        score += 45
        reasons.append("CRM health flag is 'red' (+45)")
    elif cust["health"] == "amber":
        score += 20
        reasons.append("CRM health flag is 'amber' (+20)")

    if days_since is not None:
        if days_since > 270:
            score += 25
            reasons.append(f"no order for {days_since} days (+25)")
        elif days_since > 180:
            score += 15
            reasons.append(f"no order for {days_since} days (+15)")
        elif days_since > 90:
            score += 5
            reasons.append(f"no order for {days_since} days (+5)")
    else:
        score += 25
        reasons.append("never placed an order (+25)")

    if open_tickets:
        score += 12 * len(open_tickets)
        reasons.append(f"{len(open_tickets)} open support ticket(s) (+{12 * len(open_tickets)})")
    if oldest_open_days is not None and oldest_open_days > 60:
        score += 10
        reasons.append(f"oldest open ticket is {oldest_open_days} days old (+10)")

    if trend_pct <= -40:
        score += 15
        reasons.append(f"revenue down {abs(trend_pct)}% vs previous 180 days (+15)")
    elif trend_pct <= -15:
        score += 8
        reasons.append(f"revenue down {abs(trend_pct)}% vs previous 180 days (+8)")
    elif trend_pct >= 20 and cust["health"] != "red":
        score -= 10
        reasons.append(f"revenue up {trend_pct}% (-10)")

    if cust["plan"] == "Basic" and cust["segment"] in ("Mid-Market", "Enterprise"):
        score += 5
        reasons.append("large account on the Basic plan (+5)")

    score = max(0, min(100, score))
    band = "high" if score >= 60 else ("medium" if score >= 35 else "low")

    result = _json(
        {
            "customer_id": key,
            "company": cust["company"],
            "segment": cust["segment"],
            "owner": cust["owner"],
            "total_revenue_eur": total,
            "order_count": len(live),
            "avg_order_value_eur": aov,
            "last_order_date": last.isoformat() if last else None,
            "days_since_last_order": days_since,
            "revenue_last_180d_eur": round(recent, 2),
            "revenue_previous_180d_eur": round(prior, 2),
            "revenue_trend_pct": trend_pct,
            "open_support_tickets": len(open_tickets),
            "oldest_open_ticket_days": oldest_open_days,
            "churn_risk_score": score,
            "churn_risk_band": band,
            "risk_reasons": reasons,
        }
    )
    _record("account_metrics", args, result, False)
    return result


@tool
def product_lookup(query: str = "", category: str = "") -> str:
    """Look up products in the catalogue. `query` matches the SKU or product
    name (partial matches allowed), `category` filters by category. Returns
    name, SKU, category, unit price in EUR, units in stock and the lead time in
    days. Use this before quoting a price or promising a delivery date."""
    args = {"query": query, "category": category}
    q = (query or "").strip().lower()
    out = []
    for r in table("products"):
        if q and q not in r["sku"].lower() and q not in r["name"].lower():
            continue
        if category and category.strip().lower() not in r["category"].lower():
            continue
        out.append(r)
    if not out:
        names = [r["name"] for r in table("products")]
        hint = get_close_matches(query, names, n=3, cutoff=0.4) if q else []
        result = _err("no product matches those filters", did_you_mean=hint)
        _record("product_lookup", args, result, False)
        return result
    result = _json({"count": len(out), "products": out})
    _record("product_lookup", args, result, False)
    return result


@tool
def get_support_tickets(customer_id: str = "", status: str = "") -> str:
    """List support tickets. `customer_id` filters to one account, `status`
    filters by 'open' or 'closed'. Returns ticket id, customer, date opened,
    category, status and a summary. Read the open tickets before writing any
    message to an unhappy customer."""
    args = {"customer_id": customer_id, "status": status}
    key = (customer_id or "").strip().upper()
    out = []
    for t in table("support_cases"):
        if key and t["customer_id"].upper() != key:
            continue
        if status and t["status"] != status.strip().lower():
            continue
        out.append(t)
    out.sort(key=lambda t: str(t["opened"]), reverse=True)
    result = _json({"count": len(out), "tickets": out})
    _record("get_support_tickets", args, result, False)
    return result


@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal sales playbook (policies on discounts, lead times,
    service recovery, lead qualification, compliance, credit holds, tenders).
    `query` is a few keywords such as 'late delivery complaint' or 'discount
    policy'. Returns the most relevant policy documents. ALWAYS check policy
    here before promising a discount, a delivery date or a credit."""
    args = {"query": query}
    words = [w.strip(".,;:()").lower() for w in (query or "").split() if len(w) > 2]
    scored = []
    for doc in table("knowledge_base"):
        hay = (doc["title"] + " " + " ".join(doc["tags"]) + " " + doc["text"]).lower()
        score = sum(hay.count(w) for w in words) + sum(2 for w in words if w in doc["title"].lower())
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        result = _err("no policy document matches that query",
                      try_keywords=["discount", "lead time", "complaint", "qualification",
                                    "compliance", "credit hold", "tender"])
        _record("search_knowledge_base", args, result, False)
        return result
    result = _json(
        {
            "matches": [
                {"kb_id": d["kb_id"], "title": d["title"], "relevance": s, "text": d["text"]}
                for s, d in scored[:3]
            ]
        }
    )
    _record("search_knowledge_base", args, result, False)
    return result


@tool
def get_inbox_leads(lead_id: str = "") -> str:
    """List the inbound leads waiting in the sales inbox, or fetch one lead by
    its id (e.g. 'L-2005'). Each lead has the company, contact, country,
    employee count, indicated budget in EUR, urgency, source and the original
    message. This is the raw material for the lead-qualification workflow."""
    args = {"lead_id": lead_id}
    key = (lead_id or "").strip().upper()
    rows = table("inbox_leads")
    if key:
        rows = [r for r in rows if str(r["lead_id"]).upper() == key]
        if not rows:
            result = _err(f"no lead with id '{lead_id}'",
                          available=[r["lead_id"] for r in table("inbox_leads")])
            _record("get_inbox_leads", args, result, False)
            return result
    result = _json({"count": len(rows), "leads": rows})
    _record("get_inbox_leads", args, result, False)
    return result


# --------------------------------------------------------------------------
# Deterministic decision tools (business logic lives here, not in the prompt)
# --------------------------------------------------------------------------

@tool
def score_lead(company: str, employees: int, budget_eur: float, urgency: str,
               message: str, is_existing_customer: bool = False) -> str:
    """Score an inbound lead with Northwind's published qualification rules and
    return the score (0-100), a grade (A/B/C/D), whether it is sales-qualified,
    the recommended next action, and the reasons. Deterministic: the same input
    always gives the same score. Use this instead of judging a lead yourself."""
    args = {"company": company, "employees": employees, "budget_eur": budget_eur,
            "urgency": urgency, "is_existing_customer": is_existing_customer}
    score = 0
    reasons: list[str] = []
    flags: list[str] = []

    budget = float(budget_eur or 0)
    if budget >= 200000:
        score += 35
        reasons.append(f"budget EUR {budget:,.0f} (>= 200k) (+35)")
    elif budget >= 75000:
        score += 30
        reasons.append(f"budget EUR {budget:,.0f} (>= 75k) (+30)")
    elif budget >= 40000:
        score += 24
        reasons.append(f"budget EUR {budget:,.0f} (>= 40k) (+24)")
    elif budget >= 15000:
        score += 16
        reasons.append(f"budget EUR {budget:,.0f} (>= 15k) (+16)")
    elif budget >= 5000:
        score += 10
        reasons.append(f"budget EUR {budget:,.0f} (>= 5k) (+10)")
    elif budget >= 1000:
        score += 4
        reasons.append(f"budget EUR {budget:,.0f} (>= 1k) (+4)")
    else:
        score -= 5
        reasons.append(f"budget EUR {budget:,.0f} is below the EUR 1,000 minimum order value (-5)")
        flags.append("below_minimum_order_value -> route to self-service web shop")

    emp = int(employees or 0)
    if emp >= 1000:
        score += 20
        reasons.append(f"{emp} employees (>= 1000) (+20)")
    elif emp >= 100:
        score += 14
        reasons.append(f"{emp} employees (>= 100) (+14)")
    elif emp >= 20:
        score += 8
        reasons.append(f"{emp} employees (>= 20) (+8)")
    else:
        reasons.append(f"{emp} employees (< 20) (+0)")

    urg = (urgency or "").strip().lower()
    urg_points = {"high": 18, "medium": 8, "low": 0}.get(urg, 0)
    score += urg_points
    if urg == "low":
        score -= 6
        reasons.append("urgency 'low' (0 points, -6 no-time-pressure penalty)")
    else:
        reasons.append(f"urgency '{urg or 'unknown'}' (+{urg_points})")

    # Word-boundary matching: naive substring search would match "public"
    # inside "accessibility", which silently corrupts the score.
    text = (message or "").lower()

    def _has(*phrases: str) -> bool:
        return any(re.search(rf"\b{re.escape(ph)}\b", text) for ph in phrases)

    if _has("deadline", "before the end of", "closes in", "this week",
            "next quarter", "procurement closes", "this month"):
        score += 8
        reasons.append("message contains a concrete deadline (+8)")
    if _has("referred by", "referral"):
        score += 6
        reasons.append("inbound referral (+6)")
    if _has("tender", "framework agreement", "public sector", "RFP"):
        score += 5
        flags.append("public sector / tender rules apply (KB-07)")
        reasons.append("tender or framework mentioned (+5)")
    if _has("competitor", "cancel", "unhappy", "late", "dispute", "complaint",
            "escalate", "frustrated"):
        score += 10
        flags.append("at-risk or complaining account -> service recovery playbook KB-03 applies")
        reasons.append("risk / complaint language detected (+10)")

    if is_existing_customer:
        score += 5
        reasons.append("already a customer (+5)")

    score = max(0, min(100, score))
    grade = "A" if score >= 70 else ("B" if score >= 50 else ("C" if score >= 30 else "D"))
    qualified = score >= 50 and "below_minimum_order_value -> route to self-service web shop" not in flags

    if grade == "A":
        action = "Assign an account owner today, call within 1 business day, send a full quote."
    elif grade == "B":
        action = "Assign an account owner, qualify by email within 2 business days."
    elif grade == "C":
        action = "Nurture: add to the newsletter and re-check in 30 days."
    else:
        action = "Route to the self-service web shop; no sales time."

    result = _json(
        {
            "company": company,
            "lead_score": score,
            "grade": grade,
            "sales_qualified": bool(qualified),
            "recommended_action": action,
            "flags": flags,
            "reasons": reasons,
        }
    )
    _record("score_lead", args, result, False)
    return result


@tool
def build_quote(customer_or_company: str, items: list, discount_pct: float = 0.0,
                valid_for_days: int = 30) -> str:
    """Build a priced quote. `items` is a list of {'sku': str, 'qty': int}
    dictionaries. `discount_pct` is the discount to apply (the tool refuses a
    discount above the policy limit for that order value unless
    `requires_director_approval` is acknowledged in the output). Returns the
    line items with catalogue prices, subtotal, discount, VAT (19%), total,
    the longest lead time in days and an estimated delivery date."""
    args = {"customer_or_company": customer_or_company, "items": items,
            "discount_pct": discount_pct, "valid_for_days": valid_for_days}
    catalogue = {r["sku"].upper(): r for r in table("products")}
    lines = []
    unknown = []
    subtotal = 0.0
    worst_lead = 0
    for it in items or []:
        sku = str(it.get("sku", "")).upper()
        qty = int(it.get("qty", 0))
        if sku not in catalogue:
            unknown.append(it.get("sku"))
            continue
        p = catalogue[sku]
        if qty <= 0:
            unknown.append(f"{it.get('sku')} (qty must be > 0)")
            continue
        line_total = round(qty * float(p["unit_price_eur"]), 2)
        subtotal += line_total
        worst_lead = max(worst_lead, int(p["lead_time_days"]))
        lines.append(
            {
                "sku": sku, "name": p["name"], "qty": qty,
                "unit_price_eur": float(p["unit_price_eur"]),
                "line_total_eur": line_total,
                "in_stock": int(p["stock"]),
                "lead_time_days": int(p["lead_time_days"]),
            }
        )
    if not lines:
        result = _err("quote has no valid line items",
                      unknown_skus=unknown,
                      valid_skus=sorted(catalogue.keys()))
        _record("build_quote", args, result, False)
        return result

    discount_pct = float(discount_pct or 0)
    # --- policy from KB-02 ---
    cap = 5.0 if subtotal < 50000 else 10.0
    needs_approval = discount_pct > cap
    applied = min(discount_pct, cap)
    discount_value = round(subtotal * applied / 100, 2)
    net = round(subtotal - discount_value, 2)
    vat = round(net * 0.19, 2)
    total = round(net + vat, 2)
    delivery = _TODAY + timedelta(days=worst_lead)

    result = _json(
        {
            "customer_or_company": customer_or_company,
            "quote_date": _TODAY.isoformat(),
            "valid_until": (_TODAY + timedelta(days=int(valid_for_days))).isoformat(),
            "lines": lines,
            "subtotal_eur": round(subtotal, 2),
            "discount_requested_pct": discount_pct,
            "discount_applied_pct": applied,
            "discount_value_eur": discount_value,
            "net_eur": net,
            "vat_19pct_eur": vat,
            "total_eur": total,
            "longest_lead_time_days": worst_lead,
            "earliest_full_delivery": delivery.isoformat(),
            "policy_notes": (
                [f"requested {discount_pct}% but policy caps discounts at {cap}% for an order of "
                 f"EUR {subtotal:,.0f}; sales director approval required for more"]
                if needs_approval else []
            )
            + [f"{len(lines)} line(s); catalogue prices used, floor prices respected"]
            + ([f"unknown or invalid items ignored: {unknown}"] if unknown else []),
        }
    )
    _record("build_quote", args, result, True)
    return result


# --------------------------------------------------------------------------
# Write tools (they only append to local CSVs - safe to run in class)
# --------------------------------------------------------------------------

def _append(table_name: str, row: dict) -> None:
    import pandas as pd

    path = os.path.join(data_dir(), f"{table_name}.csv")
    df_new = pd.DataFrame([row])
    if os.path.exists(path):
        df_old = pd.read_csv(path)
        for col in df_new.columns:
            if col not in df_old.columns:
                df_old[col] = None
        df = pd.concat([df_old, df_new[df_old.columns]], ignore_index=True)
    else:
        df = df_new
    df.to_csv(path, index=False)
    _cache.pop(table_name, None)          # force a reload next time


@tool
def log_activity(customer_id: str, activity_type: str, summary: str,
                 owner: str = "Revenue Copilot") -> str:
    """Write an activity to the customer's CRM timeline. `activity_type` is one
    of call, email, meeting, note, task. Every action the agent takes on an
    account MUST be logged here so the sales team can audit it."""
    args = {"customer_id": customer_id, "activity_type": activity_type, "summary": summary}
    valid = {"call", "email", "meeting", "note", "task"}
    if activity_type not in valid:
        result = _err(f"activity_type must be one of {sorted(valid)}", got=activity_type)
        _record("log_activity", args, result, True)
        return result
    if not (customer_id or "").strip():
        result = _err("customer_id is required")
        _record("log_activity", args, result, True)
        return result
    row = {
        "activity_id": f"A-9{len(table('activities')) + 1:04d}",
        "customer_id": customer_id.strip().upper(),
        "date": _TODAY.isoformat(),
        "type": activity_type,
        "owner": owner,
        "summary": summary.strip(),
    }
    _append("activities", row)
    result = _json({"status": "logged", **row})
    _record("log_activity", args, result, True)
    return result


@tool
def create_pipeline_record(company: str, contact_name: str, contact_email: str,
                           estimated_value_eur: float, stage: str = "New",
                           owner: str = "", notes: str = "") -> str:
    """Create a CRM pipeline record for a new lead. `stage` is one of New,
    Qualified, Quoted, Negotiation, Won, Lost. Use this after qualifying an
    inbound lead so it enters the pipeline with an owner and a value."""
    args = {"company": company, "contact_name": contact_name, "contact_email": contact_email,
            "estimated_value_eur": estimated_value_eur, "stage": stage, "owner": owner}
    valid = {"New", "Qualified", "Quoted", "Negotiation", "Won", "Lost"}
    if stage not in valid:
        result = _err(f"stage must be one of {sorted(valid)}", got=stage)
        _record("create_pipeline_record", args, result, True)
        return result
    pid = f"P-3{len(table('pipeline')) + 1:03d}"
    row = {
        "pipeline_id": pid,
        "company": company,
        "contact_name": contact_name,
        "contact_email": contact_email,
        "stage": stage,
        "estimated_value_eur": round(float(estimated_value_eur or 0), 2),
        "owner": owner or "Unassigned",
        "created": _TODAY.isoformat(),
        "notes": notes,
    }
    _append("pipeline", row)
    result = _json({"status": "created", **row})
    _record("create_pipeline_record", args, result, True)
    return result


@tool
def draft_email(to_name: str, subject: str, purpose: str, key_points: list,
                tone: str = "professional", sender: str = "Northwind Supply Co.") -> str:
    """Draft (never send) a customer email. `purpose` is one of quote,
    follow_up, service_recovery, win_back, qualification, nurture. `key_points`
    is a list of short strings to include. Returns the draft plus a checklist of
    what a human must verify before sending. The agent may not send email."""
    args = {"to_name": to_name, "subject": subject, "purpose": purpose, "key_points": key_points}
    openings = {
        "quote": f"Thank you for your interest in Northwind Supply Co. Please find our offer below.",
        "follow_up": "Following up on our recent conversation.",
        "service_recovery": "I am writing about the problems you have experienced with us. You are right to raise them, and I am sorry.",
        "win_back": "It has been a while since we last worked together, and we would like to make that right.",
        "qualification": "Thank you for getting in touch. To make sure we propose the right solution, I have a few short questions.",
        "nurture": "A quick note with something that may be useful for your team.",
    }
    if purpose not in openings:
        result = _err(f"purpose must be one of {sorted(openings)}", got=purpose)
        _record("draft_email", args, result, True)
        return result
    points = [str(p).strip() for p in (key_points or []) if str(p).strip()]
    if not points:
        result = _err("key_points must contain at least one item")
        _record("draft_email", args, result, True)
        return result

    body_lines = [f"Dear {to_name},", "", openings[purpose], ""]
    for p in points:
        body_lines.append(f"- {p}")
    body_lines += [
        "",
        "If anything here is unclear, just reply to this email and I will sort it out.",
        "",
        "Kind regards,",
        sender,
    ]
    draft = "\n".join(body_lines)
    result = _json(
        {
            "to": to_name,
            "subject": subject,
            "purpose": purpose,
            "tone": tone,
            "draft": draft,
            "word_count": len(draft.split()),
            "human_review_required": [
                "verify every price and lead time against the quote tool output",
                "confirm no discount above policy was promised",
                "check the account is not on credit hold before promising delivery",
                "approve wording, then send manually",
            ],
            "sent": False,
        }
    )
    _record("draft_email", args, result, True)
    return result


# --------------------------------------------------------------------------
# A ready-made bundle for the notebooks
# --------------------------------------------------------------------------

READ_TOOLS = [search_customers, get_customer, get_order_history, account_metrics,
              product_lookup, get_support_tickets, search_knowledge_base,
              get_inbox_leads, score_lead]

WRITE_TOOLS = [build_quote, log_activity, create_pipeline_record, draft_email]

ALL_TOOLS = READ_TOOLS + WRITE_TOOLS


def tool_specs() -> list[dict]:
    """Name/description/argument schema for every tool - useful for teaching
    what an LLM actually 'sees' when we give it tools."""
    return [
        {"name": t.name, "description": t.description.strip().split("\n")[0],
         "args": t.args}
        for t in ALL_TOOLS
    ]
