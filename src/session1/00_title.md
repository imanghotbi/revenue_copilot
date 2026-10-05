# Session 1 — From LLM to Agent

### *Building a Revenue Copilot for Northwind Supply Co.*

<a name="top"></a>

| | |
|---|---|
| **Course** | Introduction to AI Agents |
| **Session** | 1 of 2 (≈ 2 hours, with breaks) |
| **Scenario** | A fictional B2B office-furniture distributor with a sales problem |
| **Stack** | Python · Hugging Face · pandas · LangChain / LangGraph from §6 on |
| **Audience** | Mixed: some Python is enough. New to ML? Read the 🧠 blocks and run the 💻 cells. Comfortable with Python? Do every ✍️ exercise. |
| **Runs in** | Google Colab, free tier. **No GPU needed. No payment needed.** |
| **API keys** | Optional — everything runs offline in `mock` mode |

---

## The scenario

**Northwind Supply Co.** sells office furniture and supplies to 28 business
accounts across Europe: chairs, sit-stand desks, acoustic meeting pods, printer
toner, breakroom bundles. Two years of order history, €4.6M in revenue, four
account managers.

The sales team has a problem you will recognise:

> **The inbox is winning.**

- 90 inbound enquiries a month arrive. Each one needs the same treatment: *is
  this company already a customer? what do they buy? is the budget real? does
  our policy allow that discount? what can we actually deliver by when?*
- That is 12–20 minutes of clicking between CRM, catalogue, spreadsheets and the
  policy handbook — **per lead**.
- So the team does what every overloaded team does: it answers the loudest email
  and lets the rest age. Four accounts are quietly drifting towards churn. One of
  them has an unresolved complaint that is **110 days old**.

Your job over two sessions is to build **Revenue Copilot**: an agent that reads
the inbox, pulls the facts from the CRM, applies company policy, prepares a
quote and a draft reply, logs everything, and hands a human something worth
approving.

By the end of Session 2 you will have a number a manager can argue with —
**hours and euros saved per month** — and an honest list of the ways the agent
can be wrong.

---

## What you will be able to do after this session

1. Explain, precisely, the difference between *calling an LLM* and *running an agent*.
2. Load a model from Hugging Face and see with your own eyes what a chat
   template, a token and a context window are.
3. Read a LangChain **tool schema** — the JSON that tells a model what it is allowed to do.
4. **Run a working tool-calling agent with the framework** (`bind_tools`,
   `create_agent`, LangGraph `ToolNode`) on the real CRM.

Point 4 is the important one. The loop is the same one from §2 — the framework
is *somebody else's well-tested version of it, plus state management.* Session 2
then wraps that loop in routing, approval gates and memory.

---

## Session map

| # | Section | ~min | Hands-on |
|---|---------|------|----------|
| 1 | Setup and the CRM | 10 | ✓ |
| 2 | What an agent is (and is not) | 15 | — |
| 3 | Loading a model from Hugging Face | 20 | ✓ |
| 4 | Chat templates, tokens, context windows | 15 | ✓ |
| 5 | A hosted model: HF Inference Providers | 10 | ✓ |
| 6 | Tools: the JSON contract | 20 | ✓ |
| 7 | The agent loop, via the framework | 25 | ✓ |
| 8 | First working agent on the real CRM | 15 | ✓ |
| 9 | When agents go wrong | 10 | ✓ |
| 10 | Quiz + homework | 10 | ✓ |

**Legend used in this notebook**

> 🧠 **concept** — read this, it will be on the quiz
> 💻 **run this** — execute the cell and look at the output
> ✍️ **your turn** — an exercise, solution hidden below
> ⚠️ **trap** — a mistake almost everyone makes
> 🔑 **needs a key** — cell is optional without an API key

---
