---
name: bulk-confirm
description: Use when the user types /bulk-confirm, says "resolve all confirmations", "batch confirm", or "confirm multiple items" — resolves multiple [CONFIRM] placeholders at once from a file or inline list.
---

# bulk-confirm

## Overview
Resolve multiple pending confirmations in a single pass. The user supplies values either as a file in context/dev-inputs/ or as inline key=value pairs. Each item is resolved using the same logic as /confirm-item.

## Triggers
- /bulk-confirm
- "resolve all confirmations"
- "batch confirm"
- "confirm multiple items"

## Instructions

1. Determine the input source:
   - If the user names a file, read it from context/dev-inputs/. Expect rows in the format: ID,value (one per line, CSV). Skip blank lines and lines starting with #.
   - If the user types values inline, parse the format: ID1=value1, ID2=value2.
   - If neither is provided, list all open items from MASTER_CONTEXT.md section 6 and ask the user to supply values in one of the two formats above.

2. For each ID-value pair, apply the full /confirm-item logic:
   a. Locate the item in projects/<SystemName>/project_data.py PENDING_CONFIRMATIONS.
   b. Set confirmed=True and fill the value field.
   c. Update MASTER_CONTEXT.md: mark the item Resolved with the confirmed value and today's date.
   d. Search deliverables/ for the ID. Note any files containing it for step 4.

3. Track three counts: Resolved (found and updated), Not Found (ID not in project_data.py), Still Open (ID found but value was blank or "TBD").

4. After processing all items, list each deliverable that contains a resolved ID and ask: "These documents reference resolved items: <list>. Regenerate affected sections? (yes/no)".

5. Run /update-context.

6. Print the summary: "Resolved: X. Not found: Y. Still open: Z."

## Rules
Values of "TBD", "to be confirmed", or blank shall be rejected and counted as Still Open. Every resolution shall record today's date and the source (file or inline). The input file shall not be modified or deleted.
