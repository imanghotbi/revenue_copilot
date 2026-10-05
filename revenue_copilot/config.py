"""
Setup + model-provider plumbing for the Revenue Copilot notebooks.

The single most important thing in this file is `get_chat_model()`.  It returns
a LangChain chat model for whichever provider you configure, and it always
falls back to the offline `MockSalesLLM` when no API key is available.  Every
graph in both notebooks is built from that one function, so changing provider
is a one-line edit and nothing else in the notebook has to change.

Providers
---------
"mock"       offline, deterministic, no key, no network, no cost
"openrouter" OpenAI-compatible gateway with genuinely free models
"groq"       OpenAI-compatible, fast, free tier
"hf"         Hugging Face Inference Providers (uses your HF token's monthly credit)
"openai"     plain OpenAI
"auto"       (default) use the first provider that has a key, else "mock"
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import Any, Optional

# --------------------------------------------------------------------------
# Sensible defaults - edit these, they are the only knobs students need
# --------------------------------------------------------------------------

# Free-tier models that support tool calling (checked against OpenRouter's
# public model list).  Any of them will drive the agent.
OPENROUTER_MODEL = os.environ.get("RC_MODEL", "qwen/qwen3.8-27b:free")
OPENROUTER_FALLBACKS = [
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/free",
]
GROQ_MODEL = os.environ.get("RC_GROQ_MODEL", "meta-llama/llama-3.3-70b-versatile")
OPENAI_MODEL = os.environ.get("RC_OPENAI_MODEL", "gpt-4o-mini")
HF_MODEL = os.environ.get("RC_HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
HF_PROVIDER = os.environ.get("RC_HF_PROVIDER", "auto")

# The small model we download and run *locally* in Session 1.  ~1 GB, runs on a
# Colab CPU in a few seconds per reply - slow, but it is yours and it is free.
LOCAL_MODEL_ID = os.environ.get("RC_LOCAL_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

PROVIDER = os.environ.get("RC_PROVIDER", "auto")

# Packages the notebooks need.  Everything except torch/transformers is small.
BASE_PACKAGES = [
    "langgraph>=1.0",
    "langchain>=1.0",
    "langchain-openai>=1.0",
    "huggingface_hub>=0.34",
    "pandas>=2.0",
    "pydantic>=2.7",
    "matplotlib>=3.7",
]
LOCAL_MODEL_PACKAGES = ["transformers>=4.51", "accelerate>=1.0", "torch>=2.2"]


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------

def in_colab() -> bool:
    return "google.colab" in sys.modules


def _have(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def ensure_packages(with_local_model: bool = False, quiet: bool = True) -> list[str]:
    """Install anything missing.  Returns the list of packages it installed.

    Safe to call repeatedly - if everything is present it does nothing at all,
    so re-running the setup cell costs no time.
    """
    wanted = list(BASE_PACKAGES) + (LOCAL_MODEL_PACKAGES if with_local_model else [])
    probe = {"langgraph": "langgraph", "langchain": "langchain",
             "langchain-openai": "langchain_openai", "huggingface_hub": "huggingface_hub",
             "pandas": "pandas", "pydantic": "pydantic", "matplotlib": "matplotlib",
             "transformers": "transformers", "accelerate": "accelerate", "torch": "torch"}
    missing = [p for p in wanted if not _have(probe.get(p.split(">=")[0].split("[")[0], p))]
    if not missing:
        return []

    cmd = [sys.executable, "-m", "pip", "install", "--quiet", *missing]
    if in_colab():
        cmd.insert(4, "--upgrade")       # Colab ships old versions of langchain
    if not quiet:
        print("installing:", " ".join(missing))
    subprocess.check_call(cmd)
    # make the freshly installed packages importable without a restart
    try:
        import IPython
        IPython.get_ipython().run_line_magic("load_ext", "autoreload")
    except Exception:
        pass
    return missing


def find_repo(clone_url: Optional[str] = None, subdir: str = "revenue_copilot") -> str:
    """Make the `revenue_copilot` package importable.

    In Colab the notebook is usually opened standalone, so we try, in order:
      1. already importable (you are running from a checked-out repo)
      2. git clone of `clone_url`, if you published the material
      3. the notebook's own folder (the package ships next to the notebooks)
    """
    if _have(subdir):
        return os.getcwd()

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(here, subdir)) and here not in sys.path:
        sys.path.insert(0, here)
        if _have(subdir):
            return here

    if clone_url:
        target = os.path.join(os.getcwd(), os.path.basename(clone_url).replace(".git", ""))
        if not os.path.isdir(target):
            subprocess.check_call(["git", "clone", "--depth", "1", clone_url])
        if os.path.isdir(os.path.join(target, subdir)):
            sys.path.insert(0, target)
            return target

    raise ImportError(
        f"Could not find the '{subdir}' package.  Put the notebooks inside the "
        f"repository folder, or pass clone_url=... to find_repo()."
    )


# --------------------------------------------------------------------------
# Keys
# --------------------------------------------------------------------------

def get_secret(name: str, default: str = "") -> str:
    """Read a secret from the environment, or from Colab's Secrets panel.

    In Colab: left sidebar -> 🔑 Secrets -> add e.g. OPENROUTER_API_KEY, then
    grant the notebook access.  Never paste a key into a cell you will share.
    """
    val = os.environ.get(name, "").strip()
    if val:
        return val
    if in_colab():
        try:
            from google.colab import userdata
            return (userdata.get(name) or "").strip()
        except Exception:
            return default
    return default


def available_keys() -> dict[str, bool]:
    return {
        "OPENROUTER_API_KEY": bool(get_secret("OPENROUTER_API_KEY")),
        "GROQ_API_KEY": bool(get_secret("GROQ_API_KEY")),
        "OPENAI_API_KEY": bool(get_secret("OPENAI_API_KEY")),
        "HF_TOKEN": bool(get_secret("HF_TOKEN")),
    }


def resolve_provider(provider: str = "auto") -> str:
    keys = available_keys()
    if provider != "auto":
        return provider
    for name, key in [("openrouter", "OPENROUTER_API_KEY"), ("groq", "GROQ_API_KEY"),
                      ("openai", "OPENAI_API_KEY"), ("hf", "HF_TOKEN")]:
        if keys.get(key):
            return name
    return "mock"


# --------------------------------------------------------------------------
# The model factory
# --------------------------------------------------------------------------

def get_chat_model(provider: str = PROVIDER, model: Optional[str] = None,
                   temperature: float = 0.0, verbose_mock: bool = False,
                   **kwargs: Any) -> Any:
    """Return a LangChain chat model for `provider`.

    Falls back to MockSalesLLM (offline) when the key for the requested
    provider is missing, so a notebook never dies mid-lesson.
    """
    provider = resolve_provider(provider)

    if provider == "mock":
        from .mock_llm import MockSalesLLM
        return MockSalesLLM(temperature=temperature, verbose_trace=verbose_mock)

    if provider in ("openrouter", "groq", "openai"):
        from langchain_openai import ChatOpenAI

        key_name = {"openrouter": "OPENROUTER_API_KEY", "groq": "GROQ_API_KEY",
                    "openai": "OPENAI_API_KEY"}[provider]
        api_key = get_secret(key_name)
        if not api_key:
            print(f"[config] no {key_name} found -> falling back to the offline mock model.")
            return get_chat_model("mock", temperature=temperature, verbose_mock=verbose_mock)
        base_url = {"openrouter": "https://openrouter.ai/api/v1",
                    "groq": "https://api.groq.com/openai/v1",
                    "openai": None}[provider]
        default_model = {"openrouter": OPENROUTER_MODEL, "groq": GROQ_MODEL,
                         "openai": OPENAI_MODEL}[provider]
        extra = {}
        if provider == "openrouter":
            # identifies your app in OpenRouter's rankings; harmless and polite
            extra["default_headers"] = {
                "HTTP-Referer": "https://github.com/teaching/revenue-copilot",
                "X-Title": "Revenue Copilot (teaching)",
            }
        return ChatOpenAI(
            model=model or default_model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            timeout=120,
            max_retries=2,
            **extra,
            **kwargs,
        )

    if provider == "hf":
        api_key = get_secret("HF_TOKEN")
        if not api_key:
            print("[config] no HF_TOKEN found -> falling back to the offline mock model.")
            return get_chat_model("mock", temperature=temperature, verbose_mock=verbose_mock)
        try:
            from langchain_hf import ChatHuggingFace
            from huggingface_hub import InferenceClient

            client = InferenceClient(model=model or HF_MODEL, provider=HF_PROVIDER,
                                     token=api_key, timeout=120)
            return ChatHuggingFace(client=client, temperature=temperature, **kwargs)
        except ImportError:
            # no langchain-huggingface?  Use the thin adapter taught in Session 2.
            from .hf_adapter import ChatHFInference

            return ChatHFInference(model=model or HF_MODEL, token=api_key,
                                   provider=HF_PROVIDER, temperature=temperature)

    raise ValueError(f"unknown provider '{provider}'")


# --------------------------------------------------------------------------
# Diagnostics
# --------------------------------------------------------------------------

def describe_setup(with_local_model: bool = False) -> None:
    """Print a one-screen health check.  Run this first in every session."""
    from importlib.metadata import version as _v

    print("=" * 68)
    print("Revenue Copilot - environment check")
    print("=" * 68)
    print(f"  Python           {sys.version.split()[0]}")
    print(f"  Running in Colab {in_colab()}")
    for pkg in ["langgraph", "langchain", "langchain-core", "langchain-openai",
                "huggingface_hub", "pandas", "pydantic"] + (
                ["transformers", "torch"] if with_local_model else []):
        try:
            print(f"  {pkg:<16} {_v(pkg)}")
        except Exception:
            print(f"  {pkg:<16} NOT INSTALLED")

    keys = available_keys()
    print("  API keys present:")
    for k, v in keys.items():
        print(f"    {k:<20} {'yes' if v else 'no'}")
    provider = resolve_provider()
    print(f"  Resolved provider: {provider}")
    if provider == "mock":
        print("  -> Offline mode: every cell still runs, using MockSalesLLM.")
        print("     Add a free OPENROUTER_API_KEY (or GROQ_API_KEY) to use a real model.")

    from . import crm

    d = crm.data_dir()
    print(f"  CRM data dir     {d}")
    import pandas as pd

    from .data import TABLES

    counts = {}
    for t in TABLES:
        try:
            counts[t] = len(pd.read_csv(os.path.join(d, f"{t}.csv")))
        except Exception:
            counts[t] = 0
    print("  Tables:          " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    print("=" * 68)


# --------------------------------------------------------------------------
# One-call bootstrap for the notebooks
# --------------------------------------------------------------------------

def prepare(clone_url: Optional[str] = None, with_local_model: bool = False,
            verbose: bool = True) -> str:
    """Everything a notebook needs, in the right order.

    1. install any missing packages
    2. make the `revenue_copilot` package importable (cloning if needed)
    3. materialise the synthetic CRM on disk
    4. print the environment health check

    Returns the resolved provider name ("mock" when no API key is present).
    Idempotent: re-running it in the same session is cheap.
    """
    installed = ensure_packages(with_local_model=with_local_model)
    if installed and verbose:
        print(f"[setup] installed: {', '.join(installed)}")
    elif verbose:
        print("[setup] all packages already present")

    root = find_repo(clone_url)
    if verbose:
        print(f"[setup] package root: {root}")

    from . import crm

    crm.reset_cache()
    d = crm.data_dir()
    if verbose:
        print(f"[setup] CRM data:    {d}")

    provider = resolve_provider()
    if verbose:
        print()
        describe_setup(with_local_model=with_local_model)
    return provider
