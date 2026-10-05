"""
Synthetic CRM data for the "Revenue Copilot" teaching scenario.

The story
---------
Northwind Supply Co. is a (fictional) B2B distributor of office furniture and
supplies.  It has ~30 accounts, 2 years of orders, a small knowledge base, and
an inbox full of inbound leads that the sales team never gets round to answering.

Everything here is generated deterministically from a fixed random seed, so
every student in the class gets exactly the same numbers.  That matters: it
means the exercises have stable, checkable answers.

No file is written until `write_all()` is called, and no network is needed.
"""

from __future__ import annotations

import csv
import os
import random
from datetime import date, timedelta

# --------------------------------------------------------------------------
# Fixed reference dates so the dataset never "ages" between teaching sessions
# --------------------------------------------------------------------------
TODAY = date(2026, 9, 30)
DATA_START = TODAY - timedelta(days=730)  # two years of order history

SEED = 20260930

# --------------------------------------------------------------------------
# Reference data
# --------------------------------------------------------------------------

# (sku, name, category, unit_price_eur, stock, lead_time_days)
PRODUCTS = [
    ("SKU-CH-100", "Ergo Pro Task Chair", "Seating", 289.00, 140, 5),
    ("SKU-CH-120", "Ergo Pro Task Chair (Mesh)", "Seating", 319.00, 62, 5),
    ("SKU-CH-210", "Executive Leather Chair", "Seating", 649.00, 18, 14),
    ("SKU-DS-300", "Sit-Stand Desk 160cm", "Desks", 749.00, 35, 10),
    ("SKU-DS-320", "Sit-Stand Desk 180cm (Dual motor)", "Desks", 899.00, 12, 17),
    ("SKU-DS-410", "Fixed Desk 140cm", "Desks", 329.00, 88, 7),
    ("SKU-ST-500", "Acoustic Meeting Pod (4p)", "Storage & Acoustics", 4250.00, 4, 35),
    ("SKU-ST-520", "Acoustic Phone Booth (1p)", "Storage & Acoustics", 2150.00, 7, 28),
    ("SKU-CB-600", "Storage Cabinet 3-drawer", "Storage & Acoustics", 419.00, 51, 9),
    ("SKU-LT-700", "LED Monitor Arm", "Accessories", 129.00, 220, 3),
    ("SKU-LT-710", "Laptop Riser", "Accessories", 79.00, 310, 3),
    ("SKU-PP-800", "A4 Copy Paper (box of 10 reams)", "Office Supplies", 42.50, 640, 2),
    ("SKU-PP-810", "Toner Cartridge CF-400", "Office Supplies", 88.90, 96, 4),
    ("SKU-PP-820", "Breakroom Bundle (coffee + snacks)", "Office Supplies", 156.00, 74, 4),
]

SEGMENTS = ["Enterprise", "Mid-Market", "SMB", "Public Sector"]
REGIONS = ["DACH", "Nordics", "Benelux", "UK & Ireland", "Southern Europe"]
OWNERS = ["Priya Raman", "Tom Becker", "Sofia Almeida", "Jack O'Neill"]
PLANS = ["Basic", "Growth", "Scale"]

# (customer_id, company, contact_name, contact_email, segment, region,
#  owner, plan, employee_count, signup_date, health, notes)
CUSTOMERS = [
    ("C-1001", "Acme Logistik GmbH", "Hannah Vogel", "h.vogel@acme-logistik.example", "Enterprise", "DACH", "Priya Raman", "Scale", 2400, "2022-03-14", "green", "HQ in Hamburg. Prefers delivery in Q1 budget cycle."),
    ("C-1002", "Bluepeak Analytics", "Marcus Feld", "marcus@bluepeak.example", "Mid-Market", "UK & Ireland", "Tom Becker", "Growth", 180, "2023-01-09", "green", "Fast-growing data consultancy; buys desks in batches of 20."),
    ("C-1003", "Cedar & Stone Architects", "Nina Okafor", "nina@cedarstone.example", "SMB", "UK & Ireland", "Tom Becker", "Basic", 24, "2023-08-02", "amber", "Price sensitive; asked twice for a discount."),
    ("C-1004", "Delta Foods NV", "Luc Peeters", "luc.peeters@deltafoods.example", "Enterprise", "Benelux", "Sofia Almeida", "Scale", 5100, "2021-11-23", "green", "Annual framework contract, renewed each November."),
    ("C-1005", "Everline Insurance", "Rita Kowalski", "r.kowalski@everline.example", "Enterprise", "DACH", "Priya Raman", "Scale", 3300, "2022-06-30", "amber", "Procurement process is slow (6-8 weeks). Needs compliance docs."),
    ("C-1006", "Fjord Energi AS", "Lars Haugen", "lars.haugen@fjordenergi.example", "Mid-Market", "Nordics", "Sofia Almeida", "Growth", 420, "2023-04-17", "red", "Unhappy about a late delivery in June. At risk of churn."),
    ("C-1007", "Greenline Retail", "Amira Haddad", "amira@greenline.example", "Mid-Market", "Southern Europe", "Jack O'Neill", "Growth", 610, "2022-09-05", "green", "Opens 3 new stores per quarter; steady repeat orders."),
    ("C-1008", "Helix Biotech", "Daniel Roth", "d.roth@helixbio.example", "SMB", "DACH", "Priya Raman", "Basic", 45, "2024-02-11", "amber", "Lab furniture enquiry pending; waiting on budget approval."),
    ("C-1009", "Ironwood Construction", "Sean Duffy", "sean@ironwood.example", "Mid-Market", "UK & Ireland", "Tom Becker", "Growth", 260, "2022-12-01", "green", "Site offices: buys pods and booths in volume."),
    ("C-1010", "Juniper Health Clinics", "Dr. Eva Lindqvist", "eva.lindqvist@juniperhealth.example", "Public Sector", "Nordics", "Sofia Almeida", "Scale", 1800, "2021-07-19", "green", "Tender-driven purchasing. Requires accessibility certification."),
    ("C-1011", "Kite Media Group", "Owen Blake", "owen@kitemedia.example", "SMB", "UK & Ireland", "Tom Becker", "Basic", 38, "2024-05-22", "red", "No orders for 9 months. Last invoice dispute unresolved."),
    ("C-1012", "Lumen Schools Trust", "Grace Mbeki", "grace@lumenscholars.example", "Public Sector", "UK & Ireland", "Jack O'Neill", "Growth", 950, "2023-02-27", "green", "Buys in August for the September term."),
    ("C-1013", "Meridian Bank", "Claudia Fischer", "c.fischer@meridianbank.example", "Enterprise", "DACH", "Priya Raman", "Scale", 8200, "2021-05-08", "green", "Largest account by revenue. Strict security questionnaire."),
    ("C-1014", "Northgate Hotels", "Pedro Sousa", "pedro.sousa@northgate.example", "Mid-Market", "Southern Europe", "Jack O'Neill", "Growth", 700, "2023-06-14", "amber", "Seasonal buyer; quiet in Q4."),
    ("C-1015", "Orion Robotics", "Yuki Tanaka", "yuki@orionrobotics.example", "SMB", "Benelux", "Sofia Almeida", "Basic", 62, "2024-08-30", "green", "New logo. Interested in sit-stand desks for the lab."),
    ("C-1016", "Pinetail Publishing", "Fiona Marsh", "fiona@pinetail.example", "SMB", "UK & Ireland", "Tom Becker", "Basic", 19, "2023-10-03", "red", "Downgraded plan in May. Low engagement."),
    ("C-1017", "Quartz Manufacturing", "Milan Horak", "m.horak@quartzmfg.example", "Enterprise", "DACH", "Priya Raman", "Scale", 4100, "2022-01-25", "green", "Factory floor seating every 18 months."),
    ("C-1018", "Riverbend Legal", "Anne Dubois", "anne@riverbendlegal.example", "Mid-Market", "Benelux", "Sofia Almeida", "Growth", 140, "2023-03-12", "green", "Prefers premium finishes; high average order value."),
    ("C-1019", "Solstice Energy", "Tomas Nyman", "tomas@solstice.example", "Mid-Market", "Nordics", "Sofia Almeida", "Growth", 310, "2022-10-08", "amber", "Considering a competitor on price."),
    ("C-1020", "Tidewater Shipping", "Rui Costa", "rui@tidewater.example", "Enterprise", "Southern Europe", "Jack O'Neill", "Scale", 2900, "2021-09-15", "green", "Port offices across 6 countries."),
    ("C-1021", "Umber Design Studio", "Lea Braun", "lea@umberdesign.example", "SMB", "DACH", "Priya Raman", "Basic", 12, "2024-11-04", "green", "Small but very responsive; refers other studios."),
    ("C-1022", "Vantage Sports Ltd", "Chris Nolan", "chris@vantagesports.example", "Mid-Market", "UK & Ireland", "Tom Becker", "Growth", 230, "2023-07-21", "amber", "Two orders returned in 2026 - quality complaints."),
    ("C-1023", "Westfield Council", "Sarah Jennings", "s.jennings@westfield.example", "Public Sector", "UK & Ireland", "Jack O'Neill", "Scale", 3600, "2021-12-06", "green", "Framework agreement expires 2027-03-31."),
    ("C-1024", "Xenon Labs", "Arun Patel", "arun@xenonlabs.example", "SMB", "Benelux", "Sofia Almeida", "Basic", 28, "2025-01-18", "green", "Start-up; small orders but growing fast."),
    ("C-1025", "Yellowbrick Logistics", "Marta Nowak", "marta@yellowbrick.example", "Mid-Market", "DACH", "Priya Raman", "Growth", 480, "2022-08-11", "green", "Depot refits every spring."),
    ("C-1026", "Zephyr Airlines", "Kenji Mori", "kenji@zephyrair.example", "Enterprise", "Nordics", "Sofia Almeida", "Scale", 6700, "2021-06-02", "amber", "Head office refurb paused pending merger news."),
    ("C-1027", "Aurora Cosmetics", "Elise Grand", "elise@auroracosm.example", "Mid-Market", "Southern Europe", "Jack O'Neill", "Growth", 205, "2023-09-29", "green", "Retail rollout in 4 countries planned for 2027."),
    ("C-1028", "Bastion Security", "Viktor Ivanov", "viktor@bastionsec.example", "SMB", "DACH", "Tom Becker", "Basic", 55, "2024-04-06", "red", "Payment 45 days overdue. Credit hold applies."),
]

# --------------------------------------------------------------------------
# Inbound leads (the agent's raw material)
# --------------------------------------------------------------------------
INBOX = [
    {
        "lead_id": "L-2001",
        "company": "Cascade Interiors BV",
        "contact_name": "Bram de Vries",
        "contact_email": "bram@cascadeinteriors.example",
        "country": "Netherlands",
        "employees": 240,
        "budget_eur": 45000,
        "urgency": "high",
        "received": "2026-09-28",
        "source": "web_form",
        "message": (
            "We are refitting two floors of our Amsterdam office (about 120 "
            "workstations) and need sit-stand desks plus task chairs delivered "
            "before the end of November. We also want acoustic pods for the "
            "open-plan area. Budget is around EUR 45k. Can you send a quote "
            "and confirm lead times?"
        ),
    },
    {
        "lead_id": "L-2002",
        "company": "Meridian Bank",
        "contact_name": "Claudia Fischer",
        "contact_email": "c.fischer@meridianbank.example",
        "country": "Germany",
        "employees": 8200,
        "budget_eur": 120000,
        "urgency": "medium",
        "received": "2026-09-29",
        "source": "email",
        "message": (
            "Our Frankfurt trading floor is replacing 60 chairs next quarter. "
            "Please quote the Ergo Pro Task Chair (mesh) with monitor arms, and "
            "confirm you can meet our 2027 Q1 delivery window. We will need "
            "the updated security questionnaire completed."
        ),
    },
    {
        "lead_id": "L-2003",
        "company": "Fjord Energi AS",
        "contact_name": "Lars Haugen",
        "contact_email": "lars.haugen@fjordenergi.example",
        "country": "Norway",
        "employees": 420,
        "budget_eur": 8000,
        "urgency": "high",
        "received": "2026-09-29",
        "source": "email",
        "message": (
            "Honestly we are close to moving our office supply contract to a "
            "competitor. The June delivery was three weeks late and nobody "
            "followed up. If you want to keep our business, I need a concrete "
            "plan this week, plus a quote for 25 replacement chairs."
        ),
    },
    {
        "lead_id": "L-2004",
        "company": "Pixel & Pine Studio",
        "contact_name": "Tara Whelan",
        "contact_email": "tara@pixelandpine.example",
        "country": "Ireland",
        "employees": 6,
        "budget_eur": 900,
        "urgency": "low",
        "received": "2026-09-27",
        "source": "web_form",
        "message": (
            "Tiny design studio, just looking for two laptop risers and maybe "
            "a box of paper. Do you have a minimum order value?"
        ),
    },
    {
        "lead_id": "L-2005",
        "company": "Sable Pharmaceuticals",
        "contact_name": "Dr. Ingrid Sauer",
        "contact_email": "i.sauer@sablepharma.example",
        "country": "Switzerland",
        "employees": 1500,
        "budget_eur": 210000,
        "urgency": "high",
        "received": "2026-09-30",
        "source": "referral",
        "message": (
            "Referred by Juniper Health. We are building a new research campus "
            "in Basel: 300 workstations, 12 acoustic phone booths and a "
            "4-person meeting pod, phased delivery over 2027. Please provide a "
            "budgetary quote and confirm whether your products meet EN 1335 "
            "and accessibility requirements. Procurement closes in 3 weeks."
        ),
    },
]

# --------------------------------------------------------------------------
# Support cases (used by the knowledge-base / churn exercises)
# --------------------------------------------------------------------------
SUPPORT_CASES = [
    ("T-9001", "C-1006", "2026-06-12", "late_delivery", "open",
     "Order #O-4417 (20 task chairs) delivered 21 days after the promised date; "
     "customer had to rent temporary seating. Requested a written explanation "
     "and compensation."),
    ("T-9002", "C-1006", "2026-07-02", "late_delivery", "closed",
     "Follow-up call promised but never made. Customer escalated to their "
     "account manager. Still no credit note issued."),
    ("T-9003", "C-1011", "2026-01-20", "billing_dispute", "open",
     "Invoice INV-88214 charged for 12 monitor arms, customer received 10. "
     "Dispute unresolved for 8 months; customer stopped ordering."),
    ("T-9004", "C-1022", "2026-04-03", "product_quality", "closed",
     "Two Ergo Pro chairs arrived with damaged gas lifts. Replaced under warranty."),
    ("T-9005", "C-1022", "2026-08-19", "product_quality", "open",
     "Third quality complaint this year. Customer asked whether the batch has "
     "a known defect. Awaiting supplier report."),
    ("T-9006", "C-1016", "2026-05-11", "plan_downgrade", "closed",
     "Downgraded from Growth to Basic, citing budget cuts. No win-back attempt "
     "was made."),
    ("T-9007", "C-1028", "2026-08-25", "billing_dispute", "open",
     "Payment 45 days overdue; account placed on credit hold. Customer disputes "
     "the delivery address on the invoice."),
    ("T-9008", "C-1003", "2026-09-05", "pricing", "closed",
     "Requested a 15% discount on a 10-desk order. Approved at 8%."),
]

KNOWLEDGE_BASE = [
    {
        "kb_id": "KB-01",
        "title": "Standard lead times and delivery windows",
        "tags": ["delivery", "lead time", "logistics"],
        "text": (
            "Standard lead times: office supplies 2-4 days, accessories 3 days, "
            "seating 5 days, desks 7-17 days, acoustic pods and phone booths "
            "28-35 days (built to order). Orders above EUR 25,000 qualify for a "
            "named delivery coordinator and a guaranteed delivery window of +/- 2 "
            "working days. Express delivery (+15% surcharge) is available for "
            "seating and accessories only."
        ),
    },
    {
        "kb_id": "KB-02",
        "title": "Discount and pricing policy",
        "tags": ["discount", "pricing", "policy"],
        "text": (
            "Discount authority: up to 5% for orders over EUR 10,000; up to 10% "
            "for orders over EUR 50,000; up to 15% requires sales director "
            "approval. Public Sector tenders follow the published framework "
            "price with no additional discount. Never discount below the "
            "floor price in the product catalogue. Volume tier discounts do not "
            "stack with seasonal promotions."
        ),
    },
    {
        "kb_id": "KB-03",
        "title": "Service recovery playbook (late or damaged deliveries)",
        "tags": ["complaint", "late delivery", "churn", "service recovery", "escalation"],
        "text": (
            "When a customer reports a late or damaged delivery: (1) acknowledge "
            "within one business day and apologise without excuses; (2) issue a "
            "credit note of 10% of the affected order value for delays over 10 "
            "working days, or 15% plus free express delivery for delays over 20 "
            "working days; (3) offer a named delivery coordinator for the next "
            "two orders at no cost; (4) schedule a call with the account manager "
            "within 5 working days; (5) log everything in the CRM. Accounts with "
            "an unresolved complaint older than 60 days must be flagged to the "
            "sales director."
        ),
    },
    {
        "kb_id": "KB-04",
        "title": "Lead qualification criteria (BANT-lite)",
        "tags": ["qualification", "lead", "scoring", "BANT"],
        "text": (
            "A lead is sales-qualified when it has: a budget indication, a "
            "decision timeframe within 6 months, at least 20 employees or an "
            "order value above EUR 5,000, and a named contact. Leads below the "
            "EUR 1,000 minimum order value are routed to the self-service web "
            "shop. Enterprise and Public Sector leads always get a human owner "
            "assigned within one business day."
        ),
    },
    {
        "kb_id": "KB-05",
        "title": "Compliance and certifications",
        "tags": ["compliance", "certification", "security", "accessibility", "EN 1335"],
        "text": (
            "Seating is certified to EN 1335-1/2/3 and BS 5459. Desks meet "
            "EN 527 and the GS safety mark. Acoustic pods carry the CE mark and "
            "a fire rating of class B-s1,d0. All products have a 5-year warranty "
            "(2 years for office supplies). The current ISO 9001 and ISO 14001 "
            "certificates, the security questionnaire and the EPD declarations "
            "are in the sales portal under Documents > Compliance."
        ),
    },
    {
        "kb_id": "KB-06",
        "title": "Credit hold and overdue payment procedure",
        "tags": ["payment", "credit hold", "billing", "overdue"],
        "text": (
            "Accounts more than 30 days overdue are placed on credit hold: no "
            "new orders may be quoted until the balance is cleared or a payment "
            "plan is agreed by finance. The agent must never promise delivery "
            "dates to an account on credit hold; it should route the request to "
            "finance and inform the customer of the outstanding balance."
        ),
    },
    {
        "kb_id": "KB-07",
        "title": "Public Sector tender requirements",
        "tags": ["public sector", "tender", "framework", "procurement"],
        "text": (
            "Public Sector customers buy through framework agreements. Quotes "
            "must reference the framework number, be valid for 120 days, and "
            "include accessibility statements. Tenders above EUR 100,000 need "
            "legal review before submission and a 10 working day turnaround."
        ),
    },
]

ACTIVITY_TYPES = ["call", "email", "meeting", "note", "task"]


# --------------------------------------------------------------------------
# Generation helpers
# --------------------------------------------------------------------------

def _daterange_days(start: date, end: date) -> int:
    return (end - start).days


def build_orders(rng: random.Random) -> list[dict]:
    """Two years of plausible order history, biased by customer health."""
    rows: list[dict] = []
    oid = 4000

    # How often each health state orders, per customer, over two years
    frequency = {"green": (10, 18), "amber": (5, 10), "red": (1, 4)}
    # Recency: red accounts have gone quiet recently
    recency_cap_days = {"green": 70, "amber": 160, "red": 260}

    for c in CUSTOMERS:
        cid, _, _, _, segment, _, _, _, employees, signup, health, _ = c
        lo, hi = frequency[health]
        n_orders = rng.randint(lo, hi)
        # bigger companies order a bit more
        if segment in ("Enterprise", "Public Sector"):
            n_orders += rng.randint(2, 6)

        first_allowed = max(DATA_START, date.fromisoformat(signup))
        # "red" accounts have gone quiet: their newest order is months old
        end_for_this = TODAY - timedelta(days=rng.randint(5, recency_cap_days[health]))
        span = max(30, _daterange_days(first_allowed, end_for_this))

        for _ in range(n_orders):
            oid += 1
            order_date = first_allowed + timedelta(days=rng.randint(0, span))
            n_lines = rng.randint(1, 4)
            lines = rng.sample(PRODUCTS, k=min(n_lines, len(PRODUCTS)))
            total = 0.0
            line_notes = []
            for sku, name, _cat, price, _stock, _lt in lines:
                if segment in ("Enterprise", "Public Sector"):
                    qty = rng.randint(2, 22)
                elif segment == "Mid-Market":
                    qty = rng.randint(1, 10)
                else:
                    qty = rng.randint(1, 3)
                line_total = round(qty * price, 2)
                total += line_total
                line_notes.append(f"{qty} x {sku}")
            status = rng.choices(
                ["delivered", "delivered", "delivered", "shipped", "processing", "cancelled"],
                weights=[70, 10, 5, 6, 6, 3],
            )[0]
            rows.append(
                {
                    "order_id": f"O-{oid}",
                    "customer_id": cid,
                    "date": order_date.isoformat(),
                    "items": " | ".join(line_notes),
                    "total_eur": round(total, 2),
                    "status": status,
                    "owner": c[6],
                }
            )

    # Guarantee the story beats used by the exercises
    rows.append(
        {
            "order_id": "O-4417",
            "customer_id": "C-1006",
            "date": "2026-05-20",
            "items": "20 x SKU-CH-100",
            "total_eur": 5780.00,
            "status": "delivered",
            "owner": "Sofia Almeida",
        }
    )
    rows.sort(key=lambda r: r["date"])
    return rows


def build_activities(rng: random.Random) -> list[dict]:
    rows = []
    aid = 500
    for c in CUSTOMERS:
        cid = c[0]
        owner = c[6]
        for _ in range(rng.randint(2, 7)):
            aid += 1
            when = TODAY - timedelta(days=rng.randint(1, 300))
            rows.append(
                {
                    "activity_id": f"A-{aid}",
                    "customer_id": cid,
                    "date": when.isoformat(),
                    "type": rng.choice(ACTIVITY_TYPES),
                    "owner": owner,
                    "summary": rng.choice(
                        [
                            "Quarterly check-in call",
                            "Sent updated price list",
                            "Discussed upcoming office move",
                            "Reviewed open support tickets",
                            "Contract renewal conversation",
                            "Left voicemail, no answer",
                            "Demo of the new acoustic pod range",
                        ]
                    ),
                }
            )
    return rows


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

TABLES = ["customers", "orders", "products", "inbox_leads", "support_cases",
          "knowledge_base", "activities", "pipeline"]

PIPELINE_COLUMNS = ["pipeline_id", "company", "contact_name", "contact_email",
                    "stage", "estimated_value_eur", "owner", "created", "notes"]


def all_tables() -> dict[str, list[dict]]:
    """Return every table as a list of dicts (deterministic)."""
    rng = random.Random(SEED)
    products = [
        {"sku": s, "name": n, "category": c, "unit_price_eur": p, "stock": st, "lead_time_days": lt}
        for (s, n, c, p, st, lt) in PRODUCTS
    ]
    customers = [
        {
            "customer_id": cid, "company": comp, "contact_name": cn, "contact_email": ce,
            "segment": seg, "region": reg, "owner": own, "plan": plan,
            "employee_count": emp, "signup_date": sd, "health": h, "notes": notes,
        }
        for (cid, comp, cn, ce, seg, reg, own, plan, emp, sd, h, notes) in CUSTOMERS
    ]
    return {
        "customers": customers,
        "orders": build_orders(rng),
        "products": products,
        "inbox_leads": INBOX,
        "support_cases": [
            {"ticket_id": t, "customer_id": c, "opened": o, "category": cat, "status": s, "summary": summ}
            for (t, c, o, cat, s, summ) in SUPPORT_CASES
        ],
        "knowledge_base": KNOWLEDGE_BASE,
        "activities": build_activities(rng),
        "pipeline": [],   # created empty; the agent appends records to it
    }


def write_all(data_dir: str) -> list[str]:
    """Write every table to `<data_dir>/<table>.csv`. Returns the paths."""
    os.makedirs(data_dir, exist_ok=True)
    tables = all_tables()
    written = []
    for name, rows in tables.items():
        path = os.path.join(data_dir, f"{name}.csv")
        if not rows:
            if name == "pipeline":
                # header-only file so pipeline counts start at zero
                with open(path, "w", newline="", encoding="utf-8") as fh:
                    csv.DictWriter(fh, fieldnames=PIPELINE_COLUMNS).writeheader()
                written.append(path)
            continue
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        written.append(path)
    return written


def summary(data_dir: str) -> dict:
    """Row counts per table, used by the setup cell's self-check."""
    import pandas as pd

    out = {}
    for name in TABLES:
        path = os.path.join(data_dir, f"{name}.csv")
        if os.path.exists(path):
            out[name] = len(pd.read_csv(path))
        else:
            out[name] = 0
    return out


if __name__ == "__main__":
    here = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    for p in write_all(here):
        print("wrote", p)
    print(summary(here))
