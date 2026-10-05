# 💻 Same question, twice: once with no tools, once with the tool schema shown.
QUESTION = ("How much revenue has customer C-1006 generated for us, and should we "
            "be worried about losing them?")

print("=" * 72)
print("A) NO TOOLS - the model must answer from its own 'knowledge'")
print("=" * 72)
answer_no_tools = local_generate(
    [
        {"role": "system", "content": "You are a sales analyst at Northwind Supply Co. Answer briefly."},
        {"role": "user", "content": QUESTION},
    ],
    max_new_tokens=120,
    show_prompt=True,
)
print(answer_no_tools)

print()
print("=" * 72)
print("B) TOOLS ANNOUNCED - the model is offered a way to look it up")
print("=" * 72)
messages_with_tools = [
    {"role": "system", "content": "You are a sales analyst at Northwind Supply Co."},
    {"role": "user", "content": QUESTION},
]
tools = [{
    "type": "function",
    "function": {
        "name": "account_metrics",
        "description": "Return revenue, order count and churn risk for one customer.",
        "parameters": {
            "type": "object",
            "properties": {"customer_id": {"type": "string", "description": "e.g. C-1006"}},
            "required": ["customer_id"],
        },
    },
}]

if tokenizer is not None:
    rendered = tokenizer.apply_chat_template(
        messages_with_tools, tools=tools, add_generation_prompt=True, tokenize=False
    )
    print("=== EXACT TEXT THE MODEL RECEIVES (tools included) ===")
    print(rendered)
    print("=== end ===")
    print("\nNotice: tools are injected into the SYSTEM turn as JSON inside "
          "<tools>...</tools>, and the template tells the model to answer with "
          "<tool_call>{...}</tool_call>. There is no magic - it is prompt text.")
else:
    print("[tokenizer not loaded]")
