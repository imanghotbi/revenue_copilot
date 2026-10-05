# ------------------------------------------------------------
# Cell 1 of 2: make the `revenue_copilot` package importable.
# Runs in Colab, in a local checkout, and standalone.
# ------------------------------------------------------------
import os
import subprocess
import sys

REPO_URL = ""   # <-- optional: "https://github.com/your-org/revenue-copilot.git"

def _bootstrap(repo_url: str = "") -> str:
    """Return a directory that contains the revenue_copilot package."""
    candidates = [os.getcwd(), "/content", os.path.dirname(os.path.abspath("__file__"))]
    for c in candidates:
        if c and os.path.isdir(os.path.join(c, "revenue_copilot")):
            return c

    if repo_url:
        target = os.path.join(os.getcwd(), repo_url.rstrip("/").split("/")[-1].replace(".git", ""))
        if not os.path.isdir(target):
            print(f"cloning {repo_url} ...")
            subprocess.check_call(["git", "clone", "--depth", "1", repo_url])
        return target

    raise RuntimeError(
        "Could not find the `revenue_copilot` folder.\n"
        "  -> In Colab: set REPO_URL above, or upload the folder via "
        "Session -> Files -> Upload, then re-run this cell.\n"
        "  -> Locally: run the notebook from the repository root."
    )

ROOT = _bootstrap(REPO_URL)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
print(f"package root: {ROOT}")
