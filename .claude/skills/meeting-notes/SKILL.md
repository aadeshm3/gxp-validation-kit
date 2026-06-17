---
name: meeting-notes
description: Use when the user types /meeting-notes <filename>, says "process meeting notes", or "I just dropped meeting notes in context/" — extracts structured decisions, actions, and confirmations and updates project context.
---

# meeting-notes

## Overview
Process meeting notes dropped in context/meeting-notes/ and extract structured information to update project context.

## Triggers
- /meeting-notes <filename>
- "process meeting notes"
- "I just dropped meeting notes in context/"

## Instructions

1. Find the most recently added file in context/meeting-notes/ (or the file named by the user).

2. Read the full file.

3. Extract and structure:
   - Meeting date and attendees
   - DECISIONS MADE: each decision as one sentence, with owner
   - ACTION ITEMS: each action with owner, due date if mentioned
   - OPEN ITEMS: questions raised, unresolved topics, items sent to dev team
   - DEV TEAM CONFIRMATIONS: any value confirmed by dev/engineering team
   - SCOPE CHANGES: any in-scope/out-of-scope decisions
   - TIMELINE UPDATES: any date changes

4. For each dev team confirmation: check whether it matches a pending item in the MASTER_CONTEXT Open Items section. If yes, mark it resolved.

5. Update MASTER_CONTEXT.md:
   - merge decisions into section 7 (Key Decisions Made)
   - merge action items into section 10 (Pending Work)
   - close resolved items in section 6

6. Save the structured extract as context/decisions/<date>_<meeting-topic>_extract.md

7. For each extracted action item, link it to a deliverable as follows:
   - Read the deliverable list from DELIVERABLE_STATUS.md (all rows) and from workbench.config.yaml (aliases field, if present). Combine both into a single reference list.
   - For each action item, check whether the action text explicitly names or implies a deliverable by matching against that reference list (exact name match or alias match).
   - If a match is found: add the action as an open item row in the "Next Action" column of the matching row in DELIVERABLE_STATUS.md. The entry shall use the format: ACTION [date]: [owner] — [action text]
   - If DELIVERABLE_STATUS.md has no row matching the deliverable yet: record the action in MASTER_CONTEXT.md section 6 (Open Items) using the same format.
   - Count the results and hold them for the print step: X = number of actions linked to a deliverable row in DELIVERABLE_STATUS.md; Y = number of actions added to MASTER_CONTEXT.md section 6.

8. Print summary: "Processed: X decisions, Y action items, Z open items, W confirmations. MASTER_CONTEXT updated. X actions linked to deliverables, Y added to open items."

## GxP rules
Record decisions and confirmations attributably (who decided, when). Convert relative dates to absolute dates. Keep unconfirmed items as [CONFIRM: description — ref: owner].
