---
name: adr-conventions
description: Where and how QACR decisions are recorded — the log's location, entry grammar, id rules, and the PR that publishes them. Use when recording a decision or answer for any QACR feature or spec.
---

# Recording a QACR decision

**Every answer goes to `decisions/adr/DECISIONS.md` — one append-only log for the whole product.**
iOS and Android answer from and write to the same file. No per-feature log, no per-platform log,
no second location: a decision recorded anywhere else is one `qacr-context` never folds back into
a contract, so the question it answered gets asked again.

## The id spaces that already exist — never mint into them

A log entry's id is a question-derived slug (`FR-PLT-002-min-os-mechanism`) and belongs to
**none** of these spaces. A new id that reads like any row below is a collision, not a convention:

| id space | what it names | whose | lives in |
|---|---|---|---|
| `FR-XXX-NNN` | requirements | PM's | `product/FR-01/requirements.json` |
| `Q-nn` | the PM's decision log / review register | PM's | `product/FR-01/decisions.json`, `register.json` |
| `U1` / `Un` | brief open items | PM's | the brief |
| `SPEC-nn/Dn` | departures — **per-brief** ids, always qualified with their brief: `SPEC-01/D1` and `SPEC-02/D1` are different decisions | PM's | the brief |
| `PQ-nn` | questions this repository raises for Product | this repo | `decisions/*.md` |
| `SD-n` / `SQ-x` | a spec's own Decisions-needed / Open-Questions rows, scoped to that spec | the spec | the spec |
| `AD-nn`, `Ln`, `E-n`, `C-n`, `G-n`, `OZ-n` | backend-architecture decisions, and the layers, evidence, corrections, gaps and review comments behind them | the architecture spine | `architecture/spine-decision-log.md` |

**There are two append-only logs in this repository, and they are not interchangeable.** This one
answers questions a *feature specification* raised — per requirement, per feature, keyed to a brief.
`architecture/spine-decision-log.md` records decisions about the *backend architecture spine*, and
`architecture/spine.md` is distilled from it. A decision belongs to whichever log owns its subject;
recording it in both makes two records that will disagree, and recording it in neither is how it
gets decided twice.

**A mobile `architectural` decision has no settled home yet.** The side-write below names
`architecture/ios.md` / `architecture/android.md`, and neither file exists — while
`architecture/spine-decision-log.md` does, and is scoped to the backend. Do not resolve this by
writing a mobile decision into the spine log. Record it here, and raise the destination as a
question rather than choosing one.

## Entry rules

The full template lives in `decisions/adr/DECISIONS.md` itself — copy it from there, never from
memory. What it encodes:

- **Append-only.** Entries are never edited or deleted. Superseding = appending a new entry with
  `supersedes: <old id>`; currency is derived by scanning. The one in-place edit the log permits
  is `record_status` (below).
- **One `## <id> — <question>` heading + one fenced yaml block + short prose.** Every field
  present on every entry, `n/a` when not applicable, never omitted.
- **Ids derive from the question** — requirement id plus a slug. Sequential numbering is
  forbidden: two developers answering the same question must produce the same id and conflict
  loudly in git.
- **`status: deferred` is a legitimate answer** — reason, owner, and what reopens it — and counts
  as resolved for gating.
- **Context** (evidence, citations) and **Decision** are mandatory prose. **What the document
  must say** — exact paste-ready text for the document owner — on `product` entries only.
  **Alternatives considered** only when alternatives were genuinely weighed.

## The architectural side-write

**A `type: architectural` entry is not finished until its rule is also registered in
`architecture/ios.md` or `architecture/android.md`** — or both, when it binds both domains —
citing the entry id. The log records the decision; the architecture file is where the next
feature's `qacr-context` run reads the rule. One without the other is half a record.

## The gate, and the PR that publishes

**Answers accumulate uncommitted in the working tree.** `qacr-context` reads the working tree, so
the developer's own next run already sees them — nothing needs publishing for the loop to keep
moving.

**When every Decisions-needed row of the spec in hand is answered or deferred, publish — do not
ask first.** An answer that never leaves the developer's machine is invisible to the other
platform's next run, which is the one thing this shared log exists to prevent, and the way it
fails is silence: nothing errors, the log simply never arrives. A prompt at this point is the
user error, not the safeguard against it. A pull request is reviewable, amendable and closeable;
it is not a merge, and merging stays a human's decision.

**One pull request per feature, reused across rounds.** The branch is `decisions/<feature-id>` —
derived, never invented, so every round finds the same one:

1. **Look for an open pull request on `decisions/<feature-id>` first.** If one exists, add a
   commit to that branch and say which PR was updated. A second PR for the same feature splits
   the review and lets two versions of the same decisions land independently.
2. If none exists, create the branch from the default branch, commit, push, and open the PR.
3. If the PR for this feature is already **merged or closed**, start a fresh branch and PR for
   the new round — do not reopen a settled one.

**Never force-push, never merge, never commit onto the default branch.** If the remote branch has
moved since you last saw it, fetch and rebase onto it; if that cannot be done cleanly, stop and
report rather than overwriting — someone else's review context lives on that branch.

**Announce, do not gate.** Before pushing, state what is going out: the entries added or amended,
the branch, and whether this creates a PR or extends one. Afterwards, report the URL. That is
disclosure, and it is what replaces the old confirmation step.

The developer keeps two overrides: they may tell you not to publish this round, and they may
close the PR. Neither requires asking in advance.

## The export digest

After publishing, generate a digest of the `product`-type entries, grouped by `decided_by` /
document owner, each carrying its **What the document must say** text — for the developer to
deliver **themselves** to the document owners. This skill generates the digest; it never sends
anything anywhere.

## The `record_status` duty

When a requirements revision lands (via `revision-intake`), every entry whose awaited revision
arrived gets `record_status` updated in place to `in-<revision>` — the one edit the log permits.

**If the revision contradicts an `accepted` entry, that is a stop.** Surface both — the entry's
answer and the revision's wording, verbatim — for a human. Never silently supersede; the
contradiction is the finding.

## Boundaries

This path writes **only**:

- `decisions/adr/DECISIONS.md`
- `architecture/ios.md` / `architecture/android.md` — the architectural side-write

Never `product/`, never `features/`, never `evidence/`, never `decisions/*.md` — the `PQ-nn`
files are questions this repository raises for Product, not answers, and this path does not own
them.
