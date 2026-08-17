# decisions/

Questions only Product can close. **Empty because Product has raised no question here yet.**

One file per question, `D-nn.md`. Written by whoever ingests a spec, answered by Product.

A question lands here the moment a spec leaves something undecided, or a trace finds a requirement
the spec is silent on. It never gets resolved by picking the more likely reading — that buries it
until verification, which is the expensive place to find it.

## Format

```yaml
---
id: D-nn
raised_on: 2026-08-13
raised_against: QACR-APP-SPEC-nn Rev n.n
affects: [FR-XXX-NNN]
blocks: [F0n.n]
owner: Product
status: open        # open -> sent -> answered -> closed
---
```

Then, in prose:

- **The question.** One sentence, answerable.
- **What makes it a question.** The evidence — what each platform does today, with citations, or
  the requirement wording that admits two readings.
- **What happens if nobody answers.** What gets built by default, or what stops.

When the answer comes back, record it **verbatim**, set `status: answered`, and update the feature
files it unblocks.

## The two that already exist elsewhere

SPEC-01 carries departures D1 (battery check — the platforms disagree) and D2 (configuration set
travels with the test data). They are recorded in the spec itself rather than here, because the PM
resolved them before the brief was issued. Anything the PM has *not* resolved comes here.
