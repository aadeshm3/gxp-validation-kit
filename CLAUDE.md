# Validation AI Workbench — Claude Code Project Instructions

## What this repo is
A generic AI workbench for computer system validation projects. It is not tied to any organization, risk model, or fixed set of documents. A user clones it, drops in their own document templates and procedures, and generates and manages validation deliverables through skills. It is built to be usable by a non-technical validation engineer with no setup beyond dropping files into folders.

## Core principle — nothing is hardcoded
The framework supplies generic engines. All project-specific and organization-specific content comes from three places:
1. templates/ — the documents the user wants to produce. These define what a deliverable looks like.
2. sops/ — the user's procedures. These define the rules and the citations.
3. workbench.config.yaml — names, vocabulary, naming conventions, and preferences.

If a value is not set in the config and not derivable from templates/ or sops/, ask the user or insert a placeholder. Never invent a value, a document structure, a risk category, an artifact list, or an SOP section number.

## What the framework must never assume
- A specific risk-classification model. Risk category, if used at all, is optional free-text metadata. It never decides which deliverables exist.
- A fixed catalog of document types. The available deliverables are whatever templates exist in templates/.
- A required section list for any document. Required sections come from the template itself and the user's SOPs.
- Any organization name, tool name, or SOP numbering scheme. These come from the config or the files the user provides.

## Auto-context rule
After every skill run or session where project work was done, call /update-context. Context must always reflect current project state.

## User profile
- Validation Lead or Validation and Test Engineer, or any user managing a validation effort.
- May be non-technical. Prefer plain language. Explain what to do, not how the code works.
- Concise replies preferred — no fluff, no trailing summaries.
- Use markdown links for file references, never backticks.
- Never use emojis unless explicitly asked.

## Writing rules (applied to all generated content)
Language rules are defined in workbench.config.yaml under language_rules and are fully editable. When that config is present, enforce exactly what it specifies. When it is absent, apply these defaults:
- Use "shall" for requirements, not "should".
- No open lists: no "e.g.", "such as", "including but not limited to", "etc.".
- Every testable requirement names a specific mechanism, value, threshold, or document/SOP reference.
- No vague terms: "appropriate", "sufficient", "as required", "as needed".
- No hedges: "where applicable", "if applicable", "as appropriate", "when necessary".
- Use closed lists: "the following:" followed by an explicit list.

## Folder roles
- context/ — the user drops any project file here. Never edit manually.
- templates/ — the user's document templates. Never modify. These define the deliverables.
- sops/ — the user's procedures. Read-only reference for rules and citations.
- deliverables/in-progress/ — active generated drafts.
- deliverables/approved/ — signed-off documents only, moved by /approve-doc.
- scripts/ — generic Python engines.
- projects/ — one subfolder per project for multi-project use.

## SOP and template lookup rule
Before writing any deliverable, requirement, criterion, or section:
- Use the matching template in templates/ as the structure. If none exists, offer a generic structure and tell the user which template to add.
- Check sops/ for applicable rules and cite the specific file and section. If sops/ is empty, note which SOP to add for cited content. Never cite a section number not read from a file in sops/.

## Shell
Windows PowerShell 5.1. Chain commands with ; not &&. No heredocs.

## Skill invocation
When the user types any /skill-name, invoke it via the Skill tool immediately before any response.
