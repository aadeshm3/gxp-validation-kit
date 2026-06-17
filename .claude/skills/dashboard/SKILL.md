---
name: dashboard
description: Use when the user says "show me the dashboard", "open the status dashboard", "show status visually", or types /dashboard — builds the visual HTML status view and tells the user how to open it. The user never runs anything themselves.
---

# dashboard

## Overview
Produce the visual status page (status.html) and hand it to the user. The user asks in plain language; you run the tool for them.

## Triggers
- /dashboard
- "show me the dashboard", "open the status dashboard", "show status visually"

## Instructions

1. Run the generator for the user: `python scripts/dashboard.py` (use the Bash tool). The user does not run this.

2. Tell the user it is ready and how to open it, matched to where they are:
   - In a browser environment (Codespaces or VS Code): "Click status.html in the file list on the left, then choose Open Preview (or Open in Browser)."
   - On their own computer: "Double-click status.html in the project folder."

3. Also summarize the headline numbers in plain language, in case they cannot open the file right now: how many deliverables, how many open items, and the single recommended next step.

## Rules
Plain language only. Never tell the user to run a command — you run it for them and report the result. If the script reports a problem, explain it in plain terms and suggest the next step.
