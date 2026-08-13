# product/specs/

The PM's `QACR-APP-SPEC-nn` briefs. **Read-only, like everything under `product/`.** To change a
spec, change the document and drop in the new revision.

## What is here

| | |
|---|---|
| `QACR-APP-SPEC-01 Rev1.2.md` | Readiness and eligibility. Covers F01.1–F01.6, F01.8, F01.9 of epic E01. Status: **ready** — reviewed and settled, build from it. |

## What a spec is, and what it is not

A brief is a **recreation brief**, not a specification of behaviour. Its governing rule:

> All the features it covers are recreations. **The current product is their specification.** Build
> them as Minuteful Kidney US behaves.

So the brief records only three things: what **departs** from the current product, what is **still
undecided**, and which requirement each feature answers to. It deliberately does not describe the
behaviour it is asking for — a brief that listed readiness conditions would be read as listing all
of them, and the current product has more than twenty, so a team building to that list would
silently remove working capability.

Where a brief and the current product disagree on anything not in its departures table, **the
current product is right.** Raise it rather than implementing the brief.

## Naming

`QACR-APP-SPEC-nn Rev<major>.<minor>.md`. Keep every revision that has been built against; the
highest revision is the live one.

## When a new one arrives

Run the `spec-intake` skill (`.claude/skills/spec-intake/`), or step through `SDLC.md` by hand. It
traces the spec against `product/FR-01/requirements.json`, checks its as-is claims against what the
code actually does, writes the feature files, and escalates whatever the spec leaves undecided.
