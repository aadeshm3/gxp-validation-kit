# Put your document templates here

A template is just your normal document — usually a Word file (.docx) — with the
headings and sections you want a finished deliverable to have. You do not need to
prepare anything special. The workbench makes a copy of your template and fills it
in with your project information.

## How to add a template
1. Copy your Word (or Markdown) document into this folder.
2. That's it. Type "generate a document" (or /generate-doc) and the assistant lists
   what is here and fills one in.

## Don't have a template?
Type "generate a document" anyway. The assistant will build a sensible starting
structure for you, which you can later replace with your own template.

## Good to know
- Files here are never modified. The workbench only reads them.
- You can give a template a short nickname in workbench.config.yaml so you can type
  a short word instead of the full filename. This is optional.
- Anywhere you write a marker like [CONFIRM: what is needed — ref: owner] in your
  template, the assistant treats it as a blank to be filled in or flagged.
