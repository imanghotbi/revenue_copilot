# 💻 Tools are just functions: call one yourself, no model involved.
import json

print(">>> crm.get_customer.invoke({'customer_id': 'C-1006'})\n")
print(crm.get_customer.invoke({"customer_id": "C-1006"}))

print("\n\n>>> now with a typo - note how the tool responds:\n")
print(crm.get_customer.invoke({"customer_id": "C-9999"}))

print("\n\n>>> the objective business metrics (a MODEL must never compute these):\n")
print(json.dumps(json.loads(crm.account_metrics.invoke({"customer_id": "C-1006"})), indent=2))
