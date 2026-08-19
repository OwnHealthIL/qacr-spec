#!/usr/bin/env python3
"""Bring `evidence/coverage.tsv` back into agreement with `product/`.

    python3 tools/update_coverage.py            # report what would change
    python3 tools/update_coverage.py --write    # write it

`coverage.tsv` answers one question: has anyone actually looked at this
requirement in the code. A revision changes the population it has to answer for
— new requirements arrive with no rows, removed ones stop existing — and nothing
else in this repository notices.

**This extends and re-counts; it does not regenerate.** The distinction matters.
`requirements.json` is regenerated from the document, because the document holds
every fact in it. Coverage does not work that way: "somebody extracted evidence
for this requirement, under this revision" is not written down in the PM's
document and cannot be recovered from it. It lives only in this file. So a row
already here keeps its own `extraction_scope`, and only genuinely new rows are
stamped with the revision at which they arrived.

Re-deriving the column instead would rewrite 241 rows to claim an extraction
pass that never ran over them.

Columns, unchanged:

    requirement  feature  epic  extraction_scope  evidence_rows  state

`evidence_rows` is recounted from `behaviour.tsv` every time, because that is
derivable. `state` follows from it: rows exist, or they do not. A requirement
with zero rows reads `no-evidence-found`, which says nobody has extracted
evidence — never that the code does nothing.
"""
import os
import sys
import csv
import json
import argparse
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from parse_product_docs import only_docx, revision_of  # noqa: E402

COVERAGE = os.path.join(REPO, "evidence", "coverage.tsv")
BEHAVIOUR = os.path.join(REPO, "evidence", "behaviour.tsv")
REQS = os.path.join(REPO, "product", "FR-01", "requirements.json")
COLUMNS = ["requirement", "feature", "epic", "extraction_scope",
           "evidence_rows", "state"]


FR_STEM = "QACR-APP-FR-01"


def scope_now():
    """'QACR-APP-FR-01 Rev1.20' — the document's id and its revision.

    Both halves come from the filename, but not the whole filename: the PM's
    title drifts between revisions (Rev 1.19 was `QACR-APP-FR-01 Rev1.19.docx`,
    Rev 1.20 `QACR-APP-FR-01 Functional Requirements Rev1.20.docx`) and this
    column exists to be compared down the file. Carrying the full basename would
    leave two naming shapes in one column and nothing able to sort them.
    """
    p = only_docx(os.path.join(REPO, "product", "FR-01"), FR_STEM)
    return f"{FR_STEM} Rev{revision_of(p)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    reqs = {r["id"]: r for r in json.load(open(REQS))}
    rows_per_req = Counter()
    with open(BEHAVIOUR) as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            rows_per_req[row["requirement"]] += 1
    existing = {}
    with open(COVERAGE) as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            existing[row["requirement"]] = row

    scope = scope_now()
    added = sorted(set(reqs) - set(existing))
    dropped = sorted(set(existing) - set(reqs))

    out, rescoped, recounted, remapped = [], [], [], []
    for rid in sorted(reqs):
        r = reqs[rid]
        n = rows_per_req.get(rid, 0)
        prev = existing.get(rid)
        row = {
            "requirement": rid,
            "feature": r["feature"],
            "epic": r["epic"],
            # A row already here keeps the scope it was extracted under.
            "extraction_scope": prev["extraction_scope"] if prev else scope,
            "evidence_rows": str(n),
            "state": "evidenced" if n else "no-evidence-found",
        }
        if prev:
            if (prev["feature"], prev["epic"]) != (row["feature"], row["epic"]):
                remapped.append(f"{rid}: {prev['feature']}/{prev['epic']} -> "
                                f"{row['feature']}/{row['epic']}")
            if prev["evidence_rows"] != row["evidence_rows"]:
                recounted.append(f"{rid}: {prev['evidence_rows']} -> "
                                 f"{row['evidence_rows']} rows")
        out.append(row)

    print(f"requirements in product/ : {len(reqs)}")
    print(f"rows in coverage.tsv     : {len(existing)}")
    print(f"new rows, scoped {scope}: {len(added)}")
    for rid in added:
        n = rows_per_req.get(rid, 0)
        print(f"  + {rid}  {reqs[rid]['feature']}  "
              f"{'evidenced' if n else 'no-evidence-found'} ({n} rows)")
    if dropped:
        # A coverage row for a requirement that no longer exists must go, and
        # that is not a tidy-up: it is a requirement having been removed.
        print(f"\nrows for requirements no longer in product/: {len(dropped)}")
        for rid in dropped:
            print(f"  - {rid}  was {existing[rid]['feature']}, "
                  f"{existing[rid]['evidence_rows']} rows")
    for label, lst in (("re-counted", recounted), ("feature reassigned", remapped)):
        if lst:
            print(f"\n{label}: {len(lst)}")
            for l in lst:
                print(f"  ~ {l}")

    states = Counter(r["state"] for r in out)
    print(f"\nafter: {len(out)} rows — {dict(sorted(states.items()))}")

    if not args.write:
        unchanged = (len(added) == 0 and not dropped and not recounted
                     and not remapped)
        print("\nno change" if unchanged else "\nrun again with --write to apply")
        return 0

    with open(COVERAGE, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"wrote {COVERAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
