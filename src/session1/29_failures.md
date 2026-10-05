## 9. ⚠️ When agents go wrong

An agent fails in ways a chatbot does not, because it *acts*. Four failure
modes show up in every production system. We will provoke three of them on
purpose with framework machinery, and leave the fourth as a reading.

### 9.1 The loop that never exits

If the model keeps emitting tool calls, the LangGraph run hits
`recursion_limit` (the framework's `max_steps`) and stops. Without that limit
it would spend your API budget until the process is killed. Always set one.
