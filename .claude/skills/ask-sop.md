---
name: ask-sop
description: Use when the user types /ask-sop <question> or asks any question about procedures, compliance, validation approach, change control, audit trail, or record retention — answers from the SOPs in sops/ with citations.
---

# ask-sop

## Overview
Answer any GxP, process, or compliance question by searching the SOPs in the sops/ folder and citing the specific source.

## Triggers
- /ask-sop <question>
- Any question about procedures, compliance, validation approach, change control, audit trail, or record retention.

## Instructions

1. Identify the question topic.

2. Glob sops/ for all files. If the folder has files, read them and cite only what you find — specific SOP name, section number, and page. If sops/ is empty or the relevant SOP is not present, answer from built-in GxP knowledge and tell the user: Add the current version of your [topic] SOP to sops/ to enable cited responses. Never cite a section number you did not read from a file.

3. Always end the answer with one of:
   - "Source: <SOP name> §<section>"
   - "Note: Add <SOP name> to sops/ for cited responses"

4. Never invent SOP section numbers. If unsure of a section, say so.

## Red flags
- Citing a section number you did not read from a file in sops/. Do not do this.
- Answering a process question without checking sops/ first.
