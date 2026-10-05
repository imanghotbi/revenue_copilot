## 9. ⚠️ When agents go wrong

An agent fails in ways a chatbot does not, because it *acts*. Four failure
modes show up in every production system. We will provoke three of them on
purpose, and leave the fourth as a reading.

### 9.1 The loop that never exits

If the model keeps emitting tool calls, `native_agent_loop` hits `max_steps` and
stops. Without that limit it would spend your API budget until the process is
killed. Always set one. Session 2 will also show LangGraph's `recursion_limit`.
