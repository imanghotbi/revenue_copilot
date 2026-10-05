## 2. 🧠 What an agent is (and is not)

### 2.1 The one-sentence definition

> **An agent is a language model in a loop, deciding which tools to call until
> the task is done.**

Three words in that sentence carry all the weight:

| Word | Why it matters |
|---|---|
| **loop** | The model is called *repeatedly*. One call is a chatbot. Many calls, where the model chooses what happens next, is an agent. |
| **deciding** | The *model* picks the next action — not your `if/else`. That is the difference between an agent and a workflow. |
| **tools** | The model can act on the world: query a database, write a file, book a meeting. Without tools it can only produce text. |

### 2.2 The ladder

People say "agent" about four different things. Knowing which rung you are on
is most of system design.

```
 rung 1  LLM call            prompt -> text                          (a chatbot)
 rung 2  Chain / pipeline     prompt -> text -> prompt -> text        (fixed steps, YOU decide the order)
 rung 3  RAG                  retrieve -> stuff into prompt -> text    (fixed steps + outside knowledge)
 rung 4  AGENT                model chooses the next step, repeatedly, (THE MODEL decides the order)
                              using tools, until done or stuck
```

Rungs 1–3 are **workflows**: you wrote the control flow, the model only fills in
the text. Rung 4 is an **agent**: the control flow is decided at runtime, by the
model, based on what it has seen so far.

⚠️ **Trap — "more agentic is better."** It is not. Every rung you climb buys
flexibility and costs predictability, latency and money. A workflow that always
does the same five steps is easier to test, cheaper to run and far easier to
explain to an auditor than an agent that improvises. In Session 2 we will build
the lead-triage process as a **workflow with one agentic step inside it** — which
is what most production systems actually look like.

### 2.3 The loop, drawn properly

```
                       ┌──────────────────────────────────────────┐
                       │                                          │
   user task ──────►   │   ┌───────────┐      tool_calls?         │
                       │   │    LLM    │───────────┐              │
                       │   │ (reasons) │           │              │
                       │   └─────▲─────┘           ▼              │
                       │         │           ┌───────────┐        │
                       │  tool   │           │  EXECUTE  │        │
                       │  result │           │   TOOLS   │        │
                       │         └───────────┤ (act on   │        │
                       │                     │  the CRM) │        │
                       │                     └───────────┘        │
                       │         no more tool_calls?              │
                       └────────────────┬─────────────────────────┘
                                        ▼
                                 final answer + side effects
                                 (quote, draft email, CRM entries)
```

The box in the middle is usually called the **ReAct loop** — *Reason* then
*Act*, then read the result, then reason again. Every agent framework you will
ever meet is an implementation of this picture, with extra features bolted on:

| Extra feature | What it adds | Where we cover it |
|---|---|---|
| **State** | The loop remembers what happened so far | §7, Session 2 §3 |
| **Memory** | State that survives across conversations | Session 2 §5 |
| **Guardrails** | Limits on steps, spend, and which tools may write | §9, Session 2 §4 |
| **Human in the loop** | Pause and ask a person before an irreversible act | Session 2 §4 |
| **Multiple agents** | Several loops, each with its own tools | Session 2 §6 (stretch) |

### 2.4 Vocabulary you will hear in every meeting about agents

| Term | Plain meaning |
|---|---|
| **tool / function** | A Python function the model is allowed to call. |
| **tool schema** | The JSON description of that function: name, purpose, arguments. This is what the model actually reads. |
| **tool call** | The model's structured request: "call `get_customer` with `customer_id="C-1006"`". |
| **tool result / observation** | What your function returned, fed back to the model as text. |
| **step / turn / iteration** | One pass through the loop. |
| **state** | The data the loop carries between steps (usually the message history). |
| **system prompt** | Standing instructions: role, rules, what it must never do. |
| **context window** | The total number of tokens the model can see at once. Tool results eat into it. |
| **grounding** | Making the model use retrieved facts instead of remembered ones. This is the entire reason tools exist. |
| **hallucination** | Confident invention. In an agent this is worse than in a chatbot, because the invention can trigger a real action. |
| **agentic workflow** | Fixed steps, but some steps are model decisions. |
| **orchestrator** | The code that runs the loop and enforces the limits. |

🧠 **The mental model to keep:** an LLM has no hands, no memory and no eyes. It
is a very well-read consultant locked in a room with no phone. Tools are the
phone. The loop is you going back into the room after each call and saying
*"here is what they told you — what next?"*

---
