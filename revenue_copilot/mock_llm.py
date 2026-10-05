"""
MockSalesLLM - an offline, rule-based stand-in for a real chat model.

Why this exists
---------------
A classroom of 25 students hitting a free API tier at the same time is a
reliable way to spend a lesson waiting on rate limits.  This model needs no
key, no network and no money, and it still exercises the *real* LangChain and
LangGraph machinery: the same message loop, the same tool schemas, the same
graph, the same checkpointer.

It is deliberately simple: given the conversation so far, it follows a
hard-coded plan of tool calls and then writes a summary from the tool outputs.
That makes it a useful reference point in class - you can show students exactly
what a *deterministic* agent looks like, and then swap in a real model to show
what the LLM adds (flexibility, language, judgement) and what it costs
(unpredictability).

Swap `PROVIDER="mock"` for `PROVIDER="openrouter"` in config.py and the very
same graphs run on a real model.  That single switch is the lesson.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

# --------------------------------------------------------------------------
# Plans: what the mock model "decides" to do
# --------------------------------------------------------------------------

LEAD_PLAN = [
    ("get_inbox_leads", {"lead_id": "{lead_id}"}),
    ("search_customers", {"query": "{company}"}),
    ("account_metrics", {"customer_id": "{customer_id}"}),
    ("score_lead", {"company": "{company}", "employees": "{employees}",
                    "budget_eur": "{budget_eur}", "urgency": "{urgency}",
                    "message": "{message}", "is_existing_customer": "{is_existing}"}),
    ("search_knowledge_base", {"query": "{kb_query}"}),
    ("product_lookup", {"category": "{category}"}),
    ("build_quote", {"customer_or_company": "{company}", "items": "{items}",
                     "discount_pct": "{discount}"}),
    ("draft_email", {"to_name": "{contact_name}", "subject": "{subject}",
                     "purpose": "{purpose}", "key_points": "{key_points}"}),
    ("create_pipeline_record", {"company": "{company}", "contact_name": "{contact_name}",
                                "contact_email": "{contact_email}",
                                "estimated_value_eur": "{budget_eur}",
                                "stage": "Qualified", "owner": "{owner}",
                                "notes": "{notes}"}),
    ("log_activity", {"customer_id": "{customer_id}", "activity_type": "note",
                      "summary": "{activity_summary}"}),
]

AT_RISK_PLAN = [
    ("get_customer", {"customer_id": "{customer_id}"}),
    ("account_metrics", {"customer_id": "{customer_id}"}),
    ("get_support_tickets", {"customer_id": "{customer_id}", "status": "open"}),
    ("get_order_history", {"customer_id": "{customer_id}", "last_n_days": 365}),
    ("search_knowledge_base", {"query": "service recovery late delivery complaint credit note"}),
    ("build_quote", {"customer_or_company": "{company}", "items": "{items}", "discount_pct": 0}),
    ("draft_email", {"to_name": "{contact_name}", "subject": "{subject}",
                     "purpose": "service_recovery", "key_points": "{key_points}"}),
    ("log_activity", {"customer_id": "{customer_id}", "activity_type": "task",
                      "summary": "{activity_summary}"}),
]

REVIEW_PLAN = [
    ("get_customer", {"customer_id": "{customer_id}"}),
    ("account_metrics", {"customer_id": "{customer_id}"}),
    ("get_order_history", {"customer_id": "{customer_id}", "last_n_days": 730}),
    ("get_support_tickets", {"customer_id": "{customer_id}"}),
    ("search_knowledge_base", {"query": "discount policy lead time"}),
]


# --------------------------------------------------------------------------
# The model
# --------------------------------------------------------------------------

class MockSalesLLM(BaseChatModel):
    """A deterministic 'sales analyst' language model for offline teaching."""

    model_name: str = "mock-sales-analyst-v1"
    temperature: float = 0.0
    verbose_trace: bool = True

    # Internal state lives in "private" attributes.  Pydantic models reject
    # plain `self.x = ...` assignment for undeclared fields, so we initialise
    # them in `model_post_init` and only ever *mutate* them afterwards.
    _plan: list = []
    _step: int = 0
    _facts: dict = {}
    _tool_names: list = []

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._reset_state()

    def _reset_state(self) -> None:
        object.__setattr__(self, "_plan", [])
        object.__setattr__(self, "_step", 0)
        object.__setattr__(self, "_facts", {})
        object.__setattr__(self, "_tool_names", [])

    @property
    def _llm_type(self) -> str:
        return "mock-sales-analyst"

    @property
    def _identifying_params(self) -> dict:
        return {"model_name": self.model_name}

    # --- LangChain integration points -------------------------------------
    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> Runnable:
        """A real provider turns tools into an API schema and sends it with the
        request.  Here we only remember the names so the trace prints nicely."""
        self._tool_names = [getattr(t, "name", str(t)) for t in tools]
        return self

    def with_structured_output(self, schema: Any, **kwargs: Any) -> Runnable:
        """Rule-based structured output: fills the schema from the plan facts."""
        from langchain_core.runnables import RunnableLambda

        def _produce(_input: Any) -> Any:
            data = self._structured_from_facts(schema)
            if hasattr(schema, "model_validate"):
                return schema.model_validate(data)
            return data

        return RunnableLambda(_produce)

    def _structured_from_facts(self, schema: Any) -> dict:
        f = self._facts
        fields = getattr(schema, "model_fields", {})
        out: dict[str, Any] = {}
        for name, field in fields.items():
            ann = str(field.annotation).lower()
            if name in ("lead_score", "score"):
                out[name] = int(f.get("lead_score", 0))
            elif name in ("grade",):
                out[name] = f.get("grade", "C")
            elif "qualified" in name or "existing" in name:
                out[name] = bool(f.get(name, f.get("sales_qualified", True)))
            elif name in ("company", "customer_id", "contact_name", "owner"):
                out[name] = f.get(name, "")
            elif "reason" in name or "risk" in name or "action" in name or "next" in name:
                out[name] = f.get(name, f.get("recommended_action", ""))
            elif "summary" in name or "brief" in name:
                out[name] = f.get("summary", "Mock summary.")
            elif "int" in ann:
                out[name] = 0
            elif "float" in ann:
                out[name] = 0.0
            elif "bool" in ann:
                out[name] = False
            elif "list" in ann:
                out[name] = f.get(name, [])
            else:
                out[name] = f.get(name, "")
        return out

    # --- generation --------------------------------------------------------
    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None,
                  **kwargs: Any) -> ChatResult:
        self._harvest_facts(messages)
        if not self._plan:
            object.__setattr__(self, "_plan", self._choose_plan(messages))
            object.__setattr__(self, "_step", 0)

        if self._step < len(self._plan):
            name, arg_template = self._plan[self._step]
            object.__setattr__(self, "_step", self._step + 1)
            # If the caller bound a subset of tools, skip plan steps the
            # agent is not allowed to take (read-only researcher, etc.).
            if self._tool_names and name not in self._tool_names:
                return self._generate(messages, stop, run_manager, **kwargs)
            args = self._fill(arg_template)
            if args is None:                     # precondition not met: skip
                return self._generate(messages, stop, run_manager, **kwargs)
            call_id = f"mock_{self._step:02d}_{name}"
            msg = AIMessage(
                content="",
                tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"}],
                additional_kwargs={},
                usage_metadata={"input_tokens": self._count(messages),
                                "output_tokens": 12,
                                "total_tokens": self._count(messages) + 12},
            )
            if self.verbose_trace:
                print(f"  [mock-llm] -> tool_call {name}({json.dumps(args, default=str)[:110]})")
            return ChatResult(generations=[ChatGeneration(message=msg)])

        text = self._final_answer(messages)
        msg = AIMessage(
            content=text,
            usage_metadata={"input_tokens": self._count(messages),
                            "output_tokens": len(text.split()),
                            "total_tokens": self._count(messages) + len(text.split())},
        )
        if self.verbose_trace:
            print(f"  [mock-llm] -> final answer ({len(text.split())} words)")
        return ChatResult(generations=[ChatGeneration(message=msg)])

    # --- helpers -----------------------------------------------------------
    @staticmethod
    def _count(messages: list[BaseMessage]) -> int:
        return sum(len(str(getattr(m, "content", ""))) for m in messages) // 4

    def _harvest_facts(self, messages: list[BaseMessage]) -> None:
        """Read tool outputs back out of the message history - exactly the way a
        real model would 'see' them."""
        f = self._facts
        for m in messages:
            if not isinstance(m, ToolMessage):
                continue
            try:
                payload = json.loads(m.content) if isinstance(m.content, str) else m.content
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            name = getattr(m, "name", "") or ""
            if name == "get_inbox_leads" and "leads" in payload:
                leads = payload["leads"]
                if leads:
                    lead = leads[0] if len(leads) == 1 else self._pick_lead(leads, f)
                    f.update(
                        {
                            "lead_id": lead.get("lead_id"),
                            "company": lead.get("company"),
                            "contact_name": lead.get("contact_name"),
                            "contact_email": lead.get("contact_email"),
                            "employees": lead.get("employees", 50),
                            "budget_eur": float(lead.get("budget_eur") or 0),
                            "urgency": lead.get("urgency", "medium"),
                            "message": lead.get("message", ""),
                            "country": lead.get("country", ""),
                        }
                    )
            if name == "score_lead":
                for k in ("lead_score", "grade", "sales_qualified", "recommended_action", "flags", "reasons"):
                    if k in payload:
                        f[k] = payload[k]
            if name in ("get_customer", "account_metrics"):
                for k in ("customer_id", "company", "segment", "owner", "health",
                          "contact_name", "contact_email",
                          "total_revenue_eur", "avg_order_value_eur", "days_since_last_order",
                          "churn_risk_score", "churn_risk_band", "risk_reasons",
                          "open_support_tickets", "revenue_trend_pct", "order_count"):
                    if k in payload and k not in ("company",) or (k == "company" and "company" not in f):
                        f[k] = payload[k]
            if name == "get_support_tickets" and "tickets" in payload:
                f["tickets"] = payload["tickets"]
            if name == "get_order_history" and "orders" in payload:
                f["orders"] = payload["orders"]
            if name == "build_quote":
                for k in ("total_eur", "net_eur", "subtotal_eur", "earliest_full_delivery",
                          "discount_applied_pct", "policy_notes", "lines"):
                    if k in payload:
                        f.setdefault("quote_" + k, payload[k])
            if name == "search_customers" and "customers" in payload and payload["customers"]:
                f.setdefault("matched_customer_id", payload["customers"][0]["customer_id"])
            if name == "create_pipeline_record" and "pipeline_id" in payload:
                f["pipeline_id"] = payload["pipeline_id"]
            if name == "draft_email" and "draft" in payload:
                f["draft"] = payload["draft"]

    def _pick_lead(self, leads: list[dict], facts: dict) -> dict:
        wanted = facts.get("requested_lead_id") or facts.get("lead_id")
        if wanted:
            for l in leads:
                if str(l.get("lead_id", "")).upper() == str(wanted).upper():
                    return l
        # highest budget wins - a simple, explainable default
        return max(leads, key=lambda l: float(l.get("budget_eur") or 0))

    def _choose_plan(self, messages: list[BaseMessage]) -> list:
        text = " ".join(str(getattr(m, "content", "")) for m in messages).lower()
        cid = re.findall(r"\bc-\d{4}\b", text)
        if cid:
            self._facts["customer_id"] = cid[-1].upper()
        lid = re.findall(r"\bl-\d{4}\b", text)
        if lid:
            self._facts["requested_lead_id"] = lid[-1].upper()
            self._facts["lead_id"] = lid[-1].upper()
        if "inbox" in text or "lead" in text or "qualif" in text:
            return LEAD_PLAN
        if any(w in text for w in ("at risk", "at-risk", "churn", "unhappy", "win back",
                                   "win-back", "service recovery", "complaint", "save")):
            return AT_RISK_PLAN
        if cid:
            return REVIEW_PLAN
        return []

    def _fill(self, template: Any) -> Any:
        """Resolve {placeholders} against the facts we have harvested.  Returns
        None when a hard prerequisite is missing, so the step is skipped."""
        f = self._facts
        if isinstance(template, dict):
            out = {}
            for k, v in template.items():
                r = self._fill(v)
                if r is None:
                    return None
                out[k] = r
            return out
        if isinstance(template, list):
            return [self._fill(v) for v in template]
        if not isinstance(template, str):
            return template

        if template == "{customer_id}":
            cid = f.get("customer_id") or f.get("matched_customer_id")
            return cid if cid else None
        if template == "{lead_id}":
            return f.get("requested_lead_id") or f.get("lead_id") or ""
        if template == "{company}":
            return f.get("company") or "Unknown Company"
        if template == "{is_existing}":
            return bool(f.get("matched_customer_id") or f.get("customer_id"))
        if template == "{kb_query}":
            flags = " ".join(f.get("flags", [])).lower()
            if "at-risk" in flags or "complaint" in flags:
                return "service recovery late delivery complaint credit note"
            if "tender" in flags or "minimum order" in flags:
                return "qualification minimum order value tender framework"
            return "discount policy lead time delivery quote"
        if template == "{category}":
            return "Desks" if f.get("budget_eur", 0) >= 20000 else "Seating"
        if template == "{items}":
            return self._suggest_items()
        if template == "{discount}":
            b = float(f.get("budget_eur", 0) or 0)
            return 10.0 if b >= 50000 else (5.0 if b >= 10000 else 0.0)
        if template == "{contact_name}":
            return f.get("contact_name") or "there"
        if template == "{contact_email}":
            return f.get("contact_email") or ""
        if template == "{owner}":
            return f.get("owner") or "Priya Raman"
        if template == "{subject}":
            if f.get("grade") == "A":
                return f"Quote and next steps for {f.get('company', 'your office project')}"
            return f"Your enquiry - {f.get('company', 'Northwind Supply Co.')}"
        if template == "{purpose}":
            return "quote" if f.get("sales_qualified", True) else "nurture"
        if template == "{key_points}":
            return self._key_points()
        if template == "{notes}":
            return (f"Auto-qualified by Revenue Copilot: grade {f.get('grade', '?')} "
                    f"(score {f.get('lead_score', '?')}).")
        if template == "{activity_summary}":
            return (f"Revenue Copilot qualified this lead as grade {f.get('grade', '?')} "
                    f"(score {f.get('lead_score', '?')}/100) and prepared a draft reply.")
        if template.startswith("{") and template.endswith("}"):
            return f.get(template[1:-1], "")
        return template

    def _suggest_items(self) -> list[dict]:
        budget = float(self._facts.get("budget_eur", 0) or 0)
        if budget >= 150000:
            return [{"sku": "SKU-DS-320", "qty": 200}, {"sku": "SKU-ST-520", "qty": 10},
                    {"sku": "SKU-ST-500", "qty": 1}]
        if budget >= 40000:
            return [{"sku": "SKU-DS-300", "qty": 40}, {"sku": "SKU-CH-120", "qty": 40}]
        if budget >= 10000:
            return [{"sku": "SKU-CH-120", "qty": 25}]
        return [{"sku": "SKU-CH-100", "qty": 10}]

    def _key_points(self) -> list[str]:
        f = self._facts
        pts = []
        if "quote_total_eur" in f:
            pts.append(f"Total including 19% VAT: EUR {f['quote_total_eur']:,.2f}")
        if f.get("quote_discount_applied_pct"):
            pts.append(f"Volume discount applied: {f['quote_discount_applied_pct']}%")
        if "quote_earliest_full_delivery" in f:
            pts.append(f"Earliest complete delivery: {f['quote_earliest_full_delivery']}")
        if f.get("churn_risk_band") in ("high", "medium"):
            pts.append("We have reviewed your open tickets and are taking action on each one")
        if f.get("flags"):
            pts.append("Your account has been flagged for priority handling by our sales director")
        if not pts:
            pts.append("We can supply the full range from our European warehouse")
        return pts[:5]

    def _final_answer(self, messages: list[BaseMessage]) -> str:
        f = self._facts
        if not f:
            return (
                "[mock model] I am Revenue Copilot, an offline stand-in for a hosted LLM. "
                "Give me a customer id (C-1006) or a lead id (L-2005) and I will use tools."
            )
        lines = ["## Revenue Copilot - summary (mock model)", ""]
        if f.get("lead_id"):
            lines += [
                f"**Lead:** {f.get('company')} ({f.get('lead_id')})",
                f"**Qualification:** grade {f.get('grade', '?')} - score {f.get('lead_score', '?')}/100 "
                f"({'sales-qualified' if f.get('sales_qualified') else 'not qualified'})",
                f"**Recommended action:** {f.get('recommended_action', 'n/a')}",
            ]
        if f.get("customer_id"):
            lines += [
                f"**Account:** {f.get('company', '')} ({f.get('customer_id')})",
                f"**Revenue:** EUR {f.get('total_revenue_eur', 0):,.2f} over "
                f"{f.get('order_count', 0)} orders (AOV EUR {f.get('avg_order_value_eur', 0):,.2f})",
                f"**Churn risk:** {f.get('churn_risk_score', 0)}/100 ({f.get('churn_risk_band', '?')})",
            ]
            if f.get("risk_reasons"):
                lines.append("**Why:** " + "; ".join(f["risk_reasons"]))
        if "quote_total_eur" in f:
            lines.append(f"**Quote prepared:** EUR {f['quote_total_eur']:,.2f} incl. VAT, "
                         f"delivery from {f.get('quote_earliest_full_delivery', 'n/a')}")
        if f.get("pipeline_id"):
            lines.append(f"**Pipeline record:** {f['pipeline_id']} created")
        if f.get("draft"):
            lines += ["", "**Draft email (not sent):**", "", "> " + f["draft"].replace("\n", "\n> ")]
        lines += ["", "_Generated offline by MockSalesLLM - swap in a real model to compare._"]
        return "\n".join(lines)

    # --- bookkeeping used by the notebooks ---------------------------------
    def reset(self) -> "MockSalesLLM":
        """Start a fresh plan.  Call this between runs so the trace is clean."""
        self._reset_state()
        return self

    @property
    def facts(self) -> dict:
        return dict(self._facts)
