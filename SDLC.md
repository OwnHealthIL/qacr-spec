# How work moves through this repository

From a spec arriving to code merged. Seven steps; the order matters, because each one is a check
that gets much more expensive to run later.

The mechanical version of steps 1–6 is the `spec-intake` skill in `.claude/skills/spec-intake/`.
Run it rather than doing this by hand.

---

## 1 · A spec arrives

The PM writes a `QACR-APP-SPEC-nn` brief. It goes in `product/specs/` unchanged, and is never
edited here.

A brief does **not** describe behaviour. Its governing rule is that the current ACR product *is*
the specification, and the brief records only what **departs** from it, what is **still undecided**,
and which requirement each feature answers to.

## 2 · Trace it against `product/requirements.json`

For every feature the spec names, pull that feature's requirements from
`product/EPIC-01/features.json` and classify what the spec says about each one:

**departure** · **as-is** · **open** · **silent**

**Report every silent requirement.** A silent requirement has no stated QACR intent, so nobody can
build it — not because it is hard but because nobody has said what it should do. Silence is not a
decision and must never be read as "as-is".

Also check the spec's own traceability against `features.json` in both directions: a requirement
the spec lists that the feature does not own, or one the feature owns that the spec omits, is a
defect in the spec and goes back to the PM.

## 3 · Read what the evidence layer already records

A recreation brief rests on a codebase survey. **That survey is not done here.** It is
completed before the spec is written, by the people who write the spec, and its result is
what `evidence/behaviour.tsv` publishes. This repository is where R&D consumes it — not
where it is re-derived, re-validated or second-guessed.

So the step is to read, not to check:

- Pull the rows for each requirement the feature owns. They record what the code does, per
  product, with a `file:line` citation.
- `evidence/coverage.tsv` says whether anyone has extracted evidence for a requirement at
  all. A requirement with no rows means the vault carries none — nothing more than that.
- `evidence/pins.yaml` names the commit every citation was read against.

Re-run `python3 tools/check_citations.py` whenever you want to confirm the citations still
point at real code. That checks the citations, not the reading of them.

## 4 · Write the feature file

One file per feature, at `features/<epic>/<feature>.md`.

A feature file **never restates what the spec says.** It links to the spec and adds only the three
things the spec does not have:

1. the requirements it owns, by id, each with its disposition from step 2
2. the evidence rows — what the code does today, cited `file:line`
3. the per-platform task and the acceptance criteria

If you are copying a sentence out of the spec, stop and link instead. Two copies of a statement
become two statements.

## 5 · Derive the per-platform tasks

iOS and Android are separate tasks against the same requirement ids, because the starting points
differ — often sharply. Write each one against what that platform actually has today, and name the
divergences that are sanctioned versus the ones that are defects.

## 6 · Build, with tests tagged by requirement id

Every acceptance criterion is testable or it is not a criterion. Tag each test with the requirement
id it demonstrates, so the traceability the submission needs is a query rather than a
reconstruction. Mark a criterion manual only with a reason — needs a real kit, needs torch
hardware, needs a person to read a screen.

## 7 · Record the evidence

New rows for what the code now does, cited, against the commit recorded in `evidence/pins.yaml`.

---

## Anything Product must decide goes to `decisions/`

One file per question, never into a feature file as an assumption.

A question that gets answered by picking the more likely reading is not answered — it is buried,
and it surfaces during verification when it is expensive. Record the question, what makes it a
question, and what happens if nobody answers. When the answer arrives, record it **verbatim**.

## The things that are never done

- Filling in a QACR intent by inference from what ACR does. Different product, different kit,
  different chemistry. Prior art is evidence, not a decision.
- Copying requirement text out of `product/` — that document holds the current wording, and a copy
  is a fork.
- Adding an acceptance criterion for behaviour no spec has stated.
- Treating a silent requirement as as-is.
