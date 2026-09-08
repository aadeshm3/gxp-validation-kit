"""
generate_doc.py — Generate a deliverable by reading a template's sections and
their instruction text, then filling each section with project information.

HOW IT WORKS
------------
A template is the user's own document. Each section usually has a heading plus
some instruction or guidance text describing what belongs there (for example,
under "System Overview": "Describe the system, its purpose, and where it runs.").
This script and the generate-doc skill work together in three steps:

  1. Outline   — extract every section: its heading and its instruction text.
                 python scripts/generate_doc.py <template> --outline
  2. Compose   — the generate-doc skill reads the outline and the project
                 context (MASTER_CONTEXT.md), then writes, for each section, the
                 real content that satisfies the instruction. Where the project
                 does not have the information, it writes a [CONFIRM: ...] marker
                 instead. The skill saves this as a JSON map: {heading: content}.
  3. Fill      — replace each section's instruction text with the composed
                 content, keeping the template's headings, order, and formatting.
                 python scripts/generate_doc.py <template> --fill content.json

Running with no flag copies the template to deliverables/in-progress/ as a
starting draft and prints the outline so a draft always exists.

INPUTS
------
- template: a filename in templates/, or an alias under deliverables in
  workbench.config.yaml.
- MASTER_CONTEXT.md: project data (read by the skill, checked here).
- workbench.config.yaml: aliases, naming pattern.

DEPENDENCIES
------------
python-docx, openpyxl, PyYAML  (see requirements.txt). Markdown templates need
no extra packages; Word templates need python-docx.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

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
        return {}
    try:
        return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print("Warning: could not parse workbench.config.yaml: {}".format(exc))
        return {}


def resolve_template(arg, config):
    """Resolve a template argument to a path.

    Order: an existing file path given directly (for running --tokens,
    --structure, or --compare-structure against a deliverable or a prior
    version, not just a template) -> config alias -> exact filename in
    templates/ -> case-insensitive fuzzy match in templates/.
    """
    direct = Path(arg)
    if direct.is_file():
        return direct
    if not TEMPLATES_DIR.is_dir():
        return None
    candidates = [p for p in TEMPLATES_DIR.iterdir()
                  if p.is_file() and p.name not in (".gitkeep", "README.md")]
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


# --- Outline extraction -----------------------------------------------------

_BODY_TERMS = ("Body", "Txt", "Bullet", "Step", "List", "Table", "Caption",
               "TOC", "toc", "Footer", "Header", "Note", "example", "Example",
               "Instructions", "Instruction")


def _is_heading_style(para_style):
    """Return True if this paragraph style is a heading.

    Walks the style inheritance chain first (catches corporate aliases like
    H1-QS that inherit from Heading 1). Falls back to a naming convention
    check for top-level styles like H0-QS that derive directly from Normal.
    """
    if para_style is None:
        return False
    style = para_style
    visited = set()
    while style is not None:
        name = style.name or ""
        if name in visited:
            break
        visited.add(name)
        if name.startswith("Heading") or name == "Title":
            return True
        try:
            style = style.base_style
        except Exception:
            break
    # Fallback: H0 / H1 / H2 … naming pattern without body-text qualifiers.
    style_name = para_style.name or ""
    if re.match(r"^H\d+", style_name):
        return not any(t in style_name for t in _BODY_TERMS)
    return False


def _heading_level_from_style_obj(para_style):
    """Return the numeric heading level, walking the inheritance chain."""
    style = para_style
    visited = set()
    while style is not None:
        name = style.name or ""
        if name in visited:
            break
        visited.add(name)
        m = re.match(r"Heading\s+(\d+)", name)
        if m:
            return int(m.group(1))
        try:
            style = style.base_style
        except Exception:
            break
    m = re.search(r"(\d+)", para_style.name if para_style else "")
    return int(m.group(1)) if m else 1


def _heading_level_from_style(style_name):
    match = re.search(r"(\d+)", style_name or "")
    return int(match.group(1)) if match else 1


def extract_outline_md(text):
    sections = []
    current = None
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if current:
                current["instruction"] = current["instruction"].strip("\n")
                sections.append(current)
            current = {"level": len(m.group(1)), "heading": m.group(2).strip(), "instruction": ""}
        elif current is not None:
            current["instruction"] += line + "\n"
    if current:
        current["instruction"] = current["instruction"].strip("\n")
        sections.append(current)
    return sections


def extract_outline_docx(path):
    from docx import Document
    doc = Document(str(path))
    sections = []
    current = None
    for para in doc.paragraphs:
        if _is_heading_style(para.style) and para.text.strip():
            if current:
                current["instruction"] = current["instruction"].strip("\n")
                sections.append(current)
            current = {"level": _heading_level_from_style_obj(para.style),
                       "heading": para.text.strip(), "instruction": ""}
        elif current is not None and para.text.strip():
            current["instruction"] += para.text + "\n"
    if current:
        current["instruction"] = current["instruction"].strip("\n")
        sections.append(current)
    return sections


def extract_outline(path):
    if path.suffix.lower() == ".docx":
        return extract_outline_docx(path)
    return extract_outline_md(path.read_text(encoding="utf-8", errors="replace"))


# --- Filling ----------------------------------------------------------------

def fill_md(text, content_map):
    """Rebuild a markdown template, replacing each section's body with mapped content."""
    out = []
    current_heading = None
    buffer_emitted = False
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            out.append(line)
            current_heading = m.group(2).strip()
            if current_heading in content_map:
                out.append("")
                out.append(content_map[current_heading].rstrip())
                # skip original body lines until the next heading
                i += 1
                while i < len(lines) and not re.match(r"^#{1,6}\s+", lines[i]):
                    i += 1
                continue
        else:
            out.append(line)
        i += 1
    return "\n".join(out) + "\n"


def fill_docx(path, content_map, dest, token_map=None):
    from docx import Document
    doc = Document(str(path))
    current_heading = None
    wrote_for_heading = set()
    for para in doc.paragraphs:
        if _is_heading_style(para.style) and para.text.strip():
            current_heading = para.text.strip()
            continue
        if current_heading in content_map and para.text.strip():
            if current_heading not in wrote_for_heading:
                _set_paragraph_text(para, content_map[current_heading])
                wrote_for_heading.add(current_heading)
            else:
                _set_paragraph_text(para, "")
    if token_map:
        fill_header_footer_tokens(doc, token_map)
    doc.save(str(dest))


def _set_paragraph_text(paragraph, new_text):
    """Replace a paragraph's text while keeping its style. Clears extra runs."""
    if paragraph.runs:
        paragraph.runs[0].text = new_text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(new_text)


_TOKEN_RE = re.compile(r"<[^<>\n]{1,80}>")


def _header_footer_parts(doc):
    """Yield each header/footer part that owns its own content (skips parts
    linked to the previous section, whose content belongs to another part)."""
    for section in doc.sections:
        parts = [section.header, section.footer]
        if section.different_first_page_header_footer:
            parts += [section.first_page_header, section.first_page_footer]
        if doc.settings.odd_and_even_pages_header_footer:
            parts += [section.even_page_header, section.even_page_footer]
        for part in parts:
            if not part.is_linked_to_previous:
                yield part


def _iter_part_paragraphs(part):
    """Yield every paragraph in a header/footer, including inside tables."""
    for para in part.paragraphs:
        yield para
    for table in part.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    yield para


def extract_placeholder_tokens(doc):
    """Return every distinct <...> token found in the document's headers/footers."""
    tokens = set()
    for part in _header_footer_parts(doc):
        for para in _iter_part_paragraphs(part):
            tokens.update(_TOKEN_RE.findall(para.text))
    return sorted(tokens)


def _replace_tokens_in_paragraph(paragraph, token_map):
    """Substitute known <token> occurrences in a paragraph's text in place.

    Only rewrites the paragraph when a token actually matches, so paragraphs
    with no bracket token (including page-number fields) are left untouched.
    """
    original = paragraph.text
    if not any(token in original for token in token_map):
        return False
    new_text = original
    for token, value in token_map.items():
        new_text = new_text.replace(token, value)
    _set_paragraph_text(paragraph, new_text)
    return True


def fill_header_footer_tokens(doc, token_map):
    """Apply token_map substitutions to every header/footer paragraph."""
    if not token_map:
        return
    for part in _header_footer_parts(doc):
        for para in _iter_part_paragraphs(part):
            _replace_tokens_in_paragraph(para, token_map)


def extract_structure_docx(path):
    """Return a structural fingerprint: headings, tables, fonts, colors, TOC presence."""
    from docx import Document
    doc = Document(str(path))

    headings = [{"level": _heading_level_from_style_obj(p.style), "heading": p.text.strip()}
                for p in doc.paragraphs if _is_heading_style(p.style) and p.text.strip()]

    tables = [{"row_count": len(t.rows), "col_count": len(t.columns)} for t in doc.tables]

    fonts = set()
    colors = set()
    for para in doc.paragraphs:
        for run in para.runs:
            name = run.font.name
            size = run.font.size.pt if run.font.size else None
            if name or size:
                fonts.add("{}:{}".format(name or "?", size or "?"))
            color = run.font.color
            if color is not None and color.rgb is not None:
                colors.add(str(color.rgb))
            if run.font.highlight_color is not None:
                colors.add(str(run.font.highlight_color))

    xml = doc.element.xml
    has_toc = (r"TOC \o" in xml) or (r"TOC \h" in xml)

    return {
        "headings": headings,
        "tables": tables,
        "fonts": sorted(fonts),
        "colors": sorted(colors),
        "has_toc": has_toc,
    }


def _diff_structure(prior, current):
    prior_headings = [h["heading"] for h in prior["headings"]]
    current_headings = [h["heading"] for h in current["headings"]]
    missing_headings = [h for h in prior_headings if h not in current_headings]
    added_headings = [h for h in current_headings if h not in prior_headings]

    table_deltas = []
    for i, (p_t, c_t) in enumerate(zip(prior["tables"], current["tables"])):
        if p_t != c_t:
            table_deltas.append({"table_index": i, "prior": p_t, "current": c_t})
    if len(prior["tables"]) != len(current["tables"]):
        table_deltas.append({"table_count_prior": len(prior["tables"]),
                              "table_count_current": len(current["tables"])})

    fonts_removed = sorted(set(prior["fonts"]) - set(current["fonts"]))
    colors_removed = sorted(set(prior["colors"]) - set(current["colors"]))

    return {
        "missing_headings": missing_headings,
        "added_headings": added_headings,
        "table_deltas": table_deltas,
        "fonts_removed": fonts_removed,
        "colors_removed": colors_removed,
        "toc_lost": bool(prior["has_toc"] and not current["has_toc"]),
    }


# --- Modes ------------------------------------------------------------------

def do_outline(template):
    outline = extract_outline(template)
    print(json.dumps(outline, indent=2, ensure_ascii=False))


def do_tokens(template):
    if template.suffix.lower() != ".docx":
        print(json.dumps([], indent=2))
        return
    from docx import Document
    doc = Document(str(template))
    print(json.dumps(extract_placeholder_tokens(doc), indent=2, ensure_ascii=False))


def do_structure(template):
    if template.suffix.lower() != ".docx":
        print(json.dumps({"headings": [], "tables": [], "fonts": [], "colors": [], "has_toc": False}, indent=2))
        return
    print(json.dumps(extract_structure_docx(template), indent=2, ensure_ascii=False))


def do_compare_structure(template, prior_path, config):
    if template.suffix.lower() != ".docx":
        print(json.dumps({"missing_headings": [], "added_headings": [], "table_deltas": [],
                          "fonts_removed": [], "colors_removed": [], "toc_lost": False}, indent=2))
        return 0
    resolved_prior = resolve_template(prior_path, config)
    if resolved_prior is None or resolved_prior.suffix.lower() != ".docx":
        print("Could not read the prior version '{}'. Check the filename in context/prior-versions/.".format(prior_path))
        return 1
    current = extract_structure_docx(template)
    prior = extract_structure_docx(resolved_prior)
    print(json.dumps(_diff_structure(prior, current), indent=2, ensure_ascii=False))
    return 0


def do_fill(template, config, system, doc_label, fill_path):
    try:
        raw_map = json.loads(Path(fill_path).read_text(encoding="utf-8"))
    except Exception as exc:
        print("Could not read the content map '{}': {}".format(fill_path, exc))
        return 1
    if not isinstance(raw_map, dict):
        print("The content map must be a JSON object of {\"heading\": \"content\"}.")
        return 1
    if "sections" in raw_map or "tokens" in raw_map:
        content_map = raw_map.get("sections") or {}
        token_map = raw_map.get("tokens") or {}
    else:
        content_map = raw_map
        token_map = {}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = template.suffix.lower()
    dest = OUTPUT_DIR / output_name(config, system, doc_label, suffix if suffix in (".docx", ".md") else ".md")
    try:
        if suffix == ".docx":
            fill_docx(template, content_map, dest, token_map)
        else:
            filled = fill_md(template.read_text(encoding="utf-8", errors="replace"), content_map)
            dest.write_text(filled, encoding="utf-8")
    except ImportError:
        print("python-docx is required for .docx templates. Run setup first.")
        return 1
    except Exception as exc:
        print("Could not fill the template: {}".format(exc))
        return 1

    filled_text = dest.read_text(encoding="utf-8", errors="replace") if suffix != ".docx" else ""
    confirms = filled_text.count("[CONFIRM:")
    print("Filled draft created: {}".format(dest.relative_to(REPO_ROOT).as_posix()))
    if suffix != ".docx":
        print("{} section(s) still need a confirmed value.".format(confirms))
    if suffix == ".docx":
        from docx import Document as _Document
        remaining = extract_placeholder_tokens(_Document(str(dest)))
        if remaining:
            print("Warning: header/footer placeholder(s) remain unresolved: {} — add the missing field to workbench.config.yaml or resolve manually.".format(", ".join(remaining)))
    return 0


def do_copy(template, config, system, doc_label):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = template.suffix.lower()
    dest = OUTPUT_DIR / output_name(config, system, doc_label, suffix if suffix in (".docx", ".md") else ".md")
    try:
        if suffix == ".docx":
            from docx import Document
            Document(str(template)).save(str(dest))
        else:
            dest.write_text(template.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    except ImportError:
        print("python-docx is required for .docx templates. Run setup first.")
        return 1
    except Exception as exc:
        print("Could not create the draft: {}".format(exc))
        return 1
    print("Draft created: {}".format(dest.relative_to(REPO_ROOT).as_posix()))
    print("Sections found in this template:")
    for sec in extract_outline(template):
        print("  - {}".format(sec["heading"]))
    print("Next: the generate-doc skill fills each section from your project context.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a deliverable from a template.")
    parser.add_argument("template", help="Template filename or config alias.")
    parser.add_argument("--outline", action="store_true",
                        help="Print the template's sections and instruction text as JSON.")
    parser.add_argument("--tokens", action="store_true",
                        help="Print placeholder tokens (e.g. <System Name>) found in the document's headers/footers.")
    parser.add_argument("--structure", action="store_true",
                        help="Print a structural fingerprint (headings, tables, fonts, colors, TOC) as JSON.")
    parser.add_argument("--compare-structure", metavar="PRIOR.docx", default=None,
                        help="Compare this document's structure against a prior version and print a diff.")
    parser.add_argument("--fill", metavar="MAP.json", default=None,
                        help="Fill sections from a JSON map {heading: content} and write the draft.")
    parser.add_argument("--system", default=None, help="System name (defaults to MASTER_CONTEXT).")
    parser.add_argument("--doc", default=None, help="Document label for the filename.")
    args = parser.parse_args(argv)

    config = load_config()
    template = resolve_template(args.template, config)
    if template is None:
        available = [p.name for p in TEMPLATES_DIR.iterdir()
                     if p.is_file() and p.name not in (".gitkeep", "README.md")] if TEMPLATES_DIR.is_dir() else []
        print("No template matched '{}'.".format(args.template))
        if available:
            print("Available templates: " + ", ".join(available))
        else:
            print("templates/ has no templates yet. Add one, then re-run.")
        return 1

    if args.outline:
        do_outline(template)
        return 0

    if args.tokens:
        do_tokens(template)
        return 0

    if args.structure:
        do_structure(template)
        return 0

    if args.compare_structure:
        return do_compare_structure(template, args.compare_structure, config)

    # Context must be built before composing or copying a real draft.
    if not CONTEXT_FILE.is_file() or "[populated by /build-context]" in CONTEXT_FILE.read_text(encoding="utf-8", errors="replace"):
        print("MASTER_CONTEXT.md is not populated. Run /build-context first.")
        return 1

    system = args.system or system_name_from_context() or "System"
    doc_label = args.doc or args.template

    if args.fill:
        return do_fill(template, config, system, doc_label, args.fill)
    return do_copy(template, config, system, doc_label)


if __name__ == "__main__":
    sys.exit(main())
