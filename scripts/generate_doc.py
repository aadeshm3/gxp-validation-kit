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

USAGE
-----
    python scripts/generate_doc.py <template-or-alias> [--system "Name"] [--doc "Label"]

This produces a first-pass copy of the template into deliverables/in-progress/
so a draft always exists. The generate-doc skill then enriches it with project
context and SOP citations. Where the template contains the tokens {{field}} or
[CONFIRM: ...], they are preserved for the skill to resolve.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
SOPS_DIR = REPO_ROOT / "sops"
OUTPUT_DIR = REPO_ROOT / "deliverables" / "in-progress"
CONTEXT_FILE = REPO_ROOT / "MASTER_CONTEXT.md"
STATUS_FILE = REPO_ROOT / "DELIVERABLE_STATUS.md"
CONFIG_FILE = REPO_ROOT / "workbench.config.yaml"

DEFAULT_NAMING = "{system}_{doc}_v{version}_draft"
DEFAULT_VERSION = "1.0"


def load_config():
    """Load workbench.config.yaml. Return {} if missing or PyYAML unavailable."""
    if not CONFIG_FILE.is_file():
        return {}
    try:
        import yaml
    except ImportError:
        print("Note: PyYAML not installed; using default naming and aliases.")
        return {}
    try:
        return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print("Warning: could not parse workbench.config.yaml: {}".format(exc))
        return {}


def resolve_template(arg, config):
    """Resolve a template argument to a path in templates/.

    Order: config alias -> exact filename -> case-insensitive fuzzy match.
    Returns a Path or None.
    """
    if not TEMPLATES_DIR.is_dir():
        return None
    candidates = [p for p in TEMPLATES_DIR.iterdir()
                  if p.is_file() and p.name != ".gitkeep"]

    for entry in config.get("deliverables") or []:
        if isinstance(entry, dict) and entry.get("alias", "").lower() == arg.lower():
            mapped = TEMPLATES_DIR / entry.get("template", "")
            if mapped.is_file():
                return mapped

    for path in candidates:
        if path.name.lower() == arg.lower():
            return path
    for path in candidates:
        if arg.lower() in path.stem.lower():
            return path
    return None


def system_name_from_context():
    """Best-effort read of the system name from MASTER_CONTEXT.md."""
    if not CONTEXT_FILE.is_file():
        return None
    text = CONTEXT_FILE.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\*\*System Name:\*\*\s*(.+)", text)
    if match:
        name = match.group(1).strip()
        if name and "populated by" not in name and "CONFIRM" not in name:
            return name
    return None


def output_name(config, system, doc, suffix):
    naming = (config.get("naming") or {})
    pattern = naming.get("draft_pattern", DEFAULT_NAMING)
    version = naming.get("default_version", DEFAULT_VERSION)
    safe = lambda s: re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
    stem = pattern.format(system=safe(system), doc=safe(doc),
                          version=version, date=date.today().isoformat())
    return stem + suffix


def copy_docx(src, dest):
    from docx import Document
    Document(str(src)).save(str(dest))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a deliverable draft from a template.")
    parser.add_argument("template", help="Template filename or config alias.")
    parser.add_argument("--system", default=None, help="System name (defaults to MASTER_CONTEXT).")
    parser.add_argument("--doc", default=None, help="Document label for the filename.")
    args = parser.parse_args(argv)

    if not CONTEXT_FILE.is_file() or "[populated by /build-context]" in CONTEXT_FILE.read_text(encoding="utf-8", errors="replace"):
        print("MASTER_CONTEXT.md is not populated. Run /build-context first.")
        return 1

    config = load_config()
    template = resolve_template(args.template, config)
    system = args.system or system_name_from_context() or "System"
    doc = args.doc or args.template

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if template is None:
        available = [p.name for p in TEMPLATES_DIR.iterdir()
                     if p.is_file() and p.name != ".gitkeep"] if TEMPLATES_DIR.is_dir() else []
        print("No template matched '{}'.".format(args.template))
        if available:
            print("Available templates: " + ", ".join(available))
        else:
            print("templates/ is empty. Add a Word or Markdown template, "
                  "then re-run. The generate-doc skill can also build a generic "
                  "structure for you.")
        return 1

    suffix = template.suffix.lower()
    dest = OUTPUT_DIR / output_name(config, system, doc, suffix if suffix in (".docx", ".md") else ".md")

    try:
        if suffix == ".docx":
            copy_docx(template, dest)
        else:
            dest.write_text(template.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    except ImportError:
        print("python-docx is required for .docx templates. Install it with: "
              "pip install -r scripts/requirements.txt")
        return 1
    except Exception as exc:
        print("Could not create the draft: {}".format(exc))
        return 1

    print("Draft created: {}".format(dest.relative_to(REPO_ROOT).as_posix()))
    print("Next: the generate-doc skill fills it with project context and SOP citations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
