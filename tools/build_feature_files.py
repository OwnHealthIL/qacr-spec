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

## The SPECS table is step 1's output

Reading a brief *is* judgement — which features it covers, the disposition it
gives each one, which requirement each departure names as its driver. A regex
over the traceability table would be guessing at prose. So a human (or the
`spec-intake` skill) reads the brief once and records what it says here, where
it is version-controlled and reviewable in the PR alongside the files it
produced. Everything downstream of this table is mechanical.

`product/` is read-only, which is why this record lives beside the renderer
rather than beside the brief.

To publish a new brief: add one entry, run the script, read the diff.
"""
import collections
import csv
import json
import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPECS = {
    "SPEC-01": {
        "id": "QACR-APP-SPEC-01",
        # `product/specs/<file>`; the header link points here.
        "file": "QACR-APP-SPEC-01 Rev1.2.md",
        # The brief's revision and what it traces to, from its own header.
        "provenance": "QACR-APP-SPEC-01 Rev 1.2 · FR-01 Rev 1.19 · EPIC-01 Rev 1.13",
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


def render(spec, fid, feature, requirements, rows):
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
    out += ["", "## Provenance", "", spec["provenance"], ""]
    return "\n".join(out)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SPECS:
        sys.exit(f"usage: {sys.argv[0]} <{'|'.join(sorted(SPECS))}>")
    spec = SPECS[sys.argv[1]]
    features, requirements, rows = load_inputs()

    for fid in spec["features"]:
        feature = features[fid]
        path = os.path.join(ROOT, "features", feature["epic"], f"{fid}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render(spec, fid, feature, requirements, rows))
        print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
