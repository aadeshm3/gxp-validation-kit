---
name: sop-check
description: Use when the user types /sop-check, says "check my SOPs", "are my SOPs current", or "SOP status" — reads every file in sops/, checks for version, effective date, and owner metadata, and flags stale or incomplete SOPs.
---

# sop-check

## Overview
Audit the SOPs in sops/ for required metadata and staleness. No SOP file is modified. Output is a status table with a count summary.

## Triggers
- /sop-check
- "check my SOPs"
- "are my SOPs current"
- "SOP status"

## Instructions

1. List all files in sops/. If the folder is empty, print: "sops/ contains no files. Add your SOPs to sops/ to enable cited responses and SOP-based gap checks." Stop.

2. For each file, read the first 60 lines. Attempt to extract the following three fields using pattern matching against common label formats (Version:, Effective Date:, Document Owner:, Author:, Approved By:):
   - Version number
   - Effective date
   - Document owner

3. Evaluate each file against the following criteria:
   - INCOMPLETE: one or more of the three fields is absent or unreadable.
   - POTENTIALLY STALE: effective date is present and is more than 2 years before 2026-06-12 (that is, before 2024-06-12).
   - CURRENT: all three fields present and effective date is 2024-06-12 or later.

4. A file may carry more than one status flag if both conditions apply.

5. Output a markdown table with the following columns: SOP File | Version | Effective Date | Owner | Status. Use "—" for any field that could not be extracted.

6. End with: "X SOPs complete and current. Y need metadata. Z potentially stale."

## Rules
No SOP file shall be modified by this skill. Status flags shall be derived solely from the content read from the file — no assumed values shall be substituted. A file with an unreadable or ambiguous date shall be flagged INCOMPLETE, not POTENTIALLY STALE.
