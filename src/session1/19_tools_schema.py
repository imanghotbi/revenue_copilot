# 💻 Build a tool schema by hand, from a plain Python function.
# This is exactly what LangChain's @tool decorator does for you in Session 2 -
# doing it once by hand is what makes the framework legible later.
import inspect
import json
from typing import get_type_hints

PY_TO_JSON = {str: "string", int: "integer", float: "number", bool: "boolean",
              list: "array", dict: "object"}

def make_schema(fn) -> dict:
    """Turn a Python function into the JSON a model needs in order to call it."""
    hints = get_type_hints(fn)
    sig = inspect.signature(fn)
    properties, required = {}, []
    for pname, param in sig.parameters.items():
        ptype = PY_TO_JSON.get(hints.get(pname, str), "string")
        prop = {"type": ptype}
        if param.default is inspect.Parameter.empty:
            required.append(pname)
        else:
            prop["default"] = param.default
        properties[pname] = prop
    doc = inspect.getdoc(fn) or ""
    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": doc.split("\n")[0],
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


def revenue_last_year(customer_id: str) -> float:
    """Return the customer's total revenue in EUR over the last 365 days."""
    return 0.0

print("=== the schema the model would be shown ===")
print(json.dumps(make_schema(revenue_last_year), indent=2))

# ---------------------------------------------------------------
# Now look at Northwind's REAL tool set (Session 2 will use these).
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
