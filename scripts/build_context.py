"""
build_context.py — Build MASTER_CONTEXT.md from all files in context/.

PURPOSE
-------
Programmatic backend for the /build-context skill. Walks every file under
context/ (recursively), extracts validation-relevant information from each,
and assembles a fully structured MASTER_CONTEXT.md at the repository root.

This script does the heavy file-reading and parsing so the skill can focus on
synthesis. The skill may call this script, or perform the work inline; this
file is the canonical reference for the intended behaviour.

INPUTS
------
- context/ subtree:
    context/project-docs/   charters, BRDs, architecture docs
    context/meeting-notes/  raw meeting notes
    context/decisions/      structured decision extracts
    context/dev-inputs/     dev team confirmations, requirement drafts
- Supported file types:
    .docx   parsed with python-docx
    .pdf    parsed with pypdf
    .txt    read directly
    .md     read directly
    .xlsx   parsed with openpyxl (tables of stakeholders, requirements)
- .gitkeep files are ignored.

EXTRACTION
----------
From each file, attempt to identify:
    system name, project background, stakeholders and roles,
    architecture decisions, open items, timeline/milestones,
    risk category, compliance framework, pending dev-team confirmations,
    approved decisions.

OUTPUTS
-------
- MASTER_CONTEXT.md (repo root) with sections:
    Header (system name, last refreshed date, risk category, go-live date)
    1. Project Overview
    2. Stakeholders / RACI
    3. Architecture & Tech Stack
    4. Validation Deliverables Status
    5. Requirements Status
    6. Open Items & Pending Confirmations
    7. Key Decisions Made
    8. Timeline
    9. Key Files & Scripts
    10. Pending Work
- A processing report: count of files read, files skipped, parse warnings.

DEPENDENCIES
------------
python-docx, pypdf, openpyxl  (see requirements.txt)

INTEGRATION
-----------
Called by the build-context skill. The skill announces the run, invokes this
script (or replicates its logic), then prompts the user to review and correct
any misread values. update_context.py performs the incremental counterpart.

STATUS
------
Stub. Logic to be implemented.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_DIR = REPO_ROOT / "context"
OUTPUT_FILE = REPO_ROOT / "MASTER_CONTEXT.md"


def main():
    raise NotImplementedError(
        "build_context.py is a stub. Implement context extraction and "
        "MASTER_CONTEXT.md generation per the module docstring."
    )


if __name__ == "__main__":
    main()
