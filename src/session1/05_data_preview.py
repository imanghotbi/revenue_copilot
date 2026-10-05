# 💻 Run this: the whole company in four tables.
customers = pd.read_csv(os.path.join(crm.data_dir(), "customers.csv"))
orders    = pd.read_csv(os.path.join(crm.data_dir(), "orders.csv"))
leads     = pd.read_csv(os.path.join(crm.data_dir(), "inbox_leads.csv"))
tickets   = pd.read_csv(os.path.join(crm.data_dir(), "support_cases.csv"))

print(f"{len(customers)} customers | {len(orders)} orders | "
      f"{len(leads)} inbound leads | {len(tickets)} support tickets")
print(f"Revenue in the last 2 years: EUR {orders[orders.status != 'cancelled'].total_eur.sum():,.0f}")
print()
customers[["customer_id", "company", "segment", "region", "owner", "plan", "health"]].head(8)
