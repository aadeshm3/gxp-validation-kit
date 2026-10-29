"""
context_freshness.py — decide whether MASTER_CONTEXT.md is due for its
automatic refresh.

Invoked by the SessionStart hook in .claude/settings.json. If the last context
refresh was at least context_refresh.interval_hours ago (default 24) and files
in context/ or deliverables/approved/ changed since, it prints an instruction that Claude reads at the
start of the session: run /update-context before doing anything else.
Otherwise it prints nothing.

The last refresh time is the most recent /update-context or /build-context run
recorded in audit/ledger.jsonl. If the ledger has no such entry, the
modification time of MASTER_CONTEXT.md is used.

Settings come from workbench.config.yaml:
  context_refresh:
    enabled: true
    interval_hours: 24

The script is silent on any error and always exits 0, so it can never block a
session from starting.
"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER = REPO_ROOT / "audit" / "ledger.jsonl"
SOURCE_DIRS = (REPO_ROOT / "context", REPO_ROOT / "deliverables" / "approved")
MASTER = REPO_ROOT / "MASTER_CONTEXT.md"
CONFIG = REPO_ROOT / "workbench.config.yaml"
REFRESH_SKILLS = ("update-context", "build-context")

DEFAULT_INTERVAL_HOURS = 24


def load_settings():
    """Return (enabled, interval_hours) from the config, with safe defaults."""
    enabled, hours = True, DEFAULT_INTERVAL_HOURS
    if not CONFIG.is_file():
        return enabled, hours
    text = CONFIG.read_text(encoding="utf-8")
    block = re.search(r"^context_refresh:\s*\n((?:[ \t]+.*\n?)*)", text, re.M)
    if not block:
        return enabled, hours
    body = block.group(1)
    on = re.search(r"^\s+enabled:\s*(\w+)", body, re.M)
    if on:
        enabled = on.group(1).lower() == "true"
    iv = re.search(r"^\s+interval_hours:\s*([0-9.]+)", body, re.M)
    if iv:
        hours = float(iv.group(1))
    return enabled, hours


def last_refresh():
    """Return the time of the last context refresh as an aware datetime, or None."""
    latest = None
    if LEDGER.is_file():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
                stamp = datetime.fromisoformat(entry["timestamp_utc"])
            except Exception:
                continue
            skill = str(entry.get("skill", ""))
            if skill.endswith(REFRESH_SKILLS) and (latest is None or stamp > latest):
                latest = stamp
    if latest is None and MASTER.is_file():
        latest = datetime.fromtimestamp(MASTER.stat().st_mtime, timezone.utc)
    return latest


def changed_files(since):
    """Files in context/ and deliverables/approved/ modified after `since`,
    excluding .gitkeep."""
    cutoff = since.timestamp()
    return sorted(
        p.relative_to(REPO_ROOT).as_posix()
        for folder in SOURCE_DIRS if folder.is_dir()
        for p in folder.rglob("*")
        if p.is_file() and p.name != ".gitkeep" and p.stat().st_mtime > cutoff
    )


def main():
    enabled, hours = load_settings()
    if not enabled or not MASTER.is_file():
        return
    since = last_refresh()
    if since is None:
        return
    age = datetime.now(timezone.utc) - since
    if age < timedelta(hours=hours):
        return
    changed = changed_files(since)
    if not changed:
        return
    shown = "\n".join("- " + name for name in changed[:20])
    more = "\n- ...and {} more".format(len(changed) - 20) if len(changed) > 20 else ""
    print(
        "AUTOMATIC CONTEXT REFRESH DUE. MASTER_CONTEXT.md was last refreshed "
        "{:.0f} hours ago (limit: {:g} hours) and {} file(s) in context/ changed "
        "since. Run /update-context now, before the user's first request, then "
        "continue with what the user asked.\nChanged files:\n{}{}".format(
            age.total_seconds() / 3600, hours, len(changed), shown, more
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
