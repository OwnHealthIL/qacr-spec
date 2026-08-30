#!/usr/bin/env python3
"""Emit `features/<epic>/<feature>.md` for one published spec brief.

    python3 tools/build_feature_files.py SPEC-01

This is step 3 of `SDLC.md`, and it is deliberately a script rather than a
writing task. Every line it emits is either a fixed heading or a value copied
out of one of four files:

    product/specs/<brief>.md            what the spec decided — via SPECS below
    product/EPIC-01/features.json       which features exist, what each owns
    product/FR-01/requirements.json     the milestone per requirement
    evidence/behaviour.tsv              what the code does today, cited

Because nothing here is generated from judgement, running it twice on unchanged
inputs produces byte-identical files. That is the correctness test. A non-empty
`git diff -- features/` after a second run means something leaked in.

The second test is `validate()`, which runs before anything is written: every
id a SPECS entry names must be one `product/` actually holds. A brief routinely
lands ahead of the `product/` export and names requirements that have not been
exported yet — those must be declared `pending`, so that the feature file
reports them instead of coming up silently short.

## The SPECS table is step 1's output

Reading a brief *is* judgement — which features it covers, the disposition it
gives each one, which requirement each departure names as its driver. A regex
over the traceability table would be guessing at prose. So a human (or the
`spec-intake` skill) reads the brief once and records what it says here, where
it is version-controlled and reviewable in the PR alongside the files it
produced. Everything downstream of this table is mechanical.

`product/` is read-only, which is why this record lives beside the renderer
rather than beside the brief.

To publish a new brief: add one entry, run the script, read the diff. The
script refuses to write anything if the entry names an id `product/` has not
got and the entry has not acknowledged it.
"""
import collections
import csv
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# One definition of "which document is this, and what revision does it name".
from parse_product_docs import only_docx, revision_of  # noqa: E402

SPECS = {
    "SPEC-01": {
        "id": "QACR-APP-SPEC-01",
        # `product/specs/<file>`; the header link points here.
        "file": "QACR-APP-SPEC-01 Rev1.2.md",
        # The brief's own revision, from its header.
        "revision": "Rev 1.2",
        # What the brief's header claims it traces to. The provenance line
        # reports the revision actually rendered, and notes this one only where
        # the two diverge — see `provenance()`.
        "traces": {"FR-01": "1.19", "EPIC-01": "1.13"},
        # §2 Departures, keyed by the requirement each row names as its driver.
        "departures": {
            "FR-RDY-007": "departure D1",
            "FR-CFG-003": "departure D2",
        },
        # §5 Traceability, one entry per covered feature: the brief's own
        # disposition wording, and the requirements it answers for. A
        # requirement a feature owns but this list omits is `silent`.
        "features": {
            "F01.1": {
                "disposition": "as-is",
                "covers": ["FR-PLT-001", "FR-PLT-002", "FR-PLT-003",
                           "FR-PLT-004"],
            },
            "F01.2": {
                "disposition": "as-is",
                "covers": ["FR-PLT-005", "FR-RDY-002", "FR-RDY-003",
                           "FR-RDY-004"],
            },
            "F01.3": {
                "disposition": "as-is",
                "covers": ["FR-RDY-001"],
            },
            "F01.4": {
                "disposition": "as-is except D1 · U1 open",
                "covers": ["FR-RDY-005", "FR-RDY-006", "FR-RDY-007",
                           "FR-RDY-008", "FR-RDY-009", "FR-RDY-010"],
            },
            "F01.5": {
                "disposition": "as-is",
                "covers": ["FR-RDY-011", "FR-RDY-013", "FR-RDY-014",
                           "FR-SUP-003"],
            },
            "F01.6": {
                "disposition": "as-is",
                "covers": ["FR-RDY-012"],
            },
            "F01.8": {
                "disposition": "as-is",
                "covers": ["FR-PLT-008"],
            },
            "F01.9": {
                "disposition": "as-is except D2",
                "covers": ["FR-CFG-001", "FR-CFG-002", "FR-CFG-003",
                           "FR-CFG-006", "FR-CFG-004", "FR-CFG-008",
                           "FR-LCM-018"],
            },
        },
    },
    "SPEC-02": {
        "id": "QACR-APP-SPEC-02",
        "file": "QACR-APP-SPEC-02 Rev1.0.md",
        "revision": "Rev 1.0",
        "traces": {"FR-01": "1.20", "EPIC-01": "1.14"},
        # §2 Departures. D2's cell reads "FR-AUT-012, unchanged — see Q-101";
        # the requirement it names as the driver is FR-AUT-012.
        "departures": {
            "FR-AUT-003": "departure D1",
            "FR-AUT-012": "departure D2",
        },
        # §5 Traceability named four ids `product/` had not got at EPIC-01
        # Rev 1.13 / FR-01 Rev 1.19 — FR-AUT-021, -022, -023, -024 — and they
        # were declared `pending` so the feature files said so rather than
        # reading as complete. The Rev 1.14 / Rev 1.20 export landed those four
        # ids, the build failed until this map was emptied, and it is now gone.
        # That failure is the mechanism working: the declaration cannot outlive
        # what it describes without someone being told.
        "features": {
            "F02.1": {
                "disposition": "as-is except D1",
                "covers": ["FR-AUT-001", "FR-AUT-002", "FR-AUT-003",
                           "FR-AUT-023"],
            },
            "F02.2": {
                "disposition": "as-is",
                "covers": ["FR-AUT-004", "FR-AUT-005", "FR-AUT-018",
                           "FR-AUT-019", "FR-AUT-024"],
            },
            "F02.3": {
                "disposition": "as-is",
                "covers": ["FR-AUT-006"],
            },
            "F02.4": {
                "disposition": "as-is except D2",
                "covers": ["FR-AUT-008", "FR-AUT-010", "FR-AUT-012",
                           "FR-AUT-007", "FR-AUT-011", "FR-AUT-015",
                           "FR-AUT-020"],
            },
            "F02.5": {
                "disposition": "as-is · U1 open",
                "covers": ["FR-AUT-013", "FR-AUT-014", "FR-AUT-021",
                           "FR-AUT-022", "FR-SEC-008", "FR-COM-010"],
            },
            "F02.6": {
                "disposition": "as-is",
                "covers": ["FR-AUT-016"],
            },
            "F02.7": {
                "disposition": "as-is",
                "covers": ["FR-CNS-001", "FR-CNS-002", "FR-CNS-003",
                           "FR-CNS-005", "FR-CNS-006", "FR-CNS-007"],
            },
            "F02.8": {
                "disposition": "as-is",
                "covers": ["FR-AUT-017"],
            },
        },
    },
    "SPEC-03": {
        "id": "QACR-APP-SPEC-03",
        "file": "QACR-APP-SPEC-03 Rev1.1.md",
        "revision": "Rev 1.1",
        "traces": {"FR-01": "1.24", "EPIC-01": "1.18"},
        # §2 Departures, ten rows, keyed by the requirement each names as its
        # driver. Three requirements drive more than one row — FR-KIT-005 D5 and
        # D9, FR-KIT-007 D6, D9 and D10, FR-KIT-008 D3 and D4 — so a value may
        # name several. Five rows also name a driver no E03 feature owns — D2
        # FR-PLT-006, D7 FR-PRT-015, D8 FR-RDY-014 and FR-AUT-020, D10
        # FR-LCM-006 — which therefore render nowhere here and are recorded only
        # in this comment.
        "departures": {
            "FR-KIT-003": "departure D2",
            "FR-KIT-005": "departure D5, D9",
            "FR-KIT-007": "departure D6, D9, D10",
            "FR-KIT-008": "departure D3, D4",
            "FR-KIT-009": "departure D1",
        },
        # §5 Traceability. Each cell lists its M5 requirements after a "future
        # development at M5:" run-in; they are covered all the same, so `covers`
        # carries every id the cell names. U1 is the kit-identifier template
        # (register Q-104), open at the feature level as the brief states it.
        "features": {
            "F03.1": {
                "disposition": "as-is except D1 (M5), D2, D3, D4 · U1 open",
                "covers": ["FR-KIT-001", "FR-KIT-002", "FR-KIT-003",
                           "FR-KIT-008", "FR-KIT-009"],
            },
            "F03.2": {
                "disposition": "as-is except D5 (M5), D6, D7, D8, D9 (M5), D10",
                "covers": ["FR-KIT-004", "FR-KIT-007", "FR-KIT-005",
                           "FR-KIT-010"],
            },
        },
    },
}

# The §5 cells read "as-is except **D1** · U1 open" and "as-is except **D2**".
# The emphasis is the table's formatting rather than the wording, so the line
# is carried across without it.


def load_inputs():
    with open(os.path.join(ROOT, "product/EPIC-01/features.json")) as fh:
        features = {f["id"]: f for f in json.load(fh)}
    with open(os.path.join(ROOT, "product/FR-01/requirements.json")) as fh:
        requirements = {r["id"]: r for r in json.load(fh)}
    rows = collections.defaultdict(list)
    with open(os.path.join(ROOT, "evidence/behaviour.tsv"), newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            rid = row["requirement"].strip()
            if rid:
                rows[rid].append(row)
    return features, requirements, rows


def product_revisions():
    """The revision of each product document actually rendered.

    `features.json` and `requirements.json` carry no revision of their own —
    they are parsed out of the `.docx` beside them, and that filename is the
    only record of which revision they hold.

    Which file that is, and what revision it names, are `parse_product_docs`'s
    `only_docx()` and `revision_of()` — imported rather than reimplemented. This
    function used to glob `'<stem> Rev*.docx'`, which requires the revision to
    follow the stem immediately. Rev 1.19 arrived as `QACR-APP-FR-01 Rev1.19.docx`
    and Rev 1.20 as `QACR-APP-FR-01 Functional Requirements Rev1.20.docx`, so the
    glob found nothing while the parser found it: two definitions of "which
    document is this" that agreed until the PM renamed a file. One definition.
    """
    return {key: revision_of(only_docx(os.path.join(ROOT, folder), stem))
            for key, folder, stem in
            (("FR-01", "product/FR-01", "QACR-APP-FR-01"),
             ("EPIC-01", "product/EPIC-01", "QACR-APP-EPIC-01"))}


def provenance(spec, actual):
    """The brief, then each product document at the revision actually read.

    A brief states what it traces to; this line states what was rendered. The
    two diverge whenever a brief lands ahead of the `product/` export, and
    where they do the line carries both rather than repeating the brief's
    claim over data that is not there yet.
    """
    parts = [f"{spec['id']} {spec['revision']}"]
    for key in ("FR-01", "EPIC-01"):
        cited, read = spec["traces"][key], actual[key]
        parts.append(f"{key} Rev {read}"
                     + (f" (brief cites {cited})" if cited != read else ""))
    return " · ".join(parts)


def validate(spec, features, requirements):
    """Every id the SPECS entry names must exist in `product/`, or be `pending`.

    The renderer walks the requirements a feature owns, so an id the brief
    lists but `product/` has not got yet would otherwise be dropped in
    silence: the file comes out short by a requirement and still says
    `Nothing.` under *Not covered*, which reads as complete coverage. Fail
    instead, naming the ids, unless the entry declares them `pending`.
    """
    problems = []
    for fid, entry in spec["features"].items():
        if fid not in features:
            problems.append(f"{fid}: no such feature in features.json")
            continue
        owned = features[fid]["requirements"]
        pending = spec.get("pending", {}).get(fid, [])
        for rid in entry["covers"]:
            if rid not in owned and rid not in pending:
                problems.append(
                    f"{fid}: covers {rid}, which features.json does not give "
                    f"it — declare it in `pending` or correct the entry")
        for rid in pending:
            if rid in owned:
                problems.append(
                    f"{fid}: {rid} is declared `pending` but features.json now "
                    f"carries it — drop it from `pending`")
            if rid not in entry["covers"]:
                problems.append(
                    f"{fid}: {rid} is declared `pending` but is not in `covers`")
        for rid in owned:
            if rid not in requirements:
                problems.append(
                    f"{fid}: owns {rid}, which is not in requirements.json")
    if problems:
        sys.exit("SPECS entry does not agree with product/:\n  "
                 + "\n  ".join(problems)
                 + "\n\nEither product/ is behind the brief and needs "
                   "re-exporting, or the entry misreads the traceability table.")


def bullet(row):
    """One evidence row: status, claim and citation, each copied verbatim.

    A row whose source stated no status, or which is a negative claim with
    nothing to cite, simply loses that part — nothing is substituted for it.
    """
    parts = []
    if row["status"].strip():
        parts.append(f"**{row['status'].strip()}**")
    parts.append(row["claim"].strip())
    if row["citation"].strip():
        parts.append(f"`{row['citation'].strip()}`")
    return "- " + " — ".join(parts)


def render(spec, fid, feature, requirements, rows, actual):
    covers = spec["features"][fid]["covers"]
    owned = feature["requirements"]
    link = "../../product/specs/" + urllib.parse.quote(spec["file"])

    out = [f"# {fid} — {feature['title']}", ""]
    out.append(f"{feature['epic']} · {', '.join(feature['milestones'])} · "
               f"{', '.join(feature['domains'])} · [{spec['id']}]({link})")
    if spec["features"][fid].get("disposition"):
        out += ["", f"**Spec disposition:** {spec['features'][fid]['disposition']}"]

    out += ["", "## Requirements owned", "",
            "| Requirement | Milestone | Disposition | Evidence rows |",
            "|---|---|---|---|"]
    for rid in owned:
        if rid not in covers:
            disposition = "silent"
        else:
            disposition = spec["departures"].get(rid, "as-is")
        out.append(f"| {rid} | M{requirements[rid]['milestone']} | "
                   f"{disposition} | {len(rows.get(rid, []))} |")

    out.append("")
    out.append("## What the vault records about the code")
    for rid in owned:
        out += ["", f"### {rid}"]
        if not rows.get(rid):
            out += ["", "No rows recorded."]
            continue
        by_product = collections.OrderedDict()
        for row in rows[rid]:
            by_product.setdefault(row["product"].strip(), []).append(row)
        for product in sorted(by_product):
            out += ["", f"**{product}**", ""]
            out += [bullet(row) for row in by_product[product]]

    silent = sorted(set(owned) - set(covers))
    out += ["", "## Not covered by this spec", "",
            ", ".join(silent) if silent else "Nothing."]

    # Omitted entirely when the entry declares none, so a feature whose
    # requirements `product/` fully carries renders exactly as before.
    pending = sorted(spec.get("pending", {}).get(fid, []))
    if pending:
        out += ["", "## Named by this spec, absent from `product/`", "",
                ", ".join(pending), "",
                f"Listed for this feature in the brief's traceability table, "
                f"and not carried by EPIC-01 Rev {actual['EPIC-01']} / FR-01 "
                f"Rev {actual['FR-01']}. They render here once `product/` is "
                f"re-exported."]

    out += ["", "## Provenance", "", provenance(spec, actual), ""]
    return "\n".join(out)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SPECS:
        sys.exit(f"usage: {sys.argv[0]} <{'|'.join(sorted(SPECS))}>")
    spec = SPECS[sys.argv[1]]
    features, requirements, rows = load_inputs()
    validate(spec, features, requirements)
    actual = product_revisions()

    for fid in spec["features"]:
        feature = features[fid]
        path = os.path.join(ROOT, "features", feature["epic"], f"{fid}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render(spec, fid, feature, requirements, rows, actual))
        print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
