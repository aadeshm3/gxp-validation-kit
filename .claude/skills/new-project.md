---
name: new-project
description: Use when the user types /new-project, says "start new project", or "set up new project" — scaffolds a new validation project with a MASTER_CONTEXT skeleton, project_data.py, and folder structure.
---

# new-project

## Overview
Scaffold a new validation project for a system not yet in the workbench. Creates the MASTER_CONTEXT skeleton, project_data.py, and folder structure. The deliverables a project needs are decided by the user and by the templates available, not by any built-in risk model.

## Triggers
- /new-project
- "start new project"
- "set up new project"

## Instructions

1. Read workbench.config.yaml if present, to know the configured metadata fields and any template aliases.

2. Ask the user for the project metadata, one question at a time. Use the project_metadata_fields list from the config. If the config is absent, ask for the system name and go-live date, and ask whether they want to record any other metadata (for example a risk category or compliance framework). All metadata is optional free text and never decides which deliverables are produced.

3. Ask the user which deliverables they need for this project. Offer the choices in this order:
   - Any template files present in templates/ (these are the concrete documents available).
   - Any aliases defined under deliverables in workbench.config.yaml.
   - The option to decide later.
   Do not impose a fixed artifact set. Record only what the user selects.

4. Multi-project support: create projects/<SystemName>/ with its own context/, deliverables/in-progress/, and deliverables/approved/ subfolders. For a single-project setup, use the repo root structure.

5. Create projects/<SystemName>/project_data.py by copying data/project_data_template.py and filling in:
   - System metadata from step 2
   - Stakeholders, if provided
   - PENDING_CONFIRMATIONS (empty, with the format comment retained)
   - DELIVERABLE_SCOPE (the deliverables the user selected in step 3)
   - OSS_LIBRARIES and INTERFACES (empty placeholders)

6. Populate MASTER_CONTEXT.md (or projects/<SystemName>/MASTER_CONTEXT.md) with the known values. Mark unknowns with the placeholder marker from the config (default: [CONFIRM: description — ref: owner]).

7. Create a row in DELIVERABLE_STATUS.md for each selected deliverable with status "Not Started".

8. Print:
   - "Project scaffolded: <SystemName>"
   - The selected deliverables with count
   - "Next: drop your templates into templates/, your SOPs into sops/, source docs into context/project-docs/, then run /build-context"

## Rules
Apply the language rules from workbench.config.yaml. Record stakeholders attributably. Mark every unknown as a placeholder rather than guessing. Never assume a risk category, an artifact set, or a document type.
