"""
generate_doc.py — Generate a validation deliverable from template + context.

PURPOSE
-------
Programmatic backend for the /generate-doc skill. Produces a validation
deliverable by combining a Word template, the current MASTER_CONTEXT.md
data, and relevant SOP guidance, then writes a draft to
deliverables/in-progress/.

INPUTS
------
- template (str): a template filename in templates/, or an alias defined under
  deliverables in workbench.config.yaml. There is no fixed list of document
  types — the available deliverables are whatever templates the user provides.
- MASTER_CONTEXT.md (repo root): source of project data.
- templates/: the chosen template, used as the base structure.
- sops/: SOPs for citation, if present.
- workbench.config.yaml: template aliases, naming pattern, placeholder marker,
  and language rules.

SOP CITATION
------------
There is no built-in document-type to SOP mapping. The script checks sops/ for
procedures relevant to the chosen deliverable and cites the specific file and
section it finds. If none is present, it inserts a placeholder naming the SOP
to add. It never invents an SOP or a section number.

BEHAVIOUR
---------
- If MASTER_CONTEXT.md is empty/missing: abort and instruct user to run
  build_context first.
- Resolve the template from the argument (alias in config, or filename in
  templates/). If no template exists: generate from a generic document
  structure and warn, naming the template to add.
- Insert placeholders for missing/unconfirmed data using the marker from
  workbench.config.yaml (default: [CONFIRM: description — ref: owner]).

OUTPUTS
-------
- A draft in deliverables/in-progress/, named per the naming pattern in
  workbench.config.yaml (.docx when the template is Word, otherwise .md).
- A new/updated row in DELIVERABLE_STATUS.md (status "Draft", date, filename).
- Count of placeholders requiring input.

DEPENDENCIES
------------
python-docx, openpyxl, PyYAML  (see requirements.txt)

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
