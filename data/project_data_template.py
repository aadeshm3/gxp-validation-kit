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

Nothing here is specific to any organization, tool, or risk model. The example
entries are illustrative only — replace them with your project's actual values.
"""

# System metadata. "name" and "go_live_date" are the only common fields.
# Add any other descriptive fields your project uses (for example a risk
# category or compliance framework) to the "extra" dict. These are descriptive
# only and never decide which deliverables a project needs.
SYSTEM_METADATA = {
    "name": "",            # the system or project name
    "go_live_date": "",    # YYYY-MM-DD, if known
    "extra": {},           # any other metadata fields, e.g. {"Risk Category": "", "Compliance Framework": ""}
}

# Stakeholders — one dict per person. Use whatever role labels your process uses.
STAKEHOLDERS = [
    {"name": "", "role": "", "org": "", "email": ""},
]

# The deliverables this project will produce. Filled by /new-project from the
# templates the user selects. Each entry is a short alias or template name.
DELIVERABLE_SCOPE = []

# Pending confirmations — every value awaiting input from another party.
# Set confirmed=True and fill value when resolved (use /confirm-item).
# blocking_doc is the deliverable that needs this value; use your own names.
PENDING_CONFIRMATIONS = [
    {"id": "PC-001", "description": "", "owner": "", "confirmed": False, "value": None, "blocking_doc": ""},
]

# Third-party or open-source components in scope, if relevant. Confirm license per item.
COMPONENTS = [
    {"name": "", "version": "", "license": "", "confirmed": False},
]

# Interfaces, if relevant. direction is inbound/outbound; protocol is free text.
INTERFACES = [
    {"name": "", "direction": "", "protocol": "", "endpoint": "", "confirmed": False},
]


def get_pending():
    """Return all confirmation items that are not yet confirmed."""
    return [item for item in PENDING_CONFIRMATIONS if not item["confirmed"]]


def get_confirmed():
    """Return all confirmation items that have been confirmed."""
    return [item for item in PENDING_CONFIRMATIONS if item["confirmed"]]
