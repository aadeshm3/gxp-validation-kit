"""
append_ledger.py — append one entry to the activity ledger.

Invoked by the PostToolUse hook in .claude/settings.json after every skill runs.
Reads the hook payload as JSON on stdin and appends a single JSON line to
audit/ledger.jsonl recording what ran and when. This is the workbench audit
trail: an append-only, human-readable record useful for validation evidence.

The script is deliberately silent and never fails the hook. Any error is
swallowed and it exits 0, so a logging problem can never block a skill.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "audit" / "ledger.jsonl"


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        return
    payload = {}
    if raw:
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}

    tool_input = payload.get("tool_input") or {}
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": payload.get("tool_name", ""),
        "skill": tool_input.get("skill") or tool_input.get("command") or "",
        "args": tool_input.get("args", ""),
        "cwd": payload.get("cwd", ""),
        "session": payload.get("session_id", ""),
    }

    try:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
    except Exception:
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
