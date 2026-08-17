---
name: spec-intake
description: Publish a QACR-APP-SPEC-nn brief as feature files. Assembles the spec's dispositions, the requirements it covers, and the evidence rows already recorded, into one file per feature. Use when a new spec arrives in product/specs/, or when regenerating feature files after a spec or requirements revision.
---

# Spec intake

Turns one spec brief into one file per feature it covers.

**This is assembly, not analysis.** The codebase survey was completed by the PM and the spec author
before the spec was written. This repository publishes that result. It does not re-derive it.

> **The one rule.** Every sentence in a feature file is either a fixed heading from the layout
> below, or copied from one of the four input files. If you are about to write a sentence that is
> neither, stop — it does not belong in the output.

Consequence: running this twice on unchanged inputs produces byte-identical files. That is the
correctness test, and it is at the end of this document.

## Inputs — the only files you read

| | |
|---|---|
| `product/specs/QACR-APP-SPEC-nn.md` | the brief |
| `product/EPIC-01/features.json` | which features exist, which requirements each owns |
| `product/FR-01/requirements.json` | requirement text, milestone |
| `evidence/behaviour.tsv` | what the code does, cited |

Nothing else. Not the vault, not the application repositories, not `git log`.

## Step 1 · Read the spec

From its header and traceability table, take: the features it covers, and for each requirement of
those features, the disposition the spec gives it. Copy the disposition wording from the spec —
do not restate it.

Four dispositions only:

| | |
|---|---|
| `as-is` | the spec confirms current behaviour stands |
| `departure D-n` | the spec states QACR differs. Use the spec's own reference |
| `open` | the spec names an undecided value or question |
| `silent` | the spec says nothing about this requirement |

`silent` is assigned by set difference, not by judgement: the requirement is in `features.json`
for a covered feature and does not appear in the spec.

## Step 2 · Extract missing evidence

For each requirement of the covered features, check whether `evidence/behaviour.tsv` has rows.

If some have none, run the extractor scoped to those ids only:

```
python3 tools/extract_behaviour_candidates.py /tmp/candidates.jsonl
```

Compress each candidate's sentence into a one-line claim, append the rows to `behaviour.tsv`,
update `coverage.tsv`. Cap at 5 concurrent agents.

**Scope:** only requirements owned by features this spec covers, and only those with zero rows.
Never the whole corpus.

If the vault carries nothing for a requirement, it keeps zero rows. That is a valid outcome and
the feature file states it.

Skip this step entirely when every requirement already has rows.

## Step 3 · Write one file per feature

`features/<epic>/<feature>.md`. Exactly this layout, in this order, nothing added:

```markdown
# F01.4 — Pre-test resource and permission checks

E01 · M1, M3 · iOS, Android · [QACR-APP-SPEC-01](../../product/specs/QACR-APP-SPEC-01 Rev1.2.md)

**Spec disposition:** as-is except D1 · U1 open

## Requirements owned

| Requirement | Milestone | Disposition | Evidence rows |
|---|---|---|---|
| FR-RDY-009 | M1 | as-is | 13 |
| FR-RDY-007 | M3 | departure D1 | 0 |

## What the vault records about the code

### FR-RDY-009

**acr-android**

- **present** — <claim, byte-for-byte from behaviour.tsv> — `<citation>`

**acr-ios**

- ...

### FR-RDY-007

No rows recorded.

## Not covered by this spec

FR-XXX-nnn, FR-YYY-nnn

## Provenance

QACR-APP-SPEC-01 Rev 1.2 · FR-01 Rev 1.19 · EPIC-01 Rev 1.13
```

**Field sources, so nothing is invented:**

| Field | From |
|---|---|
| title, epic, milestones, domains | `features.json` |
| requirement list and its order | `features.json`, in its own order |
| milestone per requirement | `requirements.json`, rendered `M<n>` — the file stores `1`, the column shows `M1` |
| feature-level spec disposition | the spec's own line for this feature, verbatim. Omit the line if the spec gives none |
| disposition | the spec |
| evidence row count | `behaviour.tsv`, counted |
| product grouping | `behaviour.tsv` `product` column, alphabetical |
| status, claim, citation | `behaviour.tsv`, copied verbatim |
| row order within a product | as they appear in `behaviour.tsv` |
| "Not covered" list | set difference, ascending |

**Fixed strings.** A requirement with no rows gets exactly `No rows recorded.` A feature where the
spec covers everything gets exactly `Nothing.` under *Not covered*. Do not vary the wording.

**Never** paste requirement text — reference by id. `product/` holds the wording.

## Step 4 · Commit and open a PR

```
git checkout -b spec/SPEC-nn
git add features/ evidence/
git commit -m "SPEC-nn: feature files for <features>"
git push -u origin spec/SPEC-nn
```

PR body: the features written, requirement count per disposition, how many rows were extracted in
step 2, and any requirement that ended with zero rows.

## Do not

These are the three ways this has gone wrong before. Each is a hard stop, not a judgement call.

1. **Do not open the application repositories.** Not `iosDip`, `AndroidDip`, `AndroidQacr` or
   `urine.com.ios-qacr-app`, not to verify a row, not to fetch a code excerpt, not at a pinned
   commit. `behaviour.tsv` is the record. If a row looks wrong, say so in the PR body and leave it.
2. **Do not compare the platforms.** Rows from `acr-ios` and `acr-android` are presented under
   separate headings and never characterised against each other. A difference between them is data
   the reader can see, not a finding to report. Do not write "platforms disagree", "diverges",
   "inconsistent", or any equivalent.
3. **Do not write to `decisions/`.** That folder is for questions Product raises. Nothing this
   skill produces belongs there.

Also: do not summarise a set of rows, do not add a section the layout does not list, and do not
add commentary to the disposition column.

## Self-check before committing

Run the skill twice on unchanged inputs.

```
git diff --stat -- features/
```

**Empty diff, or the run is wrong.** A non-empty diff means something in the output came from
judgement rather than from an input file — find it and remove it.

Then confirm:

- every citation in a new row resolves: `python3 tools/check_citations.py`
- every requirement of every covered feature appears exactly once in its feature file
- `decisions/` is unchanged
- no file outside `features/` and `evidence/` was modified
