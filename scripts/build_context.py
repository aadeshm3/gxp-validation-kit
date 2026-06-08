"""
build_context.py — Build MASTER_CONTEXT.md from all files in context/.

PURPOSE
-------
Walks context/ recursively, extracts validation-relevant information from each
supported file, and writes a structured MASTER_CONTEXT.md at the repo root
using the 10-section template. Every field that cannot be identified is marked
[CONFIRM: field name — source file not found].

INPUTS
------
- context/ subtree. Supported: .txt and .md (read directly), .docx
  (python-docx), .pdf (pypdf). .gitkeep files are skipped.

OUTPUT
------
- MASTER_CONTEXT.md (repo root). If context/ has no files other than .gitkeep,
  prints drop-in instructions instead of writing the file.

DEPENDENCIES
------------
python-docx, pypdf (see requirements.txt). Import failures are caught and
reported as warnings; the affected file is skipped.

INTEGRATION
-----------
Backend for the /build-context skill. update_context.py is the incremental
counterpart. Identification here is heuristic — the skill prompts the user to
review and correct misread values.
"""

import re
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_DIR = REPO_ROOT / "context"
OUTPUT_FILE = REPO_ROOT / "MASTER_CONTEXT.md"

CONFIRM = "[CONFIRM: {} — source file not found]"


def read_txt(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print("Warning: could not read {}: {}".format(path.name, exc))
        return ""


def read_docx(path):
    try:
        from docx import Document
    except ImportError:
        print("Warning: python-docx not installed; skipping {}".format(path.name))
        return ""
    try:
        doc = Document(str(path))
    except Exception as exc:
        print("Warning: could not parse {}: {}".format(path.name, exc))
        return ""
    return "\n".join(p.text for p in doc.paragraphs)


def read_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Warning: pypdf not installed; skipping {}".format(path.name))
        return ""
    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        print("Warning: could not parse {}: {}".format(path.name, exc))
        return ""
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def gather_text():
    """Return (combined_text, processed_files) for all supported context files."""
    combined = []
    processed = []
    if not CONTEXT_DIR.is_dir():
        return "", processed
    for path in sorted(CONTEXT_DIR.rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        suffix = path.suffix.lower()
        if suffix in (".txt", ".md"):
            text = read_txt(path)
        elif suffix == ".docx":
            text = read_docx(path)
        elif suffix == ".pdf":
            text = read_pdf(path)
        else:
            continue
        if text:
            combined.append("\n# SOURCE: {}\n{}".format(path.name, text))
            processed.append(path)
    return "\n".join(combined), processed


def first_match(text, pattern, group=1):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else None


def identify(text):
    """Heuristically pull known fields out of the combined context text."""
    fields = {}
    fields["system_name"] = first_match(
        text, r"system name[:\-]\s*(.+)") or first_match(
        text, r"\bproject[:\-]\s*(.+)")
    fields["risk_category"] = first_match(
        text, r"risk category[:\-]\s*([A-Za-z0-9#\- ]+)")
    fields["go_live"] = first_match(
        text, r"go[- ]?live(?:\s*date)?[:\-]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})") or first_match(
        text, r"go[- ]?live(?:\s*date)?[:\-]\s*(.+)")
    return fields


def build_document(fields, processed):
    sn = fields.get("system_name") or CONFIRM.format("system name")
    rc = fields.get("risk_category") or CONFIRM.format("risk category")
    gl = fields.get("go_live") or CONFIRM.format("go-live date")
    today = date.today().isoformat()

    lines = []
    lines.append("# MASTER_CONTEXT — {}".format(sn))
    lines.append("")
    lines.append("**System Name:** {}".format(sn))
    lines.append("**Last Refreshed:** {}".format(today))
    lines.append("**Risk Category:** {}".format(rc))
    lines.append("**Go-Live Date:** {}".format(gl))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Project Overview")
    lines.append(CONFIRM.format("project overview — review source files and complete one paragraph"))
    lines.append("")
    lines.append("## 2. Stakeholders / RACI")
    lines.append("| Name | Role | Organization | R/A/C/I |")
    lines.append("|------|------|--------------|---------|")
    lines.append("| {} | | | |".format(CONFIRM.format("stakeholders")))
    lines.append("")
    lines.append("## 3. Architecture & Tech Stack")
    lines.append(CONFIRM.format("architecture and tech stack"))
    lines.append("")
    lines.append("## 4. Validation Deliverables Status")
    lines.append("| Document | Status | Due | Notes |")
    lines.append("|----------|--------|-----|-------|")
    lines.append("| {} | | | |".format(CONFIRM.format("deliverables")))
    lines.append("")
    lines.append("## 5. Requirements Status")
    lines.append(CONFIRM.format("requirements status"))
    lines.append("")
    lines.append("## 6. Open Items & Pending Confirmations")
    lines.append("| ID | Description | Owner | Status |")
    lines.append("|----|-------------|-------|--------|")
    lines.append("| | {} | | |".format(CONFIRM.format("open items")))
    lines.append("")
    lines.append("## 7. Key Decisions Made")
    lines.append("| Date | Decision | Rationale | Owner |")
    lines.append("|------|----------|-----------|-------|")
    lines.append("| | {} | | |".format(CONFIRM.format("key decisions")))
    lines.append("")
    lines.append("## 8. Timeline")
    lines.append("| Milestone | Date | Status |")
    lines.append("|-----------|------|--------|")
    lines.append("| {} | | |".format(CONFIRM.format("timeline milestones")))
    lines.append("")
    lines.append("## 9. Key Files & Scripts")
    if processed:
        for path in processed:
            lines.append("- {}".format(path.relative_to(REPO_ROOT).as_posix()))
    else:
        lines.append(CONFIRM.format("key files"))
    lines.append("")
    lines.append("## 10. Pending Work")
    lines.append("- [ ] {}".format(CONFIRM.format("pending work")))
    lines.append("")
    return "\n".join(lines)


def main():
    combined, processed = gather_text()
    if not processed:
        print("context/ has no source files to process.")
        print("Drop project material into the relevant subfolder, then re-run:")
        print("  - charters, BRDs, architecture docs -> context/project-docs/")
        print("  - meeting notes                      -> context/meeting-notes/")
        print("  - dev team confirmations             -> context/dev-inputs/")
        print("  - decision records                   -> context/decisions/")
        return

    fields = identify(combined)
    document = build_document(fields, processed)
    OUTPUT_FILE.write_text(document, encoding="utf-8")
    print("MASTER_CONTEXT.md built. {} files processed. Review and correct any misread values.".format(len(processed)))


if __name__ == "__main__":
    main()
