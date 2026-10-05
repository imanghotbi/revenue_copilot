# 💻 Clear the inbox. One row per lead, checkable against the policy table.
inbox_graph = build_triage_graph(config.get_chat_model(verbose_mock=False), with_gate=False)

rows = []
for lead_id in ["L-2001", "L-2002", "L-2003", "L-2004", "L-2005"]:
    crm.reset_call_log()
    out = inbox_graph.invoke({"lead_id": lead_id})
    tools_used = [r["tool"] for r in crm.CALL_LOG]
    rows.append({
        "lead_id": lead_id,
        "company": out.get("company"),
        "grade": out.get("grade"),
        "score": out.get("lead_score"),
        "existing": out.get("is_existing"),
        "route": out.get("route"),
        "model_called": "researcher" if out.get("route") == "agent" else "no",
        "tools": ", ".join(tools_used[:8]),
        "brief": (out.get("brief") or "").replace("\n", " ")[:160],
    })

inbox_report = pd.DataFrame(rows)
print(inbox_report[["lead_id", "company", "grade", "score", "existing",
                    "route", "model_called"]].to_string(index=False))

# The design claim, checked rather than hoped.
assert inbox_report.loc[inbox_report.lead_id == "L-2004", "route"].item() == "self_serve"
assert inbox_report.loc[inbox_report.lead_id == "L-2005", "route"].item() == "agent"
assert inbox_report.loc[inbox_report.lead_id == "L-2003", "existing"].item() == True
print("\nchecks passed: Pixel & Pine skipped the model; Sable reached the agent; Fjord is an existing customer.")
