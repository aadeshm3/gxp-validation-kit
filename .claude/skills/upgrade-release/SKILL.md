---
name: upgrade-release
description: Use when the user types /upgrade-release <new-version>, or says "upgrade everything to release 2.0", "revise all approved documents for the new release" — takes every approved Word document to the new version in one pass, adding the new release content without removing or rewording anything approved, updating each revision history, and proving each approved document is intact.
---

# upgrade-release
## Overview
Move the whole validated system to a new release. The release inputs are gathered once, the user is asked once for anything missing, and then every approved document is upgraded using the per-document procedure in /upgrade-doc. To upgrade a single document use /upgrade-doc.

## Triggers
- /upgrade-release <new-version>
- "upgrade everything to release 2.0"
- "revise all approved documents for the new release"

## Instructions

1. List the .docx files in deliverables/approved/. Tell the user any file that is not a .docx and will be skipped. If no new version was given, ask for it. Show the list and ask whether every document should be upgraded or only some; documents the user excludes are left out of every later step.

2. Make the project context current: follow /upgrade-doc step 2. MASTER_CONTEXT.md is built from every approved document and the files in context/, so it covers the whole release in one step.

3. Gather the release inputs once: follow /upgrade-doc step 3, but for the whole release. Show the files read, the release changes derived with their source files, and what is not established (change reference number, who is revising, any affected document the sources do not describe). Then ask: "Is there anything else I need for release <new-version>? You can add files to context/ or tell me details that are not in the files." Do not continue until the user says there is nothing more.

4. Show a release plan table: Document | Expected to change? | Reason. A document that no release change touches is still opened as a new version when the user asks for it, with only its revision history updated. Wait for the user to approve the plan.

5. For each document in the plan, run /upgrade-doc steps 4 through 11 with the release inputs from step 3. Do not repeat /upgrade-doc steps 1 through 3, and do not ask the user to approve each table separately unless a document raises a Conflict; show the decision tables together after all drafts are prepared and wait for approval before step 7 of /upgrade-doc writes anything.

6. Check consistency across the whole set once all drafts exist. A fact added to one document that another document in the set also states shall be added to that document, or listed for the user. Report any document whose verification failed and exclude it from the summary of finished drafts.

7. Print a table: Document | Draft | Sections added | Conflicts | Placeholders | Approved content check. Then list all conflict files written to context/decisions/. Remind the user that new text is highlighted, that highlighting is cleared before routing, and that /gap-check should be run on each draft next. Run /update-context automatically.

## Rules
All rules of /upgrade-doc apply to every document: approved content shall never be removed, reworded, reordered, or overwritten; a draft whose verification failed is never registered or offered; nothing is invented; conflicts are reported and never resolved silently. Never skip the question in step 3.
