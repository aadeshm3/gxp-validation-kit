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

   If the file is under context/prior-versions/, it describes what the
   system was at a specific past version, which may now be stale. Tag
   every fact extracted from it with its source, e.g. "per prior version
   (v1.0): ..." — never present it as current fact.

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

6. Determine the section list for MASTER_CONTEXT.md:

   a. Determine the in-scope templates: read the `deliverables:` list in
      workbench.config.yaml. If it lists one or more aliases, resolve each
      to its file in templates/ — that is the in-scope set. If the list is
      empty, treat every file in templates/ (excluding .gitkeep and
      README.md) as in scope.

   b. If the in-scope set is empty (no deliverables configured and
      templates/ has no usable files), use the generic fallback structure
      in step 6-fallback below and skip to step 7.

   c. For each in-scope template, run:
      `python scripts/generate_doc.py <template> --outline`
      and collect its returned `heading` values as that document type's
      section list.

   d. Merge shared front-matter across templates: any heading that
      case-insensitively matches one of Purpose, Scope, Out of Scope,
      Reviewers, Approvers, Revision History, or Stakeholders is folded
      into ONE shared MASTER_CONTEXT section (do not repeat it once per
      template).

   e. Any other heading is specific to that document type. Group these
      under a subsection named after the document (e.g. "Deliverable —
      Backup and Restoration SOP").

   f. Always include this fixed bookkeeping scaffold regardless of what
      templates produced (this is the framework's own project-tracking
      structure, not deliverable content, so it is not "invented"):
      - Open Items & Pending Confirmations (numbered, owner, description)
      - Key Decisions Made (with date and rationale)
      - Timeline
      - Key Files & Scripts
      - Pending Work

6-fallback. Generic structure (used only when step 6b applies — no
   templates and no configured deliverables):
   - Header: system name, last refreshed date, go-live date, plus any
     metadata fields configured in workbench.config.yaml
   - 1. System Overview (one paragraph)
   - 2. Stakeholders
   - 3. Architecture
   - 4. Requirements
   - 5. Open Items & Pending Confirmations
   - 6. Key Decisions Made (with date and rationale)
   - 7. Timeline
   - 8. Pending Work

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
