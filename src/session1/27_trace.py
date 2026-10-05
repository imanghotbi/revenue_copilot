# 💻 What actually happened, in the CRM's own words.
print("=== tool-call log (the audit trail a manager would read) ===")
log = crm.call_log_frame()
if len(log):
    print(log[["n", "tool", "writes", "result_preview"]].to_string(index=False))
    print(f"\n{int(log['writes'].sum())} write(s), "
          f"{int((~log['writes'].astype(bool)).sum())} read(s).")
else:
    print("(no tools were recorded — the model answered from the prompt alone)")
