"""
dashboard.py — render a visual status dashboard as a single HTML file.

Reuses the parsing helpers in check_status.py and writes status.html at the
repo root. Open that file in any web browser for a friendly view of
deliverables, open items, coverage, and unprocessed files — no markdown or
terminal needed. Run it any time:

    python scripts/dashboard.py
"""

import html
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_status as cs  # noqa: E402

OUTPUT = Path(__file__).resolve().parent.parent / "status.html"

STYLE = """
body { font-family: Segoe UI, Arial, sans-serif; margin: 2rem; color: #1d1d1f; }
h1 { margin-bottom: 0.2rem; }
.meta { color: #666; margin-bottom: 1.5rem; }
.card { border: 1px solid #e2e2e2; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 0.5rem 0.75rem; border-bottom: 1px solid #eee; font-size: 0.95rem; }
th { background: #f6f6f8; }
.next { background: #eef6ff; border: 1px solid #cfe3fb; border-radius: 10px; padding: 1rem 1.25rem; font-size: 1.05rem; }
.empty { color: #888; font-style: italic; }
.badge { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 999px; font-size: 0.8rem; }
.ok { background: #e7f7ec; color: #1a7f37; }
.warn { background: #fff3cd; color: #8a6d00; }
"""


def esc(value):
    return html.escape(str(value))


def render_table(headers, rows, empty_msg):
    if not rows:
        return '<p class="empty">{}</p>'.format(esc(empty_msg))
    head = "".join("<th>{}</th>".format(esc(h)) for h in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join("<td>{}</td>".format(esc(c)) for c in row) + "</tr>"
    return "<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(head, body)


def main():
    master_text = cs.read_text(cs.CONTEXT_FILE)
    last_refreshed = cs.parse_last_refreshed(master_text)
    in_progress = cs.scan_deliverables(cs.IN_PROGRESS_DIR)
    approved = cs.scan_deliverables(cs.APPROVED_DIR)
    open_items = cs.parse_open_items(master_text)
    unprocessed = cs.find_unprocessed(last_refreshed)

    deliverable_rows = []
    for path, count in in_progress:
        ph = "unknown" if count is None else count
        badge = '<span class="badge ok">clean</span>' if count == 0 else '<span class="badge warn">{} open</span>'.format(ph)
        deliverable_rows.append([path.name, "in-progress", badge])
    for path, count in approved:
        deliverable_rows.append([path.name, "approved", '<span class="badge ok">approved</span>'])

    if not master_text or "[populated by /build-context]" in master_text:
        next_action = "Run /build-context — your project context is not built yet."
    elif unprocessed:
        next_action = "Run /update-context — {} file(s) changed since the last refresh.".format(len(unprocessed))
    elif any(c for _, c in in_progress if c):
        next_action = "Resolve the open [CONFIRM] items, then run /gap-check before routing."
    elif in_progress:
        next_action = "Run /gap-check on your drafts before routing for review."
    else:
        next_action = "Nothing outstanding. Add templates or start a deliverable with /generate-doc."

    # render_table accepts pre-escaped badge HTML, so build deliverable rows raw.
    if deliverable_rows:
        head = "<th>Document</th><th>Stage</th><th>Status</th>"
        body = "".join("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(esc(r[0]), esc(r[1]), r[2]) for r in deliverable_rows)
        deliverables_html = "<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(head, body)
    else:
        deliverables_html = '<p class="empty">No deliverables yet. Use /generate-doc to create one.</p>'

    open_html = render_table(open_items[0], open_items[1:], "No open items.") if open_items else '<p class="empty">No open items recorded.</p>'
    unprocessed_html = ("<ul>" + "".join("<li>{}</li>".format(esc(cs.rel(p))) for p in unprocessed) + "</ul>") if unprocessed else '<p class="empty">All context files are processed.</p>'

    refreshed = last_refreshed.strftime("%Y-%m-%d") if last_refreshed else "not set"
    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Validation Workbench Status</title>
<style>{style}</style></head><body>
<h1>Validation Workbench Status</h1>
<div class="meta">Generated {now} &middot; Context last refreshed: {refreshed}</div>
<div class="next"><strong>Next step:</strong> {next_action}</div>
<div class="card"><h2>Deliverables</h2>{deliverables}</div>
<div class="card"><h2>Open items</h2>{open_items}</div>
<div class="card"><h2>Files waiting to be processed</h2>{unprocessed}</div>
</body></html>""".format(
        style=STYLE,
        now=datetime.now().strftime("%Y-%m-%d %H:%M"),
        refreshed=esc(refreshed),
        next_action=esc(next_action),
        deliverables=deliverables_html,
        open_items=open_html,
        unprocessed=unprocessed_html,
    )

    OUTPUT.write_text(page, encoding="utf-8")
    print("Dashboard written to status.html. Open it in your web browser.")


if __name__ == "__main__":
    main()
