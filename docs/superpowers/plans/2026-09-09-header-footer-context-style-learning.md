# Header/Footer Fill, Template-Driven Context, and Style-Learning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix header/footer placeholder fill in generate-doc, make MASTER_CONTEXT.md's structure template-driven, and add two new style-learning mechanisms (reference-docs and older-version-doc) plus a structural-consistency check in gap-check.

**Architecture:** All deterministic, mechanical work (finding/replacing header-footer tokens, extracting a structural fingerprint, diffing two fingerprints) lives in `scripts/generate_doc.py` as new functions exposed via new CLI flags (`--tokens`, `--structure`, `--compare-structure`), following the existing `--outline`/`--fill` pattern exactly. All judgment work (composing content, matching a reference doc to a template, writing a style summary, deciding section merges) stays in skill prose (`.claude/skills/*/SKILL.md`), since that is how every existing skill in this repo divides work between script and prompt.

**Tech Stack:** Python 3 + python-docx 1.2.0 (already installed, confirmed via `python -c "import docx"`), PyYAML. No test framework exists in this repo (confirmed: no `tests/` directory, no pytest config) — verification steps in this plan run small inline Python scripts via Bash heredocs and check printed output, matching how this codebase is actually developed and checked today. Do not introduce a pytest suite; that would be a larger, unrequested restructuring.

**Spec:** [docs/superpowers/specs/2026-09-09-header-footer-context-style-learning-design.md](../specs/2026-09-09-header-footer-context-style-learning-design.md)

## Global Constraints

- Never invent a section list, a risk model, or an SOP citation — this repo's core rule (CLAUDE.md, workbench.config.yaml). Every new skill step must derive structure from templates/, sops/, or workbench.config.yaml, or fall back to an explicitly documented generic structure.
- The placeholder marker format is `[CONFIRM: {description} — ref: {owner}]`, read from `placeholder_marker` in workbench.config.yaml — reuse this exact convention for any new "unresolved value" case; do not invent a new marker syntax.
- Every skill file follows the two-field frontmatter (`name`, `description`) and `# name / ## Overview / ## Triggers / ## Instructions / ## Rules` structure used by all 26 existing skills — new skill files must match this exactly.
- Files in templates/, sops/, reference-docs/, and context/prior-versions/ are read-only from the framework's perspective — never modified by any skill or script.
- `resolve_template()` in scripts/generate_doc.py is the one place that resolves a filename/alias/path argument to a file — reuse it everywhere a script needs to accept a template, deliverable, or prior-version path, rather than writing new resolution logic.

---

## Task 1: Header/footer placeholder token extraction and fill (script)

**Files:**
- Modify: `scripts/generate_doc.py:257-282` (extend `fill_docx`, add new functions after `_set_paragraph_text`)
- Modify: `scripts/generate_doc.py:292-323` (`do_fill` — extend JSON schema, add self-review warning)
- Modify: `scripts/generate_doc.py:350-391` (`main` — add `--tokens` flag)

**Interfaces:**
- Produces: `extract_placeholder_tokens(doc) -> list[str]` (sorted, deduplicated `<...>` tokens found in headers/footers), `fill_header_footer_tokens(doc, token_map: dict[str, str]) -> None`, `_header_footer_parts(doc)` (generator of header/footer parts that own their own content), `_iter_part_paragraphs(part)` (generator of paragraphs, including inside tables), `_replace_tokens_in_paragraph(paragraph, token_map) -> bool`. `fill_docx(path, content_map, dest, token_map=None)` — signature extended with a new optional 4th parameter.
- Consumes: existing `_set_paragraph_text(paragraph, new_text)` (line 275), existing `output_name()`, existing `REPO_ROOT`.

- [ ] **Step 1: Write a verification script and confirm it fails (functions don't exist yet)**

Run via Bash:
```bash
python - <<'PY'
import sys
sys.path.insert(0, "scripts")
from docx import Document
import generate_doc as gd

doc = Document()
# Simulate a real Lilly template: placeholder tokens live inside a table
# cell in the header (confirmed against templates/CSV TEMPLATE- System
# Overview.docx), and the footer has both a token-free line and a page
# text line that must never be touched.
table = doc.sections[0].header.add_table(rows=1, cols=1, width=1)
table.rows[0].cells[0].paragraphs[0].text = "<System Name> Overview  CI: <CI###########>"
doc.sections[0].footer.paragraphs[0].text = "Page 1 of 1"
doc.save("scratch_test.docx")

doc2 = Document("scratch_test.docx")
tokens = gd.extract_placeholder_tokens(doc2)
assert tokens == ["<CI###########>", "<System Name>"], tokens

gd.fill_header_footer_tokens(doc2, {"<System Name>": "Acme", "<CI###########>": "CI-12345"})
doc2.save("scratch_test_filled.docx")

doc3 = Document("scratch_test_filled.docx")
header_text = doc3.sections[0].header.tables[0].rows[0].cells[0].paragraphs[0].text
footer_text = doc3.sections[0].footer.paragraphs[0].text
assert header_text == "Acme Overview  CI: CI-12345", header_text
assert footer_text == "Page 1 of 1", footer_text
print("PASS")
PY
```
Expected: `AttributeError: module 'generate_doc' has no attribute 'extract_placeholder_tokens'` (or similar) — the functions don't exist yet.

- [ ] **Step 2: Add the token-extraction and fill functions**

In `scripts/generate_doc.py`, insert immediately after `_set_paragraph_text` (after line 282, before the `# --- Modes ---` comment):

```python
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
```

- [ ] **Step 3: Extend `fill_docx` to apply header/footer tokens**

Replace the existing `fill_docx` function (lines 257-272):
```python
def fill_docx(path, content_map, dest):
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
    doc.save(str(dest))
```
with:
```python
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
```

- [ ] **Step 4: Run the verification script again and confirm it passes**

Run the exact same command from Step 1.
Expected: prints `PASS`.

- [ ] **Step 5: Clean up scratch files**

```bash
rm -f scratch_test.docx scratch_test_filled.docx
```

- [ ] **Step 6: Add the `--tokens` CLI flag and wire it into `main()`**

In `scripts/generate_doc.py`, add this function near `do_outline` (after it, before `do_fill`):
```python
def do_tokens(template):
    if template.suffix.lower() != ".docx":
        print(json.dumps([], indent=2))
        return
    from docx import Document
    doc = Document(str(template))
    print(json.dumps(extract_placeholder_tokens(doc), indent=2, ensure_ascii=False))
```

In `main()`, add the argument right after the `--outline` argument (currently lines 353-354):
```python
    parser.add_argument("--tokens", action="store_true",
                        help="Print placeholder tokens (e.g. <System Name>) found in the document's headers/footers.")
```

And add the handling right after the existing `if args.outline:` block (currently lines 373-375):
```python
    if args.tokens:
        do_tokens(template)
        return 0
```

- [ ] **Step 7: Verify the CLI flag against a real template**

Run:
```bash
python scripts/generate_doc.py "CSV TEMPLATE- System Overview.docx" --tokens
```
Expected output (JSON array containing at least):
```json
[
  "<CI###########>",
  "<System Name>"
]
```

- [ ] **Step 8: Extend `do_fill`'s JSON schema and add the self-review warning**

Replace the existing `do_fill` function (lines 292-323) with:
```python
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
```
Note the old flat `{heading: content}` shape still works unchanged (the `else` branch), so nothing that already calls `--fill` with the old shape breaks.

- [ ] **Step 9: Verify backward compatibility and the new self-review warning end-to-end**

Run:
```bash
python - <<'PY'
import json, subprocess, sys
from pathlib import Path

# Old flat shape still works (backward compatibility).
Path("scratch_map_old.json").write_text(json.dumps({"Purpose": "Test purpose."}))
r = subprocess.run([sys.executable, "scripts/generate_doc.py",
                     "CSV TEMPLATE- System Overview.docx", "--fill", "scratch_map_old.json",
                     "--system", "TestSys", "--doc", "smoketest-old"],
                    capture_output=True, text=True)
print("OLD SHAPE STDOUT:", r.stdout)
assert r.returncode == 0, r.stderr
assert "Filled draft created" in r.stdout

# New shape with a deliberately incomplete tokens map triggers the warning.
Path("scratch_map_new.json").write_text(json.dumps({
    "sections": {"Purpose": "Test purpose."},
    "tokens": {"<System Name>": "Acme"}
}))
r2 = subprocess.run([sys.executable, "scripts/generate_doc.py",
                      "CSV TEMPLATE- System Overview.docx", "--fill", "scratch_map_new.json",
                      "--system", "TestSys", "--doc", "smoketest-new"],
                     capture_output=True, text=True)
print("NEW SHAPE STDOUT:", r2.stdout)
assert r2.returncode == 0, r2.stderr
assert "Warning: header/footer placeholder(s) remain unresolved" in r2.stdout
assert "<CI###########>" in r2.stdout
print("PASS")
PY
```
Expected: prints both stdout captures, then `PASS`. (This will also require MASTER_CONTEXT.md to exist and not contain `[populated by /build-context]` — if it doesn't, temporarily note this in your test run; the live repo's MASTER_CONTEXT.md already satisfies this.)

- [ ] **Step 10: Clean up scratch and generated test files**

```bash
rm -f scratch_map_old.json scratch_map_new.json
rm -f "deliverables/in-progress/TestSys_smoketest-old_v1.0_draft.docx"
rm -f "deliverables/in-progress/TestSys_smoketest-new_v1.0_draft.docx"
```

- [ ] **Step 11: Commit**

```bash
git add scripts/generate_doc.py
git commit -m "feat: fill header/footer placeholder tokens and warn if any survive"
```

---

## Task 2: Wire token discovery into the generate-doc skill

**Files:**
- Modify: `.claude/skills/generate-doc/SKILL.md`

**Interfaces:**
- Consumes: `--tokens` and the extended `--fill` JSON schema from Task 1.

- [ ] **Step 1: Replace the Instructions section**

Replace the entire `## Instructions` section (through the end of `## Rules`) with:

```markdown
## Instructions

1. Read MASTER_CONTEXT.md. If it is empty or missing, stop and tell the user to run /build-context first.

2. Resolve the template. Read workbench.config.yaml for any alias under deliverables. If no argument was given, list the files in templates/ and ask which to use. If no template matches, tell the user which file to add to templates/ and offer to generate a generic structure instead.

3. Get the section outline and instruction text. Run:
   `python scripts/generate_doc.py <template> --outline`
   This returns each section as { level, heading, instruction }. The instruction is the guidance text the template author placed under that heading.

4. Discover header/footer placeholder tokens. Run:
   `python scripts/generate_doc.py <template> --tokens`
   This returns the distinct <...> tokens (e.g. <System Name>, <CI###########>) found in the template's running headers and footers. For each token, resolve a value from MASTER_CONTEXT.md or the fields under project_metadata_fields in workbench.config.yaml. Where no value is known, use the configured placeholder marker as that token's value rather than guessing.

5. For each section, read its instruction text and understand what content that section asks for. Then compose the content that satisfies it:
   - Draw the facts from MASTER_CONTEXT.md and the project files.
   - Cite the specific SOP file and section from sops/ where a rule applies. Never invent an SOP name or section number.
   - Apply the language rules from workbench.config.yaml (defaults in CLAUDE.md if the config is absent).
   - The composed content replaces the instruction text. Do not keep the original guidance in the finished section.
   - Where the project does not have the information, write the placeholder marker from the config (default: [CONFIRM: what is needed — ref: owner]) in place of the instruction, rather than guessing.

6. Build a content map as JSON: { "sections": { "<exact heading text>": "<composed content>" }, "tokens": { "<token>": "<resolved value>" } }, covering every section you can fill or mark and every token from step 4. Save it to a temporary file.

7. Produce the filled draft, preserving the template's formatting:
   `python scripts/generate_doc.py <template> --fill <content-map.json>`
   This writes the draft to deliverables/in-progress/ using the naming pattern from the config, replacing each mapped section's instruction text with your content and substituting each resolved token in the headers/footers, leaving any section or token you did not map with its original text. If any header/footer placeholder remains unresolved in the finished draft, this command prints a warning naming it — carry that warning into the final message in step 10.

8. Update DELIVERABLE_STATUS.md: add a row with status "Draft", date, and filename.

9. Run /update-context automatically.

10. Print: "Generated: deliverables/in-progress/<filename>. X sections still need a confirmed value. Review before routing." If step 7 printed a header/footer placeholder warning, include it in this message.

## Rules
The template defines the sections — never impose a section list of your own. Replace instruction text with real content or a [CONFIRM] marker; never leave raw guidance in a filled section and never invent a value. Apply the configured language rules and cite only SOPs that exist in sops/. Never resolve a header/footer token by guessing a value not found in MASTER_CONTEXT.md or workbench.config.yaml.
```

- [ ] **Step 2: Verify the file is well-formed**

Run:
```bash
python -c "import yaml,re,pathlib; t=pathlib.Path('.claude/skills/generate-doc/SKILL.md').read_text(encoding='utf-8'); fm=t.split('---')[1]; print(yaml.safe_load(fm)); print('OK')"
```
Expected: prints the parsed frontmatter dict (`{'name': 'generate-doc', 'description': ...}`) then `OK` — confirms the frontmatter is still valid YAML after the edit.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/generate-doc/SKILL.md
git commit -m "docs: wire header/footer token discovery and self-review into generate-doc"
```

---

## Task 3: Structural fingerprint and comparison (script)

**Files:**
- Modify: `scripts/generate_doc.py:78-98` (`resolve_template` — accept a direct file path)
- Modify: `scripts/generate_doc.py` (add `extract_structure_docx`, `_diff_structure`, `do_structure`, `do_compare_structure`; wire into `main()`)

**Interfaces:**
- Produces: `extract_structure_docx(path) -> dict` with keys `headings` (list of `{level, heading}`), `tables` (list of `{row_count, col_count}`), `fonts` (sorted list of `"name:size"` strings), `colors` (sorted list of color strings), `has_toc` (bool). `_diff_structure(prior, current) -> dict` with keys `missing_headings`, `added_headings`, `table_deltas`, `fonts_removed`, `colors_removed`, `toc_lost`.
- Consumes: `_is_heading_style`, `_heading_level_from_style_obj` (existing, lines 130-176), `resolve_template` (extended in Step 1 of this task).

- [ ] **Step 1: Extend `resolve_template` to accept a direct file path**

Replace the existing `resolve_template` function (lines 78-98):
```python
def resolve_template(arg, config):
    """Resolve a template argument to a path in templates/.

    Order: config alias -> exact filename -> case-insensitive fuzzy match.
    """
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
```
with:
```python
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
```

- [ ] **Step 2: Verify existing template resolution still works and direct paths now resolve**

Run:
```bash
python - <<'PY'
import sys
sys.path.insert(0, "scripts")
import generate_doc as gd

config = gd.load_config()
# Existing behavior: resolve by filename in templates/.
p1 = gd.resolve_template("CSV TEMPLATE- System Overview.docx", config)
assert p1 is not None and p1.name == "CSV TEMPLATE- System Overview.docx", p1

# New behavior: a direct existing path resolves immediately.
p2 = gd.resolve_template(str(p1), config)
assert p2 == p1, p2

# Non-existent direct path still falls through to the "not found" case.
p3 = gd.resolve_template("no/such/file.docx", config)
assert p3 is None, p3
print("PASS")
PY
```
Expected: prints `PASS`.

- [ ] **Step 3: Write a verification script for the structure functions and confirm it fails**

```bash
python - <<'PY'
import sys
sys.path.insert(0, "scripts")
from docx import Document
import generate_doc as gd

doc = Document()
doc.add_heading("Purpose", level=1)
doc.add_paragraph("Some text.")
doc.add_heading("Scope", level=1)
t = doc.add_table(rows=2, cols=3)
doc.save("scratch_structure.docx")

fp = gd.extract_structure_docx("scratch_structure.docx")
assert [h["heading"] for h in fp["headings"]] == ["Purpose", "Scope"], fp["headings"]
assert fp["tables"] == [{"row_count": 2, "col_count": 3}], fp["tables"]
assert fp["has_toc"] is False, fp

prior = dict(fp)
prior["headings"] = fp["headings"] + [{"level": 1, "heading": "Removed Section"}]
diff = gd._diff_structure(prior, fp)
assert diff["missing_headings"] == ["Removed Section"], diff
print("PASS")
PY
```
Expected: `AttributeError: module 'generate_doc' has no attribute 'extract_structure_docx'`.

- [ ] **Step 4: Add `extract_structure_docx` and `_diff_structure`**

Insert into `scripts/generate_doc.py`, immediately after the `fill_header_footer_tokens` function added in Task 1:

```python
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
```

- [ ] **Step 5: Run the verification script again and confirm it passes**

Run the exact command from Step 3.
Expected: prints `PASS`.

- [ ] **Step 6: Clean up scratch file**

```bash
rm -f scratch_structure.docx
```

- [ ] **Step 7: Add `--structure` and `--compare-structure` CLI flags**

Add these two functions near `do_outline`/`do_tokens`:
```python
def do_structure(template):
    if template.suffix.lower() != ".docx":
        print(json.dumps({"headings": [], "tables": [], "fonts": [], "colors": [], "has_toc": False}, indent=2))
        return
    print(json.dumps(extract_structure_docx(template), indent=2, ensure_ascii=False))


def do_compare_structure(template, prior_path):
    if template.suffix.lower() != ".docx":
        print(json.dumps({"missing_headings": [], "added_headings": [], "table_deltas": [],
                          "fonts_removed": [], "colors_removed": [], "toc_lost": False}, indent=2))
        return
    current = extract_structure_docx(template)
    prior = extract_structure_docx(Path(prior_path))
    print(json.dumps(_diff_structure(prior, current), indent=2, ensure_ascii=False))
```

In `main()`, add these two arguments after the `--tokens` argument added in Task 1:
```python
    parser.add_argument("--structure", action="store_true",
                        help="Print a structural fingerprint (headings, tables, fonts, colors, TOC) as JSON.")
    parser.add_argument("--compare-structure", metavar="PRIOR.docx", default=None,
                        help="Compare this document's structure against a prior version and print a diff.")
```

And add the handling after the `if args.tokens:` block added in Task 1:
```python
    if args.structure:
        do_structure(template)
        return 0

    if args.compare_structure:
        do_compare_structure(template, args.compare_structure)
        return 0
```

- [ ] **Step 8: Verify the CLI flags end-to-end against real templates**

```bash
python scripts/generate_doc.py "CSV TEMPLATE- System Overview.docx" --structure
```
Expected: JSON with non-empty `headings`, `has_toc: true` (this template has a table of contents), and at least one entry in `fonts`.

```bash
python - <<'PY'
import subprocess, sys, shutil
shutil.copy("templates/CSV TEMPLATE- System Overview.docx", "scratch_prior.docx")
from docx import Document
d = Document("scratch_prior.docx")
d.add_heading("Extra Section Only In Prior", level=1)
d.save("scratch_prior.docx")
r = subprocess.run([sys.executable, "scripts/generate_doc.py",
                     "CSV TEMPLATE- System Overview.docx",
                     "--compare-structure", "scratch_prior.docx"],
                    capture_output=True, text=True)
print(r.stdout)
assert r.returncode == 0, r.stderr
assert "Extra Section Only In Prior" in r.stdout
PY
rm -f scratch_prior.docx
```
Expected: prints a JSON diff whose `missing_headings` includes `"Extra Section Only In Prior"`.

- [ ] **Step 9: Commit**

```bash
git add scripts/generate_doc.py
git commit -m "feat: add structural fingerprint extraction and comparison (--structure, --compare-structure)"
```

---

## Task 4: Template-driven MASTER_CONTEXT sections; retire orphaned build_context.py

**Files:**
- Modify: `.claude/skills/build-context/SKILL.md`
- Delete: `scripts/build_context.py`

**Interfaces:**
- Consumes: `--outline` (existing, unchanged).

- [ ] **Step 1: Confirm `scripts/build_context.py` is unreferenced before deleting it**

```bash
grep -rn "build_context" --include="*.md" --include="*.py" --include="*.yaml" . | grep -v "^./.git/" | grep -v "^./scripts/build_context.py" | grep -v "^./docs/superpowers/"
```
Expected: no output (already confirmed during research — this re-check catches any change since then).

- [ ] **Step 2: Delete the orphaned script**

```bash
git rm scripts/build_context.py
```

- [ ] **Step 3: Replace build-context's section-list step**

In `.claude/skills/build-context/SKILL.md`, replace step 6 (the fixed 10-section list):
```markdown
6. Build MASTER_CONTEXT.md with these sections:
   - Header: system name, last refreshed date, go-live date, plus any metadata fields configured in workbench.config.yaml
   - 1. Project Overview (one paragraph)
   - 2. Stakeholders / RACI table
   - 3. Architecture & Tech Stack
   - 4. Validation Deliverables Status table (doc | status | due | notes)
   - 5. Requirements Status
   - 6. Open Items & Pending Confirmations (numbered, owner, description)
   - 7. Key Decisions Made (with date and rationale)
   - 8. Timeline
   - 9. Key Files & Scripts
   - 10. Pending Work
```
with:
```markdown
6. Determine the section list for MASTER_CONTEXT.md:

   a. Determine the in-scope templates: read the `deliverables:` list in
      workbench.config.yaml. If it lists one or more aliases, resolve each
      to its file in templates/ — that is the in-scope set. If the list is
      empty, treat every file in templates/ (excluding .gitkeep and
      README.md) as in scope.

   b. If the in-scope set is empty (no deliverables configured and
      templates/ has no usable files), use the generic fallback structure
      in step 6-fallback below and skip to step 7.

   c. For each in-scope template, run:
      `python scripts/generate_doc.py <template> --outline`
      and collect its returned `heading` values as that document type's
      section list.

   d. Merge shared front-matter across templates: any heading that
      case-insensitively matches one of Purpose, Scope, Out of Scope,
      Reviewers, Approvers, Revision History, or Stakeholders is folded
      into ONE shared MASTER_CONTEXT section (do not repeat it once per
      template).

   e. Any other heading is specific to that document type. Group these
      under a subsection named after the document (e.g. "Deliverable —
      Backup and Restoration SOP").

   f. Always include this fixed bookkeeping scaffold regardless of what
      templates produced (this is the framework's own project-tracking
      structure, not deliverable content, so it is not "invented"):
      - Open Items & Pending Confirmations (numbered, owner, description)
      - Key Decisions Made (with date and rationale)
      - Timeline
      - Key Files & Scripts
      - Pending Work

6-fallback. Generic structure (used only when step 6b applies — no
   templates and no configured deliverables):
   - Header: system name, last refreshed date, go-live date, plus any
     metadata fields configured in workbench.config.yaml
   - 1. System Overview (one paragraph)
   - 2. Stakeholders
   - 3. Architecture
   - 4. Requirements
   - 5. Open Items & Pending Confirmations
   - 6. Key Decisions Made (with date and rationale)
   - 7. Timeline
   - 8. Pending Work
```

- [ ] **Step 4: Verify the skill file is still well-formed**

```bash
python -c "import yaml,pathlib; t=pathlib.Path('.claude/skills/build-context/SKILL.md').read_text(encoding='utf-8'); fm=t.split('---')[1]; print(yaml.safe_load(fm)); print('OK')"
```
Expected: prints the frontmatter dict then `OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/build-context/SKILL.md
git commit -m "feat: derive MASTER_CONTEXT sections from templates present, with a generic fallback"
```
(The `scripts/build_context.py` deletion from Step 2 is already staged from `git rm` — it will be included in this commit.)

---

## Task 5: context/prior-versions/ folder and provenance tagging

**Files:**
- Create: `context/prior-versions/.gitkeep`
- Modify: `.claude/skills/build-context/SKILL.md` (step 4 — extraction rules)
- Modify: `.claude/skills/update-context/SKILL.md` (step 4 — extraction rules)
- Modify: `CLAUDE.md` (Folder roles section)

- [ ] **Step 1: Create the folder**

```bash
mkdir -p context/prior-versions
touch context/prior-versions/.gitkeep
```

- [ ] **Step 2: Verify build-context's existing Glob already covers the new folder**

```bash
grep -n "Glob" .claude/skills/build-context/SKILL.md
```
Expected: step 2 reads `Use Glob to list every file in context/ recursively.` — confirms no change is needed to the Glob step itself, since it already recurses into every subfolder including the new one.

- [ ] **Step 3: Add the provenance rule to build-context**

In `.claude/skills/build-context/SKILL.md`, find step 4 (the extraction bullet list):
```markdown
4. From each file, extract:
   - system name
   - project background
   - stakeholders and roles
   - architecture decisions
   - open items
   - timeline / milestones
   - any metadata fields listed under project_metadata_fields in workbench.config.yaml
   - pending confirmations from other parties
   - approved decisions
```
Replace with:
```markdown
4. From each file, extract:
   - system name
   - project background
   - stakeholders and roles
   - architecture decisions
   - open items
   - timeline / milestones
   - any metadata fields listed under project_metadata_fields in workbench.config.yaml
   - pending confirmations from other parties
   - approved decisions

   If the file is under context/prior-versions/, it describes what the
   system was at a specific past version, which may now be stale. Tag
   every fact extracted from it with its source, e.g. "per prior version
   (v1.0): ..." — never present it as current fact.
```

- [ ] **Step 4: Add the matching provenance rule to update-context**

In `.claude/skills/update-context/SKILL.md`, find step 4:
```markdown
4. For each new or changed file, extract only the delta:
   - new decisions
   - new confirmations
   - new open items
   - status changes
   - new stakeholders
```
Replace with:
```markdown
4. For each new or changed file, extract only the delta:
   - new decisions
   - new confirmations
   - new open items
   - status changes
   - new stakeholders

   If the file is under context/prior-versions/, tag every extracted fact
   with its source, e.g. "per prior version (v1.0): ...", the same way
   build-context does — never present it as current fact.
```

- [ ] **Step 5: Document the new folder in CLAUDE.md's Folder roles section**

In `CLAUDE.md`, find:
```markdown
## Folder roles
- context/ — the user drops any project file here. Never edit manually.
```
Replace with:
```markdown
## Folder roles
- context/ — the user drops any project file here. Never edit manually. context/prior-versions/ holds a prior version of the system's own document(s), used both as project knowledge (tagged with its source version, since it may be stale) and as a style/formatting reference (see /learn-style) and a structural-consistency baseline (see /gap-check).
```

- [ ] **Step 6: Verify both skill files are still well-formed**

```bash
python -c "import yaml,pathlib; [print(f, yaml.safe_load(pathlib.Path(f).read_text(encoding='utf-8').split('---')[1])) for f in ['.claude/skills/build-context/SKILL.md', '.claude/skills/update-context/SKILL.md']]; print('OK')"
```
Expected: prints both frontmatter dicts then `OK`.

- [ ] **Step 7: Commit**

```bash
git add context/prior-versions/.gitkeep .claude/skills/build-context/SKILL.md .claude/skills/update-context/SKILL.md CLAUDE.md
git commit -m "feat: add context/prior-versions/ with provenance tagging in build-context and update-context"
```

---

## Task 6: reference-docs/ folder and the learn-style skill

**Files:**
- Create: `reference-docs/README.md`
- Create: `reference-docs/.gitkeep`
- Create: `reference-docs/style-notes/.gitkeep`
- Create: `.claude/skills/learn-style/SKILL.md`

**Interfaces:**
- Consumes: `--outline` (existing), the fuzzy-match convention already documented in `resolve_template()`.
- Produces: `reference-docs/style-notes/<template-stem>.md` files, consumed by generate-doc in Task 7.

- [ ] **Step 1: Create the reference-docs folder and its README**

```bash
mkdir -p reference-docs/style-notes
touch reference-docs/.gitkeep reference-docs/style-notes/.gitkeep
```

Create `reference-docs/README.md`:
```markdown
# Put approved documents here to learn their writing style

A reference document is an approved document of the same type as one of your
templates — from a different project or a different system — that you want
the assistant to learn writing and formatting conventions from: tone, how
scope and out-of-scope sections read, whether a section favors a table or
prose, how densely it cites SOPs, and how sections that don't apply are
handled. It is never read for facts — only for style.

## How to use it
1. Copy the approved document into this folder.
2. Type `/learn-style <filename>`.
3. The assistant matches it to a template in templates/, asks you to confirm
   the match, and saves a style-notes file that /generate-doc uses
   automatically the next time that template is generated.

## Good to know
- Files here are never modified. The workbench only reads them.
- Style notes are saved to reference-docs/style-notes/ — one file per
  template — so they persist across sessions.
- A prior version of the system's own document works the same way; drop it
  in context/prior-versions/ instead and run /learn-style on it from there.
```

- [ ] **Step 2: Create the learn-style skill**

Create `.claude/skills/learn-style/SKILL.md`:
```markdown
---
name: learn-style
description: Use when the user types /learn-style <file>, says "learn style from <file>", or drops an approved document or a prior version into reference-docs/ or context/prior-versions/ — extracts writing and formatting style from it and stores a durable style-notes file for its matching template.
---

# learn-style

## Overview
Learn writing and formatting conventions from an already-approved document — either a reference document from another project (reference-docs/) or the system's own prior version (context/prior-versions/) — and store the lesson so generate-doc applies it automatically the next time that template is used. This never reads facts from the source document into project context; it studies style only.

## Triggers
- /learn-style <file>
- "learn style from <file>"

## Instructions

1. Locate the file. Look first in reference-docs/, then in context/prior-versions/ (fuzzy match on filename: exact name match first, then case-insensitive substring match). If not found in either, tell the user which folder to drop it into.

2. Determine which template in templates/ this document corresponds to:
   - Try matching by filename similarity against templates/ file stems.
   - Always show the user your best guess and ask them to confirm or correct it before proceeding. Never silently guess — an incorrect match would apply the wrong style to future documents.

3. Read the document's structure and content:
   `python scripts/generate_doc.py <file> --outline`
   For an already-filled document, the returned instruction text under each heading is the real content — read it as such, not as template guidance.

4. From that content, write a style-notes summary covering:
   - Tone (formal/informal, sentence length, voice)
   - How Scope and Out of Scope sections are phrased
   - Whether each section favors tables or prose, and roughly how much of each
   - Citation density and format (how often SOPs/other documents are cited, and the citation phrasing used)
   - How sections that don't apply are handled (omitted, marked "Not applicable", explained)

5. Save the summary to reference-docs/style-notes/<template-stem>.md, where <template-stem> is the matching template's filename without extension. If a style-notes file already exists for this template, overwrite it and note in the output that it replaced a prior version.

6. Print: "Style notes saved: reference-docs/style-notes/<template-stem>.md. generate-doc will use this the next time <template-stem> is generated."

## Rules
Never copy factual content (system names, dates, decisions) from the source document into MASTER_CONTEXT.md or any generated deliverable — this skill extracts style only. Never guess which template a source document matches without user confirmation.
```

- [ ] **Step 3: Verify the new skill file is well-formed**

```bash
python -c "import yaml,pathlib; t=pathlib.Path('.claude/skills/learn-style/SKILL.md').read_text(encoding='utf-8'); fm=t.split('---')[1]; d=yaml.safe_load(fm); assert d['name']=='learn-style'; print(d); print('OK')"
```
Expected: prints the frontmatter dict then `OK`.

- [ ] **Step 4: Commit**

```bash
git add reference-docs/ .claude/skills/learn-style/SKILL.md
git commit -m "feat: add reference-docs/ and the learn-style skill for writing-style learning"
```

---

## Task 7: generate-doc consumes style-notes

**Files:**
- Modify: `.claude/skills/generate-doc/SKILL.md`

**Interfaces:**
- Consumes: `reference-docs/style-notes/<template-stem>.md`, produced by Task 6's learn-style skill.

- [ ] **Step 1: Insert the style-notes check as a new step**

In `.claude/skills/generate-doc/SKILL.md` (as it stands after Task 2), insert a new step between the current step 4 (token discovery) and step 5 (compose content), and renumber all subsequent steps by one:

Replace:
```markdown
5. For each section, read its instruction text and understand what content that section asks for. Then compose the content that satisfies it:
   - Draw the facts from MASTER_CONTEXT.md and the project files.
   - Cite the specific SOP file and section from sops/ where a rule applies. Never invent an SOP name or section number.
   - Apply the language rules from workbench.config.yaml (defaults in CLAUDE.md if the config is absent).
   - The composed content replaces the instruction text. Do not keep the original guidance in the finished section.
   - Where the project does not have the information, write the placeholder marker from the config (default: [CONFIRM: what is needed — ref: owner]) in place of the instruction, rather than guessing.

6. Build a content map as JSON: { "sections": { "<exact heading text>": "<composed content>" }, "tokens": { "<token>": "<resolved value>" } }, covering every section you can fill or mark and every token from step 4. Save it to a temporary file.

7. Produce the filled draft, preserving the template's formatting:
   `python scripts/generate_doc.py <template> --fill <content-map.json>`
   This writes the draft to deliverables/in-progress/ using the naming pattern from the config, replacing each mapped section's instruction text with your content and substituting each resolved token in the headers/footers, leaving any section or token you did not map with its original text. If any header/footer placeholder remains unresolved in the finished draft, this command prints a warning naming it — carry that warning into the final message in step 10.

8. Update DELIVERABLE_STATUS.md: add a row with status "Draft", date, and filename.

9. Run /update-context automatically.

10. Print: "Generated: deliverables/in-progress/<filename>. X sections still need a confirmed value. Review before routing." If step 7 printed a header/footer placeholder warning, include it in this message.
```
with:
```markdown
5. Check for a style guide. Look for reference-docs/style-notes/<template-stem>.md, where <template-stem> is the template's filename without extension. If it exists, read it — you will follow its tone, section-shape, and citation-density guidance in the next step.

6. For each section, read its instruction text and understand what content that section asks for. Then compose the content that satisfies it:
   - Draw the facts from MASTER_CONTEXT.md and the project files.
   - Cite the specific SOP file and section from sops/ where a rule applies. Never invent an SOP name or section number.
   - Apply the language rules from workbench.config.yaml (defaults in CLAUDE.md if the config is absent).
   - Follow the style notes from step 5, if any were found.
   - The composed content replaces the instruction text. Do not keep the original guidance in the finished section.
   - Where the project does not have the information, write the placeholder marker from the config (default: [CONFIRM: what is needed — ref: owner]) in place of the instruction, rather than guessing.

7. Build a content map as JSON: { "sections": { "<exact heading text>": "<composed content>" }, "tokens": { "<token>": "<resolved value>" } }, covering every section you can fill or mark and every token from step 4. Save it to a temporary file.

8. Produce the filled draft, preserving the template's formatting:
   `python scripts/generate_doc.py <template> --fill <content-map.json>`
   This writes the draft to deliverables/in-progress/ using the naming pattern from the config, replacing each mapped section's instruction text with your content and substituting each resolved token in the headers/footers, leaving any section or token you did not map with its original text. If any header/footer placeholder remains unresolved in the finished draft, this command prints a warning naming it — carry that warning into the final message in step 11.

9. Update DELIVERABLE_STATUS.md: add a row with status "Draft", date, and filename.

10. Run /update-context automatically.

11. Print: "Generated: deliverables/in-progress/<filename>. X sections still need a confirmed value. Review before routing." If step 8 printed a header/footer placeholder warning, include it in this message.
```

- [ ] **Step 2: Verify the file is well-formed and steps are sequential**

```bash
python - <<'PY'
import re, pathlib
t = pathlib.Path(".claude/skills/generate-doc/SKILL.md").read_text(encoding="utf-8")
nums = [int(n) for n in re.findall(r"^(\d+)\.\s", t, flags=re.MULTILINE)]
assert nums == list(range(1, 12)), nums
print("OK", nums)
PY
```
Expected: `OK [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/generate-doc/SKILL.md
git commit -m "feat: generate-doc follows learned style notes when composing content"
```

---

## Task 8: Structural-consistency check in gap-check

**Files:**
- Modify: `.claude/skills/gap-check/SKILL.md`

**Interfaces:**
- Consumes: `--compare-structure` from Task 3, `context/prior-versions/` from Task 5.

- [ ] **Step 1: Replace gap-check's Instructions and Rules sections**

Replace the entire `## Instructions` and `## Rules` sections with:

```markdown
## Instructions

1. Find the document in deliverables/ (fuzzy match).

2. Read the document fully.

3. Determine the expected structure for this document, in this order:
   - The template it was generated from in templates/ (match by name or alias in workbench.config.yaml). Use the template's section headings as the required-section list.
   - If no template is found, check sops/ for a procedure that defines the structure for this document, and use that.
   - If neither exists, note that no template or SOP defines the structure, list the sections the document does contain, and ask the user to add a template to templates/ for a complete check.

4. Check for a prior version. Look in context/prior-versions/ for a file matching this document's type (fuzzy match on filename or template stem). If one exists, run:
   `python scripts/generate_doc.py <this-document> --compare-structure context/prior-versions/<matched-file>`
   This returns missing/added headings, table row/column count deltas, font/color-set differences, and whether a table of contents was lost. Fold each finding into the gap report at this severity:
   - CRITICAL — a heading present in the prior version is missing now, or a table of contents was lost
   - MAJOR — a table has fewer rows than the prior version (possible lost data)
   - MINOR — the set of fonts or colors used differs from the prior version
   If no prior version is found for this document type, skip this step.

5. Compare the document against the expected structure. For each missing or incomplete section, flag it:
   - CRITICAL — a required section from the template or SOP is missing
   - MAJOR — section present but incomplete
   - MINOR — wording issue or missing citation

6. Check all content against the language rules in workbench.config.yaml (weak terms, vague terms, open lists, hedges). If the config is absent, use the defaults in CLAUDE.md. Flag each violation with its location.

7. Count remaining placeholders using the marker from the config (default [CONFIRM: ...]) and list each one with its owner.

8. Verify SOP citations point to files actually present in sops/. Flag any citation that cannot be traced to a file.

9. Output the gap report as markdown: | Section | Status | Issue | Severity | Recommendation |

10. End with: "Recommendation: [Ready for review / Not ready — X critical gaps must be resolved first]"

## Rules
A document is not ready for review while any CRITICAL gap or unresolved placeholder remains. A structural regression against a prior version (missing heading, lost table of contents, or reduced table row count) is a CRITICAL or MAJOR finding regardless of how the content reads on a surface pass — never skip step 4 when a prior version is available. Treat any language-rule violation, untraceable citation, or open list as a finding. Do not assume a document type or a required section list — derive both from the template and the SOPs.
```

- [ ] **Step 2: Verify the file is well-formed and steps are sequential**

```bash
python - <<'PY'
import re, pathlib, yaml
t = pathlib.Path(".claude/skills/gap-check/SKILL.md").read_text(encoding="utf-8")
fm = yaml.safe_load(t.split("---")[1])
assert fm["name"] == "gap-check"
nums = [int(n) for n in re.findall(r"^(\d+)\.\s", t, flags=re.MULTILINE)]
assert nums == list(range(1, 11)), nums
print("OK", nums)
PY
```
Expected: `OK [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`.

- [ ] **Step 3: End-to-end smoke test of the full structural-check path**

```bash
python - <<'PY'
import subprocess, sys, shutil
from docx import Document

shutil.copy("templates/CSV TEMPLATE- System Overview.docx", "context/prior-versions/scratch_prior_overview.docx")
shutil.copy("templates/CSV TEMPLATE- System Overview.docx", "scratch_current_overview.docx")
d = Document("scratch_current_overview.docx")
# Simulate structural damage: delete the last table in the body.
if d.tables:
    tbl = d.tables[-1]
    tbl._element.getparent().remove(tbl._element)
d.save("scratch_current_overview.docx")

r = subprocess.run([sys.executable, "scripts/generate_doc.py",
                     "scratch_current_overview.docx",
                     "--compare-structure", "context/prior-versions/scratch_prior_overview.docx"],
                    capture_output=True, text=True)
print(r.stdout)
assert r.returncode == 0, r.stderr
assert "table_count_prior" in r.stdout
print("PASS")
PY
rm -f context/prior-versions/scratch_prior_overview.docx scratch_current_overview.docx
```
Expected: prints a JSON diff whose `table_deltas` includes a `table_count_prior`/`table_count_current` mismatch entry, then `PASS`. This confirms the exact failure mode described in the spec — a document that "looks fine on a surface read" (headings and text intact) but lost a table — is caught.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/gap-check/SKILL.md
git commit -m "feat: add structural-consistency check against a prior version to gap-check"
```

---

## Final check across all tasks

- [ ] **Step 1: Confirm no scratch/test artifacts were left behind**

```bash
git status --short
```
Expected: only the files intentionally modified/created/deleted by Tasks 1-8 appear — no `scratch_*` files, no stray files under `deliverables/in-progress/`.

- [ ] **Step 2: Confirm every skill file in the repo still has valid frontmatter**

```bash
python - <<'PY'
import yaml, pathlib
for f in sorted(pathlib.Path(".claude/skills").glob("*/SKILL.md")):
    t = f.read_text(encoding="utf-8")
    fm = yaml.safe_load(t.split("---")[1])
    assert "name" in fm and "description" in fm, f
print("All skill files OK")
PY
```
Expected: `All skill files OK`.
