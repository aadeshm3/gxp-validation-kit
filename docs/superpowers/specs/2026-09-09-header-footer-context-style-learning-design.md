# Design: header/footer fill, template-driven context, style learning, prior-version checks

Date: 2026-09-09
Status: Approved by user, ready for implementation planning.

## Scope

Four independent fixes/features to the GxP validation-workbench framework:

1. Fill header/footer placeholders in generated documents (bug fix).
2. Derive MASTER_CONTEXT.md's section list from templates present, with a generic fallback (bug fix).
3. Reference-docs mechanism: learn writing/formatting style from an approved document of the same deliverable type (new).
4. Older-version-doc mechanism: learn project knowledge and style from a system's own prior document version, plus a structural-consistency check (new).

Each issue is independently shippable; implementation may be phased accordingly.

---

## Issue 1 — Header/footer placeholders never get filled

### Root cause

[scripts/generate_doc.py](../../../scripts/generate_doc.py) fills documents in two passes — `extract_outline_docx()` (line 202) walks `doc.paragraphs` to find the section outline, and `fill_docx()` (line 257) walks `doc.paragraphs` again to replace each section's instruction text, keyed by heading. Neither function, nor anything else in the file, ever reads `doc.sections[i].header` or `.footer`. A grep of the whole script confirms zero references to `.sections`, `.header`, or `.footer` as python-docx objects.

Verified against real templates (unzipping `word/header*.xml`): System Overview, Business Continuity Plan, Configuration Specification, Data Migration Plan/Report, Backup and Restoration SOP, and Design Specification all carry angle-bracket tokens — `<System Name>`, `<System/Platform Name>`, `<System>`, `<CI###########>` — embedded **inline within static header text**, e.g.:

```
<System Name> System Overview Configuration Item (CI): <CI###########>
```

This is structurally different from body sections, which are whole-paragraph replacements keyed by a heading. A header paragraph mixes static text and placeholder tokens in the same run(s), so the fix must do in-place token substitution, not paragraph replacement — and must not touch anything else in the paragraph (including literal "Page X of Y" text and PAGE/NUMPAGES field codes, which live in the footer alongside these headers in the same templates).

### Design

- **`extract_placeholder_tokens(doc)`** (new) — regex-scans `<[^<>\n]{1,80}>` across every section's header and footer paragraphs (including any tables inside them), for all of `header`, `footer`, `first_page_header/footer`, and `even_page_header/footer`. Dedupe by `id()` of the header/footer part so a header shared via `is_linked_to_previous` isn't processed twice. Returns a sorted, deduplicated list of token strings (e.g. `["<CI###########>", "<System Name>"]`).
- New CLI flag **`--tokens`**, printing that list as JSON — mirrors the existing `--outline` flag, and is additive (doesn't change `--outline`'s existing output shape, so nothing else that might parse it breaks).
- **`_replace_tokens_in_paragraph(paragraph, token_map)`** (new) — joins the paragraph's run texts, does a literal substring substitution only for tokens present in `token_map`, and — only if a substitution actually occurred — rewrites the paragraph the same run-preserving way `_set_paragraph_text()` already does (first run gets the new text, remaining runs blanked). Paragraphs with no bracket-token match are left byte-for-byte untouched, which is what protects page-number fields and any other legitimate footer content: they're never bracket tokens, so they never match.
- **`fill_header_footer_tokens(doc, token_map)`** (new) — iterates all sections' header/footer variants (same dedup rule as above) and calls the paragraph-level helper on every paragraph and every table cell's paragraphs within them.
- **`fill_docx()`** calls `fill_header_footer_tokens(doc, token_map)` after the existing body-fill loop, before `doc.save()`.
- **`--fill` JSON schema**: extended to accept `{"sections": {heading: content}, "tokens": {token: value}}`. For backward compatibility, if the parsed JSON has neither a `"sections"` nor a `"tokens"` key, treat the whole object as the old flat `{heading: content}` shape (current behavior, unchanged).

### Skill changes — `.claude/skills/generate-doc/SKILL.md`

- New step after today's step 3 (get outline): run `--tokens` on the template; resolve each token from `MASTER_CONTEXT.md` / `project_metadata_fields` in workbench.config.yaml (e.g. `<System Name>` → the System Name field); where no value is known, use the configured placeholder marker as that token's value rather than leaving it as-is.
- Step 5 (build content map): also build a `tokens` map; step 6's `--fill` call passes the combined `{"sections": ..., "tokens": ...}` JSON.
- **New self-review step** (none exists today — confirmed: the skill's only "review" language is the final print statement telling the *user* to review): immediately after `--fill`, run `--tokens` again against the *produced draft* (not the template). If any token still appears, append to the final status line: `"Warning: header/footer placeholder(s) remain unresolved: <list> — add the missing field to workbench.config.yaml or resolve manually."` This is a warning, not a block — generation still completes and the draft is still written (per user decision).

### Testing

- Unit-level: run `--tokens` against each affected real template in templates/ and confirm the exact tokens found match what was verified above (System Name, CI number tokens).
- Fill a template end-to-end with a token map and confirm: (a) header/footer text no longer contains `<...>` tokens, (b) footer page-number field/text is byte-identical before and after, (c) body fill behavior is unchanged.
- Run the new self-review pass against a draft with a deliberately incomplete token map and confirm the warning fires with the correct token list.

---

## Issue 2 — MASTER_CONTEXT.md should be built from templates present

### Root cause

Two disconnected hardcoded section lists exist, neither derived from templates/:

1. Prose in [.claude/skills/build-context/SKILL.md](../../../.claude/skills/build-context/SKILL.md), step 6 (lines 59-70) — a fixed 10-section list.
2. A full standalone reimplementation in `scripts/build_context.py::build_document()` (lines 133-191) rendering the same 10 sections with hardcoded table schemas. This script is **not invoked by any skill** (confirmed by repo-wide grep) and its own docstring references a nonexistent `scripts/update_context.py` — it is orphaned/legacy.

This directly contradicts workbench.config.yaml's own stated design philosophy ("Nothing is hardcoded inside the skills"). The live MASTER_CONTEXT.md for the current project has already organically grown to 15 numbered sections, confirming the fixed 10-section shape doesn't match how the framework is actually used.

Reusable extraction logic already exists and is generic: `extract_outline()` / `extract_outline_docx()` / `extract_outline_md()` in scripts/generate_doc.py (lines 184-225), already exposed via `--outline`.

### Design

- **Delete `scripts/build_context.py`** — dead code, not invoked anywhere, references a file that doesn't exist. (Flagged for explicit confirmation before deletion, since it's a file removal.)
- **In-scope templates**: read the `deliverables:` alias list in workbench.config.yaml. If non-empty, that list (mapped to files in templates/) is the in-scope set. If empty, fall back to every file present in templates/.
- **Per-template section discovery**: for each in-scope template, run `python scripts/generate_doc.py <template> --outline` (already works today, no script change needed) and use the returned heading list as that document type's candidate sections.
- **Shared front-matter merge**: headings matching a small set of common synonyms (Purpose, Scope, Out of Scope, Reviewers/Approvers, Revision History, Stakeholders) are folded into a single shared MASTER_CONTEXT section instead of being repeated once per template.
- **Document-specific headings** (e.g. "Backup Schedule" from the Backup and Restoration SOP template) become a subsection grouped under that document type, not merged.
- **Fixed bookkeeping scaffold** (kept regardless of templates, since this is the framework's own project-tracking structure, not deliverable content): Header/metadata, Open Items & Pending Confirmations, Key Decisions Made, Timeline, Key Files & Scripts, Pending Work.
- **Fallback when templates/ has no usable templates and the config's deliverables list is empty**: use a standard generic structure suitable for any validation project — System Overview, Stakeholders, Architecture, Requirements, Open Items, Decisions, Timeline, Pending Work. This becomes the explicit, documented fallback (today's hardcoded list is repurposed as this fallback, not the default path).
- Conflict-detection (existing step 5 in build-context/SKILL.md) is unchanged — it operates the same way regardless of where the section list comes from.
- `update-context/SKILL.md`'s incremental logic is updated to match: when merging in new/changed context files, section placement follows the same template-derived shape rather than assuming the old fixed list.

### Testing

- With templates/ populated (current repo state — 38 templates) and workbench.config.yaml's `deliverables:` list empty: confirm MASTER_CONTEXT.md is built from all templates' outlines with shared sections merged.
- With `deliverables:` populated with a handful of aliases: confirm only those templates drive the section list.
- With templates/ emptied (simulated) and `deliverables:` empty: confirm the generic 8-section fallback is produced, not an empty or missing file.

---

## Issue 3 — Reference-docs mechanism for style learning

### Design

- **New folder**: `reference-docs/` (sibling to templates/, sops/, context/), for dropping an approved document of the same deliverable type from a different project, purely to learn writing/formatting style. Include a `reference-docs/README.md` explaining the purpose, matching the convention already used by templates/README.md and sops/README.md.
- **New skill**: `.claude/skills/learn-style/SKILL.md`.
  - Triggers: `/learn-style <file>`, "learn style from <file>".
  - Instructions:
    1. Locate the file in reference-docs/ (fuzzy match, same convention as `resolve_template()` in generate_doc.py).
    2. Determine which template in templates/ it corresponds to — ask the user to confirm the match rather than guessing silently (a wrong match would corrupt future generations of an unrelated document type).
    3. Extract the document's outline and per-section text via `extract_outline_docx()` (reused as-is — for an already-filled document, the "instruction" field it returns is simply the real filled content).
    4. Write a style-notes summary (a judgment task performed by Claude reading the content, not a mechanical script step) covering: tone, how scope/out-of-scope sections read, table-vs-prose ratio per section, citation density and format, and how not-applicable sections are phrased.
    5. Save durably to `reference-docs/style-notes/<template-stem>.md` — one file per template, so it survives across sessions and projects.
    6. Print confirmation naming the file written.
  - Rule: reference-docs content is a style source only — never treated as a project fact, and never merged into MASTER_CONTEXT.
- **generate-doc/SKILL.md** gets one new instruction in its composition step: before composing content for a template, check for `reference-docs/style-notes/<template-stem>.md`; if present, follow its tone, section-shape, and citation-density guidance when writing.

### Testing

- Drop a sample filled .docx into reference-docs/, run `/learn-style`, confirm a style-notes file is written and its content plausibly reflects the sample's tone/structure.
- Generate a document using a template with a matching style-notes file and confirm the skill's instructions reference it (behavioral check, since actual content quality is a judgment call for the skill run, not a unit test).

---

## Issue 4 — Older-version-doc mechanism

### Design

- **New folder**: `context/prior-versions/` — a fifth subfolder alongside the existing `decisions/`, `dev-inputs/`, `meeting-notes/`, `project-docs/`, for dropping a prior version of the system's own document (not necessarily the current draft's direct predecessor).
- **Project-knowledge use**: add `prior-versions/` to the Glob patterns already used by build-context (step 2) and update-context — no new extraction logic, since the existing field list (system name, stakeholders, architecture decisions, open items, timeline, approved decisions, etc.) already applies. New rule added to build-context step 4: facts sourced from `context/prior-versions/` are tagged with provenance, e.g. "per prior version (v1.0)", rather than presented as current fact, since the source document may be stale.
- **Style-learning use**: the same `/learn-style` skill from Issue 3, extended to also accept a file path under `context/prior-versions/` (not just reference-docs/) — writes to the same `reference-docs/style-notes/<template-stem>.md` destination. No duplicate mechanism.
- **Structural-consistency check → extends gap-check** (chosen over diff-doc or a new skill, since gap-check already performs QA on a deliverable and this is another QA dimension):
  - New function **`extract_structure_docx(path)`** in generate_doc.py — a deterministic structural fingerprint: heading list + levels (reuses `extract_outline_docx`'s heading detection), table count and per-table `{row_count, col_count}`, the set of font names/sizes actually used across all runs, highlight/theme colors used, and whether a TOC field (`TOC \o` field code) is present in the body XML.
  - New CLI flag **`--structure`** — prints that fingerprint as JSON.
  - New CLI flag **`--compare-structure <prior>`** — computes both fingerprints and prints a diff: missing/added headings, table row/column count deltas, font/color set differences, and TOC gained/lost.
  - **gap-check/SKILL.md** gets a new step (after step 3, "determine expected structure"): if a matching prior version exists in `context/prior-versions/` for this document type, run `--compare-structure` and fold the results into the existing gap report. Severity mapping: a missing heading or lost TOC is **CRITICAL**; a reduced table row count is **MAJOR** (possible lost data); a font/color-set difference is **MINOR**.
  - gap-check's Rules section gains one line: a structural regression against a prior version is a finding regardless of how the content reads on a surface pass.

### Testing

- Drop a prior version of a real deliverable into context/prior-versions/, run /build-context, confirm its facts appear with provenance tags.
- Run `/learn-style` against a file in context/prior-versions/ and confirm it writes the same style-notes destination as Issue 3.
- Deliberately strip a table row / remove a TOC field from a copy of a document and run the structural comparison against the original; confirm the regression is flagged at the expected severity.

---

## Open implementation notes

- `scripts/build_context.py` deletion (Issue 2) will be called out explicitly again at implementation time given it's a file removal, even though it's confirmed dead code.
- Backward compatibility for the `--fill` JSON schema change (Issue 1) must be verified against any existing saved content-map JSON files in the repo, if any are found during implementation.
- Both new folders (`reference-docs/`, `context/prior-versions/`) need `.gitkeep` and a README following the existing templates/README.md and sops/README.md conventions.
