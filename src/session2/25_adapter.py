# 💻 The integration, with the HTTP call left unmade unless you have a token.
import inspect
from langchain_core.language_models import BaseChatModel

print(inspect.getsource(ChatHFInference._generate))
print("---")
print("ChatHFInference subclasses BaseChatModel:", issubclass(ChatHFInference, BaseChatModel))
print("model actually driving this notebook:", type(llm).__name__)

token = config.get_secret("HF_TOKEN")
if token:
    hf_llm = ChatHFInference(model=config.HF_MODEL, token=token, provider=config.HF_PROVIDER)
    live = hf_llm.invoke([HumanMessage(content="Reply with the single word: ready")])
    print("HF reply:", (live.content or "")[:200])
else:
    print("No HF_TOKEN — skipped the live call. The adapter is loaded; the mock is driving the graphs.")
