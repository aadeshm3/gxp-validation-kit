"""
check_status.py — Report status of all validation deliverables and open items.

PURPOSE
-------
Programmatic backend for the /check-status skill. Reconciles the project state
recorded in MASTER_CONTEXT.md and DELIVERABLE_STATUS.md against the actual
files on disk, and reports deliverable status, open items, pending
confirmations, and unprocessed context files.

INPUTS
------
- MASTER_CONTEXT.md (repo root):
    section 4 (Deliverable Status), section 6 (Open Items & Pending
    Confirmations), and the Last Refreshed date in the header.
- DELIVERABLE_STATUS.md (repo root).
- deliverables/in-progress/ and deliverables/approved/: actual files.
- context/ subtree: files newer than Last Refreshed are "unprocessed".

CHECKS
------
- Cross-reference MASTER_CONTEXT and DELIVERABLE_STATUS against files on disk;
  flag any discrepancy (recorded but missing, or present but unrecorded).
- Count placeholders [CONFIRM: ...] remaining in each in-progress deliverable.
- Identify context/ files modified after the Last Refreshed date.

OUTPUTS
-------
- DELIVERABLES table: Document | Status | Location | Placeholders | Next action
- OPEN ITEMS table: ID | Description | Owner | Status
- PENDING CONFIRMATIONS table: ID | Description | Owner | Blocking which doc
- UNPROCESSED FILES IN CONTEXT/: list
- A single recommended next action.

DEPENDENCIES
------------
python-docx  (to count placeholders inside .docx drafts; see requirements.txt)

INTEGRATION
-----------
Called by the check-status skill. Read-only — never modifies project state.

STATUS
------
Stub. Logic to be implemented.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_DIR = REPO_ROOT / "context"
IN_PROGRESS_DIR = REPO_ROOT / "deliverables" / "in-progress"
APPROVED_DIR = REPO_ROOT / "deliverables" / "approved"
CONTEXT_FILE = REPO_ROOT / "MASTER_CONTEXT.md"
STATUS_FILE = REPO_ROOT / "DELIVERABLE_STATUS.md"


def main():
    raise NotImplementedError(
        "check_status.py is a stub. Implement the status reconciliation and "
        "report per the module docstring."
    )


if __name__ == "__main__":
    main()
