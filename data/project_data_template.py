# Copy this file to projects/<SystemName>/project_data.py and fill in values
# as they are confirmed by the development team.
"""
project_data_template.py — single source of truth for all confirmable project values.

This template mirrors the PENDING_CONFIRMATIONS pattern used across the workbench:
every value that is not yet certain is tracked as a structured item with an ID,
an owner, and the document it blocks. As the development team confirms each value,
set confirmed=True and fill the value field. Skills (build-context, update-context,
confirm-item, generate-doc, traceability) read this file to know what is settled and
what is still open.

The /new-project skill copies this template into projects/<SystemName>/project_data.py
and pre-fills SYSTEM_METADATA, STAKEHOLDERS, and DELIVERABLE_SCOPE from the answers
given during scaffolding.
"""

# System metadata — fill in during /new-project.
SYSTEM_METADATA = {
    "name": "",                  # e.g. LCDA Phase 1
    "risk_category": "",         # per your organization's computer system validation SOP
    "go_live_date": "",          # YYYY-MM-DD
    "compliance_framework": "",  # GxP only / 21 CFR Part 11 / HIPAA / all
    "validation_phase": "",      # New system (full CSV) / Major change / Minor change
}

# Stakeholders — one dict per person. Roles: System Owner, System Custodian,
# TSME, BSME, CSQA, etc.
STAKEHOLDERS = [
    {"name": "", "role": "", "org": "", "email": ""},
    {"name": "", "role": "", "org": "", "email": ""},
    {"name": "", "role": "", "org": "", "email": ""},
]

# Pending confirmations — every value awaiting dev-team input.
# Set confirmed=True and fill value when resolved (use /confirm-item).
PENDING_CONFIRMATIONS = [
    {"id": "PC-001", "description": "SQL Warehouse HTTP path", "owner": "", "confirmed": False, "value": None, "blocking_doc": "DS"},
    {"id": "PC-002", "description": "Service principal client ID", "owner": "", "confirmed": False, "value": None, "blocking_doc": "Security Plan"},
    {"id": "PC-003", "description": "Target catalog name", "owner": "", "confirmed": False, "value": None, "blocking_doc": "DS"},
    {"id": "PC-004", "description": "Go-live date confirmed", "owner": "", "confirmed": False, "value": None, "blocking_doc": "VTP"},
    {"id": "PC-005", "description": "Repository name and URL", "owner": "", "confirmed": False, "value": None, "blocking_doc": "SO"},
]

# Open-source libraries in scope — fill in and confirm license per item.
OSS_LIBRARIES = [
    {"name": "", "version": "", "license": "", "confirmed": False},
    {"name": "", "version": "", "license": "", "confirmed": False},
    {"name": "", "version": "", "license": "", "confirmed": False},
]

# System interfaces — direction is inbound/outbound, protocol e.g. REST/JDBC.
INTERFACES = [
    {"name": "", "direction": "", "protocol": "", "endpoint": "", "confirmed": False},
    {"name": "", "direction": "", "protocol": "", "endpoint": "", "confirmed": False},
    {"name": "", "direction": "", "protocol": "", "endpoint": "", "confirmed": False},
]


def get_pending():
    """Return all confirmation items that are not yet confirmed."""
    return [item for item in PENDING_CONFIRMATIONS if not item["confirmed"]]


def get_confirmed():
    """Return all confirmation items that have been confirmed."""
    return [item for item in PENDING_CONFIRMATIONS if item["confirmed"]]
