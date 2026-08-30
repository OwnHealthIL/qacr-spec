#!/usr/bin/env python3
"""Does a spec that lags behind the current FR revision actually need re-issuing?

    spec-impact.py <generator dir> <product dir>

A spec cites the FR revision it was written against. Until now `spec-check.py` failed
any spec citing a superseded one, which meant every FR bump re-issued every spec — and
because a published revision is immutable, "re-issue" means a whole new revision of each,
ready documents included. At FR Rev 1.23 that was four documents re-cut to change a number
in a header row, when only one of them owned a requirement that had moved.

It also made the citation useless. If every spec must cite the current revision, the
citation is current by construction and can never tell a reader the thing they want to
know: whether this document has been checked against the requirements as they now stand.

So the citation is allowed to lag, and this guard asks the question that actually matters:
**of the requirements this spec traces to, did any of them change between the revision it
cites and the current one?**

  - none changed        -> the spec is still true. Print the lag; do not fail.
  - one or more changed -> FAIL. The spec was written against text that has since moved,
                           and it needs re-reading and re-issuing.
  - the cited revision cannot be resolved to a commit -> say so and do not fail. An honest
                           "not checked" is worth more than a false pass, and the generator
                           has only lived in this repository since Rev 1.23.

A requirement counts as changed if its text moved, its milestone moved, or it stopped
existing. A note-only change is reported but does not fail: notes carry meaning — FR-KIT-007's
window rule lives in one — but they also absorb the small editorial corrections that would
otherwise re-issue the whole spec set for nothing.
"""
import io, json, os, re, subprocess, sys

DIR, ROOT = sys.argv[1], sys.argv[2]
SPECDIR = os.path.join(ROOT, "specs")
SPECNAME = re.compile(r"^(QACR-APP-SPEC-\d{2}) Rev(\d+)\.(\d+)\.md$")
CITES = re.compile(r"QACR-APP-FR-01\s+Rev\s+(\d+\.\d+)")

fails, notes = [], []


def reqs_at(ref=None):
    """Every requirement as {id: (text, note, milestone)}, at a commit or on disk."""
    if ref is None:
        script = (f"const s=[...require({json.dumps(os.path.join(DIR,'reqs-part1.js'))}),"
                  f"...require({json.dumps(os.path.join(DIR,'reqs-part2.js'))})];"
                  "const o={};s.forEach(x=>x.reqs.forEach(r=>o[r[0]]=[r[1],r[3]||'',String(r[4])]));"
                  "console.log(JSON.stringify(o));")
        return json.loads(subprocess.check_output(["node", "-e", script]).decode())
    # From history: write both modules to a scratch dir and require them there.
    import tempfile
    prefix = subprocess.check_output(["git", "rev-parse", "--show-prefix"],
                                     cwd=DIR).decode().strip()
    with tempfile.TemporaryDirectory() as tmp:
        for part in ("reqs-part1.js", "reqs-part2.js"):
            blob = subprocess.run(["git", "show", f"{ref}:{prefix}{part}"],
                                  cwd=DIR, capture_output=True)
            if blob.returncode != 0:
                return None
            io.open(os.path.join(tmp, part), "wb").write(blob.stdout)
        script = (f"const s=[...require({json.dumps(os.path.join(tmp,'reqs-part1.js'))}),"
                  f"...require({json.dumps(os.path.join(tmp,'reqs-part2.js'))})];"
                  "const o={};s.forEach(x=>x.reqs.forEach(r=>o[r[0]]=[r[1],r[3]||'',String(r[4])]));"
                  "console.log(JSON.stringify(o));")
        out = subprocess.run(["node", "-e", script], capture_output=True)
        return json.loads(out.stdout.decode()) if out.returncode == 0 else None


def commit_for(revision):
    """The newest commit at which version.js declared this FR revision."""
    log = subprocess.run(["git", "log", "--format=%H", "--", "version.js"],
                         cwd=DIR, capture_output=True)
    if log.returncode != 0:
        return None
    prefix = subprocess.check_output(["git", "rev-parse", "--show-prefix"],
                                     cwd=DIR).decode().strip()
    for sha in log.stdout.decode().split():
        blob = subprocess.run(["git", "show", f"{sha}:{prefix}version.js"],
                              cwd=DIR, capture_output=True)
        if blob.returncode != 0:
            continue
        m = re.search(r'FR:\s*"(\d+\.\d+)"', blob.stdout.decode())
        if m and m.group(1) == revision:
            return sha
    return None


V = json.loads(subprocess.check_output(
    ["node", "-e",
     f"console.log(JSON.stringify(require({json.dumps(os.path.join(DIR,'version.js'))})))"]
).decode())
CURRENT = V["FR"]
now = reqs_at()

live = {}
for f in sorted(os.listdir(SPECDIR)) if os.path.isdir(SPECDIR) else []:
    m = SPECNAME.match(f)
    if not m:
        continue
    rev = (int(m.group(2)), int(m.group(3)))
    if m.group(1) not in live or rev > live[m.group(1)][0]:
        live[m.group(1)] = (rev, f)

print("Spec impact: does a lagging spec trace to anything that moved?\n")
for spec, (rev, fname) in sorted(live.items()):
    body = io.open(os.path.join(SPECDIR, fname), encoding="utf-8").read()
    cited = CITES.search(body)
    if not cited:
        continue
    cited = cited.group(1)
    if cited == CURRENT:
        print(f"   {spec}: cites Rev {cited} — current")
        continue

    # What this spec claims coverage of: traceability rows and *Traces:* lines.
    #
    # Line by line, not paragraph by paragraph. A markdown table is one paragraph whose
    # first line is the header — `| Feature | Requirements | Disposition |` — so matching
    # on the paragraph hides every trace row underneath it. The first run of this guard
    # reported SPEC-01 as having 0 traced requirements when it has 28, and passed.
    claims = set()
    for line in body.splitlines():
        head = line.strip()
        if head.startswith("*Traces:") or head.startswith("*Trace:") \
           or re.match(r"\|\s*F\d{2}\.\d", head):
            claims |= set(re.findall(r"FR-[A-Z]{3}-\d{3}", head))

    sha = commit_for(cited)
    then = reqs_at(sha) if sha else None
    if then is None:
        print(f"   {spec}: cites Rev {cited}, current is {CURRENT} — NOT CHECKED, "
              f"that revision predates this repository's history of the data modules")
        continue

    moved, note_only = [], []
    for rid in sorted(claims):
        a, b = then.get(rid), now.get(rid)
        if a is None:
            continue                      # issued since; a new trace, not a moved one
        if b is None:
            moved.append(f"{rid} (no longer a live requirement)")
        elif a[0] != b[0]:
            moved.append(f"{rid} (text)")
        elif a[2] != b[2]:
            moved.append(f"{rid} (milestone {a[2]} -> {b[2]})")
        elif a[1] != b[1]:
            note_only.append(rid)

    if moved:
        fails.append(f"{spec} Rev {rev[0]}.{rev[1]} cites FR Rev {cited}, and "
                     f"{len(moved)} requirement(s) it traces to have moved since: "
                     f"{', '.join(moved)}. Re-read it against the current text and issue "
                     f"a new revision — the citation is what tells a developer this "
                     f"document was checked against what they are building to")
        print(f"   {spec}: cites Rev {cited} — AFFECTED: {', '.join(moved)}")
    else:
        extra = f"; note-only changes to {', '.join(note_only)}" if note_only else ""
        print(f"   {spec}: cites Rev {cited}, current is {CURRENT} — none of its "
              f"{len(claims)} traced requirements moved, so no re-issue is owed{extra}")
        if note_only:
            notes.append(f"{spec}: notes changed on {', '.join(note_only)} — read them "
                         f"before the next revision, but they do not force one")

print()
for n in notes:
    print(f"   note: {n}")
if fails:
    print("\nFAILED")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print("no lagging spec traces to a requirement that has moved")
