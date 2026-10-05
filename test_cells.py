#!/usr/bin/env python3
"""
Execute the .py cell sources of a session in one shared namespace, the way a
Jupyter kernel would, so nothing ships untested.

    python test_cells.py session1            # run every cell
    python test_cells.py session1 24         # run cells 1..24
"""
from __future__ import annotations

import os
import re
import sys
import traceback
import warnings

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


def cell_files(session: str) -> list[tuple[str, str]]:
    folder = os.path.join(HERE, "src", session)
    out = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".py"):
            with open(os.path.join(folder, name), encoding="utf-8") as fh:
                code = fh.read()
            code = "\n".join(l for l in code.splitlines() if not re.match(r"^\s*#\s*%%", l))
            out.append((name, code))
    return out


def main() -> int:
    session = sys.argv[1] if len(sys.argv) > 1 else "session1"
    upto = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9

    ns: dict = {"__name__": "__main__"}
    files = cell_files(session)
    failures = []
    for idx, (name, code) in enumerate(files, start=1):
        if idx > upto:
            break
        print("\n" + "=" * 78)
        print(f"CELL {idx:02d}  {name}")
        print("=" * 78)
        try:
            exec(compile(code, f"<{name}>", "exec"), ns)
        except Exception:
            print(f"!!! CELL {name} RAISED:")
            traceback.print_exc()
            failures.append(name)

    print("\n" + "#" * 78)
    if failures:
        print(f"FAILED {len(failures)} cell(s): {failures}")
        return 1
    print(f"OK - all {min(upto, len(files))} executed cell(s) of {session} ran cleanly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
