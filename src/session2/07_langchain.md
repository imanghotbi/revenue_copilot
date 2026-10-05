## 2. 🧠 LangChain in 15 minutes

LangChain is a toolkit for *talking to models and tools in a uniform way*.
Three objects matter today. Everything else is convenience on top of them.

| Object | What it is | Session 1 equivalent |
|---|---|---|
| **Chat model** | A class with `invoke(messages) -> AIMessage` | `call_model(messages)` / `InferenceClient.chat` |
| **Tool** | A Python function plus a JSON schema | `make_schema(fn)` + the function itself |
| **`bind_tools`** | "here is what you may call" — sent with the next request | stuffing `<tools>` into the prompt |

A fourth object, `create_agent`, is the loop you wrote. We will open that in §3.

### 2.1 One factory, five back-ends

`config.get_chat_model()` returns a LangChain chat model for whichever provider
you configured. Change the provider, change nothing else. That is the whole
point of the abstraction.
