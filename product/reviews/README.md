# product/reviews/

Behaviour reviews the development team exports for an epic, with the product manager's
marks on them. **Tracked**, unlike everything under `local/`: an export is the team's own
work and the marks are the answer to it, so both belong where they can see what happened
to what they sent.

One export per epic, `acr-behaviour-review-E0n.json`, plus a disposition where one was
written.

## First read `review_mode`, then choose how to count

**The team exports in two modes, and the field says which.** Reading a file in the wrong mode
is the single most expensive mistake available here — it cost a whole round of analysis once.

| `review_mode` | What a review item is | Seen in |
|---|---|---|
| `baseline` | **one behaviour = one item.** Count marks per line | E05, and E03 by default |
| absent, with `total_items` < `total_lines` | behaviours **grouped**; `pm_mark` and `pm_comment` belong to the group and are propagated down | E04 |

**In grouped mode, counting marks per behaviour multiplies them by the group size and tells you
nothing.** E04 read as 46 `change` marks that way; at item level it is 16 `change`, 13 `correct`,
1 `wrong` — sixteen departures against E03's fourteen, which is comparable rather than three
times worse. That misreading survived a whole round.

**In baseline mode the line is the unit again** and per-line counts are correct. E05 is
`baseline`: 181 behaviours, 76 `change`, 59 `correct`, 45 `unmarked`, 1 `wrong`.

**The check that works in both modes:** `total_items` against `total_lines`. Equal means
baseline; smaller means grouped.

### Which behaviour a comment is about

In grouped mode the comment names or quotes the behaviour it concerns, and Guy's rule applies:
**anything not referenced is correct.** A comment quoting one statement narrows to it; one
referencing nothing applies to the whole group.

In baseline mode the comment belongs to its own line and no derivation is needed.

### `complete: false` means different things in each mode

In **grouped** mode it is a field artefact: `reviewed_items` counts behaviours while
`total_items` counts groups, so 86 against 30 never reconciles and the flag never flips. Check
for `pm_mark: unmarked` instead.

In **baseline** mode the two units agree, so **`complete: false` is real information**. E05
reports 136 of 181, and the 45 unmarked are deliberate — see below.

### Not every line gets a mark, and that is not a gap

Where a feature is genuinely new, the same answer applies to many lines and Guy marks a
representative rather than all of them. **Derive the rest rather than asking again**: an
unmarked line whose subject already has an answer elsewhere in the same feature takes that
answer. E05's 45 unmarked cluster in F05.6 and F04.8 and almost all resolve to a decision he
made on a marked line nearby, or to a requirement already written.

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
