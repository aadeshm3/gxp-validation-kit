---
name: diff-doc
description: Use when the user types /diff-doc <fileA> <fileB>, says "compare versions of <doc>", "what changed between <v1> and <v2>", or "show differences" — compares two deliverable versions and outputs a section-by-section change table.
---

# diff-doc

## Overview
Compare two versions of a deliverable and report what changed at the section level. Accepts two filenames or one filename plus the keyword "approved" as shorthand for the latest approved version of that document.

## Triggers
- /diff-doc <fileA> <fileB>
- /diff-doc <doc> approved
- "compare versions of <doc>"
- "what changed between <v1> and <v2>"
- "show differences"

## Instructions

1. Resolve file paths:
   - If two filenames are given, search deliverables/ for each (fuzzy match).
   - If the second argument is "approved", locate the latest version of that document name in deliverables/approved/.
   - If a file cannot be found, report which path failed and stop.

2. Read both files fully.

3. Split each file into sections by heading (lines starting with # or ##). Build a section map keyed by heading text for each file.

4. Compare section maps:
   - Added: heading present in fileB only.
   - Removed: heading present in fileA only.
   - Modified: heading present in both but content differs.
   - Unchanged: heading present in both with identical content.

5. Output a markdown table with the following columns: Section | Status | Change Summary. For every Modified section, add a "Before / After" block immediately below its table row quoting the changed text (truncate at 300 characters per side with "...").

6. After the table, list every section where a [CONFIRM] placeholder was resolved (present in fileA, absent in fileB) or introduced (absent in fileA, present in fileB). Label each as "Placeholder resolved" or "Placeholder introduced".

7. End with: "Summary: X sections modified, Y added, Z removed, W unchanged."

## Rules
Neither file shall be modified. Heading comparison shall be case-insensitive. A section with only whitespace changes shall be reported as Unchanged. [CONFIRM] placeholder changes shall always be called out explicitly, regardless of whether the surrounding content changed.
