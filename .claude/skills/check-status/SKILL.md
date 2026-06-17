---
name: check-status
description: Use when the user types /check-status, asks "what's the status", "what's pending", or "what's done" — shows full status of all deliverables, open items, and pending confirmations.
---

# check-status

## Overview
Show the full status of all validation deliverables, open items, and pending confirmations, and reconcile recorded state against files on disk.

## Triggers
- /check-status
- "what's the status"
- "what's pending"
- "what's done"

## Instructions

1. Read MASTER_CONTEXT.md section 4 (Deliverable Status) and section 6 (Open Items & Pending Confirmations).

2. Read DELIVERABLE_STATUS.md.

3. Scan deliverables/in-progress/ and deliverables/approved/ for actual files.

4. Cross-reference: flag any discrepancy between MASTER_CONTEXT and the actual files on disk.

5. Count items in context/ that have not yet been processed (modified after the Last Refreshed date).

6. Output a clean status report:

   DELIVERABLES:
   | Document | Status | Location | Placeholders remaining | Next action |

   OPEN ITEMS:
   | ID | Description | Owner | Status |

   PENDING CONFIRMATIONS:
   | ID | Description | Owner | Blocking which doc |

   UNPROCESSED FILES IN CONTEXT/:
   List any files not yet reflected in MASTER_CONTEXT.

7. End with: "Next recommended action: <single most important thing to do now>"

## Notes
Read-only. This skill never modifies project state. If unprocessed files exist, the recommended next action is usually /update-context or /meeting-notes.
