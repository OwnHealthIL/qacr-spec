# How work moves through this repository

From a spec arriving to a feature file a developer can build from. Five steps; the order matters,
because each one is a check that gets much more expensive to run later.

The mechanical version of steps 1–5 is the `spec-intake` skill in `.claude/skills/spec-intake/`.
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

One file per feature, at `features/<epic>/<feature>.md`. This is assembly, not authorship: the
`spec-intake` skill produces it, and every line in it is copied from the spec, `features.json`,
`requirements.json` or `evidence/behaviour.tsv`.

A feature file holds four things:

1. the feature's spec disposition, verbatim from the brief
2. the requirements it owns, each with its milestone, disposition, and evidence-row count
3. the evidence rows themselves — what the code does today, per product, cited `file:line`
4. the requirements of this feature the spec says nothing about

It holds no task, no acceptance criteria, and no comparison between platforms. Those were tried
and removed: the task is judgement a developer makes at his desk, and the comparison is work the
PM and the spec author completed before the brief was written.

Because every line has a named source, running the skill twice produces byte-identical files. If
it does not, something in the output came from judgement rather than from an input.

## 5 · Open a PR

The skill branches, commits and pushes. A human reads the PR before it reaches the team — chiefly
to confirm the right features were covered and nothing appeared that has no source.

---

## After the repository

What happens next is not this repository's process, but it is what the repository is for.

A developer opens the feature file, reads what the spec says to build and what the code does
today, and writes the per-platform work himself. Tests carry the requirement id they demonstrate,
so traceability is a query rather than a reconstruction. A criterion is marked manual only with a
reason — needs a kit, needs hardware, needs a person to read a screen.

If a particular feature turns out to need its task written down, someone writes it in that one
file, in a section the skill does not touch. Not for all 82 up front.

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
- Comparing the two ACR platforms against each other, or opening an application repository to
  verify a row. `evidence/behaviour.tsv` is the record.
