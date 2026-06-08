---
name: generate-doc
description: Use when the user types /generate-doc <type> where type is vtp, ds, so, security-plan, sop, test-cases, or rtm — generates a validation deliverable from the matching template and current project context.
---

# generate-doc

## Overview
Generate a validation deliverable using the appropriate template, the current MASTER_CONTEXT.md data, and relevant SOP guidance.

## Triggers
- /generate-doc <type> where type is one of: vtp, ds, so, security-plan, sop, test-cases, rtm

## Instructions

1. Read MASTER_CONTEXT.md. If it is empty or missing, stop and tell the user to run /build-context first.

2. Identify the document type from the argument:
   - vtp = Validation and Test Plan
   - ds = Design Specification
   - so = System Overview
   - security-plan = Security Plan
   - sop = SOP — ask the user which SOP: playwright, admin, security-admin, or change-control
   - test-cases = Test case shells from approved requirements
   - rtm = Requirements Traceability Matrix

3. Check templates/ for a matching template file. If found, use it as the base. If not found, warn the user and offer to generate from scratch using a standard validation document structure.

4. Check sops/ for a CSV SOP, change control SOP, and security SOP. If found, cite the specific file and section. If not found, insert [CONFIRM: add your current [SOP type] to sops/ for cited generation].

5. Generate the document using: template structure + MASTER_CONTEXT data + SOP guidance.

6. Where information is missing or unconfirmed, insert a yellow-highlighted placeholder in the format: [CONFIRM: description of what is needed — ref: <owner>].

7. Save output to deliverables/in-progress/<SystemName>_<DocType>_v1.0_draft.docx (or .md if no template is available).

8. Update DELIVERABLE_STATUS.md: add a row for this doc with status "Draft", date, and filename.

9. Run /update-context automatically.

10. Print: "Generated: deliverables/in-progress/<filename>. X placeholders need dev team input. Review before routing."

## GxP rules
Enforce the GxP writing rules in CLAUDE.md throughout generated content: ALM-clean acceptance criteria, closed lists, specific mechanisms/values/thresholds, ALCOA+ framing, and SOP citations.
