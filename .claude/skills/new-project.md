---
name: new-project
description: Use when the user types /new-project, says "start new project", or "set up new project" — scaffolds a new validation project with MASTER_CONTEXT skeleton, project_data.py, and folder structure.
---

# new-project

## Overview
Scaffold a new validation project for a system not yet in the workbench. Creates the MASTER_CONTEXT skeleton, project_data.py, and folder structure, and derives the required artifact set from the risk category per your organization's computer system validation SOP.

## Triggers
- /new-project
- "start new project"
- "set up new project"

## Instructions

1. Ask the user for the following, one question at a time:
   - System name (for example: LCDA Phase 1, MyApp v2)
   - Risk Category (per your organization's computer system validation SOP)
   - Go-live target date
   - Primary stakeholders: System Owner, System Custodian, TSME, BSME, CSQA names
   - Compliance framework: GxP only / 21 CFR Part 11 / HIPAA / all
   - Validation phase: New system (full CSV) / Major change / Minor change

2. Determine the required artifact set. Ask the user: What risk category does your organization's CSV SOP assign to this system? Enter the category exactly as your SOP defines it. If sops/ contains a CSV SOP, read it to list the available categories and their artifact requirements. If sops/ is empty, record whatever the user provides and insert [CONFIRM: verify artifact scope against your current CSV SOP] in the generated MASTER_CONTEXT.

3. Multi-project support: create a subfolder projects/<SystemName>/ with its own context/, deliverables/in-progress/, and deliverables/approved/ subfolders. For a single-project setup, use the repo root structure instead.

4. Create projects/<SystemName>/project_data.py by copying data/project_data_template.py and filling in:
   - System metadata (name, RC, go-live, compliance)
   - Stakeholders dict
   - PENDING_CONFIRMATIONS list (empty, with the format comment retained)
   - DELIVERABLE_SCOPE list (derived from the risk category)
   - OSS_LIBRARIES list (empty placeholder)
   - INTERFACES list (empty placeholder)

5. Populate MASTER_CONTEXT.md (or projects/<SystemName>/MASTER_CONTEXT.md) with all known values. Mark unknowns as [CONFIRM: description — ref: owner].

6. Create a row in DELIVERABLE_STATUS.md for each required artifact with status "Not Started".

7. Print:
   - "Project scaffolded: <SystemName> (<risk category>)"
   - The required artifact list with count
   - "Next: drop project source docs into context/project-docs/ and run /build-context"

## GxP rules
Apply the GxP writing rules in CLAUDE.md. Derive artifact scope strictly from the confirmed risk category as defined in your organization's computer system validation SOP. Record stakeholders attributably. Mark every unknown as a [CONFIRM: ...] placeholder rather than guessing.
