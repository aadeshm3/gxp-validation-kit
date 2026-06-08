# Onboarding — Validation AI Workbench

## 1. What you need installed
- Claude Code
- Python 3.10+
- Git

## 2. First 10 minutes
1. Clone this repo.
2. Open the folder: `claude <path>`
3. Drop your project charter or BRD into context/project-docs/.
4. Type: /build-context
5. Review MASTER_CONTEXT.md — correct anything wrong.
6. Type: /check-status to see which deliverables are needed for your risk category.
7. Type: /generate-doc vtp to create your first deliverable.

## 3. Daily workflow
- Start of day: /check-status
- After any meeting: drop notes into context/meeting-notes/, then run /meeting-notes
- When the dev team confirms something: /confirm-item <ID> "<value>"
- Before routing any doc for review: /gap-check <docname>
- End of session: Claude auto-runs /update-context

## 4. Command cheat sheet
| Command | What it does |
|---------|--------------|
| /new-project | Scaffold a new validation project under projects/. |
| /build-context | Build MASTER_CONTEXT.md from scratch from all files in context/. |
| /update-context | Incrementally refresh MASTER_CONTEXT.md from new or changed files. |
| /generate-doc <type> | Generate a deliverable (vtp, ds, so, security-plan, sop, test-cases, rtm). |
| /approve-doc <filename> | Move a deliverable to approved/ and update status. |
| /ask-sop <question> | Answer a GxP/process question with SOP citations. |
| /extract-requirements <filename> | Turn a source document into ALM-ready acceptance criteria. |
| /write-test-case <requirement-id> | Generate a formal GxP test case from a requirement. |
| /gap-check <doc> | Check a deliverable against SOPs and GxP rules before routing. |
| /meeting-notes <filename> | Extract decisions, actions, and confirmations from meeting notes. |
| /confirm-item <ID> "<value>" | Resolve a pending dev-team confirmation. |
| /traceability | Generate or update the Requirements Traceability Matrix. |
| /check-status | Show full status of deliverables, open items, and pending confirmations. |
| /write-svr | Generate the System Validation Report closeout document. |
| /validate-requirement | Check a single requirement for GxP testability and ALM compliance. Read-only. |
| /change-control | Generate a change control impact assessment for a validated system. |
| /review-response <filename> | Turn reviewer comments into a structured response table with dispositions. |
| /export-alm <filename> | Format approved requirements as a CSV for import into any ALM tool. |

## 5. Adding project-specific files
- SOP PDFs → sops/ (read-only reference; enables cited responses)
- Word document templates → templates/ (used as the base for generated deliverables)
- Second project on the same repo → run /new-project to scaffold projects/<SystemName>/

## 6. GxP non-negotiables
- Never commit credentials.
- Never manually edit MASTER_CONTEXT.md — use the skills.
- Every requirement must be testable before routing.
- Every test case needs evidence defined before execution.
- approved/ folder is a GxP record — only move docs here after sign-off.
