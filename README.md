# Revenue Copilot — two teaching sessions on AI agents

A Colab-ready introduction to agents, built as one business scenario:
**Northwind Supply Co.**, a fictional B2B office-furniture distributor whose
sales inbox is winning.

| Session | Notebook | What students do |
|---|---|---|
| 1 | `notebooks/Session_1_From_LLM_to_Agent.ipynb` | Load a small Hugging Face model, see tokens and chat templates, write a tool schema, build an agent loop with no framework |
| 2 | `notebooks/Session_2_Agents_in_Production_with_LangChain_and_LangGraph.ipynb` | LangChain, LangGraph, a human approval gate, and the inbox cleared end to end |

No GPU is required. No API key is required: every graph runs on the offline
`MockSalesLLM`. A free OpenRouter, Groq, or Hugging Face token switches the
same graphs onto a hosted model.

## Run in Colab

1. Upload this `revenue_copilot` folder (the package, `data/`, and `notebooks/`),
   or set `REPO_URL` in the first code cell to a cloneable repository.
2. Open Session 1, then Session 2. Run the cells from the top.
3. Optional: Colab Secrets → add `OPENROUTER_API_KEY`, `GROQ_API_KEY`, or
   `HF_TOKEN`. Never paste a key into a cell.

Session 1 can download `Qwen/Qwen2.5-0.5B-Instruct` (~1 GB) when
`USE_LOCAL_MODEL = True`. Set it to `False` to skip that download; the rest of
the notebook still runs.

## Run locally

```bash
pip install -r requirements.txt
python test_cells.py session1
python test_cells.py session2
python build_notebooks.py
```

Notebook source lives in `src/session1` and `src/session2` as plain `.md` and
`.py` cells. `build_notebooks.py` assembles the `.ipynb` files.
