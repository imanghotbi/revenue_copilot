# 💻 Two leads, two paths. Pixel & Pine never touches the model.
crm.reset_call_log()

print("=" * 72)
print("L-2004 Pixel & Pine — expected route: self_serve")
print("=" * 72)
pine = triage.invoke({"lead_id": "L-2004"})
print("route:    ", pine.get("route"), "| grade:", pine.get("grade"),
      "| score:", pine.get("lead_score"), "| qualified:", pine.get("qualified"))
print("\nbrief:\n", pine.get("brief", "")[:900])

print("\n" + "=" * 72)
print("L-2005 Sable Pharmaceuticals — expected route: agent")
print("=" * 72)
crm.reset_call_log()
sable = triage.invoke({"lead_id": "L-2005"})
print("route:    ", sable.get("route"), "| grade:", sable.get("grade"),
      "| score:", sable.get("lead_score"), "| existing:", sable.get("is_existing"))
print("tools:    ", [r["tool"] for r in crm.CALL_LOG])
print("\nbrief:\n", (sable.get("brief") or "")[:1200])
