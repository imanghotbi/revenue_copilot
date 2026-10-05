### 6.1 What a "model integration" actually is

`get_chat_model("hf")` uses LangChain's Hugging Face chat model when that
package is installed, and otherwise `ChatHFInference` from this repo — about
80 lines. The entire contract is one method:

```
_generate(messages) -> ChatResult
```

Tools, agents, graphs and checkpointers never see HTTP. They see that method.
Read the class (it ships in the package) and notice three things:

1. Messages are translated into `{role, content}` dicts.
2. Tool results are folded into user turns, because not every host supports a
   `"tool"` role.
3. Token usage is copied onto the `AIMessage`, which is how the ROI cell later
   prices a run.

🔑 A live call needs `HF_TOKEN`. Without it, the class is still worth reading —
the mock model above implements the same `_generate` method.
