| Failure | What you just saw | What you do about it |
|---|---|---|
| **Never-ending loop** | `GraphRecursionError` via `recursion_limit` | Hard cap. Also detect *identical* repeated calls and abort. |
| **Invented tool** | `"unknown tool 'salesforce_query'"` fed back as an observation | Return a helpful error, don't crash. The model often recovers. |
| **Context bloat** | hundreds of tokens of CRM JSON, every step | Compact tool returns; summarise old observations; cap history. |
| **Irreversible write** | §8 already logged to the CRM before you read the answer | Don't give the agent write tools until a human has approved. **Session 2.** |

⚠️ **Trap — "the model will be careful."** It will not. Care is a property of the
*harness* (caps, schemas, approval gates), not of the weights.

🧠 The honest list of ways Revenue Copilot can still be wrong, even when the
loop is perfect:

1. It quotes a price from memory instead of `product_lookup`.
2. It applies a discount the policy tool would have refused, because it never called the policy tool.
3. It drafts a warm email to an account on **credit hold** (Bastion Security, C-1028).
4. It treats Fjord Energi as a new lead and ignores the open ticket.

Tools make those mistakes *detectable*. They do not make them impossible. That
is why Session 2 is about graphs, gates and evaluation — not about a cleverer
prompt.

---
