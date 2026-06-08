---
name: generate-doc
description: Use when the user types /generate-doc, says "generate a document", or names a deliverable to produce — generates any deliverable from a template in templates/ and current project context.
---

# generate-doc

## Overview
Generate any deliverable from a template the user has placed in templates/, filled with current project context and cited against the user's SOPs. The framework does not define document types — the templates do.

## Triggers
- /generate-doc <template-or-alias>
- /generate-doc (with no argument — then list available templates and ask which to generate)
- "generate a document" or naming a deliverable to produce

## Instructions

1. Read MASTER_CONTEXT.md. If it is empty or missing, stop and tell the user to run /build-context first.

2. Read workbench.config.yaml if present. Resolve the requested deliverable:
   - If the argument matches an alias under deliverables in the config, use the mapped template file.
   - Otherwise treat the argument as a template filename or a fuzzy match against files in templates/.
   - If no argument is given, list every file in templates/ and ask the user which to generate.

3. If a matching template exists in templates/, use it as the base structure. If no template exists, tell the user no template was found, name the file to add to templates/, and offer to generate from a generic document structure instead.

4. Check sops/ for procedures relevant to this deliverable. If found, cite the specific file and section in the generated content. If not found, insert a placeholder noting which SOP to add to sops/ for cited generation. Never invent SOP section numbers.

5. Generate the document from: template structure + MASTER_CONTEXT data + SOP citations. Required sections come from the template, not from any built-in list.

6. Where information is missing or unconfirmed, insert a placeholder using the marker defined in workbench.config.yaml (default: [CONFIRM: description — ref: owner]).

7. Save the output to deliverables/in-progress/ using the naming pattern in workbench.config.yaml (default: <System>_<Doc>_v<version>_draft). Use .docx if the template is Word, otherwise .md.

8. Update DELIVERABLE_STATUS.md: add a row with status "Draft", date, and filename.

9. Run /update-context automatically.

10. Print: "Generated: deliverables/in-progress/<filename>. X placeholders need input. Review before routing."

## Rules
Apply the language rules from workbench.config.yaml (defaults in CLAUDE.md if the config is absent). Do not assume any document type, section list, risk category, or artifact scope. Everything specific comes from the template, the SOPs, and the config.
