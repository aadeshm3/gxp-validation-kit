---
name: learn-comments
description: Use when the user types /learn-comments <file>, says "learn from these review comments", or "remember this feedback for next time" — reads the reviewer comments on a document, distills the reusable lessons, and stores them so generate-doc and gap-check apply them to future documents of the same type.
---

# learn-comments

## Overview
Turn reviewer comments into lasting knowledge. Reads the comments on a reviewed document, keeps the ones that were accepted, rewrites each as a reusable lesson, and stores the lessons per template. /generate-doc applies them when it writes the next document from that template, and /gap-check verifies them. This is different from /review-response, which decides how to answer the comments on one document. This skill never stores project facts — only lessons about how to write the document.

## Triggers
- /learn-comments <file>
- "learn from these review comments"
- "remember this feedback for next time"

## Instructions

1. Locate the file. Look in context/dev-inputs/, then deliverables/in-progress/, then deliverables/approved/ (exact filename first, then case-insensitive substring match). If not found, tell the user to drop the reviewed file into context/dev-inputs/.

2. Read the comments.
   - For a .docx, run: `python scripts/extract_comments.py <file>`
     This returns every Word comment with its author, text, the document text it is attached to, whether it is resolved, and which comment it replies to.
   - For a .txt or .md file, read the file and extract each comment with its section reference as in /review-response.
   - If there are zero comments, stop and tell the user.
   - Treat a reply as part of its parent comment's thread. A resolved thread with a reply that says the reviewer withdrew the comment is not learned.

3. Determine which comments were accepted.
   - Look in context/decisions/ for a review response table for this document (named <date>_review_response_<docname>.md). Keep only comments with an Accept disposition.
   - If there is no review response table, tell the user to run /review-response first, or to confirm that every comment should be treated as accepted. Do not learn from unconfirmed comments.

4. Determine which template the document corresponds to. Match by filename similarity against the templates/ file stems. Always show the best guess and ask the user to confirm or correct it before continuing. If the comment is about the whole document type rather than one template, ask whether it goes in the general lessons file instead.

5. Distill each kept comment into a lesson. A lesson states what to do or avoid in a future document, in one sentence, with the section it applies to.
   - Keep: wording rules, structure and section expectations, missing-content patterns, citation expectations, preferred level of detail, terminology the reviewers required.
   - Drop: anything that only concerns this system (names, dates, decisions, values, one-off typos). Never copy a project fact into a lesson.
   - Merge comments that teach the same thing into one lesson and list every source comment.

6. Check for duplicates. Read the existing lessons file for this template. If a lesson already exists with the same meaning, do not add it again: add the new source to the existing lesson and increase its Seen count.

7. Save the lessons to reference-docs/review-lessons/<template-stem>.md (or reference-docs/review-lessons/_general.md for lessons that apply to every document). Create the file if it does not exist. Each lesson uses this format:

   ```
   ## L-<number>: <one-sentence lesson>
   - Applies to: <section heading, or "All sections">
   - Category: Editorial | Technical | Compliance
   - Seen: <count>
   - Sources: <document filename> comment <id>; ...
   - Learned: <date>
   ```

   Number lessons in order within the file and never renumber an existing lesson.

8. Print a summary: "Learned X new lessons, reinforced Y existing lessons, skipped Z comments (project-specific or not accepted). Saved to reference-docs/review-lessons/<template-stem>.md." Then list the new lessons.

9. Run /update-context automatically.

## Rules
Store lessons, not facts: never copy system names, dates, decisions, or values from the reviewed document. Never store reviewer names. Never learn from a comment that was rejected, deferred, or not yet dispositioned. Never guess which template a document matches without user confirmation. A Compliance lesson that cites an SOP must cite only a file and section actually present in sops/.
