# 💻 Ground truth for the numeric half of the quiz.
answers = evaluation.exercise_answers()
total = evaluation.roi_table().query("task == 'TOTAL'").iloc[0]
print("best lead:        ", answers["best_lead_id"], answers["best_lead_company"],
      "score", answers["best_lead_score"])
print("self-serve lead:  ", answers["lead_to_self_serve"])
print("not qualified:    ", answers["leads_not_qualified"])
print("high-risk accounts:", answers["accounts_at_high_risk"],
      f"(EUR {answers['revenue_at_high_risk_eur']:,.0f} revenue sitting there)")
print(f"ROI total saved:   {total.saved_minutes:,.0f} min   EUR {total.saved_eur:,.0f} / month")
print("Q1–Q5 reasoning is in the cell below.")
