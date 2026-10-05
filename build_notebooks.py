#!/usr/bin/env python3
"""
Assemble the two teaching notebooks from plain .md / .py source files.

    src/session1/NN_slug.md   -> markdown cell
    src/session1/NN_slug.py   -> code cell

Keeping the notebook content in ordinary text files means the code can be
executed and tested before it ever becomes a .ipynb, and diffs stay readable.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "notebooks")

KERNEL = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}


def split_lines(text: str) -> list[str]:
    """nbformat wants a list of lines, each keeping its trailing newline."""
    lines = text.splitlines(keepends=True)
    return lines


def strip_cell_markers(text: str) -> str:
    """Allow `# %%` style separators inside the .py sources; they are not code."""
    out = []
    for line in text.splitlines(keepends=True):
        if re.match(r"^\s*#\s*%%", line):
            continue
        out.append(line)
    return "".join(out)


def build(session: str, notebook_name: str) -> str:
    folder = os.path.join(SRC, session)
    files = sorted(os.listdir(folder))
    cells = []
    for fname in files:
        path = os.path.join(folder, fname)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if fname.endswith(".md"):
            cells.append(
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": split_lines(text.rstrip() + "\n"),
                }
            )
        elif fname.endswith(".py"):
            code = strip_cell_markers(text).rstrip() + "\n"
            cells.append(
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": split_lines(code),
                }
            )
        else:
            print(f"  skipping unknown file {fname}")

    nb = {
        "cells": cells,
        "metadata": {
            "colab": {
                "provenance": [],
                "toc_visible": True,
                "machine_shape": "hm",
            },
            "kernelspec": KERNEL,
            "language_info": {
                "name": "python",
                "version": "3.11.0",
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 0,
    }

    os.makedirs(OUT, exist_ok=True)
    dest = os.path.join(OUT, notebook_name)
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(nb, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    n_md = sum(1 for c in cells if c["cell_type"] == "markdown")
    print(f"built {dest}: {len(cells)} cells ({n_md} markdown, {len(cells) - n_md} code)")
    return dest


if __name__ == "__main__":
    targets = sys.argv[1:] or [
        ("session1", "Session_1_From_LLM_to_Agent.ipynb"),
        ("session2", "Session_2_Agents_in_Production_with_LangChain_and_LangGraph.ipynb"),
    ]
    for session, name in targets:
        build(session, name)
