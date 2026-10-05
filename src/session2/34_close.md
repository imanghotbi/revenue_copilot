<details>
<summary>Suggested answers (click to reveal)</summary>

**Q1.** L-2004 Pixel & Pine. Budget is under the €1,000 minimum, so the router
sends it to self-serve. Skipping the model saves money and removes a place
where the model could invent a reason to involve a salesperson.

**Q2.** A checkpointer, a `thread_id`, and the `interrupt()` call placed
*before* the side effect.

**Q3.** The score is a business rule. It has to be the same number every time,
so a unit test can own it. The model decides whether a brief is needed; it
does not decide the grade.

**Q4.** Do not quote. KB-06: the account is on credit hold. Route to finance
and tell the customer the balance is outstanding. `build_quote` must not run.

**Q5.** `HUMAN_REVIEW_SHARE` — especially `draft_reply` at 0.5. If the team
actually rewrites every email, the labour saving collapses. The API cost is
the small number; the review share is the large one.

</details>

---

### Stretch — a second agent, only if you have time

The graph you built is already a workflow with one agent inside it. A second
agent earns its place only when the *language* is the hard part and the
*decision* is already made. The usual shape:

1. Researcher (you have this) — read tools, produces a brief.
2. Human gate (you have this).
3. Writer — a second `create_agent` whose only tools are `draft_email` and
   `search_knowledge_base`, and whose prompt says "do not change the numbers
   in the brief".

Do not give the writer `build_quote`. If it can reprice the deal, the gate
you just built is theatre.

### Take-home

1. Re-run §7 with `PROVIDER` pointed at a real key (`OPENROUTER_API_KEY` or
   `GROQ_API_KEY` in Colab's Secrets panel). Diff the tool trace against the
   mock. Every extra tool call is a behaviour you now have to test.
2. Add a credit-hold check to `qualify`. If the matched customer is C-1028,
   force `route = "self_serve"` and put KB-06 in the brief. There is a unit
   of business logic hiding in that sentence — it does not belong in the prompt.
3. Pick the review share you would actually defend, recompute `roi_table`,
   and write four sentences a sales manager could read without you in the room.

You now have the whole shape: a model, a loop, tools that own the truth, a
graph that decides when the model is allowed to run, and a human who still
owns the write.
