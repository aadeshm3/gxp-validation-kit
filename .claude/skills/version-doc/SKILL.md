---
name: version-doc
description: Use when the user types /version-doc <doc>, says "create new version of <doc>", "revise approved document", or "bump version" — creates a new draft from an approved document, increments the version, and registers it in DELIVERABLE_STATUS.md.
---

# version-doc

## Overview
Create a new draft from an approved document after a change control. The approved version is never touched. The new draft carries forward all approved content with [CONFIRM] placeholders inserted at sections affected by the change.

## Triggers
- /version-doc <doc>
- "create new version of <doc>"
- "revise approved document"
- "bump version"

## Instructions

1. Locate the source document in deliverables/approved/. If the user did not name it, list files in that folder and ask which one to version.

2. Read workbench.config.yaml for the naming convention (naming_convention key). If absent, derive the pattern from the existing filename.

3. Determine the current version number from the filename. Increment the major version by 1 (for example v1.0 becomes v2.0). Construct the new filename using the same pattern with the incremented version.

4. Ask the user: "Which sections are affected by this change?" Accept a plain-language list.

5. Copy the full approved content into the new file at deliverables/in-progress/<new_filename>.

6. For each affected section named by the user, insert the following placeholder immediately after the section heading: `[CONFIRM: describe what changed — ref: owner]`

7. Add a row to DELIVERABLE_STATUS.md with the following columns: Document | Version | Status | Notes — set Status to "Draft (v2.0)" and Notes to "Revised from approved v1.0".

8. Run /update-context.

9. Print: "Created <new_filename> in deliverables/in-progress/. X sections flagged for confirmation. Approved version unchanged."

## Rules
The approved version shall not be modified, overwritten, or deleted. Version numbers shall follow the pattern in workbench.config.yaml. Every affected section shall receive exactly one [CONFIRM] placeholder. A section with no confirmed change description shall use the text "describe what changed" verbatim until resolved.
