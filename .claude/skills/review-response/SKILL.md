---
name: review-response
description: Use when the user types /review-response or says process review comments — reads reviewer comments on a deliverable and generates a structured review response table with dispositions.
---

# review-response

## Overview
Read reviewer comments on a deliverable and generate a structured review response table with a category and disposition for each comment.

## Triggers
- /review-response <filename>
- "process review comments"
- "I got reviewer comments"

## Instructions

1. Find the review comment file in context/dev-inputs/ (fuzzy match, or ask the user). Accept .txt, .md, or .docx.

2. Read the full file.

3. Extract each comment: reviewer name (if present), document section reference, and comment text.

4. For each comment, assign a category from the following:
   - Editorial: grammar, formatting, typo
   - Technical: factual content, architecture, process
   - Compliance: GxP rule, SOP requirement, ALCOA+
   - Out-of-scope: outside the validation boundary

5. Propose a disposition from the following:
   - Accept: state the change to make
   - Reject: state the rationale
   - Defer: state when and to what

6. Output a review response table with columns: Comment# | Reviewer | Section | Comment | Category | Disposition | Proposed action

7. Save the table to context/decisions/<date>_review_response_<docname>.md

8. List all Accept dispositions as a separate action list: what to change, in which deliverable, at which section.

## GxP rules
Compliance-category comments cannot be Rejected without citing the specific SOP clause that contradicts the comment. Every Accept disposition must state exactly what change will be made.
