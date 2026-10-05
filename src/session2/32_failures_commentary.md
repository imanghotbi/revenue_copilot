**C-1028 Bastion Security** is on credit hold (KB-06). No new order may be
quoted until finance clears the balance. A fluent draft that promises a
delivery date is a defect, even if the tone is excellent. The fix is a tool
the agent must call, and a router that refuses `build_quote` when the tool
says `credit_hold`.

The other ways this system is still wrong, even when every cell is green:

| Failure | What it looks like | What you add |
|---|---|---|
| Skipped tool | A price or a date with no `product_lookup` in the trace | A checker that rejects the brief |
| Prompted policy | Discount "about 10%" written in the system prompt | Leave it in `build_quote`; the tool already caps it |
| Approved the wrong thing | Human clicked yes on a 500-character preview | Show the exact arguments, allow edits |
| Memory leak | One thread reused across two customers | A new `thread_id` per account, on purpose |
| Cost surprise | A 70B model on every grade-D lead | You already routed those around the model |

---

## 10. ✍️ Quiz

**Q1.** In the inbox table, which lead never called the model, and why is that a feature?

**Q2.** What three things does `interrupt()` need before it can pause a graph?

**Q3.** Why is `score_lead` a node of ordinary Python rather than a step inside the researcher?

**Q4.** Customer C-1028 asks for a quote tomorrow. What should the system do?

**Q5.** The TOTAL row of the ROI table is not a promise. Which assumption would you
challenge first in front of the sales manager?
