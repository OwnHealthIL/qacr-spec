---
name: revision-intake
description: Ingest a new revision of the PM's requirements documents — QACR-APP-FR-01 and QACR-APP-EPIC-01 — into product/, regenerate the parsed JSON, report exactly what changed, and bring everything downstream back into agreement. Use when a new Rev<n>.docx arrives, when asked to update the requirements to a new revision, or when a feature file declares requirements `pending` because product/ is behind. The sibling of spec-intake: that one ingests a brief, this one ingests the documents the brief traces to.
---

# Revision intake

Replaces the two product documents with a newer revision, and leaves the repository asserting the
new one and nothing else.

**The documents are the authority. This skill re-reads them and reports; it never reconciles a
disagreement by choosing.** Where the parse and a document disagree, one of them is wrong and a
human decides which. That is why every tool here exits non-zero on a mismatch instead of correcting
quietly.

> **The one rule.** A revision is not a file swap. Swapping the `.docx` and re-running the parser
> gets you correct top-level numbers over stale generated files, and nothing anywhere says so. The
> work is steps 3 and 4; step 1 is the easy part.

## Inputs — the only files you read

| | |
|---|---|
| the new `QACR-APP-FR-01 ... Rev<n>.docx` | wherever the PM sent it |
| the new `QACR-APP-EPIC-01 ... Rev<n>.docx` | the same |
| `git show HEAD:product/...` | the outgoing revision. git is the archive |

Not a brief, not the vault, not the application repositories.

## The four questions, in order

1. Does the new parse agree with what the documents say about themselves?
2. What actually changed, requirement by requirement?
3. What downstream is now stale — and did **every** piece of it get rebuilt?
4. What was blocked on this revision, and is it unblocked?

**Skipping 3 is the failure that has already happened, and it is invisible.** Every top-level count
was right and 86 generated notes went on quoting superseded requirement text, because one builder in
the chain was not re-run.

## Step 1 · Place the documents

Put each new `.docx` in `product/FR-01/` and `product/EPIC-01/`, and **delete the outgoing one.**

```bash
git rm "product/FR-01/QACR-APP-FR-01 ... Rev1.19.docx"
cp ~/Downloads/"QACR-APP-FR-01 Functional Requirements Rev1.20.docx" product/FR-01/
```

`only_docx()` refuses to run when a directory holds two `QACR-APP-FR-01*.docx`, deliberately: a
directory with two revisions in it has no answer to *which revision is this repository at*.

**git history is the archive.** Do not write `requirements-rev119.json`, do not keep
`Rev1.19.docx` beside `Rev1.20.docx`. Copies-as-archive belong to a working tree with no version
control; here they are a second copy that will be read as current.

**The revision is whatever the filename says.** `revision_of()` reads it from `Rev<n>.docx` and
nothing else consults a brief's `Traces to` header — a brief is written against the revision its
author expects, which is routinely *ahead* of what this repository holds. SPEC-02 claims FR-01
Rev 1.20 while `product/` holds Rev 1.19; that gap is the normal state, not an error.

The filename may also change shape. Rev 1.19 arrived as `QACR-APP-FR-01 Rev1.19.docx` and Rev 1.20
as `QACR-APP-FR-01 Functional Requirements Rev1.20.docx`. Both match on the stem, so both are
found; do not rename a document to look like its predecessor.

## Step 2 · Parse, and let the documents check themselves

```bash
python3 tools/parse_product_docs.py
```

The validation that matters is **against each document's own statements**, not against the previous
revision. Comparing with last revision's numbers tells you only that something moved, which you
already knew from the filename. Comparing with the document's own arithmetic catches a **mis-parse**,
which is what this step exists for.

What it checks, strongest first:

| | |
|---|---|
| **Appendix H, Priority Summary** | a 22-area by 6-milestone matrix with a total per row and per column. 132 cells. It pins every requirement's milestone *by functional area*, so two errors in opposite directions cannot net out |
| Review Register front matter | open items per group, and their total |
| Appendix D.1–D.3 headings | each states its own row count — "D.1 Not Included in This Version — 15 requirements" |
| section 2 | "This revision contains N requirements across M functional areas" |
| per-epic headers | requirements per epic |
| EPIC section 3 roadmap cells | requirements each feature introduces at that milestone |
| cross-document | every FR requirement in exactly one feature of the epic map, and the FR Feature column agreeing with it |

**Appendix H also states the document's own milestone vocabulary**, in its column headings, so the
vocabulary is read rather than hardcoded. Both documents are then validated against it.

The parse writes six files, and they are never edited by hand:

```
product/FR-01/requirements.json      the body
product/FR-01/decisions.json         Appendix G, the Decision Log — closed Q-nn
product/FR-01/register.json          the Review Register — open Q-nn, in six groups
product/FR-01/appendices.json        Appendix D.1–D.4, configurations, parameters,
                                     and the Priority Summary as data
product/EPIC-01/features.json        the epic map
product/EPIC-01/roadmap.json         the section 3 milestone roadmap, persisted so a
                                     change to it can be reported and not just checked
```

### The traps, each of which has already drawn blood

- **An appendix is identified by what it *is*, never by its letter.** Rev 1.19 deleted the backlog
  appendix and re-lettered everything below it — configs F→E, threat G→F, decisions I→G, priority
  J→H. A letter-keyed reader returned *zero backlog rows and zero decisions*, which is
  indistinguishable from "the document dropped them". `APPENDIX_ROLES` matches on title, and a title
  matching no role is **reported, and fails the parse**. That report is how the next re-lettering
  announces itself instead of arriving as silence.
- **A sub-part is identified by its position, and its letter is not required to agree either.** The
  Rev 1.19 re-lettering reached the appendix titles and not their sub-headings, so Appendix E still
  numbers its parts F.1–F.3 and Appendix F numbers its G.1–G.3. A reader requiring agreement finds
  no sub-parts at all — and the three configuration sub-parts have three *different* schemas, so
  losing the split silently mislabels the four Appendix E.3 rows, whose first column is a reason and
  not a configuration name.
- **Appendix D.1 carries `BL-` ids as well as `FR-` ids.** Rev 1.19 excluded BL-38 outright, and an
  `FR-`-only matcher under-counted the appendix and made a real scope decision look like a lost row.
- **Milestone vocabularies grow.** M5 arrived at Rev 1.19; anything holding a fixed `1|2|3|4|TBD`
  set renders a sixth of the corpus as TBD without saying so. Read the set, validate against it,
  report an unrecognised value.
- **Column positions are not schema.** Appendix tables are read through their own header row, so a
  renamed or added column appears in the JSON as itself rather than being mapped onto a name the
  parser invented. A row carrying a cell the header does not declare is reported.

## Step 3 · The change manifest, before anything is regenerated

```bash
python3 tools/diff_revisions.py
```

It diffs the working tree against `git show HEAD:` and reports, per requirement: **added · removed ·
text changed · note changed · milestone moved · feature reassigned · source changed · section
moved**; then features, per-epic counts, the Decision Log and the Review Register.
`requirements.json` carries a `sha256` of each requirement's text, so a text change is exact rather
than a similarity judgement.

**Stop here and read it against the documents.** A revision that adds requirements is routine; one
that *removes* or *reassigns* them changes what teams are building, and someone must see that before
the repository starts asserting it. Removal is the case the tool is loudest about, because nothing
else in this pipeline is designed to notice that a requirement quietly stopped existing.

**The null-diff rule.** An empty structured diff is not a result, it is a prompt to look harder.
Rev 1.17's entire content was two corrected cover pages and one deleted legend row — invisible in
the parsed data, and reported by an earlier tool as "no changes". So on an empty diff the tool
diffs the **raw document text** and requires every changed line to match a pattern declared in
`HOUSEKEEPING`. A changed line matching none is reported and the exit code is non-zero. Do not add a
pattern to that list to make a real change pass.

## Step 4 · Bring downstream back into agreement

**Every generated artefact that reads the corpus is now stale.** Enumerate them; do not rebuild the
ones you happen to remember. Grep for `requirements.json` and `features.json`, and for the outgoing
revision and the outgoing requirement total, rather than trusting the list below — which will go
stale exactly like the ones it warns about.

```bash
grep -rn "requirements\.json\|features\.json" . --exclude-dir=.git
grep -rn "Rev *1\.19\|\b241\b" . --exclude-dir=.git --exclude="*.json"
```

**1 · Clear the `pending` declarations.** A brief that named requirements `product/` did not yet
hold declares them in the `SPECS` table of `tools/build_feature_files.py`, and the build **fails**
once that declaration goes stale. That failure is the feature working: it is how the repository
tells you a revision has arrived and the brief's claim can now be honoured. Remove the ids from
`pending`, leave `covers` alone, rebuild, confirm green.

**2 · Rebuild the feature files for every published brief, not only the newest.**

```bash
python3 tools/build_feature_files.py SPEC-01
python3 tools/build_feature_files.py SPEC-02
```

The builder is deterministic, so **rebuilding at an unchanged revision produces byte-identical
files**. Across a revision it does not, and must not: the provenance footer states the revision
actually rendered, so every file of every brief gains a new footer, and a brief whose header cites
the older revision now renders `FR-01 Rev 1.20 (brief cites 1.19)`. Expect exactly that one line to
move in an otherwise untouched epic — and check that it is only that line. Anything else moving in
an epic this revision did not touch came from judgement rather than from an input, and is a defect
worth stopping for.

**3 · `evidence/coverage.tsv`.**

```bash
python3 tools/update_coverage.py           # report
python3 tools/update_coverage.py --write
```

This one **extends and re-counts; it does not regenerate**, and the distinction is the point.
"Somebody extracted evidence for this requirement, under this revision" is not written down in the
PM's document and cannot be recovered from it — it lives only in this file. So a row already there
keeps its own `extraction_scope`, and only new rows are stamped with the arriving revision.
Re-deriving the column would rewrite every row to claim an extraction pass that never ran over it.

New requirements arrive with no rows and must read `no-evidence-found`, which says *nobody has
extracted evidence* — never *the code does nothing*. Extracting evidence for them is `spec-intake`'s
step 2, not this skill's.

**4 · The prose that quotes a count.** `README.md` and `evidence/README.md` state the requirement
total, the covered/uncovered split and the revision of each document. They are as stale as any
generated file and nothing regenerates them.

**5 · Two tables of the epic document are not parsed, so no tool can tell you they moved.**
Section 4's dispositions and section 5's design queue — nine rows each — are read by nobody here.
They were unchanged at Rev 1.20, verified by hand. Until something parses them, check them by eye
and say in the commit message that you did; a blind spot that is written down is survivable, one that
is not is the `86 generated notes` failure again.

**6 · `product/EPIC-01/QACR-APP-EPIC-01 Board.html` is supplied by the PM, not built here.** It is a
rendering of the epic map, and if it did not arrive with the revision it is now stale while looking
current — its filename carries no revision, so nothing shows it. Ask for the matching export, and
until it arrives say in the commit message which revision the Board is at. Prefer a filename that
carries the revision, for the same reason `Rev<n>.docx` does.

## Step 5 · Gates

```bash
python3 tools/parse_product_docs.py     # exits 0 — every self-stated count agrees
python3 tools/diff_revisions.py         # exits 0 — nothing unexplained
python3 tools/build_feature_files.py SPEC-01 && python3 tools/build_feature_files.py SPEC-02
python3 tools/update_coverage.py        # reports "no change"
python3 tools/check_citations.py        # citations still resolve
```

Then say the numbers out loud in the commit message:

- the parse exits zero, and the Appendix H matrix agrees cell by cell
- the manifest matches what a human read in the documents
- no feature file still declares `pending` for a requirement `product/` now holds
- every published brief still renders, and an untouched epic moved only in its provenance footer
- `coverage.tsv` accounts for **every** requirement at the new total
- rebuilding twice in a row produces no diff

## Step 6 · One commit, one revision

```bash
git checkout -b revision/rev<n>-intake
git add product/ features/ evidence/coverage.tsv tools/ README.md
git commit
git push -u origin revision/rev<n>-intake
```

The message states the revision, the counts, and the manifest — added, removed, text-changed, moved.
A reviewer's job is to confirm the manifest matches the documents; make that possible **without
opening Word**.

**Commit on the branch and stop there. Do not open a pull request and do not merge.** Review of a
revision happens separately, and the branch is expected to sit until it is asked for. This is where
this skill differs from `spec-intake`, which opens one.

**Never mix a revision ingestion with a spec intake in one commit.** They fail differently and are
reverted differently.

## Do not

These are hard stops, not judgement calls.

1. **Do not correct a count mismatch to make the parse pass.** The document and the parse disagree;
   a human decides which is wrong. Editing the parser until the number comes out right is how a
   mis-parse becomes the repository's belief.
2. **Do not edit a document in `product/`.** This skill is the one thing that *replaces* them, which
   is why the filename is the provenance. Nothing here rewords, annotates or fixes a document.
3. **Do not write to `decisions/`.** That folder holds questions *this repository* raises against a
   spec, `D-nn`. The FR document's own Decision Log and Review Register are `Q-nn`, they are
   Product's, and they are parsed to `product/FR-01/` and regenerated every revision. Copying a row
   into `decisions/` forks it, collides two id spaces, and confuses who is waiting on whom — see
   `decisions/README.md`.

Also: do not trust a brief's `Traces to` line over a filename; do not keep two revisions of a
document in one directory; do not leave a `pending` declaration in place once the requirement
exists, because silencing the tripwire removes the signal; and do not read a new requirement's
absent evidence as "the code does nothing".

## Self-check before committing

```bash
git add -A
python3 tools/parse_product_docs.py && python3 tools/build_feature_files.py SPEC-01 \
  && python3 tools/build_feature_files.py SPEC-02 && python3 tools/update_coverage.py --write
git diff --stat
```

**Empty diff, or the run is wrong.** A non-empty diff on the second pass means something in the
output came from judgement rather than from an input file.

Then confirm:

- `git status` shows exactly one `.docx` per product directory, the new one added and the old one deleted
- no `-rev<n>` copy and no second `.json` per artefact was created
- the requirement total in `README.md` and `evidence/README.md` is the new one
- `decisions/` is unchanged
- nothing outside `product/`, `features/`, `evidence/coverage.tsv`, `tools/` and the two READMEs was modified

## Refinement log

- **Rev 1.17, 2026-08-13 — the null-diff lesson.** The structured diff was completely empty while
  the files had changed size. Diffing the raw document text found the whole revision: two corrected
  cover pages and one deleted legend row. A null diff is a prompt to look harder, not a result.
- **Rev 1.19, 2026-08-13 — the largest revision so far, and the one that broke the parser twice.**
  The backlog appendix was deleted and 41 of its 42 rows restored into the body at a new milestone 5;
  everything below it was re-lettered. Both parser failures were silent and both looked like the
  document had lost content. Also the revision where **86 generated notes were left quoting
  superseded requirement text** because one builder in the chain was not re-run — every top-level
  count was correct, and nothing showed it.
- **Rev 1.20, 2026-08-17 — small, and entirely traceable to a brief.** Four requirements added, all
  sourced `Review comment; QACR-APP-SPEC-02`; one text change; only E02 touched. Second revision to
  run to this pattern — SPEC-01 produced FR-RDY-014 the same way — so a brief arriving now predicts
  a revision arriving shortly, and the four ids it named were the ones sitting `pending`.
- **Rev 1.20, 2026-08-19 — what the appendices were hiding.** Reading them found the strongest check
  in the pipeline sitting unused: Appendix H states a 22-area by 6-milestone matrix about itself, and
  it validates every milestone by area rather than only the grand total. It also states the milestone
  vocabulary, which removes the fixed-vocabulary trap rather than guarding it. The same pass found
  that the document's appendix sub-numbering is itself stale — Appendix E numbers its parts F.1–F.3 —
  so sub-parts are read by position, and that the Board export has no revision in its filename and so
  goes stale invisibly.
