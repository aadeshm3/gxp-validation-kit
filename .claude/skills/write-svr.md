---
name: write-svr
description: Use when the user types /write-svr or says generate system validation report — generates the System Validation Report as the final closeout document for a validation effort.
---

# write-svr

## Overview
Generate a validation summary or closeout report that summarizes the validation effort and states the release recommendation. If a closeout template exists in templates/, use it as the structure; otherwise use the generic structure below.

## Triggers
- /write-svr
- "generate system validation report"

## Instructions

1. Read MASTER_CONTEXT.md, DELIVERABLE_STATUS.md, workbench.config.yaml, and the RTM from deliverables/.

2. Before generating, check the RTM coverage against coverage_target_percent in workbench.config.yaml (default 100; 0 disables this gate). If coverage is below the target, stop and print: "Closeout report cannot be generated: coverage is X% against a target of Y%. Resolve via /traceability before proceeding."

3. Check sops/ for a procedure that defines the closeout report structure. If found, cite the specific file and section. If not, note which SOP to add to sops/ for cited structure. Never invent a section number.

4. Use the closeout template from templates/ if present. Otherwise generate the following generic sections:
   1. Cover page: system name, go-live date, document version, date, authors, and any other metadata fields configured in workbench.config.yaml
   2. Executive summary: one paragraph covering validation approach, scope, and outcome
   3. Validation activities completed: table with columns Activity | Deliverable | Version | Date | Author | Status
   4. Test execution summary: table with columns Test Suite | Total Cases | Passed | Failed | Blocked | Pass Rate
   5. Defects summary: table with columns Defect ID | Severity | Description | Resolution | Status
   6. Open items and acceptance: any open items, the owner, and the acceptance statement
   7. Conclusion and release recommendation: explicit statement that the system is or is not recommended for release, with rationale

5. Insert placeholders, using the marker from workbench.config.yaml, for any values not present in MASTER_CONTEXT.

6. Save to deliverables/in-progress/ using the naming pattern in workbench.config.yaml.

7. Update DELIVERABLE_STATUS.md.

## Rules
Apply the language rules from workbench.config.yaml (defaults in CLAUDE.md if absent). Every test execution claim must reference a specific evidence file or report location. The coverage gate is configurable, not assumed.
