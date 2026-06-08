---
name: write-svr
description: Use when the user types /write-svr or says generate system validation report — generates the System Validation Report as the final closeout document for a validation effort.
---

# write-svr

## Overview
Generate the System Validation Report (SVR), the final closeout document that summarizes the validation effort and states the release recommendation.

## Triggers
- /write-svr
- "generate system validation report"

## Instructions

1. Read MASTER_CONTEXT.md, DELIVERABLE_STATUS.md, and the RTM from deliverables/.

2. Before generating, check that the RTM exists and shows 100% requirement coverage. If it does not, stop and print: "SVR cannot be generated: X requirements have no linked test case. Resolve via /traceability before proceeding."

3. Check sops/ for a CSV SOP. If found, cite the SVR section number. If not, note: "Add your current CSV SOP to sops/ for cited SVR structure."

4. Generate the SVR with the following sections:
   1. Cover page: system name, risk category, go-live date, validation phase, document version, date, authors
   2. Executive summary: one paragraph covering validation approach, scope, and outcome
   3. Validation activities completed: table with columns Activity | Deliverable | Version | Date | Author | Status
   4. Test execution summary: table with columns Test Suite | Total Cases | Passed | Failed | Blocked | Pass Rate
   5. Defects summary: table with columns Defect ID | Severity | Description | Resolution | Status
   6. Open items and risk acceptance: any open items, the risk owner, and the accepted risk statement
   7. Conclusion and release recommendation: explicit statement that the system is or is not recommended for release, with rationale

5. Insert [CONFIRM: ...] placeholders for any values not present in MASTER_CONTEXT.

6. Save to deliverables/in-progress/<SystemName>_SVR_v1.0_draft.md

7. Update DELIVERABLE_STATUS.md.

## GxP rules
Use "shall", never "should". No vague terms. Every test execution claim must reference a specific evidence file or report location.
