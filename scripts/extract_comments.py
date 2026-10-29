"""
extract_comments.py — list every review comment in a Word (.docx) document.

Word stores comments in word/comments.xml. This script reads them with the
Python standard library only (no extra packages) and prints JSON: for each
comment its id, author, date, text, the document text the comment is attached
to, whether it is resolved, and the id of the comment it replies to (if any).

USAGE
-----
  python scripts/extract_comments.py <file.docx>

Used by the /learn-comments skill.
"""

import json
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"


def _q(ns, tag):
    return "{%s}%s" % (ns, tag)


def _para_text(par):
    return "".join(t.text or "" for t in par.iter(_q(W, "t")))


def read_comments(archive):
    """Return {id: {author, date, text, para_id}} from word/comments.xml."""
    if "word/comments.xml" not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read("word/comments.xml"))
    comments = {}
    for node in root.iter(_q(W, "comment")):
        pars = list(node.iter(_q(W, "p")))
        comments[node.get(_q(W, "id"))] = {
            "author": node.get(_q(W, "author"), ""),
            "date": node.get(_q(W, "date"), ""),
            "text": "\n".join(_para_text(p) for p in pars).strip(),
            # The last paragraph's id links the comment to commentsExtended.xml.
            "para_id": pars[-1].get(_q(W14, "paraId")) if pars else None,
        }
    return comments


def read_extended(archive):
    """Return {para_id: {done, parent_para_id}} from word/commentsExtended.xml."""
    if "word/commentsExtended.xml" not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read("word/commentsExtended.xml"))
    return {
        ex.get(_q(W15, "paraId")): {
            "done": ex.get(_q(W15, "done")) == "1",
            "parent": ex.get(_q(W15, "paraIdParent")),
        }
        for ex in root.iter(_q(W15, "commentEx"))
    }


def read_anchors(archive):
    """Return {comment_id: anchored document text} from word/document.xml."""
    root = ET.fromstring(archive.read("word/document.xml"))
    open_ids = set()
    anchors = {}
    for el in root.iter():
        if el.tag == _q(W, "commentRangeStart"):
            open_ids.add(el.get(_q(W, "id")))
        elif el.tag == _q(W, "commentRangeEnd"):
            open_ids.discard(el.get(_q(W, "id")))
        elif el.tag == _q(W, "t") and el.text:
            for cid in open_ids:
                anchors[cid] = anchors.get(cid, "") + el.text
    return anchors


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/extract_comments.py <file.docx>")
        return 2
    path = Path(sys.argv[1])
    if path.suffix.lower() != ".docx" or not path.is_file():
        print("Error: {} is not a .docx file that exists.".format(path))
        return 1
    with zipfile.ZipFile(path) as archive:
        comments = read_comments(archive)
        extended = read_extended(archive)
        anchors = read_anchors(archive)

    by_para = {c["para_id"]: cid for cid, c in comments.items() if c["para_id"]}
    out = []
    for cid, c in comments.items():
        ext = extended.get(c["para_id"], {})
        out.append({
            "id": cid,
            "author": c["author"],
            "date": c["date"],
            "comment": c["text"],
            "anchored_text": anchors.get(cid, ""),
            "resolved": ext.get("done", False),
            "reply_to": by_para.get(ext.get("parent")),
        })
    print(json.dumps({"file": path.name, "comment_count": len(out), "comments": out},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
