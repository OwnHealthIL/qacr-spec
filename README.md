# qacr-spec

The layer between the PM's requirements documents and the two QACR applications.

`QACR-APP-FR-01` says what the product must do. `iosDip`, `AndroidDip`, `AndroidQacr` and
`urine.com.ios-qacr-app` are what the code does. Neither answers the question a developer actually
has at the start of a task — *what am I building, what already exists, and how will I know it is
done*. This repository is where that answer lives, in a form you can grep.

It holds the PM's documents unchanged, those documents parsed into data, and — as they get written
— one file per specified feature: the requirements it owns, their disposition from the spec, and
what the code does today.

It does **not** hold reasoning. The analysis behind all of this lives in the Obsidian vault
(`Healthy.io - MD/QACR - Implementation Plan`). Go there when a claim is disputed.

## Layout

```
qacr-spec/
├── product/                  the PM's documents. READ-ONLY.
│   ├── FR-01/                QACR-APP-FR-01 Rev1.24.docx + requirements.json,
│   │                         decisions.json, register.json, appendices.json
│   ├── EPIC-01/              QACR-APP-EPIC-01 Rev1.18.docx + Board.html + features.json
│   └── specs/                QACR-APP-SPEC-nn briefs, as the PM writes them
├── features/                 one file per specified feature — E01 and E02
├── evidence/                 what the code does today, cited — 2,855 rows over 83 requirements
├── decisions/                questions THIS repository raises against a spec — empty
├── tools/                    the parser, the revision differ, the citation checker,
│                             the vault extractor, the feature-file builder,
│                             the coverage updater
└── .claude/skills/           spec-intake, revision-intake, and the reading skills
```

`evidence/behaviour.tsv` covers 83 of 250 requirements — the ones the vault carries evidence for.
`evidence/coverage.tsv` records the other 167 as `no-evidence-found`, which means the vault has
none, not that the code does nothing. SPEC-01 and SPEC-02 have been published, so `features/` holds
E01 and E02.

`decisions/` is empty because ingesting a spec has not yet raised a question — which is **not** the
same as Product having none. The FR document carries its own Decision Log (62 closed) and Review
Register (48 open), and those are parsed to `product/FR-01/` rather than copied here. See
`decisions/README.md`.

### `product/`

`QACR-APP-FR-01 Rev1.24.docx` — 250 requirements across 22 functional areas.
`QACR-APP-EPIC-01 Rev1.18.docx` — the same 250 requirements rearranged into 15 epics and 82
features, the way a team would build them. `Board.html` is that map as a filterable page, built by
the PM's generator beside the map (`product/generator/build-board.js`) and landed in the same commit,
so it is at **Rev 1.18**. Its filename carries no revision; the page's own header states it.

The `.json` files beside them are parsed from the `.docx`, validated against the counts the
documents state about themselves, and regenerated rather than edited.

## The rules

**1. `product/` is read-only.** To change a requirement, change the document. Nothing in this
repository may restate, paraphrase or "clarify" a requirement — a second copy of a requirement is a
second requirement, and they drift. Reference requirements by id.

**2. Every claim about existing behaviour carries a `file:line` citation.** Without one it is not a
claim, it is a recollection. "ACR already does this" is not usable; `iosDip/Dip/Infra/Exam/
ExamBuilder.swift:8-12` is. Citations are recorded against a known commit — see
`evidence/pins.yaml`.

**3. A feature file never restates what a spec says.** It links to the spec and adds only what the
spec does not have: the requirements it owns, and the evidence rows for them. Every line has a
named source file, which is why regenerating one produces the same bytes. It holds no task and no
acceptance criteria — a developer writes those at his desk.

**4. The reasoning lives in the Obsidian vault, not here.** This repository holds conclusions in a
form you can act on. The argument that produced them — why a requirement was classified as it was,
what the code survey found, which assumptions are load-bearing — is in the vault, and that is where
to go when a row is disputed rather than re-deriving it.

## Where to start

Read `SDLC.md`. It is the path from a spec arriving to a feature file on master.
