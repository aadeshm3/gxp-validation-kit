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

5. Before writing MASTER_CONTEXT.md, run conflict detection across all files read in step 4:

   a. From each source file, extract the following fields:
      - System Name
      - Go-Live Date
      - All owner and stakeholder names

   b. For each field, collect every distinct value found and which file it came from. A conflict exists when the same field has two or more different values across different files.

   c. For each conflict detected, do the following:
      - Record the conflict as: field name | value A (from file X) | value B (from file Y).
      - Do not silently pick one value. Instead, write the field into MASTER_CONTEXT.md as a [CONFIRM: two conflicting values found — ref: user] placeholder.
      - Accumulate all conflicts into a conflict list.

   d. After processing all files, if one or more conflicts were found, print the conflict list to the user in the following format before proceeding:
      "Conflicts detected — resolve before generating deliverables:"
      Then list each conflict as: Field: <name> | File A: <filename> → "<value A>" | File B: <filename> → "<value B>"

   e. If no conflicts are found, proceed silently.

6. Build MASTER_CONTEXT.md with these sections:
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

7. Write MASTER_CONTEXT.md to the repo root.

8. Print: "MASTER_CONTEXT.md built. X files processed. Review and correct any misread values."

9. If context/ is empty (no files other than .gitkeep), do not write the file. Instead print instructions on what to drop in and where:
   - charters, BRDs, architecture docs → context/project-docs/
   - meeting notes → context/meeting-notes/
   - dev team confirmations → context/dev-inputs/
   - decision records → context/decisions/

## GxP rules
Apply the GxP writing rules in CLAUDE.md to all generated content. Surface unconfirmed values as [CONFIRM: description — ref: owner]. Cite SOPs from sops/ where relevant, or flag the SOP to add.

## After running
This skill changes project state. Run /update-context is not required here (this is the full build), but confirm the user reviews misread values before generating deliverables.
