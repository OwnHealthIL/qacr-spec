#!/usr/bin/env python3
"""The step between cleaning a spec for release and renaming it to 1.0.

    ready-check.py <spec.md> <generator dir>

Promoting a spec is mostly subtraction: the proposals come out, the answered questions
fold away, the changelog goes. Every promotion so far has been followed within days by
two or three corrections, and the ones that mattered were not disagreements about content
— they were **damage done by the cleaning itself**, or things the cleaning was supposed to
notice and did not:

  SPEC-04 Rev 1.0 went out with a reference to a `U4` that no longer existed and a row
  describing the wrong `U3`, because the open-item list was renumbered and the references
  to it were not. Three of the four defects the development team reported were that.

  SPEC-05 Rev 1.0 went out with the line saying what kind of document it was removed,
  because "strip the archaeology" was read too broadly.

  SPEC-05 Rev 1.0's milestone row omitted milestone 2 while being otherwise exhaustive.
  An independent verification found it; nothing here could.

So this asks the questions that subtraction breaks. It is not a review of the content —
Guy has already done that — and it is not a gate. It runs before the rename, and what it
finds gets fixed in the same pass rather than in a revision nobody asked for.
"""
import io, json, os, re, subprocess, sys

# abspath: DIR is interpolated into a `node -e` require(), and a bare relative path like
# `generator` resolves against node's cwd, not ours — MODULE_NOT_FOUND with a stack trace
# instead of a check result.
SPEC, DIR = sys.argv[1], os.path.abspath(sys.argv[2])
txt = io.open(SPEC, encoding="utf-8").read()
name = os.path.basename(SPEC)
fails, notes = [], []


def check(ok, msg):
    if not ok:
        fails.append(msg)


# --- what the document defines, so dangling references can be found
# A definition is the first cell of a table row, bold or not — SPEC-02 writes `| U1 |`
# and SPEC-04 writes `| **U1** |`, and reading only one of those invents dangling
# references that are not there.
defined_s = set(re.findall(r"\*\*(S\d{2}\.\d{2})\*\*", txt))
defined_d = set(re.findall(r"^\|\s*\*{0,2}(D\d+)\*{0,2}\s*\|", txt, re.M))
defined_u = set(re.findall(r"^\|\s*\*{0,2}(U\d+)\*{0,2}\s*\|", txt, re.M))

# A *reference* is a mention in a table row or an explicit "see Xn". Free prose may
# legitimately discuss an identifier that no longer exists — SPEC-04 carries a note saying
# why its numbering starts at U2, which names U1 and U4 on purpose. Counting those makes
# the check cry wolf on the very document that taught us to write the note.
ref_scope = "\n".join(l for l in txt.splitlines()
                       if l.lstrip().startswith("|") or re.search(r"\bsee [SDU]\d", l))
headings = re.findall(r"^#{2,3}\s+(\d+(?:\.\d+)?)[.\s]", txt, re.M)

# 1 · a reference to something the document no longer contains
for kind, defined, pat in (("statement", defined_s, r"\bS\d{2}\.\d{2}\b"),
                           ("departure", defined_d, r"\bD\d+\b"),
                           ("open item", defined_u, r"\bU\d+\b")):
    used = set(re.findall(pat, ref_scope))
    dangling = sorted(used - defined)
    if kind == "departure":
        dangling = [d for d in dangling if not re.search(r"\bDip|\bD\d{3}", d)]
    check(not dangling,
          f"{name}: refers to {kind}(s) it does not define -> {', '.join(dangling)}. "
          f"Renumbering a list and leaving the references to it is how three of SPEC-04 "
          f"Rev 1.0's four reported defects happened")

# 2 · a cross-reference to a section that is not there
for sec in sorted(set(re.findall(r"\bsection (\d+(?:\.\d+)?)\b", txt))):
    check(sec in headings,
          f"{name}: points at 'section {sec}', which it has no heading for. Sections "
          f"renumber when one is removed and the pointers do not follow")

# 3 · the things a ready document may never lose
check(bool(re.search(r"^##\s+What this document defines", txt, re.M)),
      f"{name}: has no 'What this document defines' section. Authority is per feature and "
      f"a delivered document without it leaves a reader to guess which source wins")
check("disagree" in txt and ("is right" in txt or "wins" in txt),
      f"{name}: carries no precedence rule. It is the one sentence that says what to do "
      f"when the document and the product differ")

# 4 · archaeology that the cleaning was supposed to remove
for marker in ("What changed from Rev", "at this revision", "the previous revision",
               "not yet re-reviewed", "draft for review"):
    if marker.lower() in txt.lower():
        notes.append(f"{name}: still contains {marker!r} — cleaning leftover?")

# 5 · the milestone row against the milestones actually owed
m = re.search(r"\|\s*Features covered\s*\|([^|]*)\|", txt)
covered = re.findall(r"F\d{2}\.\d", m.group(1)) if m else []
truth = json.loads(subprocess.check_output(["node", "-e", f"""
const E=require('{DIR}/epics.js');
const s=[...require('{DIR}/reqs-part1.js'),...require('{DIR}/reqs-part2.js')];
const pri={{}}; s.forEach(x=>x.reqs.forEach(r=>pri[r[0]]=String(r[4])));
const feat={{}}; E.forEach(e=>e.features.forEach(f=>feat[f[0]]=f[2]));
console.log(JSON.stringify({{pri,feat}}));
"""]).decode())
owed_ms = sorted({truth["pri"][i] for f in covered for i in truth["feat"].get(f, [])
                  if i in truth["pri"]})
row = re.search(r"\|\s*Milestones\s*\|([^|]*)\|", txt)
if row and owed_ms:
    stated = set(re.findall(r"\b([1-5])\b", row.group(1)))
    missing = [ms for ms in owed_ms if ms not in stated]
    check(not missing,
          f"{name}: its milestone row does not name milestone(s) {', '.join(missing)}, "
          f"which requirements it owes actually sit at. The row reads as exhaustive, so an "
          f"omission reads as a decision")

# 6 · a stated count that disagrees with what is there
#
# SPEC-04 Rev 1.0 said "Twelve rows" in section 2 and "ten departures" in its closing
# line, over a table of twelve. Prose counts go stale the moment a row is added and
# nothing else notices.
WORDS = {"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,
         "ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15}
# "rows" is deliberately not matched: SPEC-04's own note about the defects it once had
# says "two rows describing the wrong question", which is prose, not a count of anything.
# "departures" and "statements" name the thing they count and do not read that way.
for m2 in re.finditer(r"\b(\w+)\s+(departures|statements)\b", txt, re.I):
    word, kind = m2.group(1).lower(), m2.group(2).lower()
    n = WORDS.get(word) or (int(word) if word.isdigit() else None)
    if n is None:
        continue
    actual = len(defined_s) if kind.startswith("statement") else len(defined_d)
    if not actual:
        continue
    check(n == actual,
          f"{name}: says {m2.group(0)!r} but the document has {actual}. A count in prose "
          f"is wrong the moment a row is added")

# 7 · a departure its own feature's traceability row does not carry
#
# SPEC-04 Rev 1.0 put D11 under F04.6 in section 2 and left it out of F04.6's
# traceability row. The feature file copies the traceability row, so the two halves of the
# document said different things and the development team hit it building from them.
dep_feats, trace_deps = {}, {}
for line in txt.splitlines():
    m3 = re.match(r"\|\s*\*\*(D\d+)\*\*\s*\|\s*([^|]+)\|", line)
    if m3:
        dep_feats[m3.group(1)] = re.findall(r"F\d{2}\.\d", m3.group(2))
    m4 = re.match(r"\|\s*(F\d{2}\.\d)\s[^|]*\|[^|]*\|\s*([^|]*)\|", line)
    if m4:
        trace_deps[m4.group(1)] = set(re.findall(r"D\d+", m4.group(2)))
if dep_feats and trace_deps:
    for d, feats in sorted(dep_feats.items()):
        for f in feats:
            if f in trace_deps:
                check(d in trace_deps[f],
                      f"{name}: section 2 gives {d} to {f}, but {f}'s traceability row "
                      f"lists {sorted(trace_deps[f]) or 'no departures'}. The feature file "
                      f"copies that row, so the two halves disagree downstream")

# 8 · a departure that does not say what it departs from
#
# A departure IS a difference from something, so a row that states only the new behaviour is
# incomplete — the reader cannot tell what is being changed. SPEC-04 Rev 1.2 shipped eight such
# rows out of twelve, and D7 was the one that surfaced it: "Once a timeout has been presented and
# dismissed, the absence window applies again from that moment. It does not stop applying for the
# rest of the run" negates a behaviour the reader was never told existed.
#
# The cause is worth recording, because it will recur. Those eight rows were derived from the E04
# behaviour review, where each behaviour sat on the line above the mark — so the antecedent was so
# present to the writer that writing it down felt redundant. The four rows that kept it, D1 and
# D10 to D12, are the four that came from somewhere other than the export. Having the review made
# the departures worse.
#
# So the table carries the antecedent in a column of its own, where an omission is visible rather
# than a matter of prose style.
dep_rows = [l for l in txt.splitlines() if re.match(r"\|\s*\*\*D\d+\*\*\s*\|", l)]
if dep_rows:
    hdr = next((l for l in txt.splitlines()
                if l.lstrip().startswith("|") and "Today" in l and "In QACR" in l), None)
    check(hdr is not None,
          f"{name}: has a departures table with no 'Today' / 'In QACR' columns. A departure is a "
          f"difference from something, and a row that states only the new behaviour cannot be "
          f"read without the behaviour review it was written against")
    if hdr:
        cells = [c.strip() for c in hdr.strip().strip("|").split("|")]
        i = cells.index("Today")
        blank = []
        for row in dep_rows:
            rc = [c.strip() for c in row.strip().strip("|").split("|")]
            if i >= len(rc) or not rc[i]:
                blank.append(re.sub(r"[|*\s]", "", row.split("|")[1]))
        check(not blank,
              f"{name}: departure(s) {', '.join(blank)} leave the 'Today' cell empty. Say what "
              f"Minuteful Kidney does now, or the row reads as a decision with no subject")

print(f"Ready-check: {name}")
print(f"   statements {len(defined_s)}  departures {len(defined_d)}  open items {len(defined_u)}")
print(f"   milestones owed: {', '.join(owed_ms) or 'none'}")
for n in notes:
    print(f"   note: {n}")
if fails:
    print("\nNOT READY")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print("   clean — nothing the cleaning broke, nothing it should have caught")
