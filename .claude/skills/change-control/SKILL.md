---
name: change-control
description: Use when the user types /change-control or says generate change control assessment — generates a change control impact assessment for a proposed change to a validated system.
---

# change-control

## Overview
Generate a change control impact assessment for a proposed change to a validated system, including revalidation scope and a proceed recommendation.

## Triggers
- /change-control
- "change control for"
- "impact assessment for change"

## Instructions

1. Ask the user the following, one at a time:
   - What system is changing?
   - Describe the change in one sentence.
   - Is this change pre-validation or post-validation (is the system already live and in validated state)?
   - What is driving this change (defect fix / enhancement / regulatory / infrastructure)?

2. Read MASTER_CONTEXT.md for system context.

3. Check sops/ for a change control SOP. If found, cite it. If not, note: "Add your current change control SOP to sops/ for cited assessment."

4. Generate a change control impact assessment with the following sections:
   1. Change description: who, what, why, when
   2. Affected components: which parts of the validated system are touched
   3. Impact on validated state: whether this breaks any approved test case, and whether it affects audit trail, RBAC, data integrity, or backup
   4. Affected deliverables: which of the project's deliverables need updating. Read the deliverable list from DELIVERABLE_STATUS.md (or the project's selected deliverable scope) and name each affected one with what must change. Do not assume a fixed document set.
   5. Revalidation scope: Full revalidation / Partial (list affected test suites) / No revalidation required — with rationale
   6. Risk rating: High / Medium / Low, with justification
   7. Recommendation: Proceed / Do not proceed pending further review

5. Save to deliverables/in-progress/<SystemName>_ChangeControl_<YYYYMMDD>_draft.md

## GxP rules
Every impact statement must be specific. "No impact" is only acceptable with a stated rationale.
