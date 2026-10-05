<details>
<summary>Q3–Q5 suggested answers (click to reveal)</summary>

**Q3.** A chain is a fixed sequence of steps *you* wrote. An agent is a loop in
which the *model* chooses the next step (usually a tool call) until it stops.

**Q4.** Arithmetic and policy must be deterministic, auditable and easy to
change. A prompt is none of those things. The model decides *whether* to score
a lead; the tool decides *what the score is*.

**Q5.** (1) the model emits a final answer / no tool calls, (2) the reply cannot
be parsed, (3) `max_steps` is exceeded.

</details>

---

### Homework (20–30 minutes, before Session 2)

Pick **one** inbox lead other than Fjord Energi. Using only the tools (you can
call them with `.invoke({...})` — no model required), write down:

1. Is this company already a customer?
2. The `score_lead` output: score, grade, flags.
3. The policy document you would have to follow (KB id).
4. Whether you would let an agent *write* to the CRM before a human looked.

Bring that page to Session 2. We will run the same lead through LangGraph and
see whether the graph agrees with you.

If you want to go further, add an API key (OpenRouter is the path of least
resistance) and re-run §8. Compare the mock's trace with the live model's
trace. Note every tool the live model called that the mock did not, and vice
versa.

---

### What Session 2 adds

You now have a working agent loop. Session 2 wraps it in the libraries you will
actually ship:

- **LangChain** — chat models, `@tool`, `bind_tools`, `create_agent`
- **LangGraph** — state, nodes, edges, a checkpointer
- **Human-in-the-loop** — pause before every write
- **The inbox, end to end** — five leads, one morning, a number a manager can
  argue with

The loop does not get more complicated. The *harness* around it does.
