---
name: audit-log
description: Use when the user types /audit-log, says "show activity log", "show audit trail", or "what skills have been run" — reads audit/ledger.jsonl and displays the activity trail in table or summary form.
---

# audit-log

## Overview
Display the skill activity trail recorded in audit/ledger.jsonl. Supports three output modes: recent entries, filtered by skill, or a run-count summary. The ledger is never modified.

## Triggers
- /audit-log
- /audit-log <skill-name>
- /audit-log --summary
- "show activity log"
- "show audit trail"
- "what skills have been run"

## Instructions

1. Check whether audit/ledger.jsonl exists and contains at least one line. If it does not exist or is empty, print: "No activity recorded yet. The ledger will appear after the first skill run." Stop.

2. Parse the argument:
   - No argument: show the last 20 entries.
   - A skill name: filter to entries where the skill field matches that name.
   - --summary: aggregate mode (see step 4).

3. For the last-20 and filtered modes, output a markdown table with the following columns: Date/Time | Skill | Args | Session. Format Date/Time as YYYY-MM-DD HH:MM. Truncate Args values longer than 60 characters with "...". Sort entries newest first.

4. For --summary mode, output a markdown table with the following columns: Skill | Total Runs | First Run | Last Run | Unique Sessions. Sort by Total Runs descending.

5. Below the table, print the total number of entries shown and the date range covered.

## Rules
The ledger file shall not be modified, appended to, or deleted by this skill. Output shall be read-only. If a ledger entry is malformed (missing required fields), skip it and note the count of skipped entries below the table.
