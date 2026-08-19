#!/usr/bin/env python3
"""Parse the PM's two Word documents in product/ into JSON alongside them.

    product/FR-01/QACR-APP-FR-01 Rev1.19.docx     -> product/FR-01/requirements.json
                                                     product/FR-01/decisions.json
                                                     product/FR-01/register.json
                                                     product/FR-01/appendices.json
    product/EPIC-01/QACR-APP-EPIC-01 Rev1.13.docx -> product/EPIC-01/features.json

The documents are the authority. This script never edits them, and the JSON is
never edited by hand — regenerate instead:

    python3 tools/parse_product_docs.py

Every parse is validated against counts the documents state about themselves. A
mismatch is REPORTED and the exit code is non-zero. It is never silently
corrected: if the parse and the document disagree, one of them is wrong and a
human decides which.

The documents state a great deal about themselves. In order of strength:

  Appendix H, Priority Summary  a 22-area by 6-milestone matrix, with a total per
                                row and per column. The strongest check here: it
                                pins every requirement's milestone by functional
                                area rather than only in total, so two errors in
                                opposite directions cannot net out.
  Review Register front matter  open items per group, and their total
  Appendix D.1-D.3 headings     each states its own row count
  section 2                     "This revision contains N requirements across M
                                functional areas"
  EPIC per-epic headers         requirements per epic
  EPIC section 3 roadmap cells  requirements each feature introduces there

Appendix H also states the document's own MILESTONE VOCABULARY, in its column
headings, so the vocabulary is read rather than hardcoded here. It grows: M5
arrived at Rev 1.19, and a reader holding a fixed 1|2|3|4|TBD set rendered a
sixth of the corpus as TBD without saying so.

Derived from vault-build/parse_rev119.py, successor to parse_rev15.py.
Structural notes carried over from there:

- requirement rows are  Id | Pri (milestone) | Feature | Requirement | Source | Notes
- an appendix is identified by WHAT IT IS, never by its letter; Rev 1.19 deleted
  the backlog appendix and re-lettered everything below it
- an appendix SUB-PART is identified by its position, and its letter is not
  required to agree: Rev 1.19's re-lettering reached the appendix titles and not
  their sub-headings, so Appendix E still numbers its parts F.1-F.3 and Appendix
  F numbers its parts G.1-G.3. A reader requiring agreement finds no sub-parts
- appendix table columns are read from each table's own header row rather than
  assumed by position: D.1-D.3 share a schema, D.4 does not, and the three
  configuration sub-parts have three different ones
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
BLID = re.compile(r"^BL-\d+$")
QID = re.compile(r"^Q-\d+$")

DASHES = ("-", "\u2014", "\u2013")


def only_docx(directory, stem):
    hits = sorted(f for f in os.listdir(directory)
                  if f.startswith(stem) and f.endswith(".docx"))
    if not hits:
        sys.exit(f"no {stem}*.docx in {directory}")
    if len(hits) > 1:
        sys.exit(f"more than one {stem} document in {directory}: {hits}")
    return os.path.join(directory, hits[0])


def revision_of(docx_path):
    """The revision is whatever the FILENAME says.

    Never a brief's `Traces to` header: a brief is written against the revision
    its author expects, which is routinely ahead of what product/ holds.

    A filename naming no revision is a HARD STOP, not a "?". This function is the
    single definition of which revision product/ holds, and five callers write its
    answer somewhere that gets committed — appendices.json, every feature file's
    provenance footer, coverage.tsv's extraction_scope, the change manifest, and
    the parse summary. A sentinel would put "Rev?" in all of them while the parse
    still exited zero, which is the exact failure this pipeline exists to prevent:
    "nobody knows" rendered indistinguishably from a known value.

    The pattern is deliberately narrow. A file called `... Rev 1.21 FINAL.docx`
    fails here rather than being read as Rev 1.21 — whether it is, is a human's
    call, not a regex's.
    """
    m = re.search(r"Rev\s*([\d.]+)\.docx$", os.path.basename(docx_path))
    if not m:
        sys.exit(f"cannot read a revision from '{os.path.basename(docx_path)}' — a "
                 f"product document's filename must end 'Rev<n>.docx'. That "
                 f"filename is the only record of which revision product/ holds, "
                 f"so it is not something this script may guess at.")
    return m.group(1)


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


def count_cell(cell):
    """A count cell in a document table. An em dash means zero, not missing."""
    c = norm(cell)
    if c in DASHES or c == "":
        return 0
    return int(c) if c.isdigit() else None


def split_source_refs(cell):
    """'RA 4.6; SPTA 2.5; SRS STM.4, STM.5' -> four refs, each carrying its prefix.

    Semicolons separate documents. A comma inside one clause continues the same
    document prefix ('SRS STM.4, STM.5' is two SRS references, not one).
    """
    cell = norm(cell)
    if not cell or cell in DASHES:
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


# --------------------------------------------------------------- the appendices
# An appendix is identified by WHAT IT IS, never by its letter. Rev 1.19 deleted
# "Backlog for Future Revisions" — its 42 rows became requirements at a new
# milestone 5 — and re-lettered everything below it: configs F->E, threat G->F,
# decisions I->G, priority J->H. A letter-keyed reader returned zero backlog rows
# AND zero decisions, which reads exactly like "the document dropped them".
# Titles are stable; letters are not. An appendix whose title matches nothing
# here is REPORTED, never ignored — that is how the next re-lettering, or a new
# appendix, announces itself instead of arriving as silence.
APPENDIX_ROLES = {
    "terminology": "terminology",
    "system parameters": "params",
    "traceability": "traceability",
    "requirements considered": "excluded",
    "backlog": "backlog",
    "application configuration register": "configs",
    "threat analysis": "threat",
    "decision log": "decisions",
    "priority summary": "priority",
}

# Which Appendix D sub-part is which, by POSITION. The sub-heading letters are
# not dependable (see the module docstring); the order of the parts is.
D_PARTS = {"1": "excluded", "2": "superseded", "3": "consolidated",
           "4": "unaccounted"}

# Roles this script turns into JSON. The others are recognised so that they are
# not reported as unknown, and their row counts are noted, so that nothing in
# the document is invisible to a reader of the parse.
LIST_ROLES = ("excluded", "superseded", "consolidated", "unaccounted",
              "configs", "params", "decisions", "backlog")


def appendix_role(title):
    t = norm(title).lower()
    for key, role in APPENDIX_ROLES.items():
        if t.startswith(key):
            return role
    return None


def col_key(header_cell):
    """'Risk Analysis impact' -> 'risk_analysis_impact'.

    Derived from the document's own header text, so a renamed or added column
    appears in the JSON as itself rather than being quietly mapped onto a name
    this script invented for it.
    """
    k = re.sub(r"[^a-z0-9]+", "_", norm(header_cell).lower()).strip("_")
    return k or "col"


def zip_row(keys, cells):
    """Zip a data row onto its own table's header keys.

    A cell the header does not account for is kept under its position rather
    than dropped: a column that appeared is a change to report, not to discard.
    """
    row = {k: norm(cells[i]) if i < len(cells) else "" for i, k in enumerate(keys)}
    for i in range(len(keys), len(cells)):
        if norm(cells[i]):
            row[f"undeclared_col{i + 1}"] = norm(cells[i])
    return row


# ------------------------------------------------------------------ FR document
def parse_fr(path):
    section = None        # current numbered section, ('4', 'Platform, ...')
    appendix = None       # current appendix LETTER — for reporting only
    role = None           # what that appendix IS
    part = None           # its sub-part number, positional
    register = None       # 'R' in the front matter, then 'R.1' .. 'R.6'
    reqs, dupes, stated = {}, [], {}

    lists = {k: [] for k in LIST_ROLES}
    register_rows, priority_rows = [], []
    part_titles = {}          # 'excluded.1' -> the sub-heading, verbatim
    stated_parts = {}         # 'excluded.1' -> the count that heading states
    stated_register = {}      # 'R.1 Priorities not assigned' -> 4
    headers, raw_headers = {}, {}
    unknown_appendices, stale_subparts, undeclared = [], [], []
    other_counts = Counter()  # rows under a role this script does not emit

    def table_key():
        if register:
            return ("register", register)
        if role:
            return (role, part)
        return None

    for kind, val in blocks(path):
        if kind == "p":
            m = re.match(r"^(\d{1,2})\.\s+(.*)", val)
            if m and int(m.group(1)) <= 25 and len(val) < 90:
                section = (m.group(1), m.group(2).strip())
                appendix, role, part, register = None, None, None, None
            elif val.startswith("Appendix"):
                section, register, part = None, None, None
                m = re.match(r"^Appendix ([A-Z])\s*[\u2013-]\s*(.*)", val)
                if m:
                    appendix = m.group(1)
                    role = appendix_role(m.group(2))
                    if role is None:
                        entry = f"{appendix} \u2014 {norm(m.group(2))}"
                        if entry not in unknown_appendices:
                            unknown_appendices.append(entry)
                else:
                    appendix, role = None, None
            elif appendix:
                # A sub-part is taken from its POSITION within the current
                # appendix. Its letter is not required to agree — Rev 1.19's
                # re-lettering never reached these headings, so Appendix E
                # numbers its parts F.1-F.3. Requiring agreement finds none.
                m = re.match(r"^([A-Z])\.(\d+)\s+(.+)$", val)
                if m and len(val) < 140:
                    part = m.group(2)
                    if m.group(1) != appendix:
                        stale = (f"Appendix {appendix} numbers a sub-part "
                                 f"{m.group(1)}.{part}")
                        if stale not in stale_subparts:
                            stale_subparts.append(stale)
                    if role:
                        which = D_PARTS.get(part, role) if role == "excluded" else role
                        pk = f"{which}.{part}"
                        part_titles[pk] = norm(m.group(3))
                        # 'D.1 Not Included in This Version — 15 requirements'
                        c = re.search(r"[\u2014\u2013-]\s*(\d+)\s+(?:requirement|row)",
                                      val)
                        if c:
                            stated_parts[pk] = int(c.group(1))
            elif (section is None and appendix is None
                  and val.startswith("Review Register")):
                register = "R"
            elif register:
                m = re.match(r"^R\.(\d+)\s", val)
                if m:
                    register = f"R.{m.group(1)}"

            m = re.search(r"This revision contains (\d+) requirements across (\d+) "
                          r"functional areas", val)
            if m:
                stated["requirements"] = int(m.group(1))
                stated["areas"] = int(m.group(2))
            continue

        cells = list(val)
        while cells and not cells[-1]:
            cells.pop()
        if not cells:
            continue
        c0 = norm(cells[0].split("\n")[0])

        # ---- a requirement row, and ONLY inside a numbered section. The Review
        # Register's R.1 table is keyed by requirement id as well, and it sits in
        # the front matter, where such a row would otherwise be indistinguishable
        # from a requirement.
        if section and role is None and register is None:
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
                "note": "" if note in DASHES else note,
                "feature": norm(cells[2]),
                "epic": "",
                "sha256": hashlib.sha256(text.encode("utf8")).hexdigest(),
            }
            continue

        key = table_key()
        if key is None:
            continue

        # ---- every appendix and register table is read through its OWN header
        if key not in headers:
            headers[key] = [col_key(c) for c in cells]
            raw_headers[key] = [norm(c) for c in cells]
            continue
        if [norm(c) for c in cells] == raw_headers[key]:
            continue                       # the header, repeated at a page break
        row = zip_row(headers[key], cells)
        if any(k.startswith("undeclared_col") for k in row):
            entry = (f"{key[0]}.{key[1]}: header is {raw_headers[key]} but a row "
                     f"carries {len(cells)} cells")
            if entry not in undeclared:
                undeclared.append(entry)

        if key[0] == "register":
            if register == "R":
                # front matter: 'R.4 Scope questions' | '11'
                n = count_cell(cells[1]) if len(cells) > 1 else None
                if n is not None:
                    stated_register[c0] = n
                continue
            row["ref"] = c0
            row["group"] = register
            register_rows.append(row)
            continue

        if role == "excluded":
            which = D_PARTS.get(part)
            # D.1 carries BL- ids as well as FR- ids: Rev 1.19 excluded BL-38
            # outright, and an FR-only matcher under-counted the appendix and
            # made a real scope decision look like a lost row.
            # D.2's first cell reads 'FR-ALG-008 (earlier wording)', so the id is
            # the leading token rather than the whole cell.
            if which is None:
                other_counts["Appendix D rows outside a sub-part"] += 1
            elif re.match(r"^(?:FR-[A-Z]{3}-\d{3}|BL-\d+)\b", c0):
                row["id"] = c0.split()[0]
                row["part"] = part
                lists[which].append(row)
            else:
                other_counts["Appendix D rows with no recognised identifier"] += 1
            continue

        if role == "decisions":
            if QID.match(c0):
                row["ref"] = c0
                lists["decisions"].append(row)
            else:
                other_counts["decision log rows with no Q- reference"] += 1
            continue

        if role == "priority":
            priority_rows.append([norm(c) for c in cells])
            continue

        if role in ("configs", "params", "backlog"):
            row["part"] = part
            lists[role].append(row)
            continue

        other_counts[f"Appendix {appendix} ({role})"] += 1

    meta = {
        "lists": lists,
        "register": register_rows,
        "priority_rows": priority_rows,
        "priority_header": raw_headers.get(("priority", None), []),
        "part_titles": part_titles,
        "stated_parts": stated_parts,
        "stated_register": stated_register,
        "unknown_appendices": unknown_appendices,
        "stale_subparts": stale_subparts,
        "undeclared": undeclared,
        "other_counts": other_counts,
    }
    return reqs, dupes, stated, meta


# ---------------------------------------------------------------- EPIC document
# '\u00b7 M3\u2013M5 \u00b7 31 requirements, 8 future development'. The second number is a
# separate statement the epic makes about itself: how many of its requirements
# sit at the last milestone. Rev 1.20 moved E02's from 7 to 8, and nothing else
# in either document says so.
EPIC_HEAD = re.compile(
    r"\u00b7\s*M(\d+)(?:\u2013M(\d+))?\s*\u00b7\s*(\d+) requirements"
    r"(?:,\s*(\d+) future development)?")
ROADMAP_MS = re.compile(r"^3\.\d Milestone (\d+)")
# The milestone vocabulary is NOT fixed here. M5 arrived at Rev 1.19, and a
# reader holding M[1-4] grouped every M5 line under the previous heading without
# saying so. The token is matched openly and validated against the vocabulary
# Appendix H of the FR document states about itself.
REQ_MS = re.compile(r"^(M\d+|TBD|Deferred)\b[\s:\u2013-]*(.*)")


def parse_epic(path):
    epics, features = {}, {}
    cur_epic, in_catalogue, sec = None, False, None
    stated_epic_counts, roadmap, road_ms = {}, [], None
    stated_future_dev = {}
    seen_ms = set()
    for kind, val in blocks(path):
        if kind == "p":
            if re.match(r"^\d(\.\d+)?[\.\s]", val) and len(val) < 90:
                sec = val[:60]
                if re.match(r"^\d\.\s", val):
                    in_catalogue = val.startswith("6.")
            if val.startswith("Appendix"):
                in_catalogue, cur_epic = False, None
            # section 3 Milestone Roadmap: one row per (milestone, epic) with the
            # features first needed there and the count of requirements they
            # introduce at that milestone.
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
                    if m.group(4) is not None:
                        stated_future_dev[cur_epic] = int(m.group(4))
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
            domains = [d.strip() for d in re.split(r"[\u00b7,]", body_lines[0])
                       if d.strip()]
            body_lines = body_lines[1:]

        ids, milestones, cur_m = [], [], None
        for line in cells[4].split("\n"):
            line = line.strip()
            mm = REQ_MS.match(line)
            rest = mm.group(2) if mm else line
            if mm:
                cur_m = mm.group(1)
                seen_ms.add(cur_m)
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
    return epics, features, stated_epic_counts, roadmap, seen_ms, stated_future_dev


# --------------------------------------------------------------------- validate
def priority_summary(header, rows):
    """Appendix H as data: the milestone vocabulary, then the matrix.

    The header reads  Area | <milestone> ... | Total | Comments  and the last row
    is the 'All areas' total. The vocabulary is read from between Area and Total
    rather than assumed here, because it grows.
    """
    if "Area" not in header or "Total" not in header:
        return None
    i_area, i_total = header.index("Area"), header.index("Total")
    vocab = [h for h in header[i_area + 1:i_total] if h]
    areas, totals = [], None
    for cells in rows:
        counts, bad = {}, False
        for j, ms in enumerate(vocab):
            k = i_area + 1 + j
            n = count_cell(cells[k]) if k < len(cells) else None
            if n is None:
                bad = True
            counts[ms] = n or 0
        stated_total = count_cell(cells[i_total]) if i_total < len(cells) else None
        # The area name comes from the column the HEADER calls 'Area', like every
        # other cell here. Reading it from cells[0] instead would go wrong the
        # moment the table gains a leading column — the same positional
        # assumption this parser exists to stop making.
        area = cells[i_area] if i_area < len(cells) else ""
        rec = {"area": area, "counts": counts, "total": stated_total,
               "unreadable": bad}
        if re.match(r"^All areas", area, re.I):
            totals = rec
        else:
            areas.append(rec)
    return {"milestones": vocab, "areas": areas, "all_areas": totals}


def validate(reqs, dupes, stated, epics, features, epic_counts, roadmap,
             seen_ms, future_dev, meta):
    problems, notes = [], []
    lists, register = meta["lists"], meta["register"]

    # ---- section 2's own sentence
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

    # ---- an appendix whose title matches no role. Never ignored: this is how a
    # re-lettering or a new appendix announces itself, rather than arriving as
    # zero rows, which is indistinguishable from the document dropping content.
    if meta["unknown_appendices"]:
        problems.append(f"appendix title matches no known role: "
                        f"{meta['unknown_appendices']}")
    for entry in meta["stale_subparts"]:
        notes.append(f"the document's own sub-numbering is stale — {entry}; parts "
                     f"are read by position, so the parse is unaffected")
    for entry in meta["undeclared"]:
        notes.append(f"a table grew a column: {entry}")
    for what, n in sorted(meta["other_counts"].items()):
        notes.append(f"{n} rows read but not emitted: {what}")

    # ---- Appendix H: the strongest statement the document makes about itself
    ps = priority_summary(meta["priority_header"], meta["priority_rows"])
    vocab = None
    if ps is None:
        problems.append("Appendix H (Priority Summary) was not parsed — its header "
                        "no longer reads 'Area | <milestone>... | Total'")
    else:
        vocab = ps["milestones"]
        notes.append(f"milestone vocabulary, from Appendix H's own columns: {vocab}")
        by_area_ms = Counter((r["section_number"], r["milestone"])
                             for r in reqs.values())
        by_ms = Counter(r["milestone"] for r in reqs.values())
        cells_checked = 0
        for row in ps["areas"]:
            m = re.match(r"^(\d{1,2})\.", row["area"])
            if not m:
                problems.append(f"Appendix H row does not name a section: "
                                f"{row['area']}")
                continue
            sec = m.group(1)
            if row["unreadable"]:
                problems.append(f"Appendix H area {sec} has a count cell that is "
                                f"neither a number nor a dash")
            for ms, n in row["counts"].items():
                got = by_area_ms[(sec, ms)]
                if got != n:
                    problems.append(f"Appendix H area {sec} milestone {ms}: the table "
                                    f"states {n}, the Pri column gives {got}")
                cells_checked += 1
            if row["total"] is not None and row["total"] != sum(row["counts"].values()):
                problems.append(f"Appendix H area {sec}: its stated row total "
                                f"{row['total']} is not the sum of its own cells "
                                f"({sum(row['counts'].values())})")
        notes.append(f"Appendix H matrix checked: {len(ps['areas'])} areas x "
                     f"{len(vocab)} milestones = {cells_checked} cells")
        if ps["all_areas"] is None:
            problems.append("Appendix H has no 'All areas' total row")
        else:
            for ms, n in ps["all_areas"]["counts"].items():
                if by_ms[ms] != n:
                    problems.append(f"Appendix H total for milestone {ms}: the table "
                                    f"states {n}, parse found {by_ms[ms]}")
            grand = ps["all_areas"]["total"]
            if grand is not None and grand != len(reqs):
                problems.append(f"Appendix H states {grand} requirements in total, "
                                f"parse found {len(reqs)}")

    # ---- the milestone vocabulary, validated rather than assumed
    known = set(vocab) if vocab else {"1", "2", "3", "4", "5", "TBD"}
    bad_ms = sorted(r["id"] for r in reqs.values() if r["milestone"] not in known)
    if bad_ms:
        problems.append(f"{len(bad_ms)} requirements with a Pri value outside the "
                        f"document's own vocabulary {sorted(known)}: {bad_ms[:8]}")
    epic_ms = {m[1:] for m in seen_ms if m.startswith("M")}
    unknown_epic_ms = sorted(epic_ms - known)
    if unknown_epic_ms:
        problems.append(f"the epic map groups requirements under milestones the FR "
                        f"document does not list: {unknown_epic_ms}")

    no_feature = sorted(r["id"] for r in reqs.values() if not FID.match(r["feature"]))
    if no_feature:
        problems.append(f"{len(no_feature)} requirements with no valid feature in the "
                        f"FR document: {no_feature[:8]}")

    # ---- Appendix D: each of D.1-D.3 states its own row count in its heading
    for which in ("excluded", "superseded", "consolidated", "unaccounted"):
        part = next((p for p, w in D_PARTS.items() if w == which), None)
        pk = f"{which}.{part}"
        got = len(lists[which])
        want = meta["stated_parts"].get(pk)
        title = meta["part_titles"].get(pk, "")
        if want is None:
            notes.append(f"Appendix D.{part} ({which}): {got} rows; its heading "
                         f"states no count")
        elif want != got:
            problems.append(f"Appendix D.{part} heading states {want} — {title} — "
                            f"parse found {got}")
        else:
            notes.append(f"Appendix D.{part} ({which}): {got} rows, as its heading "
                         f"states")

    # ---- the Review Register front matter states its open items per group
    got_groups = Counter(r["group"] for r in register)
    for label, want in sorted(meta["stated_register"].items()):
        m = re.match(r"^(R\.\d+)", label)
        if m:
            got = got_groups[m.group(1)]
            if got != want:
                problems.append(f"Review Register {label}: the front matter states "
                                f"{want} open items, parse found {got}")
        elif re.match(r"^All groups", label, re.I):
            if want != len(register):
                problems.append(f"Review Register states {want} open items in total, "
                                f"parse found {len(register)}")
    if not meta["stated_register"]:
        problems.append("the Review Register front-matter count table was not found")
    notes.append(f"Review Register: {len(register)} open items over "
                 f"{len(got_groups)} groups {dict(sorted(got_groups.items()))}")
    notes.append(f"Decision Log: {len(lists['decisions'])} closed decisions")
    notes.append(f"Application Configuration Register: {len(lists['configs'])} "
                 f"configurations; System Parameters: {len(lists['params'])}")

    # ---- cross-document: the epic map claims every FR requirement appears once
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
    # An id the epic map names that the FR body has not got is a ghost — unless
    # Appendix D accounts for it, which is a documented disposition rather than a
    # requirement that went missing.
    accounted = {r["id"] for k in ("excluded", "superseded", "consolidated",
                                   "unaccounted") for r in lists[k]}
    ghost = sorted(r for r in feat_of if r not in reqs and r not in accounted)
    if ghost:
        problems.append(f"{len(ghost)} ids named by the epic map that are in neither "
                        f"the FR body nor Appendix D: {ghost[:8]}")
    excused = sorted(r for r in feat_of if r not in reqs and r in accounted)
    if excused:
        notes.append(f"{len(excused)} ids the epic map still names which Appendix D "
                     f"accounts for: {excused[:8]}")

    # ---- per-epic requirement counts the epic headers state about themselves
    got = Counter()
    for f in features.values():
        got[f["epic"]] += sum(1 for r in f["requirements"] if r.startswith("FR-"))
    for eid in sorted(epic_counts):
        if epic_counts[eid] != got[eid]:
            problems.append(f"{eid} header states {epic_counts[eid]} requirements, "
                            f"its feature table carries {got[eid]}")
    notes.append(f"per-epic header counts checked: {len(epic_counts)} epics")

    # ---- each epic header states a SECOND count about itself: how many of its
    # requirements sit at the last milestone — "31 requirements, 8 future
    # development". Rev 1.20 moved E02's from 7 to 8 and nothing else in either
    # document says so. Which milestone counts as "future development" is derived
    # from the vocabulary rather than named here; writing M5 in would reintroduce
    # the fixed-vocabulary trap one level up.
    numeric = sorted((int(m) for m in known if m.isdigit()), reverse=True)
    if future_dev and numeric:
        last = str(numeric[0])
        got_fd = Counter(r["epic"] for r in reqs.values() if r["milestone"] == last)
        for eid in sorted(future_dev):
            if future_dev[eid] != got_fd[eid]:
                problems.append(f"{eid} header states {future_dev[eid]} future "
                                f"development requirements, the Pri column gives "
                                f"{got_fd[eid]} at M{last}")
        notes.append(f"'future development' counts checked against M{last}: "
                     f"{len(future_dev)} epics, {sum(future_dev.values())} "
                     f"requirements")
    elif not future_dev:
        notes.append("no epic header states a 'future development' count")

    # ---- section 3 roadmap: each cell states how many requirements the features
    # FIRST NEEDED at that milestone introduce there. Not the same population as
    # "every requirement of this epic at this Pri" — a feature that starts at M1
    # keeps carrying M3 rows.
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
    fr_rev, epic_rev = revision_of(fr_path), revision_of(epic_path)
    print(f"FR   : {os.path.basename(fr_path)}")
    print(f"EPIC : {os.path.basename(epic_path)}\n")

    reqs, dupes, stated, meta = parse_fr(fr_path)
    epics, features, epic_counts, roadmap, seen_ms, future_dev = parse_epic(epic_path)

    # the epic a requirement belongs to is the epic of its feature
    epic_of_feature = {f["id"]: f["epic"] for f in features.values()}
    for r in reqs.values():
        r["epic"] = epic_of_feature.get(r["feature"], "")

    problems, notes = validate(reqs, dupes, stated, epics, features,
                               epic_counts, roadmap, seen_ms, future_dev, meta)
    for n in notes:
        print("note    ", n)
    for p in problems:
        print("MISMATCH", p)

    def write(path, obj):
        # UTF-8 explicitly, not the platform default. These files are dumped with
        # ensure_ascii=False and the documents are full of en and em dashes, so a
        # cp1252 default would raise UnicodeEncodeError rather than write them.
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)

    lists = meta["lists"]
    write(os.path.join(FR_DIR, "requirements.json"), [reqs[k] for k in sorted(reqs)])
    write(os.path.join(EPIC_DIR, "features.json"),
          [features[k] for k in sorted(features)])
    # The section 3 roadmap is validated on every parse, but it is also a thing
    # that CHANGES — Rev 1.20 moved E02's milestone-3 cell from 14 to 16 — and a
    # manifest cannot report a change to a table nobody persisted.
    write(os.path.join(EPIC_DIR, "roadmap.json"),
          sorted(roadmap, key=lambda c: (c["epic"], int(c["milestone"]))))
    # The Decision Log and the Review Register get a file each, under the
    # document's own name for them, because they are read on their own.
    write(os.path.join(FR_DIR, "decisions.json"), lists["decisions"])
    write(os.path.join(FR_DIR, "register.json"), meta["register"])
    write(os.path.join(FR_DIR, "appendices.json"), {
        "revision": fr_rev,
        "part_titles": meta["part_titles"],
        "excluded": lists["excluded"],
        "superseded": lists["superseded"],
        "consolidated": lists["consolidated"],
        "unaccounted": lists["unaccounted"],
        "configs": lists["configs"],
        "params": lists["params"],
        "backlog": lists["backlog"],
        "priority_summary": priority_summary(meta["priority_header"],
                                             meta["priority_rows"]),
    })

    print(f"\nFR-01 Rev {fr_rev} \u00b7 EPIC-01 Rev {epic_rev}")
    print(f"wrote {len(reqs)} requirements and {len(features)} features "
          f"across {len(epics)} epics")
    print(f"      {len(lists['decisions'])} closed decisions, "
          f"{len(meta['register'])} open register items, "
          f"{len(lists['configs'])} configurations, {len(lists['params'])} parameters")
    print(f"      Appendix D: {len(lists['excluded'])} excluded, "
          f"{len(lists['superseded'])} superseded, "
          f"{len(lists['consolidated'])} consolidated, "
          f"{len(lists['unaccounted'])} unaccounted")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
