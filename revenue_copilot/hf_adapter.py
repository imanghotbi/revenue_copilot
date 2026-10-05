"""
ChatHFInference - a minimal LangChain chat model backed by Hugging Face
Inference Providers.

We could just `pip install langchain-huggingface` and use `ChatHuggingFace`.
We show this ~80-line adapter instead because it is the clearest way to see
what a "model integration" actually is:

    a class with a `_generate(messages) -> ChatResult` method.

Everything else in LangChain - tools, agents, graphs, checkpointers - only ever
talks to a model through that one method.  Once you see it, the framework stops
being magic.  `get_chat_model("hf")` uses `langchain_hf` if you have it and
falls back to this class if you do not.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ChatHFInference(BaseChatModel):
    """Chat model that calls `huggingface_hub.InferenceClient.chat(...)`."""

    model: str = "Qwen/Qwen2.5-7B-Instruct"
    provider: str = "auto"
    token: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 1024
    timeout: float = 120.0

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        from huggingface_hub import InferenceClient

        object.__setattr__(
            self, "_client",
            InferenceClient(model=self.model, provider=self.provider,
                            token=self.token, timeout=self.timeout),
        )

    @property
    def _llm_type(self) -> str:
        return f"hf-inference/{self.model}"

    @property
    def _identifying_params(self) -> dict:
        return {"model": self.model, "provider": self.provider}

    # ---- the only method that really matters -----------------------------
    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None,
                  **kwargs: Any) -> ChatResult:
        payload = [{"role": _role(m), "content": _content(m)} for m in messages]
        # Tool results have to be folded back in as user turns for providers
        # that do not implement the "tool" role.
        payload = _fold_tool_messages(payload)

        resp = self._client.chat(
            messages=payload,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop,
            **kwargs,
        )
        choice = resp.choices[0]
        text = choice.message.content or ""
        usage = getattr(resp, "usage", None)
        msg = AIMessage(
            content=text,
            additional_kwargs={"finish_reason": getattr(choice, "finish_reason", None)},
            usage_metadata=(
                {
                    "input_tokens": getattr(usage, "prompt_tokens", 0),
                    "output_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0),
                }
                if usage else None
            ),
        )
        return ChatResult(
            generations=[ChatGeneration(message=msg)],
            llm_output={"model": self.model},
        )


def _role(m: BaseMessage) -> str:
    t = m.type
    return {"human": "user", "ai": "assistant", "system": "system"}.get(t, "user")


def _content(m: BaseMessage) -> str:
    if isinstance(m, ToolMessage):
        return f"[result of tool '{m.name}'] {m.content}"
    if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
        import json

        calls = "; ".join(
            f"{c['name']}({json.dumps(c['args'], ensure_ascii=False, default=str)})"
            for c in m.tool_calls
        )
        return f"{m.content}\n[requested tool calls: {calls}]".strip()
    return str(m.content)


def _fold_tool_messages(payload: list[dict]) -> list[dict]:
    out = []
    for turn in payload:
        if turn["role"] == "tool":
            if out and out[-1]["role"] == "user":
                out[-1]["content"] += "\n\n" + turn["content"]
            else:
                out.append({"role": "user", "content": turn["content"]})
        else:
            out.append(turn)
    return out
