#!/usr/bin/env python3
"""The change manifest for a revision: what actually changed, id by id.

    python3 tools/diff_revisions.py            # working tree against git HEAD
    python3 tools/diff_revisions.py --json M   # and write the manifest to M

Run it after `parse_product_docs.py` and BEFORE anything downstream is rebuilt.
A revision that adds requirements is routine; one that REMOVES or REASSIGNS them
changes what teams are building, and someone has to see that before the
repository starts asserting it.

git is the archive. The previous revision is read with `git show HEAD:<path>`,
never from a `-rev119` copy left beside the current file — a copy gets read as
current, and this repository has version control precisely so it need not exist.

The null-diff rule
------------------
An empty structured diff does NOT mean nothing changed. Rev 1.17's entire
content was two corrected cover pages and one deleted legend row: invisible in
the parsed data, and reported by an earlier tool as "no changes". So when the
structured diff comes out empty, this script diffs the RAW document text and
requires every changed line to match a declared housekeeping pattern. A changed
line that matches none is reported, and the exit code is non-zero.
"""
import re
import os
import sys
import json
import difflib
import argparse
import subprocess
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from parse_product_docs import blocks, only_docx, revision_of, norm  # noqa: E402

FR_JSON = "product/FR-01/requirements.json"
EPIC_JSON = "product/EPIC-01/features.json"
DEC_JSON = "product/FR-01/decisions.json"
REG_JSON = "product/FR-01/register.json"
ROAD_JSON = "product/EPIC-01/roadmap.json"

# Every pattern a changed raw line may match and still count as housekeeping.
# The list is deliberately short and explicit: anything not named here is a
# content change that happened to leave the structured data untouched, which is
# the case this rule exists to catch.
HOUSEKEEPING = [
    (r"^Rev(ision)?\s*[\d.]+", "a revision number"),
    (r"^Version\b", "a version line"),
    (r"^\s*Date\b", "a date line"),
    (r"^\d{1,2}\s+\w+\s+\d{4}$", "a bare date"),
    (r"^(Prepared|Authored|Approved|Reviewed)\b", "a cover-page attribution"),
    (r"^Document (id|reference|number)\b", "a document reference"),
    (r"^QACR-APP-(FR|EPIC)-01\b", "a document title line"),
    (r"^(Pri|Priority)\s*[:=]", "a legend entry for the Pri column"),
    (r"^M[1-9]\b.{0,80}$", "a legend entry naming a milestone"),
    (r"^(Legend|Key)\b", "a legend heading"),
]


def git_show(path):
    """The file as HEAD holds it, or None where HEAD has not got it."""
    r = subprocess.run(["git", "-C", REPO, "show", f"HEAD:{path}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def old_json(path):
    raw = git_show(path)
    return None if raw is None else json.loads(raw.decode("utf8"))


def new_json(path, default=None):
    """The file as the working tree holds it, or `default` where it has not got it.

    UTF-8 explicitly, and through a context manager: these files are written with
    ensure_ascii=False and carry the documents' en and em dashes, so a cp1252
    platform default would fail to read back what the parser just wrote.
    """
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        return default
    with open(full, encoding="utf-8") as fh:
        return json.load(fh)


def by_id(rows, key="id"):
    return {r[key]: r for r in rows} if rows else {}


def diff_requirements(old, new):
    """Per requirement: added, removed, and each way one can change in place."""
    o, n = by_id(old), by_id(new)
    m = {k: [] for k in ("added", "removed", "text", "note", "milestone",
                         "feature", "source", "section")}
    for rid in sorted(set(n) - set(o)):
        r = n[rid]
        m["added"].append({"id": rid, "milestone": r["milestone"],
                           "feature": r["feature"], "epic": r["epic"],
                           "source": "; ".join(r["source_refs"]),
                           "text": r["text"]})
    for rid in sorted(set(o) - set(n)):
        r = o[rid]
        m["removed"].append({"id": rid, "milestone": r["milestone"],
                             "feature": r["feature"], "text": r["text"]})
    for rid in sorted(set(o) & set(n)):
        a, b = o[rid], n[rid]
        # sha256 of the text is carried in the parse, so a text change is exact
        # rather than a similarity judgement.
        if a["sha256"] != b["sha256"]:
            m["text"].append({"id": rid, "old": a["text"], "new": b["text"],
                              "similarity": round(difflib.SequenceMatcher(
                                  None, a["text"], b["text"]).ratio(), 3)})
        if a["note"] != b["note"]:
            m["note"].append({"id": rid, "old": a["note"], "new": b["note"]})
        if a["milestone"] != b["milestone"]:
            m["milestone"].append({"id": rid, "old": a["milestone"],
                                   "new": b["milestone"]})
        if a["feature"] != b["feature"]:
            m["feature"].append({"id": rid, "old": a["feature"],
                                 "new": b["feature"]})
        if a["source_refs"] != b["source_refs"]:
            m["source"].append({"id": rid, "old": "; ".join(a["source_refs"]),
                                "new": "; ".join(b["source_refs"])})
        if (a["section_number"], a["section_name"]) != \
           (b["section_number"], b["section_name"]):
            m["section"].append({"id": rid,
                                 "old": f"{a['section_number']}. {a['section_name']}",
                                 "new": f"{b['section_number']}. {b['section_name']}"})
    return m


def diff_features(old, new):
    o, n = by_id(old), by_id(new)
    m = {k: [] for k in ("added", "removed", "title", "requirements",
                         "milestones", "domains")}
    for fid in sorted(set(n) - set(o)):
        m["added"].append({"id": fid, "epic": n[fid]["epic"],
                           "title": n[fid]["title"]})
    for fid in sorted(set(o) - set(n)):
        m["removed"].append({"id": fid, "epic": o[fid]["epic"],
                             "title": o[fid]["title"]})
    for fid in sorted(set(o) & set(n)):
        a, b = o[fid], n[fid]
        if a["title"] != b["title"]:
            m["title"].append({"id": fid, "old": a["title"], "new": b["title"]})
        if a["requirements"] != b["requirements"]:
            gained = [r for r in b["requirements"] if r not in a["requirements"]]
            lost = [r for r in a["requirements"] if r not in b["requirements"]]
            if gained or lost:
                m["requirements"].append({
                    "id": fid, "epic": b["epic"], "gained": gained, "lost": lost,
                    "count": f"{len(a['requirements'])} -> {len(b['requirements'])}"})
        if a["milestones"] != b["milestones"]:
            m["milestones"].append({"id": fid, "old": a["milestones"],
                                    "new": b["milestones"]})
        if a["domains"] != b["domains"]:
            m["domains"].append({"id": fid, "old": a["domains"],
                                 "new": b["domains"]})
    return m


def epic_counts(features):
    c = Counter()
    for f in features or []:
        c[f["epic"]] += sum(1 for r in f["requirements"] if r.startswith("FR-"))
    return c


def epic_features(features):
    c = Counter()
    for f in features or []:
        c[f["epic"]] += 1
    return c


def diff_keyed(old, new, key, label_fields):
    """Added / removed / changed for a list keyed by one stable reference.

    A changed row carries WHICH fields moved and both values. Reporting only
    that a row changed is the same failure as reporting only a total: Rev 1.20
    rewrote the body of one open register question and left its id, its group and
    the row count alone, so every count stayed put.
    """
    o = {r[key]: r for r in old} if old else {}
    n = {r[key]: r for r in new} if new else {}
    out = {"added": [], "removed": [], "changed": []}
    for k in sorted(set(n) - set(o)):
        out["added"].append({key: k, **{f: n[k].get(f, "") for f in label_fields}})
    for k in sorted(set(o) - set(n)):
        out["removed"].append({key: k, **{f: o[k].get(f, "") for f in label_fields}})
    for k in sorted(set(o) & set(n)):
        if o[k] == n[k]:
            continue
        fields = {f: [o[k].get(f, ""), n[k].get(f, "")]
                  for f in sorted(set(o[k]) | set(n[k]))
                  if o[k].get(f, "") != n[k].get(f, "")}
        out["changed"].append({key: k, "fields": fields,
                               **{f: n[k].get(f, "") for f in label_fields}})
    return out


def print_changed(rows, key, label):
    for r in rows:
        print(f"  ~ {r[key]}  {label(r)}")
        for f, (a, b) in r["fields"].items():
            print(f"      {f}")
            print(f"        was: {a or '—'}")
            print(f"        now: {b or '—'}")


# ------------------------------------------------------------- the null-diff rule
def raw_text(docx_path):
    lines = []
    for kind, val in blocks(docx_path):
        if kind == "p":
            lines.append(norm(val))
        else:
            for c in val:
                for ln in c.split("\n"):
                    if norm(ln):
                        lines.append(norm(ln))
    return lines


def housekeeping_reason(line):
    for pat, why in HOUSEKEEPING:
        if re.match(pat, line, re.I):
            return why
    return None


def raw_diff(stem, directory):
    """Diff the document text between HEAD's copy and the working tree's.

    The only way Rev 1.17's changes were ever found. Returns (changed, unexplained).
    """
    new_path = only_docx(os.path.join(REPO, directory), stem)
    rel = os.path.relpath(new_path, REPO)
    old_blob = git_show(rel)
    if old_blob is None:
        # The filename carries the revision, so a new revision is a new path and
        # HEAD has not got it. Find the one HEAD did have.
        listing = subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only",
                                  f"HEAD:{directory}"], capture_output=True)
        cands = [l for l in listing.stdout.decode("utf8").splitlines()
                 if l.startswith(stem) and l.endswith(".docx")]
        if not cands:
            return None, None
        old_blob = git_show(f"{directory}/{cands[0]}")
        rel = f"{directory}/{cands[0]}"
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as fh:
        fh.write(old_blob)
        old_path = fh.name
    try:
        before, after = raw_text(old_path), raw_text(new_path)
    finally:
        os.unlink(old_path)
    changed = [l for l in difflib.unified_diff(before, after, lineterm="", n=0)
               if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    unexplained = [l for l in changed if housekeeping_reason(l[1:].strip()) is None]
    return changed, unexplained


# ------------------------------------------------------------------------ report
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", metavar="PATH",
                    help="also write the manifest here (not written by default: "
                         "a manifest in the tree goes stale, git holds the history)")
    args = ap.parse_args()

    new_reqs = new_json(FR_JSON, [])
    new_feats = new_json(EPIC_JSON, [])
    old_reqs, old_feats = old_json(FR_JSON), old_json(EPIC_JSON)
    if old_reqs is None:
        sys.exit(f"HEAD has no {FR_JSON} — nothing to diff against")

    fr_rev = revision_of(only_docx(os.path.join(REPO, "product", "FR-01"),
                                   "QACR-APP-FR-01"))
    ep_rev = revision_of(only_docx(os.path.join(REPO, "product", "EPIC-01"),
                                   "QACR-APP-EPIC-01"))

    reqs = diff_requirements(old_reqs, new_reqs)
    feats = diff_features(old_feats, new_feats)

    dec_new = new_json(DEC_JSON, [])
    reg_new = new_json(REG_JSON, [])
    dec_old, reg_old = old_json(DEC_JSON), old_json(REG_JSON)
    decisions = diff_keyed(dec_old, dec_new, "ref", ("question", "decision"))
    register = diff_keyed(reg_old, reg_new, "ref", ("group",))

    def road_cells(rows):
        return [{"cell": f"{r['epic']}@M{r['milestone']}",
                 "features": ", ".join(r["features"]),
                 "new_reqs": r["new_reqs"]} for r in (rows or [])]

    road_new = new_json(ROAD_JSON, [])
    road_old = old_json(ROAD_JSON)
    roadmap = diff_keyed(road_cells(road_old), road_cells(road_new), "cell",
                         ("features", "new_reqs"))

    W = 78
    print("=" * W)
    print(f"CHANGE MANIFEST      FR-01 Rev {fr_rev}  ·  EPIC-01 Rev {ep_rev}")
    print("=" * W)
    print(f"{len(old_reqs):4d}  requirements before")
    print(f"{len(new_reqs):4d}  requirements after")
    for k, label in (("added", "added"), ("removed", "REMOVED"),
                     ("text", "text changed"), ("note", "note changed"),
                     ("milestone", "milestone moved"),
                     ("feature", "feature reassigned"),
                     ("source", "source changed"), ("section", "section moved")):
        print(f"{len(reqs[k]):4d}  {label}")

    # A roadmap-only change is still a structured change, and must not send this
    # off hunting for invisible edits in the raw text.
    structurally_empty = (not any(reqs.values()) and not any(feats.values())
                          and not any(roadmap.values())
                          and not any(decisions.values())
                          and not any(register.values()))

    if reqs["removed"]:
        # Loudest by design: nothing else in this pipeline notices that a
        # requirement quietly stopped existing.
        print("\n" + "!" * W)
        print(f"!! {len(reqs['removed'])} REQUIREMENT(S) REMOVED — a human must read "
              f"this before anything is rebuilt")
        print("!" * W)
        for r in reqs["removed"]:
            print(f"  {r['id']}  M{r['milestone']}  {r['feature']}")
            print(f"      {r['text'][:150]}")

    if reqs["added"]:
        print(f"\n--- ADDED ({len(reqs['added'])}) ---")
        for a in reqs["added"]:
            print(f"  {a['id']}  M{a['milestone']}  {a['feature']}  "
                  f"[{a['epic']}]  source: {a['source'] or '—'}")
            print(f"      {a['text']}")

    for k, label in (("text", "TEXT CHANGED"), ("note", "NOTE CHANGED")):
        if reqs[k]:
            print(f"\n--- {label} ({len(reqs[k])}) ---")
            for t in reqs[k]:
                extra = f"  similarity {t['similarity']}" if "similarity" in t else ""
                print(f"  {t['id']}{extra}")
                print(f"      was: {t['old'] or '—'}")
                print(f"      now: {t['new'] or '—'}")

    for k, label in (("milestone", "MILESTONE MOVED"),
                     ("feature", "FEATURE REASSIGNED"),
                     ("source", "SOURCE CHANGED"), ("section", "SECTION MOVED")):
        if reqs[k]:
            print(f"\n--- {label} ({len(reqs[k])}) ---")
            for t in reqs[k]:
                print(f"  {t['id']}  {t['old'] or '—'}  ->  {t['new'] or '—'}")

    # ---- the epic map
    oc, nc = epic_counts(old_feats), epic_counts(new_feats)
    of, nf = epic_features(old_feats), epic_features(new_feats)
    moved_epics = sorted(e for e in set(oc) | set(nc)
                         if oc[e] != nc[e] or of[e] != nf[e])
    print(f"\n--- EPIC MAP ---")
    print(f"  features: {len(old_feats or [])} -> {len(new_feats)}   "
          f"epics touched: {len(moved_epics)}")
    for e in moved_epics:
        print(f"  {e}: {oc[e]} -> {nc[e]} requirements, "
              f"{of[e]} -> {nf[e]} features")
    for f in feats["requirements"]:
        print(f"    {f['id']} ({f['epic']}) {f['count']}"
              + (f"  gained {f['gained']}" if f["gained"] else "")
              + (f"  LOST {f['lost']}" if f["lost"] else ""))
    for k, label in (("added", "features added"), ("removed", "FEATURES REMOVED"),
                     ("title", "titles changed"), ("milestones", "milestones changed"),
                     ("domains", "domains changed")):
        if feats[k]:
            print(f"  {label}: {[x['id'] for x in feats[k]]}")

    # ---- the section 3 milestone roadmap
    if road_old is None:
        print(f"\n--- MILESTONE ROADMAP ---\n  {len(road_new)} cells; HEAD has no "
              f"roadmap.json, so this is the first parse of it, not a diff")
    elif any(roadmap.values()):
        print(f"\n--- MILESTONE ROADMAP ({len(road_old)} -> {len(road_new)} cells): "
              f"{len(roadmap['added'])} added, {len(roadmap['removed'])} removed, "
              f"{len(roadmap['changed'])} changed ---")
        for c in roadmap["added"]:
            print(f"  + {c['cell']}  {c['new_reqs']} from {c['features']}")
        for c in roadmap["removed"]:
            print(f"  - {c['cell']}  was {c['new_reqs']} from {c['features']}")
        print_changed(roadmap["changed"], "cell", lambda c: "")
    else:
        print(f"\n--- MILESTONE ROADMAP ---\n  {len(road_new)} cells, unchanged")

    # ---- the decision log and the review register
    if dec_old is None:
        print(f"\n--- DECISION LOG ---\n  {len(dec_new)} closed decisions; HEAD has "
              f"no decisions.json, so this is the first parse of it, not a diff")
    else:
        print(f"\n--- DECISION LOG ({len(dec_old)} -> {len(dec_new)}): "
              f"{len(decisions['added'])} closed, {len(decisions['removed'])} gone, "
              f"{len(decisions['changed'])} reworded ---")
        for d in decisions["added"]:
            print(f"  + {d['ref']}  {d['question'][:110]}")
            print(f"        {d['decision'][:150]}")
        for d in decisions["removed"]:
            print(f"  - {d['ref']}  {d['question'][:110]}")
        print_changed(decisions["changed"], "ref", lambda d: d["question"][:100])
    if reg_old is None:
        print(f"\n--- REVIEW REGISTER ---\n  {len(reg_new)} open items; HEAD has no "
              f"register.json, so this is the first parse of it, not a diff")
    else:
        print(f"\n--- REVIEW REGISTER ({len(reg_old)} -> {len(reg_new)}): "
              f"{len(register['added'])} raised, {len(register['removed'])} closed, "
              f"{len(register['changed'])} reworded ---")
        for r in register["added"]:
            print(f"  + {r['ref']}  ({r['group']})")
        for r in register["removed"]:
            print(f"  - {r['ref']}  ({r['group']})  closed or withdrawn")
        print_changed(register["changed"], "ref", lambda r: f"({r['group']})")

    # ---- the null-diff rule
    unexplained_total, raw_changed_total = [], 0
    if structurally_empty:
        print("\n" + "=" * W)
        print("THE STRUCTURED DIFF IS EMPTY. That is not a result — it is a prompt")
        print("to look harder. Diffing the raw document text:")
        print("=" * W)
        for stem, directory in (("QACR-APP-FR-01", "product/FR-01"),
                                ("QACR-APP-EPIC-01", "product/EPIC-01")):
            changed, unexplained = raw_diff(stem, directory)
            if changed is None:
                print(f"  {stem}: HEAD holds no document to compare against")
                continue
            print(f"\n  {stem}: {len(changed)} changed raw lines, "
                  f"{len(unexplained)} not housekeeping")
            for l in changed:
                why = housekeeping_reason(l[1:].strip())
                mark = f"housekeeping — {why}" if why else "** NOT HOUSEKEEPING **"
                print(f"    {l[:110]}")
                print(f"        {mark}")
            unexplained_total += unexplained
            raw_changed_total += len(changed)
        if not raw_changed_total:
            print("\n  The document text is identical too. This is the same revision, "
                  "not a revision whose changes are invisible.")
        elif not unexplained_total:
            print("\n  Every changed line matches a declared housekeeping pattern.")

    manifest = {"fr_revision": fr_rev, "epic_revision": ep_rev,
                "requirements_before": len(old_reqs),
                "requirements_after": len(new_reqs),
                "requirements": reqs, "features": feats,
                "epics_touched": {e: {"requirements": [oc[e], nc[e]],
                                      "features": [of[e], nf[e]]}
                                  for e in moved_epics},
                "decisions": decisions, "register": register, "roadmap": roadmap,
                "structurally_empty": structurally_empty}
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=1, ensure_ascii=False)
        print(f"\nmanifest -> {args.json}")

    print("\n" + "=" * W)
    if reqs["removed"] or feats["removed"]:
        print("STOP AND READ: this revision removes requirements or features.")
    if unexplained_total:
        print(f"STOP AND READ: {len(unexplained_total)} changed raw lines match no "
              f"declared housekeeping pattern.")
        return 1
    print("Read the manifest against the documents before rebuilding anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
