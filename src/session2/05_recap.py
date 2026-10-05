# 💻 The inbox and the accounts that should make a manager wince.
leads = evaluation.lead_table()
accounts = evaluation.account_table()

print("Inbox, scored with Northwind policy (no LLM involved):")
print(leads[["lead_id", "company", "budget_eur", "urgency",
             "existing_customer", "score", "grade", "qualified"]].to_string(index=False))

print("\nAccounts already in the danger zone:")
print(accounts[accounts.churn_risk >= 60][
    ["customer_id", "company", "health", "churn_risk", "open_tickets", "revenue_eur"]
].to_string(index=False))
