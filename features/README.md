# features/

One file per specified feature, written when a spec covering it arrives. It is what a developer
opens at the start of a task.

Currently: `E01` to `E04`, 25 features — from `QACR-APP-SPEC-01 Rev 1.2`, `SPEC-02 Rev 1.0`,
`SPEC-03 Rev 1.1` and `SPEC-04 Rev 1.0`. Which brief each epic is built from is the `SPECS` table in
`tools/build_feature_files.py`.

## How they are made

Not by hand. `tools/build_feature_files.py` emits them, driven by the `spec-intake` skill:

```
python3 tools/build_feature_files.py SPEC-01
```

Every line has a named source — the spec, `product/EPIC-01/features.json`,
`product/FR-01/requirements.json`, or `evidence/behaviour.tsv`. Nothing is judged, so running it
twice produces byte-identical files. Delete them all and rebuild: you get the same bytes back.

Do not hand-edit one. The next run overwrites it.

## Layout

```
features/<epic>/<feature>.md      e.g.  features/E01/F01.4.md
```

`product/EPIC-01/features.json` is the authority for which requirements a feature owns.

## What a feature file contains

Only what the spec does not already say. It links to the spec; it never restates it.

1. **Header** — feature id and title, epic, milestones, domains, and a link to the spec.
2. **Spec disposition** — the brief's own line for this feature, verbatim.
3. **Requirements owned** — by id, each with its milestone, its disposition from the spec
   (departure with its `D-n` reference, as-is, open, silent, or new — the brief specifies the
   behaviour itself and there is no current behaviour to recreate, carried in the brief's own
   words), and its evidence-row count.
   A departure id is per-brief — the full name is `SPEC-nn/Dn`, and `SPEC-01/D1` and `SPEC-02/D1`
   are different decisions — so read it with the brief the header links to.
   Never the requirement text; `product/` holds the current wording.
4. **What the vault records about the code** — the rows from `evidence/behaviour.tsv`, grouped by
   product, each with its citation. A requirement with no rows reads `No rows recorded.`
5. **Not covered by this spec** — requirements of this feature the spec is silent on.

## What it does not contain

**No per-platform task and no acceptance criteria.** A developer writes those at his desk, from
the spec and the evidence. If one feature turns out to need its task written down, write it in
that file in a section the generator does not touch — not for all 82 up front.

**No comparison between the platforms.** Rows from `acr-ios` and `acr-android` sit under separate
headings and are never characterised against each other. The codebase survey was completed by the
PM and the spec author before the brief was written; this repository publishes its result.

## Rules

- If you are copying a sentence out of a spec, link to it instead.
- Anything undecided goes to `decisions/` — never into a feature file as an assumption.
