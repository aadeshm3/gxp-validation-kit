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
   - SOP Reference (from sops/ lookup, or a placeholder if absent)
   - Status (Draft / Approved)
   - Owner

4. Validate each requirement using the same checks as /validate-requirement before export. Flag any failing requirement in the Status column as Needs Revision. Do not silently export non-compliant requirements.

5. Save to context/dev-inputs/<SystemName>_requirements_ALM_export.csv

6. Print: "X requirements exported (Y passed validation, Z flagged as Needs Revision). Import this CSV file via your ALM tool's CSV import function."

7. Read `alm_integration` from workbench.config.yaml. Evaluate the following conditions in order:

   a. If `enabled` is `false`, or if any of the following fields is blank — `tool_url`, `project_key`, `auth_env_var`, or any entry under `field_map` (`id`, `title`, `criterion`, `topic`) — skip the REST push entirely. Print: "ALM integration not configured — CSV written to context/dev-inputs/. To enable direct push, fill in alm_integration in workbench.config.yaml."

   b. If `enabled` is `true` and all required fields are present, perform the following steps in order:
      - Read the API token from the environment variable named by `auth_env_var`. Never read the token from the config file. Never store, log, or print the token value at any point.
      - For each requirement row exported in step 3, construct the REST payload by mapping fields using `field_map`: the requirement ID maps to the field named by `field_map.id`, the title maps to `field_map.title`, the acceptance criterion maps to `field_map.criterion`, and the topic maps to `field_map.topic`.
      - Display the exact payload that would be sent for each requirement row. Do not execute the push.
      - Print: "Ready to push X requirements to [tool_url]. Confirm with 'yes, push to ALM' or copy the CSV for manual import."
      - Wait for explicit user confirmation before performing any network request.

## GxP rules
Apply the GxP writing rules in CLAUDE.md. Never export a requirement that fails validation without marking it Needs Revision. SOP references are cited only from files present in sops/, never invented.
