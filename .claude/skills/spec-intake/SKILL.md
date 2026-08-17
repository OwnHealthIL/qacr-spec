---
name: spec-intake
description: Publish a QACR-APP-SPEC-nn brief as feature files. Assembles the spec's dispositions, the requirements it covers, and the evidence rows already recorded, into one file per feature. Use when a new spec arrives in product/specs/, or when regenerating feature files after a spec or requirements revision.
---

# Spec intake

Turns one spec brief into one file per feature it covers.

**This is assembly, not analysis.** The codebase survey was completed by the PM and the spec author
before the spec was written. This repository publishes that result. It does not re-derive it.

> **The one rule.** You do not write a feature file. `tools/build_feature_files.py` writes it, and
> every line it emits is either a fixed heading or a value copied from one of the four input files.
> If you are about to type markdown into `features/`, stop — that is the script's job.

Consequence: running it twice on unchanged inputs produces byte-identical files, in this session or
any later one. That is the correctness test, and it is at the end of this document.

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

**Record what you read in the `SPECS` table of `tools/build_feature_files.py`** — one entry per
brief, holding its id, its file, its provenance line, its departures keyed by the requirement each
one names as its driver, and per covered feature the brief's own disposition wording and the
requirements it answers for. That table is the whole of the judgement in this process. Everything
after it is mechanical, which is why it lives in the repository and is reviewed in the PR rather
than being re-read from the brief each time.

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

## Step 3 · Build the feature files

```
python3 tools/build_feature_files.py SPEC-nn
```

One file per covered feature, at `features/<epic>/<feature>.md`. The script writes them; you do
not. Do not hand-edit what it emits and do not reproduce its output by writing markdown yourself —
a file written by hand is a file no future session can reproduce, which is the whole guarantee.

If a file comes out wrong, the fault is in one of the four inputs or in the step 1 `SPECS` entry.
Fix it there and run again.

The rest of this step is documentation of what the script emits, so you can read a feature file
and know where every line in it came from.

### The layout it produces

```markdown
# F01.4 — Pre-test resource and permission checks

E01 · M1, M3 · iOS, Android · [QACR-APP-SPEC-01](../../product/specs/QACR-APP-SPEC-01%20Rev1.2.md)

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

### Where each field comes from

| Field | From |
|---|---|
| title, epic, milestones, domains | `features.json` |
| requirement list and its order | `features.json`, in its own order |
| milestone per requirement | `requirements.json`, rendered `M<n>` — the file stores `1`, the column shows `M1` |
| feature-level spec disposition | the `SPECS` entry, verbatim from the brief. The line is omitted when the brief gives none |
| disposition | the `SPECS` entry: its `departures` map, else `as-is`, else `silent` by set difference |
| header link and provenance line | the `SPECS` entry |
| evidence row count | `behaviour.tsv`, counted |
| product grouping | `behaviour.tsv` `product` column, alphabetical |
| status, claim, citation | `behaviour.tsv`, copied verbatim |
| row order within a product | as they appear in `behaviour.tsv` |
| "Not covered" list | set difference, ascending |

**Fixed strings.** A requirement with no rows gets exactly `No rows recorded.` A feature where the
spec covers everything gets exactly `Nothing.` under *Not covered*. The script emits these; do not
vary them by hand.

**Requirement text never appears** — requirements are referenced by id, and `product/` holds the
wording.

## Step 4 · Commit and open a PR

```
git checkout -b spec/SPEC-nn
git add features/ evidence/ tools/build_feature_files.py
git commit -m "SPEC-nn: feature files for <features>"
git push -u origin spec/SPEC-nn
```

The `SPECS` entry goes in the same commit as the files it produced, so a reviewer can check the
output against what the brief was read to say.

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

Also: do not summarise a set of rows, do not add a section the layout does not list, do not add
commentary to the disposition column, and do not edit a file the script emitted — change the input
and run it again.

## Self-check before committing

Stage the first run, then run the script a second time on unchanged inputs.

```
git add features/
python3 tools/build_feature_files.py SPEC-nn
git diff --stat -- features/
```

**Empty diff, or the run is wrong.** A non-empty diff means something in the output came from
judgement rather than from an input file — find it and remove it.

Then confirm:

- every citation in a new row resolves: `python3 tools/check_citations.py`
- every requirement of every covered feature appears exactly once in its feature file
- `decisions/` is unchanged
- no file outside `features/`, `evidence/` and `tools/build_feature_files.py` was modified
