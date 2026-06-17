---
name: extract-requirements
description: Use when the user types /extract-requirements <filename> or says "extract requirements from <doc>" — reads a source document and produces ALM-ready GxP acceptance criteria.
---

# extract-requirements

## Overview
Read a source document (BRD, charter, architecture doc, meeting notes) and generate ALM-ready GxP acceptance criteria.

## Triggers
- /extract-requirements <filename>
- "extract requirements from <doc>"

## Instructions

1. Find the file in context/ (fuzzy match). If not found, ask the user which file.

2. Read the full document.

3. Identify all statements of system behaviour, capability, or constraint.

4. For each item, generate a formal acceptance criterion:
   - Format: "The system shall <specific, measurable action> <specific mechanism/value/threshold> [as defined in <DS/SOP reference if known>]."
   - Enforce GxP rules: no "e.g.", no hedges, no open lists, no "where applicable".
   - Group by topic: Ingestion, Data Integrity, Audit Trail, RBAC, Security, Performance, Backup/Recovery.

5. Flag any item that is NOT testable with [NOT TESTABLE — needs: specific value/threshold/component].

6. Flag any item that needs dev team input with [CONFIRM: description].

7. Output as a markdown table: | ID | Topic | Acceptance Criterion | Testable | Notes |

8. Save to context/dev-inputs/<SystemName>_requirements_draft.md for import into your ALM tool.

9. Print count: "X requirements extracted. Y not testable — need dev input. Z need confirmation."

## GxP rules
Every criterion must name a specific mechanism, value, threshold, or reference. Reject vague terms such as "appropriate", "sufficient", "as required". Use closed lists only.
