---
name: gap-check
description: Use when the user types /gap-check <doc>, says "check gaps in <doc>", or asks "is <doc> ready for review" — checks a deliverable against its template, the SOPs in sops/, and the configured language rules, then produces a gap report.
---

# gap-check

## Overview
Check a deliverable for completeness and quality before routing for review. Required structure comes from the document's own template and the user's SOPs — not from any built-in list.

## Triggers
- /gap-check <doc>
- "check gaps in <doc>"
- "is <doc> ready for review"

## Instructions

1. Find the document in deliverables/ (fuzzy match).

2. Read the document fully.

3. Determine the expected structure for this document, in this order:
   - The template it was generated from in templates/ (match by name or alias in workbench.config.yaml). Use the template's section headings as the required-section list.
   - If no template is found, check sops/ for a procedure that defines the structure for this document, and use that.
   - If neither exists, note that no template or SOP defines the structure, list the sections the document does contain, and ask the user to add a template to templates/ for a complete check.

4. Check for a prior version. Look in context/prior-versions/ for a file matching this document's type (fuzzy match on filename or template stem). If one exists, run:
   `python scripts/generate_doc.py <this-document> --compare-structure context/prior-versions/<matched-file>`
   This returns missing/added headings, table row/column count deltas, font/color-set differences, and whether a table of contents was lost. Fold each finding into the gap report at this severity:
   - CRITICAL — a heading present in the prior version is missing now, or a table of contents was lost
   - MAJOR — a table has fewer rows than the prior version (possible lost data)
   - MINOR — the set of fonts or colors used differs from the prior version
   If no prior version is found for this document type, skip this step.

5. Compare the document against the expected structure. For each missing or incomplete section, flag it:
   - CRITICAL — a required section from the template or SOP is missing
   - MAJOR — section present but incomplete
   - MINOR — wording issue or missing citation

6. Check all content against the language rules in workbench.config.yaml (weak terms, vague terms, open lists, hedges). If the config is absent, use the defaults in CLAUDE.md. Flag each violation with its location.

7. Count remaining placeholders using the marker from the config (default [CONFIRM: ...]) and list each one with its owner.

8. Verify SOP citations point to files actually present in sops/. Flag any citation that cannot be traced to a file.

9. Output the gap report as markdown: | Section | Status | Issue | Severity | Recommendation |

10. End with: "Recommendation: [Ready for review / Not ready — X critical gaps must be resolved first]"

## Rules
A document is not ready for review while any CRITICAL gap or unresolved placeholder remains. A structural regression against a prior version (missing heading, lost table of contents, or reduced table row count) is a CRITICAL or MAJOR finding regardless of how the content reads on a surface pass — never skip step 4 when a prior version is available. Treat any language-rule violation, untraceable citation, or open list as a finding. Do not assume a document type or a required section list — derive both from the template and the SOPs.
