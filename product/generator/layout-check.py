#!/usr/bin/env python3
"""The seam guard: what is published is the revision version.js declares.

    layout-check.py <generator dir> <product dir>

Every other guard in this repository reads a document and checks it against itself or
against the data. All of them pass on a document at the wrong revision, because each
half of a stale pair is internally consistent — the Rev 1.20 document agrees with the
Rev 1.20 data perfectly well. Nothing before this asked whether the document sitting
where the development team reads it is the one this repository just built.

That question did not exist while the deliverables lived in a working directory nobody
else read. It exists now, and this is the guard for it. Five checks:

  1. exactly one QACR-APP-FR-01*.docx under FR-01/, and its filename revision is
     version.js's FR. Two revisions in one directory has no answer to "which revision
     is this"; the shared repository's own parser refuses to run on it
  2. the same for the epic map under EPIC-01/
  3. no deliverable stranded at the product root. Before the move the build wrote its
     output there, so a copy left behind is a former deliverable that still looks current
  4. every spec filename's revision equals the Revision row inside the file. SPEC-02
     shipped to the development team at Rev 1.0 twice, with different text, because the
     content moved and the number did not: the filename is the only thing a reader of the
     directory sees, so it is the thing that has to be true
  5. one live revision per spec, and it is the highest. A tie or a gap means two files
     claim to be the same document
"""
import io, json, os, re, subprocess, sys

DIR, ROOT = sys.argv[1], sys.argv[2]

V = json.loads(subprocess.check_output(
    ["node", "-e",
     f"console.log(JSON.stringify(require({json.dumps(os.path.join(DIR,'version.js'))})))"]
).decode())

fails = []
checks = 0


def check(ok, message):
    global checks
    checks += 1
    if not ok:
        fails.append(message)


def sole_document(subdir, stem, declared):
    """One document, and the revision its filename states is the declared one."""
    d = os.path.join(ROOT, subdir)
    if not os.path.isdir(d):
        check(False, f"{subdir}/ does not exist — run `npm run build`")
        return
    hits = sorted(f for f in os.listdir(d)
                  if f.startswith(stem) and f.endswith(".docx"))
    check(len(hits) == 1,
          f"{subdir}/ holds {len(hits)} {stem} documents, expected exactly 1: {hits}")
    for f in hits:
        m = re.search(r"Rev\s*([\d.]+)\.docx$", f)
        check(bool(m), f"{subdir}/{f}: filename states no revision")
        if m:
            check(m.group(1) == declared,
                  f"{subdir}/{f} is Rev {m.group(1)}, version.js declares {declared} "
                  f"— built but not published, or published and not rebuilt")


sole_document("FR-01", "QACR-APP-FR-01", V["FR"])
sole_document("EPIC-01", "QACR-APP-EPIC-01", V["EPIC"])

# 3 · nothing stranded at the product root
stray = sorted(f for f in os.listdir(ROOT)
               if re.match(r"QACR-APP-(FR|EPIC)-01.*\.(docx|html)$", f))
check(not stray,
      "deliverables left at the product root — they are published from FR-01/ and "
      f"EPIC-01/ now, so these are former copies that still read as current: {stray}")

# 4 and 5 · the spec directory
SPECDIR = os.path.join(ROOT, "specs")
SPECNAME = re.compile(r"^(QACR-APP-SPEC-\d{2}) Rev(\d+)\.(\d+)\.md$")
REVROW = re.compile(r"^\|\s*Revision\s*\|\s*(\d+\.\d+)\b", re.M)

seen = {}
if os.path.isdir(SPECDIR):
    for f in sorted(os.listdir(SPECDIR)):
        if not f.endswith(".md") or f == "README.md":
            continue
        m = SPECNAME.match(f)
        check(bool(m), f"specs/{f}: not named 'QACR-APP-SPEC-nn Rev<major>.<minor>.md'")
        if not m:
            continue
        stated = f"{int(m.group(2))}.{int(m.group(3))}"
        body = io.open(os.path.join(SPECDIR, f), encoding="utf-8").read()
        row = REVROW.search(body)
        check(bool(row), f"specs/{f}: no 'Revision' row in its header table")
        if row:
            check(row.group(1) == stated,
                  f"specs/{f} says Revision {row.group(1)} inside — the filename is the "
                  f"only revision a reader of the directory sees, so they must agree")
        seen.setdefault(m.group(1), []).append((int(m.group(2)), int(m.group(3)), f))

for spec, revs in sorted(seen.items()):
    top = max(revs)
    check(len([r for r in revs if r[:2] == top[:2]]) == 1,
          f"{spec}: two files claim revision {top[0]}.{top[1]}")
    print(f"   {spec}: live {top[2]}" +
          (f"  (+{len(revs)-1} superseded)" if len(revs) > 1 else ""))

# 6 · a published spec revision is immutable
#
# Checks 4 and 5 catch a filename and a body that disagree. They cannot catch the
# defect that prompted this guard: SPEC-02's text was edited and its number left alone,
# so the filename and the body agreed with each other and both were wrong. Once the
# development team keeps every revision built against, the rule that closes it is that
# a revision, once committed, never changes again — an edit needs a new number, which is
# what makes the superseded copy beside it meaningful rather than decorative.
#
# git is the only thing that knows this, so this is the one check that asks it.
if os.path.isdir(SPECDIR):
    inside_repo = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                 cwd=SPECDIR, capture_output=True).returncode == 0
    if not inside_repo:
        print("   not a git work tree — immutability of published revisions not checked")
    else:
        rel = subprocess.check_output(["git", "rev-parse", "--show-prefix"],
                                      cwd=SPECDIR).decode().strip()
        changed = subprocess.run(
            ["git", "diff", "HEAD", "--name-only", "--", "."],
            cwd=SPECDIR, capture_output=True)
        touched = [os.path.basename(line) for line in
                   changed.stdout.decode().splitlines() if line.strip()]
        edited = [f for f in touched if SPECNAME.match(f)]
        check(not edited,
              "a published spec revision was edited in place — a revision that has been "
              "committed is what somebody built against, so a change needs a new number, "
              f"not new text under the old one: {sorted(edited)}")
        if not edited:
            print(f"   {len(seen)} spec documents, no published revision edited in place")

print(f"\n{checks} layout checks, FR Rev {V['FR']}, epic map Rev {V['EPIC']}")
if fails:
    print("\nFAILED:")
    for f in fails:
        print("   -", f)
    sys.exit(1)
print("the published documents are the revision version.js declares")
