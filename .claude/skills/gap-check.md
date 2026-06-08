---
name: gap-check
description: Use when the user types /gap-check <doc>, says "check gaps in <doc>", or asks "is <doc> ready for review" — checks a deliverable against Lilly SOPs and GxP rules and produces a gap report.
---

# gap-check

## Overview
Check a deliverable against Lilly SOPs and GxP requirements, and produce a gap report before routing for review.

## Triggers
- /gap-check <doc>
- "check gaps in <doc>"
- "is <doc> ready for review"

## Instructions

1. Find the document in deliverables/ (fuzzy match).

2. Read the document fully.

3. Identify the document type (VTP / DS / SO / Security Plan / SOP).

4. Load relevant SOP requirements from sops/. If sops/ is empty, use built-in knowledge of the Lilly LQP-302-x structure.

5. Check each required section against the document:
   - VTP must have: Purpose, Scope, Risk Assessment, Roles/Responsibilities, Test Strategy, Acceptance Criteria, Deliverables list, Traceability approach, Defect management, Evidence retention.
   - DS must have: System description, Architecture, Data flows, Interfaces, OSS components, RBAC design, Audit trail design, Backup/recovery, Configuration parameters, Schema definitions.
   - SO must have: System description, Physical/logical location, Interfaces, OSS table, AI/ML statement, Record retention, Reviewers, Approvers.
   - Security Plan must have: Authentication, Authorization, Encryption in transit/at rest, SAST/DAST, Vulnerability scanning, Incident response, Access provisioning/deprovisioning.

6. For each gap, flag as:
   - CRITICAL — missing required section
   - MAJOR — section present but incomplete
   - MINOR — wording issue, missing citation

7. Check all content for ALM violations: flag any "e.g.", "such as", "where applicable", "appropriate", "sufficient" found in acceptance criteria.

8. Count remaining yellow placeholders [CONFIRM: ...] and list each one with its owner.

9. Output the gap report as markdown: | Section | Status | Issue | Severity | Recommendation |

10. End with: "Recommendation: [Ready for review / Not ready — X critical gaps must be resolved first]"

## GxP rules
Treat any vague acceptance criterion, open list, or uncited requirement as a finding. A document is not ready for review while any CRITICAL gap or unresolved placeholder remains.
