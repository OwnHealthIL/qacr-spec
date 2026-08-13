# features/

One file per specified feature. **Empty because no spec has been ingested yet — not because the
files are missing.**

A feature file is written after a spec covering that feature arrives, by step 4 of `SDLC.md` (or
the `spec-intake` skill). It is the thing a developer opens at the start of a task.

## Layout

```
features/<epic>/<feature>.md      e.g.  features/E01/F01.4.md
```

Epics are `E01`–`E15` and features are numbered within their epic — see
`product/EPIC-01/features.json`, which is the authority for which requirements a feature owns.

## What a feature file contains

**Only what the spec does not already say.** It links to the spec; it never restates it.

1. **Header** — the feature id and title, its epic, its milestone, the domains it touches, and a
   link to the spec that covers it.
2. **Requirements owned** — by id, each with its disposition from the spec: departure (with its
   `D-n` reference), as-is, open, or silent. Never the requirement text; `product/` holds the
   current wording.
3. **What the code does today** — the relevant rows from `evidence/behaviour.tsv`, per platform,
   each with its citation. Where the two ACR platforms disagree on an as-is requirement, that
   disagreement is stated here and a decision is raised.
4. **Per-platform task** — iOS and Android separately, written against what that platform actually
   has today.
5. **Acceptance criteria** — one per testable statement, each marked automatable or manual with a
   reason.

## Rules

- If you are copying a sentence out of a spec, link to it instead.
- No acceptance criterion for behaviour no spec has stated.
- Anything undecided goes to `decisions/` — never into a feature file as an assumption.
