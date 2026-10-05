## 6. 🧠 Tools: the JSON contract

A tool is a Python function. But the model never sees your Python — it sees a
**JSON schema**. Getting that schema right is the single highest-leverage skill in
building agents, and it is almost never taught.

### 6.1 What the model actually receives

```json
{
  "type": "function",
  "function": {
    "name": "account_metrics",
    "description": "Return revenue, order count and churn risk for one customer.",
    "parameters": {
      "type": "object",
      "properties": {
        "customer_id": {"type": "string", "description": "e.g. C-1006"}
      },
      "required": ["customer_id"]
    }
  }
}
```

That whole blob is serialised into the prompt. The model reads it, and if it
decides to act it emits something like:

```json
{"name": "account_metrics", "arguments": {"customer_id": "C-1006"}}
```

**Your code** runs the requested function and puts the return value back
into the conversation as a new message. The model then reads the result and
decides what to do next. Nobody at OpenAI or Qwen is executing anything for you.
In this course that parse-and-call step is done by the framework:
`bind_tools` sends the schemas, and LangGraph's `ToolNode` (inside
`create_agent`) executes the calls and feeds the observations back.

### 6.2 Writing schemas that models can actually use

| Do | Don't | Why |
|---|---|---|
| Name it like a verb-object: `get_order_history` | `helper2`, `do_stuff` | The name is the first hint the model gets. |
| Say *when* to use it: "Use this before promising a delivery date." | "Order function." | Models choose tools by matching description to intent. |
| Give units and formats: `budget_eur`, `last_n_days`, `"C-1006"` | `budget`, `days`, `id` | Prevents the classic 100× currency and off-by-one-date errors. |
| Use `enum` for closed sets: `"stage": {"enum": ["New","Qualified",...]}` | free-text stage | Turns a validation problem into an impossible-to-get-wrong one. |
| Return compact JSON | Return a 4,000-row DataFrame as text | Tool output goes into the context window and costs money every turn. |
| Return a *helpful* error: `"no customer 'acmee'; did you mean 'Acme Logistik GmbH'?"` | Raise a stack trace | A good error lets the model self-correct on the next step. |
| 5–15 focused tools | 60 overlapping tools | Tool selection accuracy falls sharply as the list grows. |

⚠️ **Trap — the description is the prompt.** If your agent keeps calling the wrong
tool, the fix is almost always the *description*, not the code. Rewrite it as if
you were onboarding a new colleague: what is it for, when should you reach for
it, what must you check first.

⚠️ **Trap — arguments the model cannot know.** If a tool needs
`internal_account_uuid`, the model has to guess it and will hallucinate one. Give
it something it can extract from the conversation (`company` name) and resolve the
rest inside the tool.

### 6.3 The most important design rule in this course

> **Arithmetic and business rules go in tools. Judgement and language go in the model.**

Look at Northwind's tool list. `score_lead` and `account_metrics` are pure Python
with hard-coded company policy: budget bands, churn weights, discount caps. The
model never calculates a churn score or a VAT total. It *calls* something that does.

This is not because LLMs cannot multiply — modern ones often can. It is because:

1. **Determinism.** `score_lead(employees=1500, budget_eur=210000, ...)` returns
   87 every time. An LLM asked to "score this lead" returns 87, then 74, then 91.
   You cannot regression-test 91.
2. **Auditability.** "Why did we deprioritise this lead?" → "score 0, below the
   €1,000 minimum order value, rule in `score_lead`, changed in commit `a1b2c3`."
   That is an answer. "The model thought it was low value" is not.
3. **Changeability.** Finance changes the discount cap? One line of Python, one
   unit test. Prompt surgery across four agents at 2 a.m.? No.

🧠 Keep this rule in mind for Session 2: the most common way an agent project
fails in production is that someone put a business rule in a prompt.
