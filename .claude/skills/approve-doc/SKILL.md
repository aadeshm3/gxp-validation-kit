---
name: approve-doc
description: Use when the user types /approve-doc <filename> or says "mark <doc> as approved" — moves a deliverable to deliverables/approved/ and updates project status.
---

# approve-doc

## Overview
Mark a deliverable as approved, move it to deliverables/approved/, and update context and status records.

## Triggers
- /approve-doc <filename>
- "mark <doc> as approved"

## Instructions

1. Find the file in deliverables/in-progress/ (fuzzy match on name).

2. Confirm with the user: "Moving <filename> to deliverables/approved/ and marking as approved in context. Confirm? (yes/no)"

3. On confirm:
   - copy the file to deliverables/approved/
   - update DELIVERABLE_STATUS.md status to "Approved"
   - add the approval date

4. Update MASTER_CONTEXT.md section 4 (Validation Deliverables Status) to reflect approval.

5. Check whether any other deliverables reference this one and flag them for update if needed.

6. Print: "Approved. MASTER_CONTEXT and DELIVERABLE_STATUS updated."

## Notes
Do not proceed without explicit user confirmation in step 2. The approved/ folder holds signed-off records only and is versioned in git.
