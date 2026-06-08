---
name: ask-sop
description: Use when the user types /ask-sop <question> or asks any question about Lilly procedures, compliance, validation approach, change control, audit trail, or record retention — answers from the SOPs in sops/ with citations.
---

# ask-sop

## Overview
Answer any GxP, process, or compliance question by searching the SOPs in the sops/ folder and citing the specific source.

## Triggers
- /ask-sop <question>
- Any question about Lilly procedures, compliance, validation approach, change control, audit trail, or record retention.

## Instructions

1. Identify the question topic.

2. Map the topic to the likely SOP(s):
   - Computer system validation, artifacts, risk categories → LQP-302-25, LQP-302-26
   - Change control, emergency changes → LCS-501, LQP-302-27
   - Security, RBAC, SAST, encryption → LQP-302-29
   - Record retention → GRRS
   - AI/ML → LQP-302-30
   - CSV roles and responsibilities → GSOP-1201.1, GSOP-1201.2

3. Glob sops/ for matching files. If found, read the relevant sections and generate an answer with specific citations: SOP name, section number, and page if available.

4. If sops/ is empty or the file is not found, answer from built-in GxP knowledge AND tell the user exactly which SOP to add to sops/ for future cited responses.

5. Always end the answer with one of:
   - "Source: <SOP name> §<section>"
   - "Note: Add <SOP name> to sops/ for cited responses"

6. Never invent SOP section numbers. If unsure of a section, say so.

## Red flags
- Citing a section number you did not read from a file in sops/. Do not do this.
- Answering a process question without checking sops/ first.
