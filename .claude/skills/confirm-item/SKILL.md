---
name: confirm-item
description: Use when the user types /confirm-item <ID> "<value>", says "confirm item PC-001 is <value>", or "dev team confirmed <item>" — resolves a pending confirmation in project_data.py and MASTER_CONTEXT.md.
---

# confirm-item

## Overview
Resolve a specific pending confirmation when the dev team provides a value. Updates project_data.py and MASTER_CONTEXT.md, and offers to regenerate affected deliverables.

## Triggers
- /confirm-item <ID> "<value>"
- "confirm item PC-001 is <value>"
- "dev team confirmed <item>"

## Instructions

1. Parse the item ID (for example PC-001) and the confirmed value from the user input. If /confirm-item is used with no arguments, read MASTER_CONTEXT section 6, list all open items, and ask the user which one to resolve.

2. Find the item in:
   a. projects/<SystemName>/project_data.py PENDING_CONFIRMATIONS list
   b. MASTER_CONTEXT.md section 6 (Open Items & Pending Confirmations)

3. Update project_data.py: set confirmed=True and fill the value field.

4. Update MASTER_CONTEXT.md: mark the item as Resolved, and add the confirmed value and date.

5. Check which deliverables reference this item (search deliverables/ for the item ID). If found, ask: "This item appears in <doc>. Regenerate that section? (yes/no)".

6. If yes: re-run /generate-doc for the affected document.

7. Print: "Confirmed: <ID> = '<value>'. X references updated. Y documents may need regeneration."

## GxP rules
Record who confirmed the value and when. The value must be specific — reject vague confirmations such as "TBD" or "to be confirmed".
