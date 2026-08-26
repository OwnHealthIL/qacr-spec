# product/reviews/

Behaviour reviews the development team exports for an epic, with the product manager's
marks on them. **Tracked**, unlike everything under `local/`: an export is the team's own
work and the marks are the answer to it, so both belong where they can see what happened
to what they sent.

One export per epic, `acr-behaviour-review-E0n.json`, plus a disposition where one was
written.

## How to read one

Each line of the export is a behaviour statement about the shipped ACR product, with what
iOS does, what Android does, and whether they agree. The product manager's verdict is
`pm_mark` on each line:

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
