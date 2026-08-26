#!/usr/bin/env python3
"""Finds table columns too narrow for the longest unbreakable token they must hold.

    python3 Generator/column-width-probe.py "<document.docx>"

CLAUDE.md section 8 item 5 says text extraction cannot see a column too narrow for its
content, which is why the rendered pages have to be read as images. That is true of prose,
but the specific case of an *identifier* splitting across lines is measurable, and it has
now happened three times: "+TBD" breaking mid-word, "Q-36" rendering as "Q-3 / 6", and at
Rev 1.22 "FR-CAM-002" rendering as "FR- / CAM-002" in three different tables.

An identifier that wraps is worse than ugly. A reader searching the document for
FR-CFG-005 does not find it, and in a submission the register that lists withdrawn
requirements is exactly where someone goes looking.

Calibration, not theory: the body requirement tables hold a ten-character identifier in
1150 twips and render it on one line, while the review register holds the same identifier
in 1100 twips and splits it. So the bold identifier column needs about 115 twips per
character including the cell margins. That is the threshold used here. It is deliberately
approximate — this probe is a net for the obvious cases, and the rendered page is still
the authority.
"""
import re
import sys
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TWIPS_PER_CHAR_BOLD = 115      # calibrated above
TWIPS_PER_CHAR_PLAIN = 100     # regular weight sets a little narrower

# A token that must not be broken: an identifier, a configuration key, a version.
TOKEN = re.compile(r"[A-Za-z]{1,6}-[A-Za-z]{2,4}-\d{3}|Q-\d{2,3}|F\d{2}\.\d|S\d{2}\.\d{2}|BL-\d{2}")


def cell_text(tc):
    return "".join(n.text or "" for n in tc.iter() if n.tag == W + "t")


def main(path):
    from lxml import etree
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("word/document.xml"))

    findings = []
    for ti, tbl in enumerate(root.iter(W + "tbl"), 1):
        grid = [int(gc.get(W + "w")) for gc in tbl.findall(f"{W}tblGrid/{W}gridCol")]
        if not grid:
            continue
        header = None
        worst = {}
        for ri, tr in enumerate(tbl.findall(W + "tr")):
            cells = tr.findall(W + "tc")
            texts = [cell_text(tc) for tc in cells]
            if ri == 0:
                header = texts
            for ci, txt in enumerate(texts):
                if ci >= len(grid):
                    continue
                for tok in TOKEN.findall(txt):
                    # only judge a cell the token dominates; a token inside a sentence
                    # wraps like any other word and that is not this defect
                    if len(txt.strip()) > len(tok) + 3:
                        continue
                    need = len(tok) * TWIPS_PER_CHAR_BOLD
                    if need > grid[ci] and need - grid[ci] > worst.get(ci, (0,))[0] - grid[ci]:
                        worst[ci] = (need, tok)
        for ci, (need, tok) in sorted(worst.items()):
            findings.append((ti, header[ci] if header and ci < len(header) else f"col {ci}",
                             grid[ci], tok, need))

    if not findings:
        print("  no column is too narrow for an identifier it must hold")
        return 0

    print(f"  {len(findings)} column(s) too narrow for an identifier:\n")
    print("   %-5s %-26s %7s %-14s %7s" % ("table", "column", "width", "token", "needs"))
    for ti, hdr, width, tok, need in findings:
        print("   %-5d %-26s %7d %-14s %7d" % (ti, hdr.replace("\n", " ")[:26], width, tok, need))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
