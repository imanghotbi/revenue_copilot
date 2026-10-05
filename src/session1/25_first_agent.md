## 8. 💻 First working agent on the real CRM

The scripted stub proved the *orchestrator*. Now we give it a real brain — or
the offline mock, which speaks the same language.

There are two ways a model can ask for a tool:

| | Session 1 so far | What production APIs actually return |
|---|---|---|
| Shape | a JSON *string* you parse | a structured `tool_calls` list on the message |
| You wrote | `parse_model_json` | nothing — the provider already parsed it |

The function below is the same loop as §7, rewritten for **native tool calling**.
It is also, almost line for line, what LangChain's `create_agent` and LangGraph's
`ToolNode` will do for you in Session 2. Once you can read this, those libraries
stop being magic.

We will run it on **Fjord Energi (C-1006)** — the angry customer with the 110-day
ticket. The agent is allowed the full CRM tool set.
