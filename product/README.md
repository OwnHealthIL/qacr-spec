# product/

The product manager's working directory. Read-only to everyone else — to change a
requirement, change the data and rebuild.

**POC.** This directory previously held only the exported documents. It now holds the
generator that produces them, so the source of truth and the published artefact live in
one place and one commit. Nothing outside `product/` is changed by this branch.

## Layout

```
product/
├── generator/     the source of truth. The .js data modules ARE the requirements
├── FR-01/         QACR-APP-FR-01, built straight into here
├── EPIC-01/       QACR-APP-EPIC-01 and the Board, built straight into here
├── specs/         QACR-APP-SPEC-nn briefs
└── local/         not in git. Source material that is not the team's business
```

`FR-01/*.json` and `EPIC-01/*.json` are still produced by `tools/parse_product_docs.py`
on the team's side, from the `.docx`, and are still regenerated rather than edited. That
parse is now a **second, independent derivation** of the same corpus: it never reads the
data modules, so where it agrees with them the document is confirmed by something that
did not build it.

## The two commands

```bash
npm install          # once
npm run all          # build, then every guard
```

`npm run build` writes each deliverable **into the directory it is published from**.
There is no staging copy: a second copy of a deliverable is read as current by whoever
finds it first.

`npm run check` must pass before anything is circulated. It is not advisory.

## Never edit a .docx or the Board by hand

Edit the data module and rebuild. A hand edit is destroyed by the next build, and until
then the document disagrees with the data that defines it.

## The revision rules

`generator/version.js` is the only place a revision may be declared.

A spec's revision lives in its **filename** as well as its header, and the two must
agree — `QACR-APP-SPEC-nn Rev<major>.<minor>.md`. **A published revision is immutable:**
once it is committed, somebody has built against it, so a change needs a new number
rather than new text under the old one. Superseded revisions stay in `specs/`; the
highest is the live one, and the guards check only that one.

`generator/layout-check.py` enforces all of this and runs first, because every other
guard reads a file only this one proves is the right file.
