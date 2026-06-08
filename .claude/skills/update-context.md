---
name: update-context
description: Use when the user types /update-context, or automatically at the end of any session where project work was done — incrementally refreshes MASTER_CONTEXT.md from new or changed files in context/.
---

# update-context

## Overview
Incrementally update MASTER_CONTEXT.md from new or changed files in context/. Only the delta is processed; unchanged sections are left untouched.

## Triggers
- /update-context
- Automatically at the end of any session where project work was done (per the auto-context rule in CLAUDE.md).

## Instructions

1. Read the current MASTER_CONTEXT.md to understand existing state, including the Last Refreshed date in the header.

2. Glob context/ for all files (exclude .gitkeep). Compare each file's modification date to the Last Refreshed date.

3. Read only files newer than the last refresh. If MASTER_CONTEXT.md is empty or missing, read all files (and recommend /build-context instead).

4. For each new or changed file, extract only the delta:
   - new decisions
   - new confirmations
   - new open items
   - status changes
   - new stakeholders

5. Merge into MASTER_CONTEXT.md:
   - update changed sections
   - add new items
   - mark resolved items as done
   - update the Last Refreshed date in the header

6. Do NOT rewrite sections that have not changed.

7. Print summary: "Updated X sections. New items: [list]. Resolved items: [list]."

## GxP rules
Apply the GxP writing rules in CLAUDE.md. Keep unconfirmed values as [CONFIRM: description — ref: owner]. Preserve SOP citations.
