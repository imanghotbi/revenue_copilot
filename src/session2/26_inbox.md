## 7. 💻 The inbox: five leads, one morning

This is the business problem from the first page of Session 1.

For each lead the workflow:

1. loads the email
2. scores it with `score_lead` (Python, not the model)
3. sends grade D / not-qualified straight to self-serve
4. otherwise asks the read-only researcher for a brief

We do **not** auto-approve writes in the batch. Approving five leads blindly
would undo §5. The table below is what a sales lead would scan at 9:05.
