# GxP Validation Kit

## What this repo is
The GxP Validation Kit is a generic Claude Code framework for computer system validation projects. It is not tied to any organization, risk model, or fixed set of documents. A user drops their own document templates into templates/ and their procedures into sops/, builds a living project context from source material, and generates and manages whatever deliverables the project needs through skills. Nothing is hardcoded — the templates define the documents, the SOPs define the rules, and one plain-text config file holds everything else.

## Who it is for
Anyone managing a validation effort, including non-technical validation engineers. No coding is required. After cloning, drop in your templates and (optionally) your SOPs, edit workbench.config.yaml if you want to, and start running skills.

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
| templates/ | Your document templates. They define what each deliverable looks like. Read-only — never modified. |
| deliverables/in-progress/ | Active generated drafts awaiting review. |
| deliverables/approved/ | Signed-off deliverables only, moved by /approve-doc. Versioned in git. |
| sops/ | The SOPs you upload, whatever your organization uses. Read-only reference for citations. |
| scripts/ | Python helpers for context building, document generation, and status checks. |
| data/ | The project_data.py template copied per project to track pending confirmations. |
| projects/ | One subfolder per project for multi-project use. |
| audit/ | Append-only activity ledger written automatically after each skill run. |
| GLOSSARY.md | Plain-language definitions of every term. Looked up by /define. |
| setup.ps1 / setup.sh | One-step install of the Python packages. |
| .claude/skills/ | The 20 workbench skills. |

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
| Skill | Command | When to use |
|-------|---------|-------------|
| start | `/start` | The guided front door. Tells you the single next step in plain language. |
| define | `/define <term>` | Explains any validation term in plain language from the glossary. |
| build-context | `/build-context` | Build MASTER_CONTEXT.md from scratch from all files in context/. |
| update-context | `/update-context` | Incrementally refresh MASTER_CONTEXT.md from new or changed context files. |
| generate-doc | `/generate-doc <template>` | Generate any deliverable from a template in templates/. No fixed document types. |
| approve-doc | `/approve-doc <filename>` | Move a deliverable to approved/ and update status. |
| ask-sop | `/ask-sop <question>` | Answer a GxP/process/compliance question with SOP citations. |
| extract-requirements | `/extract-requirements <filename>` | Turn a source document into ALM-ready acceptance criteria. |
| write-test-case | `/write-test-case <requirement-id>` | Generate a formal GxP test case from a requirement. |
| gap-check | `/gap-check <doc>` | Check a deliverable against SOPs and GxP rules before routing. |
| meeting-notes | `/meeting-notes <filename>` | Extract decisions, actions, and confirmations from meeting notes. |
| check-status | `/check-status` | Show full status of deliverables, open items, and pending confirmations. |
| new-project | `/new-project` | Scaffold a new validation project under projects/. |
| confirm-item | `/confirm-item <ID> "<value>"` | Resolve a pending dev-team confirmation in project_data.py and context. |
| traceability | `/traceability` | Generate or update the Requirements Traceability Matrix with coverage. |
| write-svr | `/write-svr` | Generate the System Validation Report closeout document. |
| validate-requirement | `/validate-requirement` | Check a single requirement for GxP testability and ALM compliance. Read-only. |
| change-control | `/change-control` | Generate a change control impact assessment for a validated system. |
| review-response | `/review-response <filename>` | Turn reviewer comments into a structured response table with dispositions. |
| export-alm | `/export-alm <filename>` | Format approved requirements as a CSV for import into any ALM tool. |

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
Three automated workflows are included:
- Weekly status report: runs every Monday, commits STATUS_REPORT.md
- Gap check notification: triggers when deliverables/in-progress/ changes, reminds engineer to run /gap-check before routing
- Context validation: PR check that fails if MASTER_CONTEXT.md is unpopulated

### Traceability
Use /traceability to generate an RTM linking requirements to test cases. Coverage percentage is calculated automatically and compared against coverage_target_percent in workbench.config.yaml (a configurable target, default 100, set to 0 to disable).

### Confirmation tracking
project_data.py (one per project under projects/) tracks every pending dev-team confirmation with an ID, owner, and blocking document. Use /confirm-item to resolve items one by one. Context and affected deliverables update automatically.

### Guided assistant for non-technical users
Type /start at any time. The assistant inspects the current state and tells you the single next step in plain language. /define explains any term, backed by GLOSSARY.md. Plain phrases ("build context", "check gaps") work everywhere slash commands do.

### Visual dashboard
Run `python scripts/dashboard.py` to produce status.html — a browser view of deliverables, open items, coverage, and the recommended next step.

### Activity ledger
Every skill run is recorded automatically to audit/ledger.jsonl (timestamp, skill, session) by a PostToolUse hook. This append-only log is a ready-made activity trail. It is git-ignored by default; remove the line in .gitignore to retain it under version control.

### Configuration safety net
Edit workbench.config.yaml in plain text, then run `python scripts/check_config.py` to catch mistakes with friendly, line-level messages before they affect generation.

### Document engine
scripts/generate_doc.py reads a template section by section. `--outline` extracts each section's heading and its instruction text; the generate-doc skill composes the content that satisfies each instruction from your project context and SOPs; `--fill` then replaces the instruction text with that content, inserting a [CONFIRM] marker wherever a value is not yet known and preserving the template's headings and formatting.
