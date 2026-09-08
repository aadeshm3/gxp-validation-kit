# Put approved documents here to learn their writing style

A reference document is an approved document of the same type as one of your
templates — from a different project or a different system — that you want
the assistant to learn writing and formatting conventions from: tone, how
scope and out-of-scope sections read, whether a section favors a table or
prose, how densely it cites SOPs, and how sections that don't apply are
handled. It is never read for facts — only for style.

## How to use it
1. Copy the approved document into this folder.
2. Type `/learn-style <filename>`.
3. The assistant matches it to a template in templates/, asks you to confirm
   the match, and saves a style-notes file that /generate-doc uses
   automatically the next time that template is generated.

## Good to know
- Files here are never modified. The workbench only reads them.
- Style notes are saved to reference-docs/style-notes/ — one file per
  template — so they persist across sessions.
- A prior version of the system's own document works the same way; drop it
  in context/prior-versions/ instead and run /learn-style on it from there.
