---
name: learn-style
description: Use when the user types /learn-style <file>, says "learn style from <file>", or drops an approved document or a prior version into reference-docs/ or context/prior-versions/ — extracts writing and formatting style from it and stores a durable style-notes file for its matching template.
---

# learn-style

## Overview
Learn writing and formatting conventions from an already-approved document — either a reference document from another project (reference-docs/) or the system's own prior version (context/prior-versions/) — and store the lesson so generate-doc applies it automatically the next time that template is used. This never reads facts from the source document into project context; it studies style only.

## Triggers
- /learn-style <file>
- "learn style from <file>"

## Instructions

1. Locate the file. Look first in reference-docs/, then in context/prior-versions/ (fuzzy match on filename: exact name match first, then case-insensitive substring match). If not found in either, tell the user which folder to drop it into.

2. Determine which template in templates/ this document corresponds to:
   - Try matching by filename similarity against templates/ file stems.
   - Always show the user your best guess and ask them to confirm or correct it before proceeding. Never silently guess — an incorrect match would apply the wrong style to future documents.

3. Read the document's structure and content:
   `python scripts/generate_doc.py <file> --outline`
   For an already-filled document, the returned instruction text under each heading is the real content — read it as such, not as template guidance.

4. From that content, write a style-notes summary covering:
   - Tone (formal/informal, sentence length, voice)
   - How Scope and Out of Scope sections are phrased
   - Whether each section favors tables or prose, and roughly how much of each
   - Citation density and format (how often SOPs/other documents are cited, and the citation phrasing used)
   - How sections that don't apply are handled (omitted, marked "Not applicable", explained)

5. Save the summary to reference-docs/style-notes/<template-stem>.md, where <template-stem> is the matching template's filename without extension. If a style-notes file already exists for this template, overwrite it and note in the output that it replaced a prior version.

6. Print: "Style notes saved: reference-docs/style-notes/<template-stem>.md. generate-doc will use this the next time <template-stem> is generated."

## Rules
Never copy factual content (system names, dates, decisions) from the source document into MASTER_CONTEXT.md or any generated deliverable — this skill extracts style only. Never guess which template a source document matches without user confirmation.
