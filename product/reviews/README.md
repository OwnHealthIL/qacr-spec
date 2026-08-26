# product/reviews/

Behaviour reviews the development team exports for an epic, with the product manager's
marks on them. **Tracked**, unlike everything under `local/`: an export is the team's own
work and the marks are the answer to it, so both belong where they can see what happened
to what they sent.

One export per epic, `acr-behaviour-review-E0n.json`, plus a disposition where one was
written.

## Read it at the item level, not the line level

**This is the thing to get right before anything else.** From E04 onwards the team groups
similar behaviours into **review items**, because reviewing 86 statements one at a time is
worse than reviewing 30 groups. So:

| | |
|---|---|
| a **behaviour** | one statement about the shipped product, with what iOS does and what Android does |
| a **review item** | a group of related behaviours — E04 has 30 of them over 86 behaviours, from 1 to 5 each |
| `pm_mark`, `pm_comment` | properties of the **item**, written once and propagated to every behaviour under it |

**Counting marks per behaviour multiplies them by the group size and tells you nothing.**
E04 read as 46 `change` marks that way; at item level it is 16 `change`, 13 `correct`,
1 `wrong` — sixteen departures against E03's fourteen, which is comparable rather than
three times worse. That misreading survived a whole round of analysis.

**The unit of a departure is the comment, not the line.**

### Which behaviour is a comment about

The comment names or quotes the behaviour it concerns. The rule, from Guy:

> The comment is per item, and it references the relevant behaviour. **Anything not
> referenced is correct.**

So a comment quoting one statement narrows to it — *"all is correct, except for the timer
that runs out"* is one of that item's three — and a comment referencing nothing specific
applies to the item as a whole.

### `complete: false` is a field artefact

`review.reviewed_items` counts behaviours while `total_items` counts items, so 86 against
30 never reconciles and the flag never flips. **Check for `pm_mark: unmarked` instead.**

## The marks

`pm_mark` is per item:

| | |
|---|---|
| `correct` | the statement describes what QACR should do. Nothing to write |
| `change` | QACR departs here. This is the raw material of a departures table |
| `wrong` | the statement is not true of the product. **This is a research task, not a departure** |
| `unmarked` | not yet answered. Not the same as `correct` |

## Three things that are true of every export so far

**`checked_against` is a revision, and it is behind.** Every `coverage` verdict —
`covered`, `partly`, `uncovered` — is relative to the revision named there, and the file
says so itself. **Re-map every requirement against the current revision before believing a
gap.** E03's export was read against a pre-Rev-1.18 document and six of its ten proposals
were requirements that already existed.

**The `ios` and `android` columns are implementation detail.** They are here so a
requirement can be made *accurate*. They do not travel into a spec — see the altitude rule
in section 5 of CLAUDE.md, and section 11 on why proximity makes that harder rather than
looser.

**`platforms: differs` is not a finding.** Cross-platform parity is verified as a QA
activity at the end, by decision. It is not a spec item, not a development obligation, and
not a verification activity to propose.

## An export is not a triage

A `change` mark says the product differs from the statement. It does not say the feature's
spec status was right. Where an `Unchanged` feature attracts a lot of `change` marks, **the
status is what to question, not the marks** — that is the tripwire in section 5, and it
cuts both ways.
