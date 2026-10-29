# GxP Validation Kit

## What this repo is
The GxP Validation Kit is a generic Claude Code framework for computer system validation projects. It is not tied to any organization, risk model, or fixed set of documents. A user drops their own document templates into templates/ and their procedures into sops/, builds a living project context from source material, and generates and manages whatever deliverables the project needs through skills. Nothing is hardcoded — the templates define the documents, the SOPs define the rules, and one plain-text config file holds everything else.

## Who it is for
Anyone managing a validation effort, including non-technical validation engineers. No coding is required. After cloning, drop in your templates and (optionally) your SOPs, edit workbench.config.yaml if you want to, and start. You never type terminal commands yourself — you ask in plain language ("build context", "generate a document", "show me the dashboard") and the assistant runs the tools for you.

## Important — this is a template, use it locally
Clone this repository once per project and work in your local copy. Do not push a filled clone back to this shared repository, and never make a clone that contains real SOPs, project documents, or deliverables public. The repository is configured so that files you drop into sops/, context/, and deliverables/in-progress/ are ignored by git and will not be committed by accident.

## Folder structure
| Path | Purpose |
|------|---------|
| workbench.config.yaml | Central config. Everything project- or organization-specific lives here. Plain text, no coding. |
| context/ | Drop zone for any project file (docs, emails, notes, decisions). Never edited manually. |
| context/meeting-notes/ | Raw meeting notes; processed by /meeting-notes. |
| context/decisions/ | Structured decision extracts written by /meeting-notes. |
| context/dev-inputs/ | Dev team confirmations and extracted requirement drafts. |
| context/project-docs/ | Charters, BRDs, architecture docs, and other source material. |
| context/prior-versions/ | A prior version of the system's own document(s) — used as project knowledge (tagged with its source version), a style reference (/learn-style), and a structural-consistency baseline (/gap-check). |
| templates/ | Your document templates. They define what each deliverable looks like. Read-only — never modified. |
| deliverables/in-progress/ | Active generated drafts awaiting review. |
| deliverables/approved/ | Signed-off deliverables only, moved by /approve-doc. Versioned in git. Also a core source of project context: /build-context and /update-context read these documents (facts tagged with document and version), and /upgrade-doc and /upgrade-release start from them. Never modified by any skill. |
| sops/ | The SOPs you upload, whatever your organization uses. Read-only reference for citations. |
| reference-docs/ | Approved documents from other projects/systems, dropped here purely to learn writing and formatting style via /learn-style. Read-only — never modified. reference-docs/style-notes/ holds learned style; reference-docs/review-lessons/ holds lessons from reviewer comments (/learn-comments). |
| scripts/ | Python helpers for context building, document generation, release revision, review-comment extraction, and status checks. See "Scripts reference" below. |
| data/ | The project_data.py template copied per project to track pending confirmations. |
| projects/ | One subfolder per project for multi-project use. |
| audit/ | Append-only activity ledger written automatically after each skill run. |
| GLOSSARY.md | Plain-language definitions of every term. Looked up by /define. |
| setup.ps1 / setup.sh | One-step install of the Python packages. |
| .claude/skills/ | The 30 workbench skills. |
| .claude/settings.json | Permissions and hooks: the activity-ledger hook (after every skill) and the context-freshness hook (at session start). |

## Setup

### Quickest path — in your browser (Codespaces)
1. On GitHub, click "Code" → "Codespaces" → "Create codespace on main". Wait for it to finish building — it installs the Python packages and the Claude Code CLI for you.
2. In the terminal at the bottom, type `claude` and press Enter to start Claude Code. Sign in when prompted (first time only).
3. Inside Claude Code, type `/start`.

Note: `/start` and the other `/` commands are Claude Code commands, not terminal commands. They only work after you have launched `claude`. If you type `/start` straight into the terminal you will get "command not found".

### On your own computer
1. Install Claude Code, Python 3.10+, and Git.
2. Clone or copy this repo.
3. Run the one-step setup: Windows `./setup.ps1`, or Mac/Linux `bash setup.sh`. This installs python-docx, pypdf, openpyxl, and PyYAML.
4. Open the folder in Claude Code and type /start.

### First-time use
1. Type /start and follow the single next step it gives you.
2. Drop project source files into the relevant context/ subfolder (each folder has a README explaining what goes where).
3. Say "build context" to summarize them into MASTER_CONTEXT.md.
4. Review the summary and correct anything wrong.

### Configure (optional)
Open workbench.config.yaml and set your organization name, the deliverables you produce, language rules, and naming conventions. Every field is optional with a safe default — you can ignore this file entirely and the framework still works.

### Add templates
Drop your Word document templates into templates/. These define the deliverables. /generate-doc works off whatever templates are present — there is no fixed list of document types. Optionally give each template a short alias in workbench.config.yaml.

### Add SOPs
Drop your SOP PDFs or Word files into sops/. Once present, every skill cites the specific SOP and section instead of flagging it as missing.

## Skills reference

### Core workflow
| Skill | Command | When to use |
|-------|---------|-------------|
| start | `/start` | The guided front door. Tells you the single next step in plain language. |
| define | `/define <term>` | Explains any validation term in plain language from the glossary. |
| build-context | `/build-context` | Build MASTER_CONTEXT.md from scratch from all files in context/ and all approved documents in deliverables/approved/. Detects contradictions across source files before writing. |
| update-context | `/update-context` | Incrementally refresh MASTER_CONTEXT.md from new or changed context files. Also runs automatically at session start when the last refresh is over 24 hours old. |
| new-project | `/new-project` | Scaffold a new validation project under projects/. |

### Document generation
| Skill | Command | When to use |
|-------|---------|-------------|
| generate-doc | `/generate-doc <template>` | Generate any deliverable from a template in templates/. No fixed document types. |
| approve-doc | `/approve-doc <filename>` | Move a deliverable to approved/ and update status. |
| version-doc | `/version-doc <filename>` | Create a new draft version from an approved document. Increments version number, carries forward content, inserts [CONFIRM] in changed sections. For Word documents moving to a new release, prefer /upgrade-doc. |
| review-response | `/review-response <filename>` | Turn reviewer comments into a structured response table with dispositions. |
| diff-doc | `/diff-doc <file-a> <file-b>` | Compare two document versions section by section. Shows Added / Removed / Modified / Unchanged with before-and-after quotes. |
| learn-style | `/learn-style <file>` | Learn writing/formatting style from an approved document in reference-docs/ or context/prior-versions/ for a matching template. |
| upgrade-doc | `/upgrade-doc <doc> <new-version>` | Move ONE approved Word document to a new release: reads project context and context/ files, asks what else is needed, adds the new content without removing or rewording anything approved, updates the revision history, and verifies the approved content is intact. |
| upgrade-release | `/upgrade-release <new-version>` | Do the same for EVERY approved document in one pass: gather release inputs once, ask once, show one release plan, then upgrade each document and check consistency across the set. |
| learn-comments | `/learn-comments <file>` | Read the reviewer comments on a document, keep the accepted ones as reusable lessons, and apply them in future /generate-doc and /gap-check runs for the same template. |

### Requirements and traceability
| Skill | Command | When to use |
|-------|---------|-------------|
| extract-requirements | `/extract-requirements <filename>` | Turn a source document into ALM-ready acceptance criteria. |
| validate-requirement | `/validate-requirement` | Check a single requirement for GxP testability and ALM compliance. Read-only. |
| write-test-case | `/write-test-case <requirement-id>` | Generate a formal GxP test case from a requirement. |
| traceability | `/traceability` | Generate or update the Requirements Traceability Matrix with coverage. |
| export-alm | `/export-alm <filename>` | Format approved requirements as a CSV for ALM import, or push directly via REST if alm_integration is configured. |

### Quality and compliance
| Skill | Command | When to use |
|-------|---------|-------------|
| gap-check | `/gap-check <doc>` | Check a deliverable against SOPs and GxP rules before routing. |
| ask-sop | `/ask-sop <question>` | Answer a GxP/process/compliance question with SOP citations. |
| sop-check | `/sop-check` | Audit all SOPs in sops/ for missing version/date metadata and staleness. |
| change-control | `/change-control` | Generate a change control impact assessment for a validated system. |
| write-svr | `/write-svr` | Generate the System Validation Report closeout document. |

### Project tracking
| Skill | Command | When to use |
|-------|---------|-------------|
| check-status | `/check-status` | Show full status of deliverables, open items, and pending confirmations. |
| dashboard | `/dashboard` | Build a visual HTML status page with action prompts to open in a browser. |
| meeting-notes | `/meeting-notes <filename>` | Extract decisions, actions, and confirmations from meeting notes. Links blocking actions to deliverables in DELIVERABLE_STATUS.md automatically. |
| confirm-item | `/confirm-item <ID> "<value>"` | Resolve a single pending dev-team confirmation in project_data.py and context. |
| bulk-confirm | `/bulk-confirm` | Resolve multiple [CONFIRM] items at once from a CSV file or inline ID=value list. |
| audit-log | `/audit-log` | View the append-only activity ledger. Supports filtering by skill and a --summary mode. |

## Typical workflow — new project
1. Drop charter, BRD, and architecture docs into context/project-docs/.
2. Run /build-context to create MASTER_CONTEXT.md.
3. Run /extract-requirements on the BRD to produce ALM-ready criteria.
4. Add your templates to templates/ and SOPs to sops/.
5. Run /generate-doc vtp, then /generate-doc ds, then /generate-doc so.
6. Run /gap-check on each draft before routing for review.
7. After sign-off, run /approve-doc to move each deliverable to approved/.

## Typical workflow — existing project mid-validation
1. Drop the latest meeting notes into context/meeting-notes/ and run /meeting-notes.
2. Run /update-context to refresh project state.
3. Run /check-status to see what is open, pending, and unprocessed.
4. Resolve placeholders as dev team confirmations arrive (drop into context/dev-inputs/).
5. Regenerate or gap-check affected deliverables.
6. Approve completed deliverables with /approve-doc.

## Typical workflow — new release of an already-validated system
Use this when the system is already validated (release 1.0, every document approved) and you are moving it to release 2.0.

One-time setup:
1. Copy the approved Word documents into deliverables/approved/. Put the version in each filename (for example `LCDA_Validation_Plan_v1.0.docx`); the skills read the current version from the name.
2. Put your SOPs in sops/ so new text can cite them. Put your templates in templates/ if you want /gap-check, learned style, and review lessons applied.
3. Put everything about the new release in context/: change control assessments in context/decisions/, release notes and design inputs in context/dev-inputs/ and context/project-docs/, meeting notes in context/meeting-notes/.

Then, for each release:
1. Run /build-context (first time) or /update-context. Project context is built from the approved documents plus the new files in context/.
2. Run /upgrade-release 2.0 to upgrade every approved document, or /upgrade-doc <document> 2.0 for one.
3. The skill shows the release files it read, what it derived from them, and what is still missing, and asks whether anything else is needed. Answer, or drop more files into context/.
4. The skill shows a table of what it will leave untouched, add to, or flag as a conflict. Approve it.
5. Open the drafts in deliverables/in-progress/. Resolve the [CONFIRM] placeholders, decide each conflict listed in context/decisions/, run /gap-check, and clear the yellow highlighting on new text.
6. Route for review. Turn reviewer comments into lessons with /review-response then /learn-comments. After sign-off, run /approve-doc.

## GxP compliance notes
The framework enforces the following automatically:
- ALM-clean acceptance criteria — rejects "e.g.", "such as", "where applicable", "including but not limited to", and vague terms such as "appropriate" or "sufficient".
- Closed lists in place of open-ended lists.
- Every testable requirement names a specific mechanism, value, threshold, or SOP reference.
- ALCOA+ framing on data integrity content.
- Deliverable scope driven by the templates you provide and the deliverables you select — never by a built-in risk model.
- SOP citation on every requirement, criterion, and section, or an explicit flag naming the SOP to add.
- Unconfirmed information surfaced as yellow placeholders in the format [CONFIRM: description — ref: owner].

## What NOT to commit
- .env files and any environment files (already ignored)
- Credentials, tokens, API keys, connection strings
- Personal data or patient data
- Anything outside the GxP record scope of this validation

## Advanced Features

### Multi-project support
Use /new-project to scaffold a new validation project under projects/<SystemName>/. Templates and SOPs in templates/ and sops/ are shared across all projects.

### GitHub Actions
Four automated workflows are included:
- Weekly status report: runs every Monday, commits STATUS_REPORT.md
- Gap check notification: triggers when deliverables/in-progress/ or sops/ changes, reminds engineer to run /gap-check and /sop-check before routing
- SOP change notification: posts a step summary whenever a file in sops/ is pushed, reminding the team to re-run /sop-check and /gap-check on affected deliverables
- Context validation: PR check that fails if MASTER_CONTEXT.md is unpopulated

### Traceability
Use /traceability to generate an RTM linking requirements to test cases. Coverage percentage is calculated automatically and compared against coverage_target_percent in workbench.config.yaml (a configurable target, default 100, set to 0 to disable).

### Confirmation tracking
project_data.py (one per project under projects/) tracks every pending dev-team confirmation with an ID, owner, and blocking document. Use /confirm-item to resolve items one by one, or /bulk-confirm to resolve multiple items at once from a CSV or inline ID=value list. Context and affected deliverables update automatically.

### Conflict detection in context building
/build-context now checks for contradictions across all source files before writing MASTER_CONTEXT.md. If two files disagree on system name, go-live date, or owner names, the conflicting values are flagged with [CONFIRM] placeholders and printed as a conflict list. This prevents silent inconsistencies from carrying forward into generated deliverables.

### Guided assistant for non-technical users
Type /start at any time. The assistant inspects the current state and tells you the single next step in plain language. /define explains any term, backed by GLOSSARY.md. Plain phrases ("build context", "check gaps") work everywhere slash commands do.

### Visual dashboard with action prompts
Say "show me the dashboard" (or /dashboard) and the assistant builds status.html for you — a browser view of deliverables, open items, coverage, the next step, and a row of plain-language action prompts. Click any prompt text and type it into the assistant to take the next action. Technical users can also run `python scripts/dashboard.py` directly.

### Meeting notes linked to deliverables
/meeting-notes now links every extracted blocking action item to the relevant deliverable in DELIVERABLE_STATUS.md. Each entry is written in the format `ACTION [date]: [owner] — description` so /check-status can surface the link and the engineer knows which document is waiting.

### Activity ledger
Every skill run is recorded automatically to audit/ledger.jsonl (timestamp, skill, session) by a PostToolUse hook. Use /audit-log to read the ledger, filter by skill, or get a summary. This append-only log is a ready-made activity trail. It is git-ignored by default; remove the line in .gitignore to retain it under version control.

### Automatic daily context refresh
When a session starts, a SessionStart hook (scripts/context_freshness.py) checks when MASTER_CONTEXT.md was last refreshed. The last refresh time is the most recent /update-context or /build-context entry in audit/ledger.jsonl, or the file's modification time if the ledger has none. If that was more than 24 hours ago and files in context/ or deliverables/approved/ have changed since, the assistant runs /update-context before doing anything else. If nothing has changed, nothing happens. Set the interval or turn it off with context_refresh (enabled, interval_hours) in workbench.config.yaml. The check runs when you open a session, not on a background timer, and it never blocks a session from starting.

### Release upgrades without touching approved content
/upgrade-doc (one document) and /upgrade-release (all approved documents) take your approved Word documents to the next release (for example 1.0 to 2.0) without touching anything that was approved.

- **Project knowledge.** Approved documents are a core source of project context: /build-context and /update-context read them, tagging each fact with its document and version (for example "per approved Validation Plan v1.0"). A newer file in context/ that changes an approved fact is recorded as a release change, not as a conflict.
- **Release inputs.** Before writing, the skill reads the release files in context/, shows the files read, the changes it derived (each with its source), and what is missing (change reference number, reviser, affected sections the files do not describe), and asks whether anything else is needed. It does not continue until you answer.
- **Decision table.** For every section it proposes: leave untouched (the default), add, or conflict. You approve the table before anything is written.
- **Additive drafts.** The approved file is copied to deliverables/in-progress/ with the new version in the filename and in the header, footer, and cover. New paragraphs are added at the end of the affected sections in that section's formatting and highlighted yellow so reviewers can find them. Missing facts become [CONFIRM] placeholders.
- **Revision history.** A row is added to the document's revision history table (the table with Version and Summary of Changes columns). Reviser and change reference become placeholders if you have not supplied them.
- **Verification.** scripts/revise_doc.py compares the draft with the approved file and fails if any approved paragraph or table cell was removed, reworded, or reordered, or if a revision history row was lost. A draft that fails is not registered or offered.
- **Conflicts.** If an approved statement is no longer true in the new release, it is never edited. It is written to context/decisions/ with the quoted statement, the reason, and proposed wording, for your decision.
- **Whole release.** /upgrade-release gathers the inputs once, asks once, shows one release plan, upgrades each document, and then checks that a fact added to one document is carried into related ones.

Limits: Word (.docx) files only. A new section cannot be created, because the approved document defines its sections; it is listed for you instead. The version label is updated only in headers, footers, and the first 15 body paragraphs; other mentions of the old version are reported and left alone. Sections are found by Word heading styles.

### Learning from review comments
/learn-comments reads the reviewer comments on a Word document (scripts/extract_comments.py: author, comment text, the text it is attached to, resolved status, and replies), keeps only the comments accepted in a /review-response table, and stores them as reusable lessons in reference-docs/review-lessons/ — one file per template, plus _general.md for lessons that apply to every document. You confirm the template match before anything is saved. Each lesson has an ID, the section it applies to, a category (Editorial, Technical, or Compliance), a seen-count, and its sources; a repeated lesson is merged and its count raised. /generate-doc applies the matching lessons when it writes the next document from that template and lists the IDs it used, and /gap-check flags a document that breaks one. Lessons never contain project facts or reviewer names. The folder is git-ignored by default.

### Scripts reference
| Script | Used by | What it does |
|--------|---------|--------------|
| generate_doc.py | /generate-doc, /gap-check, /build-context, /learn-style | Reads a template or document section by section (`--outline`), fills it (`--fill`), lists header/footer tokens, compares structure to a prior version. |
| revise_doc.py | /upgrade-doc, /upgrade-release | `init` creates the new-version draft, `add` appends new paragraphs to sections, `revlog` adds the revision history row, `verify` proves approved content is unchanged. |
| extract_comments.py | /learn-comments | Lists every Word comment with its anchored text, resolved status, and replies. Python standard library only. |
| context_freshness.py | SessionStart hook | Decides whether the automatic context refresh is due. |
| append_ledger.py | PostToolUse hook | Appends each skill run to audit/ledger.jsonl. |
| check_status.py, dashboard.py, check_config.py | /check-status, /dashboard, "check my settings" | Status reporting, the HTML dashboard, and config validation. |

### ALM REST integration
/export-alm writes a CSV for manual import into any ALM tool by default. To push directly via REST, set alm_integration.enabled: true in workbench.config.yaml and fill in tool_url, project_key, and auth_env_var (the name of an environment variable that holds your API token — never put the token in the config). The skill reads the token from that variable, shows the payload, and asks for explicit confirmation before sending. The token is never stored, logged, or printed.

### Configuration safety net
If you change workbench.config.yaml, say "check my settings" and the assistant validates it with friendly, line-level messages before they affect generation. Technical users can run `python scripts/check_config.py` directly.

### Document engine
scripts/generate_doc.py reads a template section by section. `--outline` extracts each section's heading and its instruction text; the generate-doc skill composes the content that satisfies each instruction from your project context and SOPs; `--fill` then replaces the instruction text with that content, inserting a [CONFIRM] marker wherever a value is not yet known and preserving the template's headings and formatting.
