# Projects

Each validation project gets its own subfolder under projects/. This keeps the context, deliverables, and confirmation tracking for one system fully separated from every other system managed in this workbench.

## What is shared vs per-project

Shared across all projects:
- templates/ — standard Word document templates
- sops/ — the SOPs you upload, whatever your organization uses
- .claude/skills/ — the workbench skills

Per-project (under projects/<SystemName>/):
- context/ — source files for that system (project-docs, meeting-notes, decisions, dev-inputs)
- deliverables/in-progress/ — active generated drafts
- deliverables/approved/ — signed-off deliverables
- project_data.py — single source of truth for confirmable values and pending confirmations
- MASTER_CONTEXT.md — the living project context for that system

## Start a new project
Run /new-project. It asks for the system name and basic metadata, then asks which deliverables you need based on the templates in templates/, scaffolds the subfolder, and copies data/project_data_template.py into projects/<SystemName>/project_data.py. It does not impose any fixed artifact set — you choose what the project needs.

## Switch between projects
Tell Claude which project you are working on. Claude reads that project's MASTER_CONTEXT.md and project_data.py before acting. All skills operate against the active project's folders.
