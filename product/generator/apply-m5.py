#!/usr/bin/env python3
"""One-off migration: empties the backlog into the requirement sections.

    python3 Generator/apply-m5.py

Reads the approved disposition in m5-map.js and rewrites, in place:

  reqs-part1.js, reqs-part2.js   41 requirements inserted, each at the end of its
                                 section, carrying "formerly BL-nn" in its source so
                                 id-guard.js recognises the disposition
  appendices.js                  backlog emptied; BL-38 added to withdrawn

Kept in the repository rather than deleted, because for a regulated document set how a
bulk change was made is part of its record. Idempotent: refuses to run twice.
"""
import json, os, re, subprocess, sys

DIR = os.path.dirname(os.path.abspath(__file__))


def node(expr):
    return json.loads(subprocess.check_output(
        ["node", "-e", f"console.log(JSON.stringify({expr}))"], cwd=DIR).decode())


MAP = node("require('./m5-map.js')")
BACKLOG = {r[0]: r for r in node("require('./appendices.js').backlog")}

if not BACKLOG:
    sys.exit("appendices.backlog is already empty — this migration has run before.")

# ---------------------------------------------------------------- helpers

def esc(s):
    """A JS double-quoted string literal. Em dashes and curly quotes stay literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


NEWID = {bl: t for bl, t, *_ in MAP if t}          # BL-nn -> its new FR identifier
WITHDRAWN_BL = {bl for bl, t, *_ in MAP if not t}


def remap(s):
    """Every BL identifier in prose becomes the identifier that now carries it.

    Without this the migrated notes would cite BL-25 and BL-29, which stop existing the
    moment this script runs — a dead trace, which reads as coverage that is not there.
    """
    def sub(m):
        bl = m.group(0)
        if bl in NEWID:
            return NEWID[bl]
        if bl in WITHDRAWN_BL:
            return f"the withdrawn {bl}"
        return bl
    return re.sub(r"BL-\d\d", sub, s or "")


def clean_note(note, bl, target, milestone):
    """The backlog notes open with 'Deferred', which stops being true here.

    'Deferred with BL-21' must not become a fragment reading 'with FR-AUT-011'. Strip the
    word, remap the identifiers, then capitalise whatever is left so the remainder is a
    sentence rather than a dangling clause.
    """
    n = (note or "").strip()
    n = re.sub(r"^Deferred\b[.,;]?\s*", "", n)
    n = re.sub(r"^NOTE:\s*", "", n)
    n = remap(n)
    if n:
        n = n[0].upper() + n[1:]
        if not n.endswith((".", "!", "?")):
            n += "."
    lead = {
        "1": f"Brought into scope for the demonstration at Guy's direction, formerly {bl}.",
        "3": f"Brought into scope for the submission at Guy's direction, formerly {bl}.",
        "5": f"Future development, formerly {bl}.",
    }[milestone]
    return (lead + " " + n).strip() if n else lead


def clean_source(src, bl, target, restored, why=""):
    """Strip a 'formerly FR-...' that now names this row itself, then record the BL.

    Where the map notes an "Originally FR-..." identifier — the four survey requirements
    were FR-SUR-001 to 004 before they were superseded to the backlog — that identifier is
    recorded here too. Emptying the backlog removed the middle link, so without it the
    FR-SUR identifiers are accounted for nowhere and id-guard.js fails the build.
    """
    s = re.sub(r";?\s*formerly FR-[A-Z]{3}-\d{3}", "", src or "").strip().rstrip(";").strip()
    if restored:
        s = (s + "; " if s else "") + f"formerly {bl}, restored to its original identifier"
    else:
        s = (s + "; " if s else "") + f"formerly {bl}"
    m = re.search(r"[Oo]riginally (FR-[A-Z]{3}-\d{3})", why or "")
    if m:
        s += f", originally {m.group(1)}"
    return s


# ---------------------------------------------------------------- build the rows
rows_by_prefix = {}
withdraw = []
for bl, target, why, milestone, override, *rest in MAP:
    note_override = rest[0] if rest else None
    src = BACKLOG[bl]
    text = override or src[1]
    if target is None:                                  # BL-38
        withdraw.append((bl, text, why))
        continue
    prefix = target.split("-")[1]
    restored = why == "restore"
    row = "    [{}, {}, {}, {}, {}],\n".format(
        esc(target), esc(text),
        # Only the inherited part of the source is remapped. The disposition this
        # script writes must keep saying "formerly BL-nn": remapping it turns the row
        # into a claim that it was formerly itself, and id-guard.js then has nothing to
        # read. It passed anyway the first time this went wrong, because the manifest
        # still held the disposition from an earlier, correct run.
        esc(clean_source(remap(src[2]), bl, target, restored, why)),
        esc(note_override or clean_note(src[3], bl, target, milestone)),
        esc(milestone))
    rows_by_prefix.setdefault(prefix, []).append((int(target.split("-")[2]), row))

for p in rows_by_prefix:
    rows_by_prefix[p].sort()

# ---------------------------------------------------------------- insert
ROW_START = re.compile(r'^    \["FR-([A-Z]{3})-(\d{3})"')
inserted = 0
for fname in ("reqs-part1.js", "reqs-part2.js"):
    path = os.path.join(DIR, fname)
    lines = open(path, encoding="utf-8").read().split("\n")
    # last line index of each prefix's rows — a section's rows are contiguous
    last = {}
    for i, line in enumerate(lines):
        m = ROW_START.match(line)
        if m:
            last[m.group(1)] = i
    out, done = [], set()
    for i, line in enumerate(lines):
        out.append(line)
        for prefix, idx in last.items():
            if i == idx and prefix in rows_by_prefix and prefix not in done:
                for _, row in rows_by_prefix[prefix]:
                    out.append(row.rstrip("\n"))
                    inserted += 1
                done.add(prefix)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    if done:
        print(f"  {fname}: inserted into {', '.join('FR-' + p for p in sorted(done))}")

missing = set(rows_by_prefix) - {p for p in rows_by_prefix}
assert not missing, missing
print(f"  {inserted} requirements inserted")

# ---------------------------------------------------------------- appendices
path = os.path.join(DIR, "appendices.js")
src = open(path, encoding="utf-8").read()

bl, text, why = withdraw[0]
wrow = "  [{}, {}, {}, {}],\n".format(
    esc(bl), esc(text), esc("Not included"),
    esc(f"Withdrawn at Guy's direction, 12 Aug 2026. {why} Was a deferred backlog item and is "
        f"not carried into milestone 5."))

m = re.search(r"(exports\.withdrawn\s*=\s*\[\n)", src)
assert m, "cannot find exports.withdrawn"
src = src[:m.end(1)] + wrow + src[m.end(1):]

# empty the backlog, keeping the export and a note saying where it went
m = re.search(r"exports\.backlog\s*=\s*\[[\s\S]*?\n\];", src)
assert m, "cannot find exports.backlog"
src = src[:m.start()] + (
    "// The backlog was emptied at Rev 1.18. Every item took an FR identifier in the section\n"
    "// it belongs to, at milestone 5 (future development) except BL-34 at 1, BL-35 at 3 and\n"
    "// BL-38 withdrawn. The disposition of each is in m5-map.js and each requirement's source\n"
    "// field records 'formerly BL-nn'. Kept as an empty export so nothing needs a null check.\n"
    "exports.backlog = [];"
) + src[m.end():]

open(path, "w", encoding="utf-8").write(src)
print(f"  appendices.js: backlog emptied, {bl} added to withdrawn")

for f in ("reqs-part1.js", "reqs-part2.js", "appendices.js"):
    subprocess.run(["node", "--check", os.path.join(DIR, f)], check=True)
print("  node --check clean on all three")
