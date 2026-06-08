"""
generate_doc.py — Generate a validation deliverable from template + context.

PURPOSE
-------
Programmatic backend for the /generate-doc skill. Produces a validation
deliverable by combining a Lilly Word template, the current MASTER_CONTEXT.md
data, and relevant SOP guidance, then writes a draft to
deliverables/in-progress/.

INPUTS
------
- doc_type (str): one of
    vtp            Validation and Test Plan
    ds             Design Specification
    so             System Overview
    security-plan  Security Plan
    sop            SOP (variant supplied separately)
    test-cases     Test case shells from approved requirements
    rtm            Requirements Traceability Matrix
- MASTER_CONTEXT.md (repo root): source of system data.
- templates/: matching Lilly Word template, if present.
- sops/: relevant SOPs for citation, if present.

DOC_TYPE -> SOP MAP
-------------------
    vtp            LQP-302-25, LQP-302-26
    ds             LQP-302-26
    so             LQP-302-26
    security-plan  LQP-302-29
    sop            LQP-302-27

BEHAVIOUR
---------
- If MASTER_CONTEXT.md is empty/missing: abort and instruct user to run
  build_context first.
- If a matching template exists in templates/: use it as the base document.
- If no template exists: generate from the Lilly standard structure and warn.
- Insert yellow-highlighted placeholders for missing/unconfirmed data in the
  format: [CONFIRM: description — ref: <owner>].

OUTPUTS
-------
- deliverables/in-progress/<SystemName>_<DocType>_v1.0_draft.docx
  (or .md when no template is available).
- A new/updated row in DELIVERABLE_STATUS.md (status "Draft", date, filename).
- Count of placeholders requiring dev-team input.

DEPENDENCIES
------------
python-docx, openpyxl  (see requirements.txt)

INTEGRATION
-----------
Called by the generate-doc skill. After generation the skill triggers
update-context automatically and reports placeholder counts.

STATUS
------
Stub. Logic to be implemented.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
SOPS_DIR = REPO_ROOT / "sops"
OUTPUT_DIR = REPO_ROOT / "deliverables" / "in-progress"
CONTEXT_FILE = REPO_ROOT / "MASTER_CONTEXT.md"
STATUS_FILE = REPO_ROOT / "DELIVERABLE_STATUS.md"


def main():
    raise NotImplementedError(
        "generate_doc.py is a stub. Implement template + context + SOP "
        "document generation per the module docstring."
    )


if __name__ == "__main__":
    main()
