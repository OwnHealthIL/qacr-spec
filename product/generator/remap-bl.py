#!/usr/bin/env python3
"""Second half of the milestone-5 migration: remaps every remaining BL reference.

    python3 Generator/remap-bl.py

apply-m5.py moved the requirements. This rewrites everything that pointed at them:

  epics.js        each feature's deferred list merges into its requirement list
  review.js       the register and the decision log
  configs.js      the configuration register
  spta.js         the threat-analysis mapping
  reqs-part*.js   six notes on requirements that were never themselves deferred
  spec-status.js  the wording for features that were backlog items
  Specs/*.md      identifiers only — the prose that is now substantively wrong is
                  reported for VS Code to rewrite, because it owns the specs

Reports every substitution so the diff can be read against this output.
"""
import json, os, re, subprocess, sys
from collections import defaultdict

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)


def node(expr):
    return json.loads(subprocess.check_output(
        ["node", "-e", f"console.log(JSON.stringify({expr}))"], cwd=DIR).decode())


MAP = node("require('./m5-map.js')")
NEWID = {bl: t for bl, t, *_ in MAP if t}
GONE = {bl for bl, t, *_ in MAP if not t}
MILESTONE = {bl: m for bl, t, w, m, *_ in MAP if t}

if not NEWID:
    sys.exit("m5-map.js is empty")

counts = defaultdict(int)


# A disposition marker is not a reference. "formerly BL-19" is the audit trail that
# id-guard.js reads to know where BL-19 went; rewriting it to the new identifier makes the
# row say it was formerly itself and silently destroys the record. Same for "superseded
# to", "withdrawn" and the comment lines that describe the migration.
KEEP = re.compile(r"(formerly|superseded to|withdrawn|restored from|was)\s+$")


def remap(text, where):
    def sub(m):
        bl = m.group(0)
        before = text[max(0, m.start() - 30):m.start()]
        if KEEP.search(before) or before.lstrip().startswith("//"):
            return bl
        if bl in NEWID:
            counts[where] += 1
            return NEWID[bl]
        return bl
    return re.sub(r"BL-\d\d", sub, text)


# ------------------------------------------------------------------ epics.js
# A feature row is [id, name, [FR ids], [BL ids], intent, uxNote, split?]. The fourth
# element becomes an empty list rather than being removed: removing it would shift the
# positions of intent, uxNote and split in fourteen readers, and a prose field that
# renders in the wrong place is the kind of failure no guard here would catch. Slated
# for removal as its own change — see CLAUDE.md.
path = os.path.join(DIR, "epics.js")
src = open(path, encoding="utf-8").read()

ROW = re.compile(r'(\["F\d{2}\.\d",[\s\S]*?\],\s*)(\[((?:"BL-\d\d",?\s*)+)\])', re.M)

def merge(m):
    head, _, ids = m.group(1), m.group(2), m.group(3)
    bls = re.findall(r"BL-\d\d", ids)
    promoted = [NEWID[b] for b in bls if b in NEWID]
    dropped = [b for b in bls if b in GONE]
    # append to the requirement list that precedes it
    if promoted:
        newids = ", ".join(f'"{i}"' for i in promoted)
        # Eighteen features held only deferred items, so their requirement list was "[]".
        # Appending ", \"FR-...\"" to that yields "[, \"FR-...\"]", which JavaScript reads
        # as a hole: element zero becomes undefined and every milestone computed from the
        # list gets a stray empty entry. Handle the empty list on its own.
        if re.search(r"\[\],\s*$", head):
            head = re.sub(r"\[\],(\s*)$", lambda mm: f"[{newids}],{mm.group(1)}", head, count=1)
        else:
            head = re.sub(r"\],(\s*)$", lambda mm: f", {newids}],{mm.group(1)}", head, count=1)
        counts["epics.js requirements merged"] += len(promoted)
    if dropped:
        counts["epics.js withdrawn, dropped"] += len(dropped)
    return head + "[]"

src, n = ROW.subn(merge, src)
open(path, "w", encoding="utf-8").write(src)
print(f"  epics.js: {n} feature rows had a deferred list")

# ------------------------------------------------- the plain text substitutions
for rel in ("review.js", "configs.js", "spta.js", "reqs-part1.js", "reqs-part2.js",
            "spec-status.js"):
    path = os.path.join(DIR, rel)
    src = open(path, encoding="utf-8").read()
    out = remap(src, rel)
    if out != src:
        open(path, "w", encoding="utf-8").write(out)

for rel in ("Specs/QACR-APP-SPEC-01 Readiness and eligibility.md",
            "Specs/QACR-APP-SPEC-05 Timed waits and the reaction phase.md"):
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        continue
    src = open(path, encoding="utf-8").read()
    out = remap(src, os.path.basename(rel))
    if out != src:
        open(path, "w", encoding="utf-8").write(out)

for k in sorted(counts):
    print(f"  {k}: {counts[k]}")

# ------------------------------------------------------------------ verify
for f in ("epics.js", "review.js", "configs.js", "spta.js", "reqs-part1.js",
          "reqs-part2.js", "spec-status.js"):
    subprocess.run(["node", "--check", os.path.join(DIR, f)], check=True)
print("  node --check clean")

left = []
for dirpath, _, files in os.walk(ROOT):
    if "/.git" in dirpath or "node_modules" in dirpath or "Previous revisions" in dirpath:
        continue
    for f in files:
        if not f.endswith((".js", ".py", ".md")) or f in ("m5-map.js", "remap-bl.py", "apply-m5.py"):
            continue
        p = os.path.join(dirpath, f)
        for m in re.finditer(r"BL-\d\d", open(p, encoding="utf-8", errors="ignore").read()):
            left.append((os.path.relpath(p, ROOT), m.group(0)))

if left:
    print(f"\n  BL identifiers still present in {len({p for p, _ in left})} file(s):")
    seen = defaultdict(set)
    for p, bl in left:
        seen[p].add(bl)
    for p in sorted(seen):
        print(f"     {p}: {' '.join(sorted(seen[p]))}")
    print("  Each should be a 'formerly BL-nn' disposition or a withdrawn reference.")
