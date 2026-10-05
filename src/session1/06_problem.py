# The problem, in numbers.
accounts = evaluation.account_table()

print("Accounts with an OPEN support ticket:")
print(accounts[accounts.open_tickets > 0][
    ["customer_id", "company", "health", "days_since_last_order", "open_tickets", "churn_risk"]
].to_string(index=False))

print("\nInbox waiting for an answer:")
print(leads[["lead_id", "company", "country", "employees", "budget_eur", "urgency", "received"]]
      .to_string(index=False))
