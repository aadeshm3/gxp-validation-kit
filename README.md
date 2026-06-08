# Validation AI Workbench

## What this repo is
The Validation AI Workbench is a GxP-compliant Claude Code framework for Lilly computer system validation (CSV) projects. It lets a Validation Engineer drop raw project material into one place, build a living project context, and generate validation deliverables — Validation and Test Plan, Requirements, Design Specification, System Overview, Security Plan, SOPs, test cases, and traceability matrices — with GAMP 5, 21 CFR Part 11, and ALCOA+ rules enforced automatically.

## Who it is for
Validation Leads and Validation & Test Engineers running or supporting Lilly system validation projects, including Deloitte engineers contracted to Eli Lilly. It assumes GxP training and familiarity with the Lilly LQP-302-x SOP family.

## Folder structure
| Folder | Purpose |
|--------|---------|
| context/ | Drop zone for any project file (docs, emails, notes, decisions). Never edited manually. |
| context/meeting-notes/ | Raw meeting notes; processed by /meeting-notes. |
| context/decisions/ | Structured decision extracts written by /meeting-notes. |
| context/dev-inputs/ | Dev team confirmations and extracted requirement drafts. |
| context/project-docs/ | Charters, BRDs, architecture docs, and other source material. |
| templates/ | Lilly-standard Word document templates. Read-only — never modified. |
| deliverables/in-progress/ | Active generated drafts awaiting review. |
| deliverables/approved/ | Signed-off deliverables only, moved by /approve-doc. Versioned in git. |
| sops/ | Lilly SOPs (LQP-302-x, LCS-x, GSOP-x). Read-only reference for citations. |
| scripts/ | Python helpers for context building, document generation, and status checks. |
| .claude/skills/ | The 10 workbench skills. |

## Setup
### Prerequisites
- Claude Code installed
- Python 3.10+
- Python packages: python-docx, pypdf, openpyxl (`pip install -r scripts/requirements.txt`)

### Clone and open
1. Clone or copy this repo to your working location.
2. Open the folder in Claude Code.

### First-time setup
1. Drop project source files into the relevant context/ subfolder:
   - charters, BRDs, architecture docs → context/project-docs/
   - meeting notes → context/meeting-notes/
   - dev team confirmations → context/dev-inputs/
2. Run /build-context to populate MASTER_CONTEXT.md.
3. Review MASTER_CONTEXT.md and correct any misread values.

### Add templates
Drop Lilly-standard Word document templates into templates/. The /generate-doc skill uses a matching template as the base for each deliverable.

### Add SOPs
Drop Lilly SOP PDFs or Word files into sops/. Once present, every skill cites the specific SOP and section instead of flagging it as missing.

## Skills reference
| Skill | Command | When to use |
|-------|---------|-------------|
| build-context | /build-context | Build MASTER_CONTEXT.md from scratch from all files in context/. |
| update-context | /update-context | Incrementally refresh MASTER_CONTEXT.md from new or changed context files. |
| generate-doc | /generate-doc <type> | Generate a validation deliverable (vtp, ds, so, security-plan, sop, test-cases, rtm). |
| approve-doc | /approve-doc <filename> | Move a deliverable to approved/ and update status. |
| ask-sop | /ask-sop <question> | Answer a GxP/process/compliance question with SOP citations. |
| extract-requirements | /extract-requirements <filename> | Turn a source document into ALM-ready acceptance criteria. |
| write-test-case | /write-test-case <requirement-id> | Generate a formal GxP test case from a requirement. |
| gap-check | /gap-check <doc> | Check a deliverable against SOPs and GxP rules before routing. |
| meeting-notes | /meeting-notes <filename> | Extract decisions, actions, and confirmations from meeting notes. |
| check-status | /check-status | Show full status of deliverables, open items, and pending confirmations. |

## Typical workflow — new project
1. Drop charter, BRD, and architecture docs into context/project-docs/.
2. Run /build-context to create MASTER_CONTEXT.md.
3. Run /extract-requirements on the BRD to produce ALM-ready criteria.
4. Add Lilly templates to templates/ and SOPs to sops/.
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
- Risk-category-driven artifact scope.
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
Use /traceability to generate an RTM linking requirements to test cases. Coverage percentage is calculated automatically. 100% traceability required before SVR on RC#4/RC#5 systems.

### Confirmation tracking
project_data.py (one per project under projects/) tracks every pending dev-team confirmation with an ID, owner, and blocking document. Use /confirm-item to resolve items one by one. Context and affected deliverables update automatically.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
