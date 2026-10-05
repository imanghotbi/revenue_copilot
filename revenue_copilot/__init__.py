"""
revenue_copilot - teaching package for "From LLM to Agent" (2 sessions).

Scenario: Northwind Supply Co., a fictional B2B office-furniture distributor
with 28 accounts, two years of orders, a support queue, an internal policy
handbook and an inbox of inbound leads nobody has time to answer.

Modules
-------
data        deterministic synthetic CRM (writes CSVs, no network)
crm         the 13 tools the agent is given
mock_llm    offline rule-based chat model, so nothing needs an API key
config      provider plumbing (mock / OpenRouter / Groq / HF / OpenAI)
evaluation  ground truth for exercises + the ROI business case
hf_adapter  a ~80-line LangChain chat model, to demystify integrations
"""

from . import config, crm, data, evaluation, mock_llm

__all__ = ["config", "crm", "data", "evaluation", "mock_llm"]
__version__ = "1.0.0"
