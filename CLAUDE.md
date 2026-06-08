# Validation AI Workbench — Claude Code Project Instructions

## What this repo is
A GxP Validation Engineer's AI workbench for Lilly computer system validation projects. Used by Deloitte validation engineers contracted to Eli Lilly. Covers full CSV SDLC: requirements, design spec, validation test plan, SOPs, test cases, traceability, and change control.

## Auto-context rule
After EVERY skill run or session where project work was done, call /update-context automatically. Context must always reflect current project state. Never let MASTER_CONTEXT.md go stale.

## User profile
- Validation Lead / Validation & Test Engineer
- GxP-trained, familiar with GAMP 5, 21 CFR Part 11, ALCOA+
- Concise replies preferred — no fluff, no trailing summaries
- Use markdown links for file references, never backticks
- Never use emojis unless explicitly asked

## GxP writing rules (enforce in ALL generated content)
- ALM acceptance criteria: no "e.g.", no "such as", no "where applicable", no "including but not limited to"
- Use closed lists: "the following:" + explicit list
- Every testable requirement must name the specific mechanism, value, or SOP reference
- Never write vague criteria like "appropriate", "sufficient", "as required"
- ALCOA+ framing: Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available
- Risk category drives artifact scope: RC#4 = VTP + Requirements + DS + SO + Security Plan + SOPs + Audit Trail Assessment

## Folder roles
- context/ — user drops ANY project file here (docs, emails, notes, decisions). Never edit manually.
- templates/ — Lilly-standard Word document templates. Never modify.
- deliverables/in-progress/ — active generated docs
- deliverables/approved/ — signed-off docs only, moved by /approve-doc skill
- sops/ — Lilly SOPs (LQP-302-x, LCS-x, GSOP-x). Read-only reference.
- scripts/ — Python generation scripts

## SOP auto-lookup rule
Before writing any requirement, acceptance criterion, test case, or doc section: check sops/ for relevant guidance. If a relevant SOP exists, cite it. If sops/ is empty, note which SOP would apply and flag it.

## Shell
Windows PowerShell 5.1. Chain commands with ; not &&. No heredocs.

## Skill invocation
When user types any /skill-name, invoke it via the Skill tool immediately before any response.
