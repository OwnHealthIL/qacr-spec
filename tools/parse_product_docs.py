#!/usr/bin/env python3
"""Parse the PM's two Word documents in product/ into JSON alongside them.

    product/FR-01/QACR-APP-FR-01 Rev1.19.docx     -> product/FR-01/requirements.json
    product/EPIC-01/QACR-APP-EPIC-01 Rev1.13.docx -> product/EPIC-01/features.json

The documents are the authority. This script never edits them, and the JSON is
never edited by hand — regenerate instead:

    python3 tools/parse_product_docs.py

Every parse is validated against counts the documents state about themselves
("This revision contains 241 requirements across 22 functional areas", the
per-milestone roadmap totals, the per-epic header counts). A mismatch is
REPORTED and the exit code is non-zero. It is never silently corrected: if the
parse and the document disagree, one of them is wrong and a human decides which.

Derived from vault-build/parse_rev119.py, successor to parse_rev15.py.
Structural notes carried over from there:

- requirement rows are  Id | Pri (milestone) | Feature | Requirement | Source | Notes
- an appendix is identified by WHAT IT IS, never by its letter; Rev 1.19
  deleted the backlog appendix and re-lettered everything below it
- the Epic and Feature Map is a separate document
"""
import re
import os
import sys
import json
import html
import hashlib
import zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FR_DIR = os.path.join(REPO, "product", "FR-01")
EPIC_DIR = os.path.join(REPO, "product", "EPIC-01")

T = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)
RID = re.compile(r"^FR-[A-Z]{3}-\d{3}$")
FID = re.compile(r"^F\d{2}\.\d+$")


def only_docx(directory, stem):
    hits = sorted(f for f in os.listdir(directory)
                  if f.startswith(stem) and f.endswith(".docx"))
    if not hits:
        sys.exit(f"no {stem}*.docx in {directory}")
    if len(hits) > 1:
        sys.exit(f"more than one {stem} document in {directory}: {hits}")
    return os.path.join(directory, hits[0])


def cell_text(tc):
    """Text of one table cell, paragraphs separated by newlines."""
    paras = []
    for p in re.findall(r"<w:p\b.*?</w:p>", tc, re.S):
        t = "".join(html.unescape(x) for x in T.findall(p.replace("<w:tab/>", "\t")))
        paras.append(t)
    return "\n".join(paras).strip()


def blocks(docx_path):
    """Document-order stream of ('p', text) and ('tr', [cells])."""
    with zipfile.ZipFile(docx_path) as z:
        x = z.read("word/document.xml").decode("utf8")
    out = []
    for m in re.finditer(r"<w:(p|tr)\b.*?</w:\1>", x, re.S):
        blk = m.group(0)
        if m.group(1) == "tr":
            out.append(("tr", [cell_text(c)
                               for c in re.findall(r"<w:tc\b.*?</w:tc>", blk, re.S)]))
        else:
            if "<w:tbl" in blk or "</w:tc>" in blk:
                continue
            t = "".join(html.unescape(x)
                        for x in T.findall(blk.replace("<w:tab/>", "\t"))).strip()
            if t:
                out.append(("p", t))
    return out


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def split_source_refs(cell):
    """'RA 4.6; SPTA 2.5; SRS STM.4, STM.5' -> four refs, each carrying its prefix.

    Semicolons separate documents. A comma inside one clause continues the same
    document prefix ('SRS STM.4, STM.5' is two SRS references, not one).
    """
    cell = norm(cell)
    if not cell or cell in ("-", "—", "–"):
        return []
    refs = []
    for clause in re.split(r"\s*;\s*", cell):
        clause = clause.strip().rstrip(".")
        if not clause:
            continue
        parts = [p.strip() for p in clause.split(",")]
        m = re.match(r"^([A-Za-z][A-Za-z\- ]*?)\s+(?:[A-Z]{2,4}\.)?\d+(?:\.\d+)?$",
                     parts[0])
        prefix = m.group(1).strip() if m else ""
        refs.append(parts[0])
        for p in parts[1:]:
            if not p:
                continue
            refs.append(f"{prefix} {p}" if prefix and
                        re.match(r"^(?:[A-Z]{2,4}\.)?\d+(?:\.\d+)?$", p) else p)
    return refs


# ------------------------------------------------------------------ FR document
def parse_fr(path):
    section = None
    reqs, dupes, stated = {}, [], {}
    for kind, val in blocks(path):
        if kind == "p":
            m = re.match(r"^(\d{1,2})\.\s+(.*)", val)
            if m and int(m.group(1)) <= 25 and len(val) < 90:
                section = (m.group(1), m.group(2).strip())
            elif val.startswith("Appendix"):
                section = None
            m = re.search(r"This revision contains (\d+) requirements across (\d+) "
                          r"functional areas", val)
            if m:
                stated["requirements"] = int(m.group(1))
                stated["areas"] = int(m.group(2))
            continue

        cells = list(val)
        while cells and not cells[-1]:
            cells.pop()
        if not cells or not section:
            continue
        c0 = cells[0].strip()
        if not RID.match(c0):
            continue
        if c0 in reqs:
            dupes.append(c0)
            continue
        cells += [""] * (6 - len(cells))
        text = norm(cells[3])
        note = norm(cells[5])
        reqs[c0] = {
            "id": c0,
            "text": text,
            "section_number": section[0],
            "section_name": section[1],
            "milestone": norm(cells[1]),
            "source_refs": split_source_refs(cells[4]),
            "note": "" if note in ("—", "-", "–") else note,
            "feature": norm(cells[2]),
            "epic": "",
            "sha256": hashlib.sha256(text.encode("utf8")).hexdigest(),
        }
    return reqs, dupes, stated


# ---------------------------------------------------------------- EPIC document
EPIC_HEAD = re.compile(r"·\s*M(\d)(?:–M(\d))?\s*·\s*(\d+) requirements")
ROADMAP_MS = re.compile(r"^3\.\d Milestone (\d)")


def parse_epic(path):
    epics, features = {}, {}
    cur_epic, in_catalogue, sec = None, False, None
    stated_epic_counts, roadmap, road_ms = {}, [], None
    for kind, val in blocks(path):
        if kind == "p":
            if re.match(r"^\d(\.\d+)?[\.\s]", val) and len(val) < 90:
                sec = val[:60]
                if re.match(r"^\d\.\s", val):
                    in_catalogue = val.startswith("6.")
            if val.startswith("Appendix"):
                in_catalogue, cur_epic = False, None
            # §3 Milestone Roadmap: one row per (milestone, epic) with the features
            # first needed there and the count of requirements they introduce.
            m = ROADMAP_MS.match(val)
            if m:
                road_ms = m.group(1)
            elif re.match(r"^3\.\d Future|^[4-9]\.", val) and len(val) < 90:
                road_ms = None
            m = re.match(r"^(E\d{2})\.\s+(.*)", val)
            if m:
                cur_epic = m.group(1)
                epics[cur_epic] = {"id": cur_epic, "title": m.group(2).strip()}
                continue
            if cur_epic and in_catalogue:
                m = EPIC_HEAD.search(val)
                if m and cur_epic not in stated_epic_counts:
                    stated_epic_counts[cur_epic] = int(m.group(3))
            continue

        cells = list(val)
        while cells and not cells[-1]:
            cells.pop()
        if not cells:
            continue
        c0 = cells[0].split("\n")[0].strip()

        if road_ms and re.match(r"^E\d{2}$", c0) and len(cells) >= 4 \
                and cells[3].strip().isdigit():
            roadmap.append({"milestone": road_ms, "epic": c0,
                            "features": re.findall(r"F\d{2}\.\d+", cells[2]),
                            "new_reqs": int(cells[3].strip())})
            continue

        if not (FID.match(c0) and cur_epic):
            continue

        cells += [""] * (5 - len(cells))
        body_lines = [l for l in cells[2].split("\n") if l.strip()]
        domains = []
        if body_lines and re.match(r"^(iOS|Android|Backend|Algo|Content|Process)",
                                   body_lines[0]):
            domains = [d.strip() for d in re.split(r"[·,]", body_lines[0]) if d.strip()]
            body_lines = body_lines[1:]

        ids, milestones, cur_m = [], [], None
        for line in cells[4].split("\n"):
            line = line.strip()
            mm = re.match(r"^(M[1-5]|TBD|Deferred)\b[\s:–-]*(.*)", line)
            rest = mm.group(2) if mm else line
            if mm:
                cur_m = mm.group(1)
                if cur_m not in milestones:
                    milestones.append(cur_m)
            for a, b in re.findall(r"\b(?:FR-)?([A-Z]{3}-\d{3})\b|\b(BL-\d+)\b", rest):
                ids.append(b if b else "FR-" + a)

        features[c0] = {
            "id": c0,
            "title": body_lines[0] if body_lines else "",
            "epic": cur_epic,
            "milestones": milestones,
            "domains": domains,
            "requirements": ids,
        }
    return epics, features, stated_epic_counts, roadmap


# --------------------------------------------------------------------- validate
def validate(reqs, dupes, stated, epics, features, epic_counts, roadmap):
    problems, notes = [], []

    notes.append(f"FR document states {stated.get('requirements', '?')} requirements "
                 f"across {stated.get('areas', '?')} functional areas")
    if stated.get("requirements") != len(reqs):
        problems.append(f"requirement count: document states "
                        f"{stated.get('requirements')}, parse found {len(reqs)}")
    areas = {r["id"][3:6] for r in reqs.values()}
    if stated.get("areas") != len(areas):
        problems.append(f"functional areas: document states {stated.get('areas')}, "
                        f"parse found {len(areas)}: {sorted(areas)}")
    if dupes:
        problems.append(f"duplicate requirement ids in the FR body: {sorted(set(dupes))}")

    bad_ms = sorted(r["id"] for r in reqs.values()
                    if r["milestone"] not in ("1", "2", "3", "4", "5", "TBD"))
    if bad_ms:
        problems.append(f"{len(bad_ms)} requirements with an unrecognised Pri value: "
                        f"{bad_ms[:8]}")
    no_feature = sorted(r["id"] for r in reqs.values() if not FID.match(r["feature"]))
    if no_feature:
        problems.append(f"{len(no_feature)} requirements with no valid feature in the "
                        f"FR document: {no_feature[:8]}")

    # cross-document: the epic map claims every FR requirement appears exactly once
    placed = Counter()
    feat_of = {}
    for f in features.values():
        for rid in f["requirements"]:
            if rid.startswith("FR-"):
                placed[rid] += 1
                feat_of[rid] = f["id"]
    missing = sorted(r for r in reqs if placed[r] == 0)
    multi = sorted(r for r, n in placed.items() if n > 1)
    if missing:
        problems.append(f"{len(missing)} FR requirements appear in no feature of the "
                        f"epic map: {missing[:8]}")
    if multi:
        problems.append(f"{len(multi)} requirements appear in more than one feature: "
                        f"{multi[:8]}")
    clash = [(r, reqs[r]["feature"], feat_of[r]) for r in sorted(reqs)
             if r in feat_of and feat_of[r] != reqs[r]["feature"]]
    if clash:
        problems.append(f"{len(clash)} requirements whose Feature column disagrees with "
                        f"the epic map (id, FR doc, EPIC doc): {clash[:6]}")
    ghost = sorted(r for r in feat_of if r not in reqs)
    if ghost:
        problems.append(f"{len(ghost)} ids named by the epic map that are not in the "
                        f"FR body: {ghost[:8]}")

    # per-epic requirement counts the epic headers state about themselves
    got = Counter()
    for f in features.values():
        got[f["epic"]] += sum(1 for r in f["requirements"] if r.startswith("FR-"))
    for eid in sorted(epic_counts):
        if epic_counts[eid] != got[eid]:
            problems.append(f"{eid} header states {epic_counts[eid]} requirements, "
                            f"its feature table carries {got[eid]}")
    notes.append(f"per-epic header counts checked: {len(epic_counts)} epics")

    # §3 roadmap: each cell states how many requirements the features FIRST NEEDED at
    # that milestone introduce there. Not the same population as "every requirement of
    # this epic at this Pri" — a feature that starts at M1 keeps carrying M3 rows.
    by_feature = Counter()
    for r in reqs.values():
        by_feature[(r["feature"], r["milestone"])] += 1
    for cell in roadmap:
        got = sum(by_feature[(f, cell["milestone"])] for f in cell["features"])
        if got != cell["new_reqs"]:
            problems.append(
                f"roadmap M{cell['milestone']}/{cell['epic']} states "
                f"{cell['new_reqs']} new requirements from {cell['features']}; "
                f"the Pri column gives {got}")
    notes.append(f"roadmap cells checked: {len(roadmap)}, covering "
                 f"{sum(c['new_reqs'] for c in roadmap)} requirement introductions")
    notes.append("Pri distribution: "
                 f"{dict(sorted(Counter(r['milestone'] for r in reqs.values()).items()))}")
    return problems, notes


def main():
    fr_path = only_docx(FR_DIR, "QACR-APP-FR-01")
    epic_path = only_docx(EPIC_DIR, "QACR-APP-EPIC-01")
    print(f"FR   : {os.path.basename(fr_path)}")
    print(f"EPIC : {os.path.basename(epic_path)}\n")

    reqs, dupes, stated = parse_fr(fr_path)
    epics, features, epic_counts, roadmap = parse_epic(epic_path)

    # the epic a requirement belongs to is the epic of its feature
    epic_of_feature = {f["id"]: f["epic"] for f in features.values()}
    for r in reqs.values():
        r["epic"] = epic_of_feature.get(r["feature"], "")

    problems, notes = validate(reqs, dupes, stated, epics, features,
                               epic_counts, roadmap)
    for n in notes:
        print("note    ", n)
    for p in problems:
        print("MISMATCH", p)

    json.dump([reqs[k] for k in sorted(reqs)],
              open(os.path.join(FR_DIR, "requirements.json"), "w"),
              indent=1, ensure_ascii=False)
    json.dump([features[k] for k in sorted(features)],
              open(os.path.join(EPIC_DIR, "features.json"), "w"),
              indent=1, ensure_ascii=False)
    print(f"\nwrote {len(reqs)} requirements and {len(features)} features "
          f"across {len(epics)} epics")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
