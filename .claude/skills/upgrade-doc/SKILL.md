---
name: upgrade-doc
description: Use when the user types /upgrade-doc <doc> <new-version>, or says "upgrade <doc> to release 2.0", "revise this approved document for the new release" — opens ONE approved Word document as a new version, adds the new release content without removing or rewording anything approved, updates the revision history, and proves the approved content is unchanged. For every approved document at once use /upgrade-release.
---

# upgrade-doc

## Overview
Move one approved document to a new release. The approved document is opened as a new draft. New content is only added; approved text is never removed or reworded. Project knowledge comes from MASTER_CONTEXT.md, which is built from the approved documents and the files in context/. The revision history table is updated, and a verification step proves that every approved paragraph and table cell is still there, unchanged and in order.

Related skills: /upgrade-release does this for every approved document in one pass. /version-doc only copies and flags sections. /generate-doc is for first-time documents and replaces template instruction text, so it is never used on an approved document.

## Triggers
- /upgrade-doc <doc> <new-version>
- "upgrade <doc> to release 2.0"

## Instructions

1. Resolve the document. List the .docx files in deliverables/approved/ and match the user's name (exact first, then case-insensitive substring). If no document was named, list them and ask. If the user typed "all", tell them to use /upgrade-release. If the file is not a .docx, tell the user this skill cannot upgrade it. If no new version was given, ask for it.

2. Make the project context current. Read MASTER_CONTEXT.md. If it is empty or missing, run /build-context. If any file in deliverables/approved/ or context/ is newer than the Last Refreshed date, run /update-context. Approved documents are the core baseline of project knowledge; their facts stay tagged with document and version.

3. Gather the release inputs from context/. Read the files that describe the new release: change control assessments and review responses in context/decisions/, release notes and design inputs in context/dev-inputs/ and context/project-docs/, meeting notes in context/meeting-notes/. Then show the user:
   - The files read, grouped by folder, each with one line on what it says about this release.
   - The changes you derived for this document, each with its source file. Never infer a change that no source states.
   - What is not established: the change reference number (CHG, RITM, or similar), who is revising, and any section of this document that the release affects but the sources do not describe.
   Then ask: "Is there anything else I need for release <new-version> of <doc>? You can add files to context/ or tell me details that are not in the files." Wait for the answer. If the user adds files, read them and show what they changed. Do not continue until the user says there is nothing more.

4. Create the draft:
   `python scripts/revise_doc.py init deliverables/approved/<file>.docx --version <new-version>`
   Report any version label the script says it could not update, and any body mention of the old version it left unchanged. Never edit those mentions yourself unless the user says so.

5. Get the draft's content: `python scripts/generate_doc.py <draft> --outline`. Check for style notes and review lessons exactly as /generate-doc step 5 does (reference-docs/style-notes/ and reference-docs/review-lessons/) and apply them to new content.

6. Decide, section by section, one of the following. Show the user the decisions as a table (Section | Decision | Reason) and wait for approval before writing anything:
   - Leave untouched: the release does not affect this section. This is the default.
   - Add: the release adds something this section must now cover.
   - Conflict: an approved statement is no longer true in the new release.

7. For every Add section, compose only the new text:
   - New content shall be written as additional paragraphs. Never restate, summarize, or reword the approved text.
   - Draw facts only from MASTER_CONTEXT.md and the files read in step 3. Where the release affects a section but the fact is missing, write the configured placeholder marker (default [CONFIRM: what is needed — ref: owner]).
   - Apply the language rules from workbench.config.yaml and cite only SOP files and sections that exist in sops/.
   - Save an additions file as JSON: { "<exact heading text>": ["paragraph", ...] }, then run:
     `python scripts/revise_doc.py add <draft> <additions.json> --highlight`
     New paragraphs are highlighted so reviewers can find them. If the script reports headings it could not find, correct the heading text and rerun for those headings only. Never create a section that is not in the approved document; list it for the user instead.

8. Handle every Conflict section without touching the approved text. Write each one to context/decisions/<date>_upgrade_<docname>_modifications.md with: section, the approved statement quoted exactly, why release <new-version> contradicts it, and the proposed replacement wording. Tell the user these need an explicit decision. If the user decides to modify approved text, the change is made by hand in Word and recorded in the revision history; this skill never makes it silently.

9. Update the revision history:
   `python scripts/revise_doc.py revlog <draft> --version <new-version> --date <today> --summary "<one sentence stating what this version adds>" --by "<reviser>" --ref "<change reference>"`
   Use the configured placeholder marker for the reviser and the change reference when the user has not supplied them. If the script reports no revision history table, tell the user and put the same entry in the final message so it can be added by hand.

10. Verify. Run:
    `python scripts/revise_doc.py verify deliverables/approved/<file>.docx <draft>`
    The verification shall pass before the draft is offered to the user. If it reports violations, show each one, find the cause, and correct the draft. If the cause cannot be found, tell the user the draft is not safe to use and do not register it.

11. Add a row to DELIVERABLE_STATUS.md: Document | Version | Status | Notes, with Status "Draft (<new-version>)" and Notes "Revised from approved <old-version>; additive". Run /update-context automatically.

12. Print: "Created <draft>. Sections added to: X. Conflicts needing a decision: Y. Placeholders to resolve: Z. Approved content check: PASSED." Remind the user that new text is highlighted and the highlighting should be cleared before the document is routed for approval, and that /gap-check should be run next.

## Rules
Approved content shall never be removed, reworded, reordered, or overwritten, and the file in deliverables/approved/ shall never be modified. Never register or offer a draft whose verification failed. Never invent a release change, a fact, a change reference, a reviser, or an SOP section. Content from an approved document is tagged with its version and never presented as new-release fact. A conflict is reported, never resolved silently. Never skip the question in step 3.
