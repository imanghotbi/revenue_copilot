# Session 2 — Agents in Production with LangChain and LangGraph

### *Revenue Copilot: from a loop to a system a sales team can actually use*

<a name="top"></a>

| | |
|---|---|
| **Course** | Introduction to AI Agents |
| **Session** | 2 of 2 (≈ 2 hours, with breaks) |
| **Scenario** | Northwind Supply Co. — the inbox, the angry account, the quote |
| **Stack** | LangChain · LangGraph · the CRM tools from Session 1 |
| **Runs in** | Google Colab, free tier. **No GPU needed.** |
| **API keys** | Optional — the offline mock drives every graph |
| **Audience** | Mixed. New to Python? Run the 💻 cells and read the 🧠 blocks. Comfortable? Do every ✍️ and the stretch. |

---

## Where we left off

In Session 1 you wrote an agent loop in about fifty lines and ran it against
the Northwind CRM. You saw that:

- an **agent** is a model in a loop, choosing tools until it stops
- **tools** turn confident invention into verifiable lookup
- **arithmetic and policy belong in Python**, not in the prompt
- a loop without a **step cap** and without a **human gate on writes** is not
  a system, it is a demo

Today we do not throw that loop away. We put it inside the libraries you will
meet at work, and we use it to clear Northwind's inbox.

By the end of this session you will have:

1. A LangGraph workflow that *routes* cheap work around the model and only
   calls an agent when judgement is needed.
2. A **human approval gate** in front of every CRM write.
3. Five processed leads, including a service-recovery plan for Fjord Energi
   and a budgetary quote for Sable Pharmaceuticals.
4. A monthly **hours-and-euros** number a manager can argue with — and an
   honest list of remaining failure modes.

---

## Session map

| # | Section | ~min | Hands-on |
|---|---------|------|----------|
| 1 | Setup and recap | 10 | ✓ |
| 2 | LangChain: models, tools, `bind_tools` | 15 | ✓ |
| 3 | `create_agent`: Session 1's loop, packaged | 15 | ✓ |
| 4 | LangGraph: state, nodes, edges | 20 | ✓ |
| 5 | Guardrails and human-in-the-loop | 20 | ✓ |
| 6 | Memory that survives a turn | 10 | ✓ |
| 7 | The inbox: five leads, one morning | 20 | ✓ |
| 8 | Hours and euros | 10 | ✓ |
| 9 | How this still fails | 10 | ✓ |
| 10 | Quiz, stretch, take-home | 10 | ✓ |

**Legend**

> 🧠 **concept** — read this
> 💻 **run this** — execute the cell
> ✍️ **your turn**
> ⚠️ **trap**
> 🔑 **needs a key** — optional; the mock covers it

---
