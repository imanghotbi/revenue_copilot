🧠 **Compare this with the scripted run in §7.** Same customer, same tools, same
exit condition. The only thing that changed is *who decided the next step*.

If you are on the offline mock, the plan is deterministic: metrics → tickets →
policy → quote → draft email → log. That is a feature, not a cop-out. It lets
you see the *shape* of a good trace before a live model adds language and
judgement (and the occasional wrong tool).

If you added an API key, look at the log: a capable model will usually follow a
similar path, because the **tool descriptions** tell it to. That is why we spent
so long on schemas.

⚠️ **Trap — writes already happened.** `build_quote`, `draft_email` and
`log_activity` ran *during* the loop, before any human saw the answer. The draft
was not sent (the tool refuses to send), but the CRM timeline now has a note.
In a real CRM that is an irreversible side effect. Session 2 puts a human
approval gate in front of every write tool.

---
