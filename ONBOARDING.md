# Onboarding — GxP Validation Kit

New here? Open this folder in Claude Code and type **/start**. The assistant looks at
where your project is and tells you the one next thing to do, in plain language. You do
not need to memorize any commands. The rest of this page is for reference.

## 1. Getting set up

You have two options. The first needs nothing installed on your computer.

**Option A — In your browser (recommended, no install).**
1. On GitHub, click the green "Code" button → "Codespaces" → "Create codespace on main".
2. Wait for it to finish building. It installs the Python packages and the Claude Code CLI for you.
3. In the terminal at the bottom, type `claude` and press Enter to start Claude Code. Sign in when prompted (first time only).
4. Inside Claude Code, type `/start`.

Note: `/start` is a Claude Code command, not a terminal command. Run `claude` first; otherwise the terminal replies "command not found".

**Option B — On your own computer.**
1. Install Claude Code, Python 3.10 or newer, and Git.
2. Clone or download this repository.
3. Run the one-step setup: on Windows, run `./setup.ps1`; on Mac or Linux, run `bash setup.sh`.
4. Open the folder in Claude Code and type /start.

## 2. First 10 minutes
1. Type **/start** — the assistant greets you and points to the next step.
2. Put your project documents (charter, requirements, notes) into the context folder, under context/project-docs/.
3. Say **build context** — the assistant reads everything and writes one summary.
4. Look over the summary it created and correct anything wrong.
5. Put your document templates into the templates folder.
6. Say **generate a document** — the assistant lists your templates and fills one in.

## 3. Everyday use
- Beginning of the day: say **check status** (or open the visual dashboard — see below).
- After a meeting: drop your notes into context/meeting-notes/ and say **process meeting notes**.
- When someone confirms a value you were waiting on: say **confirm item**.
- Before sending a document for review: say **check gaps**.
- You do not need to "save" your context. The assistant keeps it up to date for you.

## 4. Command reference
You can always use plain phrases instead of these. Both work.

| Command | Plain phrase | What it does |
|---------|--------------|--------------|
| /start | "where do I begin" | Tells you the single next step for your project. |
| /define <term> | "what is an RTM" | Explains any term in plain language. |
| /new-project | "start a new project" | Sets up a separate project in its own folder. |
| /build-context | "build context" | Reads all your project files into one summary. |
| /update-context | "update context" | Refreshes the summary from new or changed files. |
| /generate-doc <template> | "generate a document" | Creates a document from a template you provided. |
| /approve-doc <filename> | "approve this document" | Files a signed-off document and updates status. |
| /ask-sop <question> | "what does our procedure say about..." | Answers from your procedures, with citations. |
| /extract-requirements <file> | "pull requirements from this" | Turns a source document into testable requirements. |
| /write-test-case <id> | "write a test case" | Creates a step-by-step test from a requirement. |
| /gap-check <doc> | "check gaps" | Reviews a document for completeness before routing. |
| /meeting-notes <file> | "process meeting notes" | Extracts decisions and actions from notes. |
| /confirm-item <id> "value" | "confirm item" | Records a value someone confirmed. |
| /traceability | "build the traceability matrix" | Links requirements to tests and reports coverage. |
| /check-status | "check status" | Shows what is done, pending, and waiting. |
| /dashboard | "show me the dashboard" | Builds a visual status page to open in a browser. |
| /write-svr | "write the closeout report" | Produces the end-of-validation summary report. |
| /validate-requirement | "is this requirement okay" | Checks one requirement for clear, testable wording. |
| /change-control | "assess this change" | Assesses the impact of a change to a live system. |
| /review-response <file> | "process review comments" | Turns reviewer comments into a response table. |
| /export-alm <file> | "export for our ALM tool" | Saves requirements as a CSV to import elsewhere. |

## 5. Where your files go
- Project documents → context/project-docs/ (charters, requirements, notes, emails).
- Meeting notes → context/meeting-notes/.
- Your document templates → templates/ (these define your deliverables).
- Your procedures (SOPs) → sops/ (these let the assistant cite specific rules).
- Each folder has a short README explaining what to put there.

## 6. Helpful extras — just ask, the assistant does it for you
You never need to run a command yourself. Ask in plain language and the assistant runs the tool and reports back.
- **Visual dashboard:** say "show me the dashboard". The assistant builds it and tells you how to open it.
- **Check your settings:** if you changed workbench.config.yaml, say "check my settings" and the assistant validates it.
- **Glossary:** just ask "what is X" (or /define X).

## 7. Ground rules
- Never put passwords, keys, or personal data into the project. Do not commit them.
- Let the assistant maintain the context summary — do not edit MASTER_CONTEXT.md by hand.
- Every requirement should be testable before you send a document for review.
- Every test should say what evidence proves it passed.
- The approved folder is your official record — move documents there only after sign-off.
