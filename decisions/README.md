# decisions/

Questions **this repository** raises that only Product can close. **Two open**, both raised against
SPEC-02 Rev 1.1. That is not the same as Product's own open questions — see below.

| | | |
|---|---|---|
| `PQ-01` | Does the current product persist an authentication credential? | `FR-SEC-008` · blocks `F02.5` |
| `PQ-02` | At M3, is anything owed client-side for the OTP attempt limit? | `FR-AUT-018` `FR-AUT-005` · blocks `F02.2` |

One file per question, `PQ-nn.md`. Written by `qacr-context` — the skill that finds silent
requirements and contradiction stops while assembling a feature's contract — and answered by
Product. Not by the intake skills: `spec-intake` and `revision-intake` both explicitly forbid
writing here.

A question lands here the moment a spec leaves something undecided, or a trace finds a requirement
the spec is silent on. It never gets resolved by picking the more likely reading — that buries it
until verification, which is the expensive place to find it.

## Format

```yaml
---
id: PQ-nn
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

## Answers to spec-raised questions live in `adr/`, not here

The `adr/` subdirectory holds the answer log — one file, `decisions/adr/DECISIONS.md`, for the
whole product. The split: a question **this repository asks Product** is a `PQ-nn` file here; an
answer to a question **a spec raised** (its Decisions-needed / Open-Questions rows) is an entry in
the log. How to write one is `.claude/skills/adr-conventions/SKILL.md`.

## The two that already exist elsewhere

SPEC-01 carries departures D1 (battery check) and D2 (configuration set
travels with the test data). They are recorded in the spec itself rather than here, because the PM
resolved them before the brief was issued. Anything the PM has *not* resolved comes here.

## Product's own questions are not in here, and must not be copied here

The FR document carries two registers of its own, and between them they are the larger backlog:

| | | |
|---|---|---|
| its **Decision Log** | questions Product has **closed**, `Q-nn` | `product/FR-01/decisions.json` |
| its **Review Register** | questions Product has **open**, `Q-nn`, in six groups | `product/FR-01/register.json` |

Both are parsed from the document by `tools/parse_product_docs.py` and validated against the counts
the document states about them — the register's front matter states its open items per group, and
their total. Read them there. **Do not copy a row of either into a `PQ-nn.md` file.**

Three reasons, and the first is the one that matters:

1. **A copy is a fork.** The same rule that stops a requirement being restated here stops a decision
   being restated. Product rewords a decision in the next revision and the copy silently becomes the
   old answer, indistinguishable from the current one. The parsed JSON is regenerated from the
   document every revision; a file here would not be.
2. **Two id spaces would collide.** `PQ-nn` is raised by this repository against a *spec*. `Q-nn` is
   raised by Product against the *requirements document*. Merging them loses which is which, and
   with it who is waiting on whom.
3. **The lifecycles are different.** A `PQ-nn` moves `open -> sent -> answered -> closed` under
   someone here. A `Q-nn` moves when Product issues a revision, and this repository only observes it.

So the question this folder answers stays narrow: *what did reading a spec against `product/` turn
up that nobody has decided?* A revision arriving is how Product answers its own; `tools/diff_revisions.py`
reports which `Q-nn` rows moved, and that report belongs in the ingestion's commit message rather
than in a file here.
