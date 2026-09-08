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

4. Discover header/footer placeholder tokens. Run:
   `python scripts/generate_doc.py <template> --tokens`
   This returns the distinct <...> tokens (e.g. <System Name>, <CI###########>) found in the template's running headers and footers. Resolve each token to a value in this order:
   a. Exact match: the token's bracket contents match a field name under project_metadata_fields in workbench.config.yaml, or the same field's value already recorded in MASTER_CONTEXT.md.
   b. Loose match: a case-insensitive match against a project_metadata_fields field name, ignoring "/" and spaces — so <System/Platform Name>, <System>, and <Platform Name> all resolve from the same "System Name" field as <System Name> does.
   c. Version-shaped token: if the token looks like a version placeholder (for example <x.x> or <X.X>), use naming.default_version from workbench.config.yaml.
   d. Year token: if the token is <YYYY>, use the current year.
   e. Otherwise, use the configured placeholder marker as that token's value rather than guessing.

5. Check for a style guide. Look for reference-docs/style-notes/<template-stem>.md, where <template-stem> is the template's filename without extension. If it exists, read it — you will follow its tone, section-shape, and citation-density guidance in the next step.

6. For each section, read its instruction text and understand what content that section asks for. Then compose the content that satisfies it:
   - Draw the facts from MASTER_CONTEXT.md and the project files.
   - Cite the specific SOP file and section from sops/ where a rule applies. Never invent an SOP name or section number.
   - Apply the language rules from workbench.config.yaml (defaults in CLAUDE.md if the config is absent).
   - Follow the style notes from step 5, if any were found.
   - The composed content replaces the instruction text. Do not keep the original guidance in the finished section.
   - Where the project does not have the information, write the placeholder marker from the config (default: [CONFIRM: what is needed — ref: owner]) in place of the instruction, rather than guessing.

7. Build a content map as JSON: { "sections": { "<exact heading text>": "<composed content>" }, "tokens": { "<token>": "<resolved value>" } }, covering every section you can fill or mark and every token from step 4. Save it to a temporary file.

8. Produce the filled draft, preserving the template's formatting:
   `python scripts/generate_doc.py <template> --fill <content-map.json>`
   This writes the draft to deliverables/in-progress/ using the naming pattern from the config, replacing each mapped section's instruction text with your content and substituting each resolved token in the headers/footers, leaving any section or token you did not map with its original text. If any header/footer placeholder remains unresolved in the finished draft, this command prints a warning naming it — carry that warning into the final message in step 11.

9. Update DELIVERABLE_STATUS.md: add a row with status "Draft", date, and filename.

10. Run /update-context automatically.

11. Print: "Generated: deliverables/in-progress/<filename>. X sections still need a confirmed value. Review before routing." If step 8 printed a header/footer placeholder warning, include it in this message.

## Rules
The template defines the sections — never impose a section list of your own. Replace instruction text with real content or a [CONFIRM] marker; never leave raw guidance in a filled section and never invent a value. Apply the configured language rules and cite only SOPs that exist in sops/. Never resolve a header/footer token by guessing a value not found in MASTER_CONTEXT.md or workbench.config.yaml.
