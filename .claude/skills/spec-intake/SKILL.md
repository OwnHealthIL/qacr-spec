---
name: spec-intake
description: Ingest a new QACR-APP-SPEC-nn brief from the PM — trace it against the requirements, verify its "same as ACR" claims against the code evidence, emit feature files, and escalate what it leaves undecided. Use when a new spec document arrives, when asked to process or ingest a spec, or when checking whether a spec covers everything its features own.
---

# Spec intake

A `QACR-APP-SPEC-nn` brief states **departures** from the current ACR product, **open values**,
and **confirmed as-is** decisions for a set of features. It does not state behaviour — its
governing rule is that the current product is the specification.

That rule has one failure mode, and catching it is the main reason this process exists.

> **Where the two ACR platforms behave differently, "as-is" is undefined.** It resolves to
> whichever platform the developer happened to read. Every such case needs an explicit departure
> or it becomes a silent cross-platform divergence.

This already happened once. `FR-RDY-007` — ACR iOS exempts a charging device from the battery
check, ACR Android does not. It became departure D1 because someone had read both codebases.
Step 4 below is that check, run mechanically.

## Inputs

| | |
|---|---|
| The spec | `product/specs/QACR-APP-SPEC-nn.md` |
| Requirements | `product/FR-01/requirements.json` |
| Features | `product/EPIC-01/features.json` |
| Code evidence | `evidence/behaviour.tsv` |

## Steps

### 1 · Register

Place the spec in `product/specs/`. Read its header: document number, revision, status, the
features it claims to cover, and its milestone spread. Record these — you will check them.

### 2 · Coverage — does the spec answer for everything it covers?

For each feature the spec names, pull its requirements from `features.json`. For each requirement,
classify what the spec says about it:

| | |
|---|---|
| **departure** | the spec states QACR must differ. Note the `D-n` reference |
| **as-is** | the spec confirms the current product's behaviour stands |
| **open** | the spec names it as an undecided value or question |
| **silent** | the spec says nothing about it |

**Report every `silent` requirement.** A silent requirement has no QACR intent, so nobody can
build it — not because it is hard, but because nobody has said what it should do. Cross-check
against the spec's own traceability table: if it lists a requirement the feature does not own, or
omits one the feature does own, that is a defect in the spec.

### 3 · Departures — are they backed by evidence?

Each departure names the requirements it changes. For each, query `evidence/behaviour.tsv`:

```
grep '^FR-XXX-NNN' evidence/behaviour.tsv
```

**Zero rows means the departure is unverified against the code.** The spec is asserting something
about what the current product does, and nothing in this repo confirms it. That is not a blocker,
but it must be recorded — SPEC-01's D1 and D2 both landed on requirements with no evidence at all.

### 4 · As-is claims — the check that matters

For every requirement the spec confirms **as-is**, compare its `acr-ios` and `acr-android` rows.

Three outcomes:

- **They agree** → as-is is well defined. Nothing to do.
- **They disagree** → **as-is is undefined. Raise it.** State both behaviours and ask the PM which
  QACR takes, or whether this needs a departure. This is the D1 case.
- **One or both have no rows** → the claim is unverified. Say so; do not assume it holds.

Run this for every as-is requirement, not a sample. It is cheap and it is the highest-value check
available before code is written.

### 5 · Emit feature files

One file per feature covered, at `features/<epic>/<feature>.md`.

**Never restate what the spec says.** Link to it. A feature file adds only what the spec does not
have:

- the requirements it owns, as ids, with each one's disposition from step 2
- the relevant rows from `evidence/behaviour.tsv` — what the code does today, cited
- the per-platform task
- the acceptance criteria, one per testable statement, marked automatable or manual with a reason

If you find yourself copying a sentence out of the spec, stop. That is how the two drift apart.

### 6 · Escalate

Everything unresolved goes to `decisions/`, one file per question:

```yaml
---
id: D-nn
raised_on: <date>
raised_against: QACR-APP-SPEC-nn Rev n.n
affects: [FR-XXX-NNN]
blocks: [F0n.n]
owner: Product
status: open        # open -> sent -> answered -> closed
---
```

Then the question, what makes it a question, and what happens if it is not answered. When the
answer comes back, record it **verbatim** and set `status: answered`.

Never resolve one of these yourself by picking the more likely reading.

## Report

- Coverage per feature: departures / as-is / open / **silent**
- Every as-is claim where the two ACR platforms disagree — **lead with these**
- Every departure with no evidence rows
- Requirements the spec references that its features do not own, or vice versa
- Feature files written, decisions raised

## Never

- Fill in a QACR intent by inference from what ACR does. That is the failure this exists to catch.
- Copy requirement text into a feature file — `product/` holds the current wording.
- Add an acceptance criterion for behaviour the spec has not stated.
- Treat a silent requirement as as-is. Silence is not a decision.
