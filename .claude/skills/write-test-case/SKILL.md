---
name: write-test-case
description: Use when the user types /write-test-case <requirement-id> or /write-test-case alone — generates a formal GxP test case from an approved requirement.
---

# write-test-case

## Overview
Generate a formal GxP test case from an approved requirement, including evidence and 21 CFR Part 11 / ALCOA+ considerations.

## Triggers
- /write-test-case <requirement-id>
- /write-test-case (then ask the user which requirement)

## Instructions

1. Read MASTER_CONTEXT.md to understand system context.

2. Ask the user for:
   - requirement text (or ID if a requirements doc is in context/)
   - test environment (Dev / QA / Prod)
   - execution method (automated Playwright / manual)

3. Generate the test case with these fields:
   - Test Case ID: TC-<topic>-<number>
   - Requirement ID: (linked)
   - Test Objective: one sentence, what is being verified
   - Preconditions: numbered list — what must be true before execution
   - Test Steps: numbered, each step is one action with exact command/input
   - Expected Result: specific, measurable, no "should" — use "shall" or "is"
   - Pass Criteria: binary — what constitutes pass
   - Fail Criteria: what constitutes fail and what to do (raise defect / script error)
   - Evidence: what evidence is captured (Playwright HTML report, screenshot, query result JSON)
   - GxP Notes: any 21 CFR Part 11 or ALCOA+ considerations

4. For automated tests (Playwright): also generate the TypeScript test function signature with correct tags (@smoke, @dbx, etc.).

5. Save to deliverables/in-progress/<SystemName>_TestCases_draft.md (append if the file exists).

6. Print: "Test case TC-<id> written."

## GxP rules
Expected results and pass/fail criteria must be specific and measurable. Use "shall" or "is", never "should". Capture attributable, contemporaneous, original evidence per ALCOA+.
