---
name: validate-requirement
description: Use when the user types /validate-requirement or pastes a requirement and asks if it is ALM-ready — checks a single requirement for GxP testability and ALM compliance without modifying any file.
---

# validate-requirement

## Overview
Check a single requirement for GxP testability and ALM compliance. Read-only: this skill never modifies or writes any file.

## Triggers
- /validate-requirement
- "is this requirement ALM-ready"
- "check this requirement"

## Instructions

1. Read the requirement text from user input. If no requirement is provided, ask which requirement to check.

2. Run the following checks in order:
   - CHECK 1 LANGUAGE: Must use "shall" or "must". Flag "should", "will", "may", "might", "can".
   - CHECK 2 SPECIFICITY: Must name a specific mechanism, threshold, value, count, or SOP reference. Flag vague terms: appropriate, sufficient, as required, as needed, adequately, timely, in a reasonable manner.
   - CHECK 3 OPEN LISTS: Flag "e.g.", "such as", "including but not limited to", "etc.", "and/or".
   - CHECK 4 TESTABILITY: Determine whether a pass/fail criterion is derivable from the text alone. If not, flag: NOT TESTABLE — needs: [what is missing].
   - CHECK 5 HEDGES: Flag "where applicable", "if applicable", "as appropriate", "when necessary".

3. Output PASS or FAIL. For each failure, list: Finding | Check | Suggested fix.

## GxP rules
Read-only. Never modify any file. Never write output to disk.
