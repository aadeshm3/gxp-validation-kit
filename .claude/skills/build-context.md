---
name: build-context
description: Use when the user types /build-context, says "build context", or "generate master context" — builds MASTER_CONTEXT.md from scratch by reading every file in context/.
---

# build-context

## Overview
Read all files in context/ subfolders and build MASTER_CONTEXT.md from scratch. This is the full rebuild; use update-context for incremental refreshes.

## Triggers
- /build-context
- "build context"
- "generate master context"

## Instructions

1. Announce: "Building MASTER_CONTEXT.md from all files in context/..."

2. Use Glob to list every file in context/ recursively. Exclude any .gitkeep file.

3. Read each file by type:
   - Word (.docx): extract text with python-docx via Bash.
   - PDF (.pdf): extract text with pypdf via Bash.
   - .txt / .md: read directly.
   - .xlsx: extract with openpyxl via Bash.

4. From each file, extract:
   - system name
   - project background
   - stakeholders and roles
   - architecture decisions
   - open items
   - timeline / milestones
   - any metadata fields listed under project_metadata_fields in workbench.config.yaml
   - pending confirmations from other parties
   - approved decisions

5. Build MASTER_CONTEXT.md with these sections:
   - Header: system name, last refreshed date, go-live date, plus any metadata fields configured in workbench.config.yaml
   - 1. Project Overview (one paragraph)
   - 2. Stakeholders / RACI table
   - 3. Architecture & Tech Stack
   - 4. Validation Deliverables Status table (doc | status | due | notes)
   - 5. Requirements Status
   - 6. Open Items & Pending Confirmations (numbered, owner, description)
   - 7. Key Decisions Made (with date and rationale)
   - 8. Timeline
   - 9. Key Files & Scripts
   - 10. Pending Work

6. Write MASTER_CONTEXT.md to the repo root.

7. Print: "MASTER_CONTEXT.md built. X files processed. Review and correct any misread values."

8. If context/ is empty (no files other than .gitkeep), do not write the file. Instead print instructions on what to drop in and where:
   - charters, BRDs, architecture docs → context/project-docs/
   - meeting notes → context/meeting-notes/
   - dev team confirmations → context/dev-inputs/
   - decision records → context/decisions/

## GxP rules
Apply the GxP writing rules in CLAUDE.md to all generated content. Surface unconfirmed values as [CONFIRM: description — ref: owner]. Cite SOPs from sops/ where relevant, or flag the SOP to add.

## After running
This skill changes project state. Run /update-context is not required here (this is the full build), but confirm the user reviews misread values before generating deliverables.
