# product/specs/

The PM's `QACR-APP-SPEC-nn` briefs. **Read-only, like everything under `product/`.** To change a
spec, change the document and drop in the new revision.

## What is here

Every revision that has been built against is kept. The highest revision of each document is
the live one; the rest are history.

| Live document | Covers | Status |
|---|---|---|
| `QACR-APP-SPEC-01 Rev1.6.md` | E01 readiness and eligibility — F01.1–F01.6, F01.8, F01.9 | **ready** |
| `QACR-APP-SPEC-02 Rev1.3.md` | E02 identity and authentication — F02.1–F02.8 | **ready** |
| `QACR-APP-SPEC-03 Rev1.3.md` | E03 kit capture and validation — F03.1, F03.2 | **ready** |
| `QACR-APP-SPEC-04 Rev1.3.md` | E04 guided test flow engine — F04.1–F04.7 | **ready** |
| `QACR-APP-SPEC-05 Rev1.3.md` | E05 timing and waiting, plus F04.8 | **ready** |

## What a spec is, and what it is not

**Authority is per feature, not per document.** Each spec opens with a *What this document
defines* table naming, for every feature it covers, the source that defines that feature's
behaviour:

| | |
|---|---|
| **`recreated`** | **Minuteful Kidney is authoritative.** The document records only what departs from it. |
| **`new`** | **The document is authoritative.** It describes the behaviour in full, because there is nothing to recreate. |

One document can hold both — SPEC-04 is six recreated features and one new one. So do not ask
what kind of document you are holding; ask which row your feature is on. The precedence rule
attaches to the row:

> Where this brief and the current product disagree on anything not in the departures table,
> **Minuteful Kidney is right.** Raise it rather than implementing the brief.

That rule is what lets a `recreated` feature stay short. Such a section deliberately does *not*
enumerate the behaviour it wants — a brief that listed readiness conditions would be read as
listing all of them, and the current product has more than twenty, so a team building to that
list would silently remove working capability. It records three things instead: what **departs**,
what is **still undecided**, and which requirement each feature answers to.

A `new` feature has no such backstop, so its behaviour is written out and the document is read as
exhaustive for it.

## Reading a departures table

The columns are `# | Feature | Today | In QACR | Driven by`.

**Today** is Minuteful Kidney's behaviour — the thing being changed. **In QACR** is what is being
asked for. Every row is readable on its own; you do not need the behaviour review it was written
against.

Where the two platforms differ today, `Today` says so — *one does X, the other does Y* — without
naming which is which, because that is implementation detail. Where a row names the platform QACR
follows, that is a product decision about which behaviour to adopt. **It is not an instruction to
compare the platforms**; verifying parity is a QA activity at the end, and no departure row
creates a development obligation to check one platform against the other.

## Naming

`QACR-APP-SPEC-nn Rev<major>.<minor>.md`. Keep every revision that has been built against; the
highest revision is the live one.

## When a new one arrives

Run the `spec-intake` skill (`.claude/skills/spec-intake/`), or step through `SDLC.md` by hand. It
traces the spec against `product/FR-01/requirements.json`, checks its as-is claims against what the
code actually does, writes the feature files, and escalates whatever the spec leaves undecided.
