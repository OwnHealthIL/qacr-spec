"""Coverage check for the spec layer: every requirement belonging to a covered
feature must be cited somewhere in the spec, and every FR cited must belong to a
covered feature."""
import re, json, subprocess, sys, glob, os

DIR = "."
truth = json.loads(subprocess.check_output(["node","-e",f"""
const E=require('{DIR}/epics.js');
const s=[...require('{DIR}/reqs-part1.js'),...require('{DIR}/reqs-part2.js')];
const A=require('{DIR}/appendices.js');
const R={{}}; s.forEach(x=>x.reqs.forEach(r=>R[r[0]]=r[4]));
const BL={{}};   // the backlog was emptied at Rev 1.18
const feat={{}}; E.forEach(e=>e.features.forEach(f=>feat[f[0]]={{fr:f[2],bl:f[3],epic:e.code}}));
console.log(JSON.stringify({{feat,pri:R,bl:BL}}));
"""]).decode())
FEAT, PRI, BL = truth["feat"], truth["pri"], truth["bl"]

# A spec cites the revisions it was written against, in its header table and again in
# its closing line. Those citations are the spec's own traceability claim, so they must
# name the current documents: a reader sent to a superseded revision may be reading
# requirement text that has since changed. Nothing checked these until the pilots were
# found still citing FR Rev 1.16 and epic map Rev 1.10.
V = json.loads(subprocess.check_output(
    ["node", "-e", f"console.log(JSON.stringify(require('{DIR}/version.js')))"]).decode())
REVPAT = re.compile(r"QACR-APP-(FR|EPIC)-01\s+Rev\s+(\d+\.\d+)")

# Every identifier ever issued, with its disposition. Used to tell a retired identifier,
# which a spec may legitimately discuss, from one that never existed.
MANIFEST = json.load(open(os.path.join(DIR, "id-manifest.json"), encoding="utf-8"))["issued"]

SPAT = r"\*\*S\d{2}\.\d{2}\*\*"
NPAT = r"\*\*S\d{2}\.(\d{2})\*\*"
# The spec directory is shared with the development team, whose rule is to keep every
# revision that has been built against — so it holds QACR-APP-SPEC-01 Rev1.2 beside
# Rev1.3, and a plain glob would check both. A superseded revision cites the FR revision
# that was current when it was written, so checking it fails the run for being exactly
# what it is: history. The highest revision of each document is the live one.
#
# It also holds a README, and anything that is not a QACR-APP-SPEC-nn document is not a
# spec. Globbing *.md and demanding a 'Features covered' row of whatever turns up makes
# every future note added to the directory a build failure.
def _live_specs(directory):
    SPECNAME = re.compile(r"^(QACR-APP-SPEC-\d{2}) Rev(\d+)\.(\d+)\.md$")
    live, skipped = {}, []
    for path in sorted(glob.glob(os.path.join(directory, "*.md"))):
        m = SPECNAME.match(os.path.basename(path))
        if not m:
            skipped.append(os.path.basename(path))
            continue
        key, rev = m.group(1), (int(m.group(2)), int(m.group(3)))
        if key not in live or rev > live[key][0]:
            live[key] = (rev, path)
    if skipped:
        print("   not a spec document, not checked: " + ", ".join(skipped))
    superseded = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(directory, "*.md"))
        if SPECNAME.match(os.path.basename(p))
        and p not in {v[1] for v in live.values()})
    if superseded:
        print("   superseded revisions, not checked: " + ", ".join(superseded))
    return [live[k][1] for k in sorted(live)]


SPECS = _live_specs(sys.argv[1])
fails = []
for path in SPECS:
    txt = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    m = re.search(r"\| Features covered \|([^|]*)\|", txt)
    if not m:
        fails.append(f"{name}: no 'Features covered' row"); continue
    covered = re.findall(r"F\d{2}\.\d", m.group(1))
    unknown = [f for f in covered if f not in FEAT]
    if unknown: fails.append(f"{name}: unknown features {unknown}")
    expect = set()
    for f in covered:
        if f in FEAT:
            expect |= set(FEAT[f]["fr"]) | set(FEAT[f]["bl"])
    cited = set(re.findall(r"FR-[A-Z]{3}-\d{3}", txt))   # BL identifiers no longer exist
    missing = sorted(x for x in expect - cited)
    extra   = sorted(x for x in cited - expect if x.startswith("FR-"))
    print(f"\n{name}")
    print(f"   features covered : {len(covered)}  -> {' '.join(covered)}")
    print(f"   requirements owed: {len(expect)}   cited: {len(cited & expect)}")
    sids = set(re.findall(SPAT, txt))
    print("   S-statements     : %d" % len(sids))
    # A trace must resolve. Coverage above only asks whether every owed requirement is cited;
    # it never asks whether a cited identifier exists. Rev 0.5 of SPEC-01 traced to
    # FR-CFG-006 and FR-CFG-007, which had been superseded to BL-35 and withdrawn, and
    # nothing complained. A trace to an identifier that is not a live requirement is worse
    # than a missing trace: it reads as coverage that is not there.
    #
    # Two different things, and only the first is a defect. A *trace* claims coverage, so it
    # must name a live requirement or backlog item. A *mention* in prose may legitimately
    # discuss a retired identifier — "superseded to BL-35", "withdrawn" — and a guard that
    # forbade that would force the document to be vaguer than the reader needs.
    claims = set()
    for para in re.split(r"\n\s*\n", txt):
        head = para.strip()
        is_trace = head.startswith("*Traces:") or head.startswith("*Trace:")
        is_trace_row = bool(re.match(r"\|\s*F\d{2}\.\d", head))
        if is_trace or is_trace_row:
            claims |= set(re.findall(r"FR-[A-Z]{3}-\d{3}", para))
            claims |= set(re.findall(r"BL-\d{2}", para))
    retired = sorted(x for x in claims
                     if (x.startswith("FR-") and x not in PRI)
                     or (x.startswith("BL-") and x not in BL))
    if retired:
        fails.append(f"{name}: traces to identifiers that are not live requirements or "
                     f"backlog items -> {retired}")
        print(f"   DEAD TRACE       : {retired}")

    # An identifier that was never issued at all is a typo or an invention, wherever it sits.
    unknown = sorted(x for x in cited
                     if x not in PRI and x not in BL and x not in MANIFEST)
    if unknown:
        fails.append(f"{name}: names identifiers that were never issued -> {unknown}")
        print(f"   UNKNOWN ID       : {unknown}")
    revs = REVPAT.findall(txt)
    if not revs:
        fails.append(f"{name}: cites no document revision, so it makes no traceability claim to check")
        print("   NO REVISION CITED")
    # A lagging citation is no longer a failure here. It used to be, and the effect was
    # that every FR bump re-issued every spec — and since a published revision is
    # immutable, a "re-issue" is a whole new revision of each document. At Rev 1.23 that
    # was four specs re-cut to change a number in a header row while only one of them
    # owned a requirement that had moved.
    #
    # It also made the citation say nothing. Forced to equal the current revision, it is
    # current by construction and can never tell a reader whether the document has been
    # checked against the requirements as they now stand.
    #
    # `spec-impact.py` asks the question that matters instead: of the requirements this
    # spec traces to, did any change between the cited revision and the current one? That
    # is what fails a build now. This check only reports the lag.
    stale = sorted({f"{d} Rev {r}" for d, r in revs if r != V[d]})
    if stale:
        print(f"   lags at          : {', '.join(stale)} — see spec-impact.py")
    elif revs:
        print(f"   traces to        : FR Rev {V['FR']}, EPIC Rev {V['EPIC']}")
    if missing:
        fails.append(f"{name}: owed but never cited -> {missing}")
        print(f"   MISSING          : {missing}")
    if extra:
        print(f"   cited from elsewhere (ok if cross-referenced): {extra}")
    # S-statement numbering must be contiguous
    nums = sorted(int(n) for n in re.findall(NPAT, txt))
    if nums and nums != list(range(1, len(nums)+1)):
        gaps = [i for i in range(1, max(nums)+1) if i not in nums]
        dup  = sorted({n for n in nums if nums.count(n) > 1})
        fails.append(f"{name}: S-statement numbering gaps={gaps} duplicates={dup}")

print("\n" + "="*60)
if fails:
    print("FAILURES")
    for f in fails: print("  -", f)
    sys.exit(1)
print("all specs: every covered requirement is cited, numbering is contiguous")
