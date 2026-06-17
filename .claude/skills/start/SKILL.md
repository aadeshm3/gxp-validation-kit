---
name: start
description: Use when the user types /start, says "help", "where do I begin", "what do I do now", "I'm new", or otherwise seems unsure how to use the workbench — looks at the current state and tells them the single next step in plain language.
---

# start

## Overview
The guided front door for any user, especially a non-technical one. Look at the current state of the project and tell the user the one next thing to do, in plain language. No memorizing commands.

## Triggers
- /start
- "help", "where do I begin", "what do I do now", "I'm new"
- Any sign the user is unsure how to proceed.

## Instructions

1. Greet the user in one short sentence. Do not dump the whole command list.

2. Check the current state, in this order, and stop at the first one that applies. Tell the user what it means and the single next action.
   - MASTER_CONTEXT.md is missing or still contains "[populated by /build-context]", and context/ has no source files (only .gitkeep):
     "Your project is empty. Put your project documents (charter, requirements, architecture notes, emails) into the context folder, then tell me to build the context." Point them to context/project-docs/.
   - context/ has files but MASTER_CONTEXT.md is not built yet:
     "You have project files but I have not read them yet. Say 'build context' and I will summarize everything into one place."
   - MASTER_CONTEXT.md is built but templates/ is empty (only .gitkeep):
     "Your project summary is ready. To create a document, add your Word template to the templates folder. A template is just your normal document with the headings you want. Don't have one? Say 'generate a document' and I will build a starting structure for you."
   - templates/ has templates but no deliverable exists yet in deliverables/in-progress/:
     "You're ready to create your first document. Say 'generate a document' and I will list your templates and fill one in."
   - A deliverable exists in deliverables/in-progress/ with open [CONFIRM: ...] items:
     "Your draft has X items waiting for a confirmed value. When someone gives you a value, say 'confirm item' and I will fill it in. When all are resolved, say 'check gaps' before sending it for review."
   - A deliverable exists with no open items:
     "Your draft looks complete. Say 'check gaps' to review it against your templates and procedures before routing. After sign-off, say 'approve' to file it."

3. Offer the three most relevant next actions as plain phrases, not slash commands. For example: "You can say: build context, generate a document, or check status." Map their plain phrase to the right skill yourself.

4. If the user asks what a term means at any point, answer plainly and offer the /define skill for the full glossary.

## Rules
Speak in plain language. Prefer outcomes ("I'll summarize your files into one place") over file paths and command names. Never show more than three suggested actions at once. Never assume the user knows validation jargon.
