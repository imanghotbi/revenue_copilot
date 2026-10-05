# 💻 The same call works for mock / OpenRouter / Groq / HF / OpenAI.
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

llm = config.get_chat_model(verbose_mock=False)
print("class:   ", type(llm).__name__)
print("provider:", config.resolve_provider())

resp = llm.invoke([
    SystemMessage(content="You are a concise sales analyst at Northwind Supply Co."),
    HumanMessage(content="In one sentence, what should a sales team do with a €900 enquiry?"),
])
print("type:    ", type(resp).__name__)
print("content: ", resp.content[:400])
print("tool_calls (should be empty — we did not bind any tools):",
      getattr(resp, "tool_calls", None) or [])
