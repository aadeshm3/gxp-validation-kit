---
name: define
description: Use when the user types /define <term>, asks "what is X", "what does X mean", or uses a validation acronym they may not know (VTP, DS, SO, RTM, SVR, ALM, ALCOA+, GAMP, RBAC, CSV, and similar) — explains the term in plain language from GLOSSARY.md.
---

# define

## Overview
Explain any validation or quality term in plain language. The source of truth is GLOSSARY.md at the repo root.

## Triggers
- /define <term>
- "what is X", "what does X mean", "explain X"
- The user uses an acronym or piece of jargon they may not understand.

## Instructions

1. Read GLOSSARY.md.

2. Find the term (case-insensitive; match the acronym or the full name). If the user gave no term, list the terms available in GLOSSARY.md grouped by topic.

3. Answer in two parts:
   - One plain-language sentence a non-technical person understands.
   - One sentence on why it matters in this project, if relevant.

4. If the term is not in GLOSSARY.md:
   - Answer from general knowledge in plain language.
   - Offer to add it: "Would you like me to add this to the glossary?" If yes, append it to GLOSSARY.md in the same format.

5. If the term relates to a skill, mention the plain phrase that runs it (for example, "you can say 'check gaps'").

## Rules
Plain language first, always. No acronym is explained using another unexplained acronym. Keep each definition to two sentences unless the user asks for more.
