# 💻 Tool schemas, the framework way: LangChain's @tool already did the work.
# No hand-written make_schema() needed — every CRM tool carries the JSON
# the model reads in `.args`, and the Python you call in `.invoke()`.
import json

print("=== what the model is shown (from the framework, not hand-written) ===")
spec = crm.tool_specs()[3]   # account_metrics
print(json.dumps({
    "name": spec["name"],
    "description": spec["description"],
    "args": spec["args"],
}, indent=2)[:800])

# ---------------------------------------------------------------
# Northwind's REAL tool set — the same objects the agent will call.
# ---------------------------------------------------------------
print("\n=== Northwind's 13 CRM tools ===")
print(f"{'tool':26s} {'arguments':52s}")
print("-" * 80)
for t in crm.ALL_TOOLS:
    args = ", ".join(t.args.keys())
    kind = "WRITE" if t in crm.WRITE_TOOLS else "read "
    print(f"{t.name:26s} {args[:52]:52s} {kind}")

print(f"\n{len(crm.READ_TOOLS)} read tools, {len(crm.WRITE_TOOLS)} write tools. "
      "Separating them is how you build an approval gate later.")

print("\n=== the @tool contract in one line each ===")
print("crm.account_metrics.args   -> JSON schema the model reads")
print("crm.account_metrics.invoke -> Python that actually runs")
print(json.dumps(crm.account_metrics.args, indent=2)[:400])
