#!/usr/bin/env python3
"""Runs every guard, with filenames derived from version.js.

    npm run check

Exits non-zero if anything disagrees. Nothing here is advisory: a failure means the
documents are internally inconsistent and must not be circulated.
"""
import json, os, subprocess, sys

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)

V = json.loads(subprocess.check_output(
    ["node", "-e", f"console.log(JSON.stringify(require({json.dumps(os.path.join(DIR,'version.js'))})))"]
).decode())

# The deliverables are built straight into the directories the shared repository reads
# them from, so these paths are the built output AND the published artefact — there is no
# second copy anywhere for the two to disagree about.
FR = os.path.join(ROOT, "FR-01", f"QACR-APP-FR-01 Functional Requirements Rev{V['FR']}.docx")
EP = os.path.join(ROOT, "EPIC-01", f"QACR-APP-EPIC-01 Epic and Feature Map Rev{V['EPIC']}.docx")
BD = os.path.join(ROOT, "EPIC-01", "QACR-APP-EPIC-01 Board.html")
SPECS = os.path.join(ROOT, "specs")

missing = [p for p in (FR, EP, BD) if not os.path.exists(p)]
if missing:
    print("These do not exist — run `npm run build` first:")
    for p in missing:
        print("   ", os.path.basename(p))
    sys.exit(1)

failed = []


def run(label, argv):
    # flush before handing stdout to the child, or the headers land after its output
    print(f"\n{'='*68}\n{label}\n{'='*68}", flush=True)
    r = subprocess.run(argv, cwd=DIR)
    if r.returncode != 0:
        failed.append(label)


# First, because every guard below reads a file this one proves is the right file. A
# document at the wrong revision passes every internal check it has, since each half is
# internally consistent; only the layout says which revision was published.
run("Layout: the published documents are the revision version.js declares",
    [sys.executable, os.path.join(DIR, "layout-check.py"), DIR, ROOT])

run("Traceability and milestone consistency across both documents and the board",
    [sys.executable, os.path.join(DIR, "consistency-check.py"), DIR, FR, EP, BD])

if os.path.isdir(SPECS) and any(f.endswith(".md") for f in os.listdir(SPECS)):
    run("Spec coverage: every requirement of a covered feature is cited",
        [sys.executable, os.path.join(DIR, "spec-check.py"), SPECS])
    # After coverage, because it asks a question about the same traces: a spec is allowed
    # to cite a superseded FR revision, and only has to be re-issued if something it
    # traces to actually moved. See the module docstring for why that replaced failing
    # every lagging citation.
    run("Spec impact: no lagging spec traces to a requirement that has moved",
        [sys.executable, os.path.join(DIR, "spec-impact.py"), DIR, ROOT])
else:
    print("\nNo specs in specs/ yet — skipping the spec coverage checks.")

print(f"\n{'='*68}")
if failed:
    print("FAILED:")
    for f in failed:
        print("   -", f)
    sys.exit(1)
print(f"All guards pass. FR Rev {V['FR']}, epic map Rev {V['EPIC']}.")
