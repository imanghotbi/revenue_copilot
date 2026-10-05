# 💻 The number a manager can argue with. Change the assumptions and re-run.
roi = evaluation.roi_table(hourly_cost_eur=45.0, api_cost_per_task_eur=0.01)
print(roi.to_string(index=False))

total = roi[roi.task == "TOTAL"].iloc[0]
saved_hours = total.saved_minutes / 60
print(f"\nAbout {saved_hours:.0f} hours and EUR {total.saved_eur:,.0f} a month,")
print("if the review shares in evaluation.HUMAN_REVIEW_SHARE are honest.")

import matplotlib.pyplot as plt

plot_df = roi[roi.task != "TOTAL"]
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(plot_df))
ax.bar([i - 0.18 for i in x], plot_df.manual_cost_eur, width=0.36, label="manual")
ax.bar([i + 0.18 for i in x], plot_df.agent_cost_eur, width=0.36, label="agent + review")
ax.set_xticks(list(x))
ax.set_xticklabels(plot_df.task, rotation=25, ha="right")
ax.set_ylabel("EUR / month")
ax.set_title("Northwind: labour cost with and without Revenue Copilot")
ax.legend()
fig.tight_layout()
try:
    plt.show()
except Exception as exc:
    print("plot saved in memory; display unavailable:", exc)
finally:
    plt.close(fig)
