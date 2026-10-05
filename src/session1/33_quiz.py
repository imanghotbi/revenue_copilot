# 💻 Ground truth for Q1 and Q2. Cover the output if you want to try first.
answers = evaluation.exercise_answers()
print("Q1 company:", answers["highest_churn_risk_company"],
      f"({answers['highest_churn_risk_customer']})")
print("Q1 score:  ", answers["highest_churn_risk_score"])
print("Q2 not sales-qualified:", answers["leads_not_qualified"],
      f"(self-serve candidate: {answers['lead_to_self_serve']})")
print("Q3-Q5 are conceptual — reveal below.")
