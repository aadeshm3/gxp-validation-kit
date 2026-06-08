---
name: traceability
description: Use when the user types /traceability, says "generate RTM", "update traceability matrix", or "traceability report" — builds or updates the Requirements Traceability Matrix linking requirements to test cases to evidence.
---

# traceability

## Overview
Generate or update the Requirements Traceability Matrix (RTM) linking requirements to test cases to execution evidence, and calculate coverage.

## Triggers
- /traceability
- "generate RTM"
- "update traceability matrix"
- "traceability report"

## Instructions

1. Read MASTER_CONTEXT.md for the system name and requirements status.

2. Find the requirements source:
   a. context/dev-inputs/<SystemName>_requirements_draft.md (from /extract-requirements)
   b. Any requirements file in context/ (ask the user if multiple are found)

3. Find the test cases source:
   a. deliverables/in-progress/<SystemName>_TestCases_draft.md
   b. deliverables/approved/<SystemName>_TestCases*.md or .docx

4. Build the RTM table with columns:
   | Req ID | Requirement (short) | Test Case ID | Test Case Title | Execution Status | Evidence Location | ALM Link | Notes |

5. Flag gaps:
   - Requirement with NO linked test case: [NO TEST CASE — gap]
   - Test case with NO linked requirement: [ORPHAN — no requirement traced]
   - Requirement with test case but no execution evidence: [NOT EXECUTED]

6. Calculate coverage: X of Y requirements have at least one test case (Z%). Compare against coverage_target_percent in workbench.config.yaml (default 100; a value of 0 disables gating).

7. Save to deliverables/in-progress/<SystemName>_RTM_draft.md

8. Update DELIVERABLE_STATUS.md: add or update the RTM row.

9. Print: "RTM generated. Coverage: X/Y requirements (Z%). Gaps: A requirements untested, B orphan test cases."

## Rules
Every requirement must have at least one linked verification item. The required coverage level is coverage_target_percent in workbench.config.yaml — it is a configurable target, not a fixed assumption. Report whether the project meets its configured target.
