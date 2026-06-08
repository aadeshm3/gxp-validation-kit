---
name: export-alm
description: Use when the user types /export-alm or says export requirements for ALM — formats approved requirements as a CSV file for import into any ALM tool.
---

# export-alm

## Overview
Format approved requirements as a CSV file for import into any ALM tool, validating each requirement before export.

## Triggers
- /export-alm <filename>
- "export requirements for ALM"
- "export to ALM"

## Instructions

1. Find the requirements file in context/dev-inputs/ or deliverables/ (fuzzy match, or ask the user).

2. Read all requirements.

3. For each requirement, produce a CSV row with the following columns:
   - ID
   - Type (Functional / Non-Functional / Security / Performance / Data Integrity)
   - Title (short — 10 words maximum)
   - Acceptance Criterion (full text)
   - Testable (Y/N)
   - Risk Category (read from MASTER_CONTEXT or [CONFIRM])
   - SOP Reference (from sops/ lookup or [CONFIRM])
   - Status (Draft / Approved)
   - Owner

4. Validate each requirement using the same checks as /validate-requirement before export. Flag any failing requirement in the Status column as Needs Revision. Do not silently export non-compliant requirements.

5. Save to context/dev-inputs/<SystemName>_requirements_ALM_export.csv

6. Print: "X requirements exported (Y passed validation, Z flagged as Needs Revision). Import this CSV file via your ALM tool's CSV import function."

## GxP rules
Apply the GxP writing rules in CLAUDE.md. Never export a requirement that fails validation without marking it Needs Revision. SOP references are cited only from files present in sops/, never invented.
