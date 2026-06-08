---
name: generate-doc
description: Use when the user types /generate-doc, says "generate a document", or names a deliverable to produce — reads a template's sections and their instruction text, then fills each section with project information or a [CONFIRM] flag.
---

# generate-doc

## Overview
Produce a deliverable by reading the chosen template section by section. Each section has a heading and usually some instruction or guidance text describing what belongs there. Replace that instruction text with real content drawn from the project, or with a [CONFIRM: ...] marker where the project does not yet have the information. Keep the template's headings, order, and formatting.

## Triggers
- /generate-doc <template-or-alias>
- /generate-doc (with no argument — then list available templates and ask which to generate)
- "generate a document" or naming a deliverable to produce

## Instructions

1. Read MASTER_CONTEXT.md. If it is empty or missing, stop and tell the user to run /build-context first.

2. Resolve the template. Read workbench.config.yaml for any alias under deliverables. If no argument was given, list the files in templates/ and ask which to use. If no template matches, tell the user which file to add to templates/ and offer to generate a generic structure instead.

3. Get the section outline and instruction text. Run:
   `python scripts/generate_doc.py <template> --outline`
   This returns each section as { level, heading, instruction }. The instruction is the guidance text the template author placed under that heading.

4. For each section, read its instruction text and understand what content that section asks for. Then compose the content that satisfies it:
   - Draw the facts from MASTER_CONTEXT.md and the project files.
   - Cite the specific SOP file and section from sops/ where a rule applies. Never invent an SOP name or section number.
   - Apply the language rules from workbench.config.yaml (defaults in CLAUDE.md if the config is absent).
   - The composed content replaces the instruction text. Do not keep the original guidance in the finished section.
   - Where the project does not have the information, write the placeholder marker from the config (default: [CONFIRM: what is needed — ref: owner]) in place of the instruction, rather than guessing.

5. Build a content map as JSON, { "<exact heading text>": "<composed content>" }, covering every section you can fill or mark. Save it to a temporary file.

6. Produce the filled draft, preserving the template's formatting:
   `python scripts/generate_doc.py <template> --fill <content-map.json>`
   This writes the draft to deliverables/in-progress/ using the naming pattern from the config, replacing each mapped section's instruction text with your content and leaving any section you did not map with its original instruction text.

7. Update DELIVERABLE_STATUS.md: add a row with status "Draft", date, and filename.

8. Run /update-context automatically.

9. Print: "Generated: deliverables/in-progress/<filename>. X sections still need a confirmed value. Review before routing."

## Rules
The template defines the sections — never impose a section list of your own. Replace instruction text with real content or a [CONFIRM] marker; never leave raw guidance in a filled section and never invent a value. Apply the configured language rules and cite only SOPs that exist in sops/.
