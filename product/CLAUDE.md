# QACR user application — document set

QACR (Kidney Check) is a prescription-only, home-use IVD: a smartphone-read urine test
reporting albumin, creatinine and their ratio. Software safety classification **IEC 62304
Class B**. Heading for **FDA submission**. Guy Raviv (Product) owns this document set.

> **You are inside `product/`, the product manager's directory of the shared `qacr-spec`
> repository.** The development team works in the same repository, in the directories
> beside this one. **Read section 11 before touching anything outside `product/` — and
> the short answer is that you do not touch anything outside `product/`.**

Because this is a regulated submission, **traceability is the product**. A requirement
that loses its trace, or a document that disagrees with its sibling, is a finding.
That is why so much of what follows is about guards rather than content.

---

## 1. The rule that governs everything: derived, not typed

The `.js` data modules in `generator/` are the **only** source of truth. Every `.docx`,
`.html` and `.xlsx` at the project root is an **output**.

> **Never edit a .docx, .html or .xlsx deliverable by hand.** Edit the data module and
> rebuild. A hand edit is silently destroyed by the next build, and until then the
> document disagrees with the data that is supposed to define it.

Milestones, feature membership, per-milestone splits, dev domains and spec status are all
**computed** from the data. Nothing is typed twice. The guards fail the build on drift.

**Run everything from `product/`.** That is where `package.json` lives.

```
npm install          # once: docx 9.7.1, jsdom for verifying the board
npm run build        # rebuilds all three deliverables, archives superseded revisions
npm run check        # every guard; exits non-zero on any disagreement
npm run all          # both
```

The layout, and the reason for it:

```
product/
├── generator/     the source of truth. The .js data modules ARE the requirements
├── FR-01/         QACR-APP-FR-01, built straight into here
├── EPIC-01/       QACR-APP-EPIC-01 and the Board, built straight into here
├── specs/         QACR-APP-SPEC-nn briefs, revision in the filename
└── local/         NOT IN GIT. Source material that is not the team's business
```

**`npm run build` writes each deliverable into the directory it is published from.**
There is no staging copy and no separate publish step. A staging area plus a copy would
put two copies of every deliverable inside `product/`, and a second copy of a deliverable
is read as current by whoever finds it first. `npm run check` reads the same paths, so
what the guards check **is** what the development team reads.

`npm run check` must pass before anything is circulated. It is not advisory.

**First run in a new clone.** `npm install`, and Python needs `python-docx` and `lxml`. On a
Homebrew Python, which is PEP 668 externally-managed, `pip install --user
--break-system-packages python-docx lxml` is what Homebrew's own message recommends.
`package-lock.json` is committed, so the `docx` version is reproducible.

---

## 2. What is in here

### Outputs — generated, never hand-edited

| File | What it is |
|---|---|
| `FR-01/QACR-APP-FR-01 Functional Requirements Rev*.docx` | **Authoritative.** 248 requirements in 22 sections, 41 of them at milestone 5, plus appendices and the review register. The document RAQA and software QA work from. |
| `EPIC-01/QACR-APP-EPIC-01 Epic and Feature Map Rev*.docx` | A delivery view of the same requirements: 15 epics, 82 features, milestone per feature. Adds no requirements and changes none. |
| `EPIC-01/QACR-APP-EPIC-01 Board.html` | The epic map as a filterable single-file page. Self-contained, no network. Shared with developers. |
| `local/QACR-APP-SPEC-00 Spec Triage.xlsx` | The answered triage: per-feature spec status. Its answers now live in `generator/spec-status.js`. |

### Sources of truth — `generator/`

| Module | Holds |
|---|---|
| `version.js` | **The only place a document revision may be declared.** Bumping `FR` requires bumping `EPIC` too: the epic map and the board both cite the FR revision in their prose, so leaving `EPIC` alone would put two different documents into circulation under one revision number. |
| `reqs-part1.js`, `reqs-part2.js` | The 248 requirements. Row: `[id, requirement, source, notes, priority]`, where priority is the milestone. |
| `epics.js` | 15 epics, 82 features. Row: `[featureId, name, [FR ids], [], intent, uxNote, split?]`. The fourth element held deferred items and is now always empty; it is kept only because removing it would shift the positions of `intent`, `uxNote` and `split` in fourteen readers, and a prose field rendering in the wrong place is a failure no guard here would catch. Removing it is its own change. |
| `appendices.js` | `withdrawn` (Appendix D). `backlog` is now empty: it was dissolved into milestone 5 at Rev 1.18. |
| `m5-map.js` | The approved disposition of all 42 former backlog items. Read it before touching any identifier that carries `formerly BL-nn`. |
| `review.js` | The open register (parameters / conflicts / scope / raEdits / consequences) and `closed`, the decision log. |
| `domains.js` | Curated dev domain per feature: iOS, Android, Backend, Algo, Content, Process. Explicit map, not derived — the build fails if a feature is missing. |
| `spec-status.js` | Spec status and "what changes" per feature, from the answered triage. Also **where each spec document has got to** — `ready` means reviewed and settled, build from it; `drafted` means written but not reviewed; unnamed means not written. The board renders it, because a developer opening a document needs to know whether it is still moving under them. |
| `spta.js`, `configs.js` | Threat-analysis mapping and the configuration register. |
| `id-guard.js`, `id-manifest.json` | Identifier stability: 319 identifiers on record. |

### Builders and guards — `generator/`

`build.js` · `build-epics.js` · `build-board.js` · `build-all.js` — generators.
`consistency-check.py` — 1,815 checks, including three added after Rev 1.18 shipped: the
review register's group counts must equal what `review.js` holds, so a document built from
data that has since moved on fails; no artefact may name a `BL-nn` outside a `formerly`
marker; and no artefact may refer to a backlog at all. Those two carry explicit allowlists for
genuine history, in the same spirit as `id-manifest.json`. A fourth: no row may claim it was
`formerly` its own identifier.
`spec-check.py` — spec coverage, that every revision a
spec cites is the current one, and that every identifier a spec **traces** to is a live
requirement. A retired identifier may be discussed in prose; it may not be traced to.
`check-all.py` — runs them all. `spec-triage.py`, `build-conflicts.py`, `build-m5-proposal.py`,
`apply-m5.py`, `remap-bl.py` — one-off builders and migrations, kept because for a regulated
document set how a bulk change was made is part of its record.

### Reference

`local/Source documents/` — Risk Analysis, both SRSs, the SPTA, the product glossary, the
development plan, the Minuteful Kidney description, the reaction-waiting-time UX study.
`local/Reference/Minuteful screenshots/` — Minuteful Kidney UI, for the recreation specs.
`local/Reference/Minuteful copy/` — the Minuteful content set as a starting point.
`specs/` — the spec layer, revision in every filename. `Previous revisions/` —
superseded outputs, not in git: git history is the archive that ships.

---

## 3. Identifier scheme

**Requirements** `FR-XXX-nnn` where XXX is the section. There are 22, and they are:
PLT, RDY, AUT, CNS, KIT, FLW, TXT, STA, TIM, IMG, CAM, COM, ALG, RES, ACC, PRT, SHR,
SUP, ANL, SEC, CFG, LCM.

`FR-SUR` (post-test survey) is **not** among them and must not be reintroduced: FR-SUR-005
was withdrawn and FR-SUR-001 to 004 were superseded to BL-29 to BL-32. Section 2 of the FR
document carries an authored prefix legend, and `consistency-check.py` fails if that legend
lists a prefix no section uses, or omits one that a section does — Rev 1.16 shipped
advertising an FR-SUR section that does not exist.

**`Q-nn`** review register. **`F0n.n`** features.
**`S0n.nn`** spec behaviour statements.

**Identifiers are never reused and never silently disappear.** `id-guard.js` fails the
build if one vanishes without a recognised disposition: withdrawn, superseded,
consolidated, or **promoted** — a backlog item brought into scope, which the notes must
record as `formerly BL-nn`.

**`BL-nn` no longer exists as a live identifier class.** The backlog was dissolved at Rev
1.18: all 42 items took FR identifiers in their own sections. Fourteen were restored to the
exact identifier they had been superseded from; four carry `originally FR-SUR-nnn` because
their chain runs through two hops; BL-38 was withdrawn. Every one of the 41 migrated
requirements records `formerly BL-nn` in its source, and that phrase is what `id-guard.js`
reads to know where the identifier went.

> **Never rewrite a `formerly BL-nn` marker to the requirement's own identifier.** A blind
> BL-to-FR substitution did exactly that during the migration, leaving 41 rows claiming they
> were formerly themselves. The build still passed, because the manifest already held the
> dispositions from an earlier correct run — the guard was satisfied by its own memory.

---

## 4. Milestones

The priority field **is** the milestone. There is no separate schedule.

| | Meaning | Date |
|---|---|---|
| 1 | Demonstration | mid-October 2026 |
| 2 | Usability rehearsal | early December 2026 |
| 3 | Clinical study and submission — must | early January 2027 |
| 4 | Clinical study — high | early January 2027 |
| 5 | Future development | none |
| TBD | undecided | — |

**Some risk controls are guarded by the product manager, not by the software.** Especially the
configuration-driven ones. A requirement may say that behaviour is determined by configuration —
whether an update is mandatory or dismissible, which checks apply to a partner — without that
weakening the control, because Guy enforces the values and keeps the mandatory ones mandatory.
So do not reach for a mechanism in the requirement to make a configured control tamper-proof.
Say what the product does and let configuration be configuration.

Milestone 5 is future development. It sits in the body with its section and its
traceability, carries no date, and carries no verification obligation for this submission.
It is not a backlog: there is no separate list and no second set of identifiers.

3 and 4 share a date, so **a must-have may not depend on a nice-to-have**. There is no
milestone between the study and the submission. Eight such inversions were found and
dispositioned; two remain open (Q-39, FR-CAM-002).

---

## 5. Writing specs

The spec layer sits below the epic map. From the answered triage: **13 spec documents cover
66 of 82 features.** E07 (content) and E15 (process) need no document at all.

Two counts that are easy to confuse. **65** features have a status other than `No spec`.
**66** are actually carried by a document, because F05.3 is `No spec` — it gets no document
of its own — yet is described inside SPEC-05, and is special-cased as such in
`spec-status.js`. So 16 features, not 17, get nothing at all.

### The altitude rule: specs stay at the product-requirement level

> **A spec says what the product must do. It never says how the existing code does it.**

The development team reads the requirement and decides whether Minuteful's implementation
serves it or whether it has to be built again. **That decision is theirs, and a spec must
not pre-empt it or appear to have made it.**

So a spec must not contain:

- a value read out of a build, a configuration file or the source — a duration, a
  threshold, a window, a retry count;
- a file, class, function, module or configuration-key name;
- any account of how the existing product achieves something, including its data
  structures, its lifecycle, or what it holds in memory;
- a verdict on whether existing code can be reused, extended or must be replaced, or any
  estimate of that work.

**What `/mind` and `local/Reference/Minuteful copy/` are for.** Context, so the product
requirement is *accurate* — that a capability already exists, that a condition is already
handled somewhere, that a flow already routes to support, that two things a requirement
treats separately are one thing to a user today. That context belongs in the spec as
product behaviour and in the `What differs from Minuteful Kidney` section as changed or
unchanged. The internals that carried you to it do not travel with it.

**When research turns up something that matters, convert it, don't quote it.** An
implementation detail that bears on the product becomes a *product question* in
`Open items`, with the implementation stripped out. "The displayed countdown is five
seconds longer than the enforced wait" is research. "Must the displayed countdown state
the same deadline the software enforces?" is the spec. Same finding, and only the second
is ours to write.

Values a spec does need — a duration, a threshold — are open items until Guy or the
relevant study sets them. `TBD` with a pointer is correct and finished. Borrowing the
predecessor's number to fill the gap is not.

### For every condition, say which of three things it does

The first draft of SPEC-01 called everything a block, and that was the biggest inaccuracy in
it — worse than any missing condition, because it read as authoritative. For each condition a
spec names, state which it is:

| | |
|---|---|
| **Blocks** | the user cannot continue |
| **Notifies** | the user is told and continues; say whether it repeats or is shown once per state |
| **Configured off** | the check does not run for this partner, so nothing was assessed |

**A check that configuration has switched off is not a check that passed**, and a register that
does not distinguish them reads as a list of guarantees it cannot make. Where a check is
configurable, that is part of the requirement — say so, and say who decides. Getting this wrong
is expensive in both directions: a notification implemented as a block costs a user their test,
and a block implemented as a notification defeats the control.

Likewise, do not assume a value the backend supplies has no fallback. Ask whether there is a
built-in default, because "the server did not answer" and "the server did not override the
default" are different conditions with different user-facing outcomes.

### Spec status means spec effort, not scope

Milestone carries scope. Status says only how much writing is needed.

| | | Count |
|---|---|---|
| **New** | no Minuteful equivalent | 7 |
| **Changed** | exists in Minuteful, differs for QACR | 18 |
| **Unchanged** | a recreation; the spec records it rather than redesigning it | 40 |
| **No spec** | nothing coming: the requirements are the spec, or it is content/process/algo | 17 |

The counts above are spec effort and have not changed. What changed at Rev 1.18 is that the
requirements those features trace to are milestone 5 rather than backlog items.

Seven **Unchanged** features are milestone-5 future development that will still be spec'd. Their
specs must say so in the header, or a reader takes them for submission scope.

### Specs are not strictly one per epic

A spec document owns an **explicit feature list**. `QACR-APP-SPEC-05` is the anchor for
the reaction wait and absorbs F05.1, F05.3, F05.5 **and F04.8, which belongs to E04**,
because the waiting-time card cannot be described apart from the countdown it carries.
Every spec'd feature must appear in exactly one document.

### Two document shapes, chosen by status — this is the most important choice you make

**An `Unchanged` feature does not get a behaviour section. It gets a recreation brief.**

For a recreation, every specific statement written is either noise or a defect. If it is
right it restates what the application already does, and the team opens the code anyway. If
it is slightly wrong it silently becomes an instruction to change a working product. There
is no version of it that adds value.

Worse, enumeration reads as complete. A register of thirteen conditions means "these are the
conditions", so a team building to it **removes capability that already works**. That is not
a risk of the approach, it is the approach's normal failure. SPEC-01 Rev 0.5 listed thirteen
where the product has more than twenty, all marked blocking where two only notify. It cost a
lot of effort to discover, and the whole feature set had been triaged `Unchanged` — meaning
the correct document was always one page.

| Status | Shape |
|---|---|
| **Unchanged** | **Recreation brief.** Records departures, undecideds, traceability. Never behaviour. |
| **Changed** | **Ask Guy for his brief on it first.** A one-liner where the rest is unchanged is a *departure row* inside the brief and needs no behaviour section — the common case. Anything larger needs a behaviour section, and that shape is not settled yet. Never assume which: a `Changed` status says something differs, not how much. |
| **New** | Full spec, per the template below. The writing earns its place because there is nothing to recreate. |

A mixed document is brief-by-default with behaviour sections only for the features marked
`Changed` or `New`. SPEC-01 is the worked example: eight features, one behaviour section.

**The brief's shape** — see the live revision of `specs/QACR-APP-SPEC-01`:

*How to read this* (carrying the precedence rule) · *Scope* · **Departures** ·
behaviour sections for `Changed`/`New` features only · *Undecided before build* ·
**Requirements proposed** · *Traceability* · *Not in this brief*.

Two properties do the work, and neither is optional:

> **Where this brief and the current product disagree on anything not in the departures
> table, the current product is right.** Raise it rather than implementing the brief.

and the brief never enumerates behaviour, so it cannot be read as exhaustive. A wrong line
in a brief cannot cost a capability.

**The departures come from the triage, not from research.** `spec-status.js` already holds
"what changes" per feature. That *is* the departures table — an `Unchanged` feature with no
note has none, and the seven `derived` notes are exactly where one is uncertain and needs
Guy. Most of a brief is derivable from data we already hold.

**Research is bounded to one question**: is the triage right, and is the departures list
complete? Never research in order to describe. That has no stopping condition and is what
made SPEC-01 expensive.

**Tripwire, and it cuts both ways.** If an `Unchanged` feature starts wanting behaviour
statements, it is mis-triaged — stop and say so rather than writing them. And if a `Changed`
feature's note carries `src: "derived"`, **the status itself is derived and may be wrong.**
F01.9 was marked Changed on a derived reading that the configuration set had been broadened
for QACR. It had not: configuration works as it does today, some values required before a test
may start and some not, some with built-in defaults and some without. Two revisions of SPEC-01
carried a behaviour section for a recreation on the strength of that one word.

**So confirm the status before writing behaviour, not after.** A derived `Changed` is a
question for Guy, and it is a cheap question — one line, answered in a sentence — against the
cost of describing a working product and then unpicking it. SPEC-01 ended with **eight
features, two departures and no behaviour statements at all**, which is what an all-recreation
brief should look like.

### A ready spec carries no proposals

**While a spec is in draft**, the requirements it calls for live in it, so they are reviewed
alongside the behaviour that revealed them.

**When it moves to ready, that section comes out.** A ready document is what a developer builds
from, and a list of requirements awaiting a product decision is not something anyone builds
from. It also dates badly: the moment one is approved the section is wrong.

So on promoting a spec to ready, **report in the conversation** — not in the document:

- which new requirements Guy approved, and which he declined;
- a **proposed milestone for each**, checked in both directions so it neither depends on
  anything later nor is depended on by anything earlier. The rule in section 4 is the trap: a
  must-have may not depend on a nice-to-have, and milestone 5 has no date at all, so a
  milestone-3 departure resting on a milestone-5 requirement is the worst version of it;
- what is needed from him to implement them across the other files — identifiers and their
  sections, any requirement text that a decision would change, and the side effects on counts,
  the review register and the epic map.

Then implement in a pass of its own, against `version.js` and the guards.

### Then propose the requirements the product already earns

A recreation inverts the usual direction: the shipping product is de facto scope, so where
it does something the requirements do not cover, **the requirements are incomplete and the
submission understates the software**. For Class B that is a regulatory gap, not
bookkeeping — SPEC-01 found ten distinct backend refusals where the FR document covers
three.

So every brief ends with a **Requirements proposed** section. Rules:

- **Propose, never edit.** The FR document is reviewed before it is changed.
- Prefer **promoting a backlog item** to inventing an identifier. Four of SPEC-01's
  configuration requirements had been written and then superseded to BL-33, BL-34 and
  BL-35, or withdrawn — so the mechanism existed and the honest move was promotion, which
  the notes must record as `formerly BL-nn`.
- Say where each came from: Guy's decision, or observation of the product.
- **Give each a proposed milestone**, because milestones 3 and 4 share a date and adding
  scope has a schedule consequence. Proposed, not assumed.
- A capability that exists and is *not* wanted is also a proposal — to exclude it
  explicitly, so nobody recreates it by default.

### Template

Read the two pilots before writing a third — they establish both shapes:
the live revisions of `specs/QACR-APP-SPEC-05` (a full spec) and
`specs/QACR-APP-SPEC-01` (a recreation brief).

The sections below are the **full-spec** template, for `New` and `Changed` features only.

Sections: **Scope** · **Concepts** · **Behaviour** · **States and transitions** ·
**Data requirements** · **Analytics events** · **Copy** · **What differs from Minuteful
Kidney** · **Open items**.

No goals, background or metrics — these are recreations of a working product, and Guy
does not want fully-blown specs.

### The behaviour section is the whole job

> **The functional requirements are written in regulatory language and are not
> descriptive enough to build from. The FR linkage is traceability only.** Behaviour
> statements must describe the product — the flow, the states, what the user sees, what
> the design must achieve — not restate the requirement.

Number them `S05.01`, `S05.02`, contiguously, and put the traces in an italic line under
each group: `*Traces: FR-TIM-001, FR-TIM-002.*`

**Never write a trace as a range.** `FR-RDY-005 to FR-RDY-010` is not machine-traceable
and `spec-check.py` will fail the file. Spell out every identifier.

Where writing the spec reveals something genuinely undecided, put it in **Open items** and
raise it. Do not invent an answer. Two came out of the pilots: whether a capture already
in progress may finish after the scanning window expires, and what the non-visual signal
is for the wait-to-act transition.

### Data requirements and analytics events

Both are placeholders to be filled later, but seed them from what the behaviour already
implies rather than leaving an empty heading.

### A spec states the rule; the product supplies the cases

> **The spec should not list which specific checks are on or off.** Guy, at the Rev 0.8 review.

The same instruction shaped the requirements SPEC-01 asks for: a requirement for the set of
backend refusals that does not enumerate the refusals, and one for block-or-notify that does
not say which conditions do which. Where the list is genuinely useful for review, it goes in an
appendix — not in the requirement and not in the brief.

The reason is the same one behind the whole brief format. A list in a spec is read as complete,
per-partner configuration changes which entries apply, and nobody updates the spec when it
does. **State the rule, and let the product be the list.**

### Copy — a spec never enforces it

> **Do not enforce copy in a spec. At all.** Guy's standing instruction, given at the Rev 0.7
> review of SPEC-01 and applying to every spec from now on. When the copy is designed,
> enforcement can start there.

So no spec states, constrains or polices user-facing wording: not a reading level, not "drawn
from the approved content set", not "labelled unmistakably". Those are content obligations, and
a spec that carries them puts a control somewhere nobody will maintain it. Where a content
obligation genuinely belongs in the requirements, it goes to the FR document as a proposal.

**Specs never quote copy.** Naming the copy *items a feature needs* is fine and useful —
which bubbles, which alerts, the key shape — because that is scoping the content work rather
than constraining its wording. Keys are engine-derived in the `urine-bible` repo, following
`chat bubble {section}` and `alert {scenario} title` conventions.

---

## 6. Content and copy

Copy lives in the **`urine-bible`** repo: CSV product folders → `bibleGeneratorEngine` →
`Localizable.strings` (iOS), `client_strings.xml` (Android), `locale.json` (web). On iOS,
SwiftGen then generates `L10n.camelCase` accessors. Product edits CSV and pushes; the apps
consume the generated files. **Product never hand-edits JSON, XML or .strings.**

Bubbles, static strings and alerts each get their own sheet — which is already how
`urine-bible` is laid out.

**The copy files hold written text only.** The spoken flow is **pre-recorded audio**, not
speech synthesised from the displayed text, so spoken and written wording are separate
artefacts that must be released together — which is why FR-TXT-004 covers both. A further
language means new recordings, not only new text.

**Voice and tone.** Grade 6 reading level (FR-TXT-001), measured **over the instructional
flow as a whole, not per string** — a button reading "Retry" produces a nonsense
Flesch-Kincaid score. Scoped to the instructional flow from test start through the results
chat, because that is what clinical study participants read and therefore what FDA
evaluates. Component names must match the product glossary (FR-TXT-002), enforced
editorially by Product, not by tooling.

`QACR content pipeline - proposal for dev review.md` is **parked** pending developer
feedback. Do not start the `qacr-us.acr` product folder or touch `KeyGenerator.py`.

---

## 7. How to see what changed — git, not a changelog

Guy works on this in two places: Cowork, and VS Code with Claude Code. **There is no
hand-maintained change log, and there must not be.** A changelog is one more file to keep
in step, and it would be the only record in here that no guard can verify.

Git is the log. To pick up where the other environment left off:

```
git log --oneline -15                # what happened, newest first
git diff HEAD~1 -- generator/        # the actual semantic change: data is text
git log -p -- generator/reqs-part2.js   # the history of one requirement set
git status                           # is anything mid-flight
```

**The data modules are the diff that matters.** The `.docx` and `.html` files are derived,
so their changes are a consequence, never a cause. A rebuild that produces no change in
`generator/` has changed nothing of substance.

Word documents still diff readably, via a textconv driver — useful for showing a reviewer
what a revision altered. Enable it once per clone:

```
git config diff.docx.textconv "python3 generator/docx2txt.py"
```

**Commit messages carry the why**, because that is the part no guard can reconstruct: what
Guy decided, what was found, what is still open. Write them for the other environment.
Standing state that outlives a commit belongs in section 9 below, not in a commit message.

**Commit *and push* before switching environments, and pull when you arrive.** This
changed when the work moved into `qacr-spec`. It used to be that git was a local notebook
with no remote, and the thing that actually carried work between Cowork and VS Code was
the shared folder — so "commit before switching" was the whole rule, and a commit nobody
could fetch was still good enough.

Now GitHub is the transport. A commit that is not pushed is invisible to the other
environment exactly as uncommitted work used to be, and it is worse, because a clean
`git status` now looks like nothing in flight while a whole branch sits locally.

```
git pull --rebase            # on arrival, before reading anything
git push                     # before leaving, every time
```

Both environments edit this file, so an uncommitted `CLAUDE.md` is still the likeliest
collision of all. If you arrive and the tree is dirty, the other environment is mid-task:
read the diff and stay read-only rather than editing over it. If you arrive and `git
status` is clean but `git log origin/HEAD..HEAD` is not empty, the other environment
committed and did not push — push it rather than building on top of it.

---

## 8. Verification discipline

Every one of these exists because something got through without it.

1. **`npm run check`.** Non-negotiable. It now runs `generator/layout-check.py` first,
   because every guard after it reads a file only that one proves is the right file — see
   section 11.
2. **Validate the XML** of every part of a rebuilt `.docx`. A malformed part opens fine in
   some readers and not others.
3. **Extract with python-docx** and confirm counts and distribution.
4. **Diff priorities against the previous revision** and prove zero unintended drift.
5. **Render to PDF and read the pages as images.** Text extraction cannot see a column
   too narrow for its content. This caught `+TBD` breaking mid-word and `Q-36` wrapping to
   `Q-3 / 6`.
6. **Never trust a guard that has only ever passed.** A guard never seen to fail is not
   known to work. Best: when you have found a real defect, **write the guard first and run
   it before fixing anything** — the shipped artefact is the test case, and it proves the
   guard against the real thing rather than against your idea of it. This is how the cover
   page, the `FR-SUR` legend row and the stale spec revisions were each confirmed. Failing
   that, inject the defect, watch it fail, then remove the injection.
7. **Ask what the guard does not look at.** All three defects above sat through every
   previous run because no guard looked, not because one was wrong. `npm run check` passing
   tells you what it tests, not that the documents are right. When something is found in
   one place, check the other places the same claim is written: the FR document, the epic
   map, the board, and the specs each state the revision independently.

### Mistakes worth not repeating

- **Specifying the mechanism when only the rule was wanted.** Proposing the amendment to
  FR-RDY-004, I worked out that a dismissible update alert would let a user proceed on an
  unsupported build and offered a two-threshold design to close it — minimum version blocks,
  recommended version nags. Guy's answer: too much implementation detail, that is how the
  product works, and the developers decide the shape. The requirement says an update may be
  mandatory or dismissible and that configuration determines which. **The pull toward
  over-specifying does not stop at behaviour statements; it reappears in requirement text, one
  level down.** See the product-manager-guarded controls in section 4.
- **A committed deliverable built from data that had already moved on.** Rev 1.18 shipped a
  review register saying 47 open items while `review.js` held 48: Q-100 was added after the
  build and the document was never rebuilt. Every guard passed, because they all compared a
  milestone or an identifier and none of them counted anything. The document and the source
  that defines it disagreed, which is the single thing section 1 exists to prevent.
  **After changing any data module, rebuild before committing** — and the register-count
  guard now enforces it, because the counts are a fingerprint of the data the document was
  built from.
- **Dissolving a concept without sweeping its prose.** The Rev 1.18 migration remapped 235
  `BL-nn` mentions across twelve files and still left eleven identifier references and fifteen
  mentions of "the backlog" in shipped text — including a requirement note pointing at "the
  backlog appendix", which had just been deleted, and a configuration register asserting the
  blocked state had no defined response in the same revision that gave it one. Identifier
  remapping is the easy half. **When a concept is retired, grep the built artefacts for the
  word, not just the identifier**, and separate genuine history from stale claims rather than
  deleting both.

- **Two documents shipped under one revision number, in two repositories.** SPEC-02 was
  issued to the development team at Rev 1.0, and then its `unauthorized` refusal was
  rewritten in prose at the Rev 1.23 pass — correctly, because a value read out of the
  backend is not something a brief may carry. The content moved and the number did not, so
  neither side could see it: each repository held a self-consistent Rev 1.0 and they were
  different documents. **A spec's revision now lives in its filename as well as its header**,
  the two must agree, and a published revision is immutable — see section 11. The lesson is
  the older one from `version.js`, arriving by a new route: a number that does not move is
  not evidence that nothing moved.
- **A guard for the seam nobody had needed yet.** Every guard in here reads a document and
  checks it against itself or against the data. All of them pass on a document at the *wrong
  revision*, because each half of a stale pair is perfectly self-consistent — the Rev 1.20
  document agrees with the Rev 1.20 data. While the deliverables sat in a working directory
  nobody else read, that was harmless. The moment they sat where a development team reads
  them it was not, and no existing guard asked the question. `layout-check.py` is that guard,
  and **its six checks were each watched failing against the real artefacts before being
  trusted** — including against this repository's own shipped `QACR-APP-SPEC-01 Rev1.2.md`.
- **A global find-and-replace on revision strings.** `Rev 1.9` → `Rev 1.10` across
  `build-epics.js` bumped the footer, missed the front matter (`"1.9 — Draft for review"`,
  no `Rev` prefix), and corrupted the "Derived from" row, which cites the *FR* revision.
  Rev 1.10 shipped saying three different things about itself. `version.js` and the
  revision guard exist because of this.
- **The fix for that mistake orphaned the one line it did not convert.** Each document
  states its revision a second time, on the cover, in a bare paragraph: `Document no.
  QACR-APP-FR-01 · Revision 1.15 (Draft)`. Until `version.js` that line was hand-edited
  every revision, and the archives show it correct all the way to FR Rev 1.15 and epic
  map Rev 1.9. Both froze at the very build that introduced `version.js` — the hand edits
  stopped, the conversion to interpolation missed this line, and each builder was left
  holding a frozen literal *directly above* a correctly interpolated one. FR Rev 1.16 and
  1.17 shipped with a title page reading Revision 1.15; epic map Rev 1.10 and 1.11 with
  Revision 1.9.
  Both guards had a hole. The revision check read table rows and the header, so it never
  saw a bare paragraph. The scan for literals in the builders used `Rev\s*1\.\d+`, which
  does not match `Revision 1.15` — after `Rev` comes `ision`, not a digit. The cover is
  now checked on its own in both documents, and the scan matches `Rev(ision)?`.
  **A guard that passes tells you what it tests, not that the document is right.** This
  one passed 1,548 checks over two shipped revisions of a submission document whose title
  page was wrong.
- **A regex spanning lines.** `[^`]*?"\)\);` ran past its intended match and swallowed
  several lines of code into a string literal. The document still built, 2KB lighter, with
  a section missing. Prefer whole-line replacement, and always `node --check` after
  patching a builder.
- **Writing a behaviour spec for an `Unchanged` feature.** SPEC-01 Rev 0.5 enumerated
  readiness conditions for eight features triaged as recreations. Every correction was the
  same shape: the list was short. It cost several rounds of review to find that out, and the
  right document was always a one-page brief. See the two shapes in section 5. **The status
  chooses the shape; check it before writing a line.**
- **A trace to an identifier that no longer exists.** Rev 0.5 traced to FR-CFG-006 and
  FR-CFG-007, both long since superseded to BL-35 or withdrawn. Coverage checking only asked
  whether owed requirements were cited, never whether a citation resolved, so it passed. A
  dead trace is worse than a missing one: it reads as coverage that is not there.
  `spec-check.py` now separates a trace, which must resolve, from a prose mention, which may
  legitimately discuss a retired identifier.
- **Em dashes are stored literally.** Match the actual `—` character, not `—`.
- **Assuming platform limits.** Detecting whether another app is installed works in
  Minuteful; platforms restrict *enumeration*, not declared per-app checks. Check before
  asserting a platform cannot do something.

---

## 9. Working with Guy

- **A change to one document means checking the paired document.** Requirements, epic map
  and board move together. Do not rebuild only the one you were asked about.
- **Do not change a requirement before he has reviewed it.** Propose, in a form he can
  comment on, then implement.
- **Keep it simple.** He has pushed back on cross-referencing requirements into each other
  and on trace notes that restate what the traceability already carries. One requirement,
  one idea.
- **Do not invent.** Where he has not decided, say so and ask. He would rather answer a
  question than unpick a guess.
- **Distinguish his words from yours.** In `spec-status.js`, `src: "pm"` is authoritative
  and `src: "derived"` needs confirming. Seven **Changed** features carry derived notes
  developers will read as scope: F04.5, F06.1, F06.6, F08.4, F12.2, F14.1. F01.9 was a seventh until Guy corrected it — see the tripwire in section 5, which now cuts both ways.
- He is concise and direct, and expects the same.

---

## 10. Open threads

| | |
|---|---|
| **WHERE WE ARE** | **Three of thirteen specs are ready: SPEC-01, SPEC-02, SPEC-03**, all recreation briefs with no behaviour statements between them. FR is at **Rev 1.23**, epic map **Rev 1.17**, 1,815 checks. Rev 1.23 was an independent verification pass run in the environment that has a PDF renderer: it corrected one Appendix I outcome, three appendix citations and four spec defects. Next: **SPEC-05**, drafted at Rev 0.7 and needing Guy's review — four `New` features and the only document carrying behaviour statements, which is where the New/Changed shape still has to be settled. That review is the unlock for the remaining New and Changed features; the recreation path is proven three times over. |
| **WHERE WE ARE, on the repository** | The document set now lives in `product/` of the shared **`qacr-spec`** repository, on branch **`poc/pm-working-directory`**. `npm run all` is green there: 1,815 guards plus 30 new layout checks. Nothing outside `product/` was touched. **This is a POC and is not merged** — the open items below are what merging waits on. See section 11. |
| **The team needs one line before their half runs** | `tools/parse_product_docs.py` fails on Rev 1.23 with *appendix title matches no known role: ['I — Conditions That Refuse a Test']*. `APPENDIX_ROLES` matches on title and fails loudly on an unknown one, by design — it is how a re-lettering announces itself instead of arriving as silence. Adding `"conditions that refuse a test"` runs the whole chain green, verified. Appendix I is the block / notify / configured-off register, so it is probably worth **emitting as data** rather than only recognising: it is the one place that distinction exists. **Theirs to fix, not ours.** |
| **Their `SPECS` table is three specs behind** | `tools/build_feature_files.py` cites SPEC-01 Rev1.2 and SPEC-02 Rev1.0, and has **no SPEC-03 entry at all** — so E03 has no feature files while FR-KIT-008, FR-KIT-009 and FR-KIT-010 are already in the corpus. Their `spec-intake` closes this. Do not do it for them. |
| **SPEC-02 was forked at one revision number, now Rev 1.1** | Their repository held Rev 1.0 and this one held different text, also Rev 1.0: the `unauthorized` refusal was rewritten in prose at the Rev 1.23 pass, correctly, because a value read out of the backend is not something a brief may carry. Fixed by bumping to **Rev 1.1**; their Rev 1.0 stays in `specs/` because their feature files were built against it. The guard is in `layout-check.py`. See the mistake in section 8. |
| **`product/FR-01/*.json` are at Rev 1.20 on the branch, deliberately** | Landing a document is ours; ingesting it is theirs. The mismatch against the Rev 1.23 `.docx` is exactly what their `diff_revisions.py` is for, and their manifest reads it correctly: **3 added, 0 removed, 2 text changed, 4 note changed, 0 milestone moves** — Rev 1.21 to 1.23 reconstructed from the documents alone. Do not regenerate them. |
| **The Board can no longer go stale invisibly** | It used to be exported by hand and its filename carries no revision, so it sat at Rev 1.13 beside a Rev 1.14 document with nothing to show it. It is now built by the same command, from the same `version.js`, in the same commit as the epic map. The filename is left alone on purpose — renaming it would break their `README.md`, and the problem it had is dissolved rather than guarded. |
| **Every rebuild dirties both `.docx`, with no change in them** | `docx` stamps `docProps/core.xml` with the build time, so a rebuild at unchanged data produces two modified binaries whose every other part is byte-identical — verified by unzipping and diffing. Harmless in a private working directory; in a shared repository it is noise in the team's history. **So do not rebuild to check something; `git checkout --` the two files if the data did not change.** Not fixed: the timestamp is provenance on a submission document, and making it deterministic is a change to the builder, not a tidy-up. Section 7's rule already covers the reading of it — a rebuild that produces no change in `generator/` has changed nothing of substance. |
| **`check_citations.py` does not pass here and is not ours** | It resolves `evidence/` citations against local clones of the four application repositories; without them it reports every row unresolved. `evidence/unresolved-citations.tsv` already holds 76 rows the vault's own prose could not resolve. **Not a finding, and not to be fixed from `product/`.** |
| **Appendix I is the block-type register** | Created at Rev 1.22 at Guy's direction. FR-RDY-011, FR-RDY-014 and FR-CFG-006 deliberately state the rule and not the cases, so the cases had nowhere to live — and **FR-RDY-014's note claimed SPEC-01 recorded the set, which SPEC-01 never did.** Appendix I now holds all three groups: refused by the backend when a test is requested, established on the device before a test starts, established at or after the scan. Every row carries the block / notify / configured-off distinction, which is the point of the table. **This is the answer to "the closed set of backend refusals" SPEC-01 had been waiting on** — eight rows, not the ten previously assumed. When a spec turns up a condition, add the row rather than enumerating it in the spec. |
| **Appendix E and F shipped with the wrong subsection letters** | Six subsections across two appendices of a submission document carried the *next* appendix's letter — E.1 to E.3 labelled F.1 to F.3, F.1 to F.3 labelled G.1 to G.3 — left behind when the appendices were re-lettered, and Appendix E carried a sentence pointing at Appendix E for its own deferred features. Both shipped through every revision because **the appendix guard asked whether a cited appendix exists, never whether a subsection sits under the appendix it names.** Fixed, and the guard is wired in — proven by running it against the Rev 1.21 artefact, where it finds exactly those six, before it was run against Rev 1.22. The pattern is narrowed to letters that are actually appendices, because the review register numbers its own groups R.1 to R.6 on purpose. |
| **SPEC-03's decisions, at Rev 1.21** | Three new requirements: **FR-KIT-008** at 3, a kit refusal the software cannot attribute states no specific reason — the job FR-ALG-012 does for an invalid test and FR-RDY-014 for a pre-test refusal; **FR-KIT-009** at 5, the user may present the identifier for reading where automatic reading fails; **FR-KIT-010** at 5, the backend may refuse a test inside a minimum interval. One amendment: **FR-KIT-007** presents a message appropriate to how the previous test ended, rather than one alert stating a new kit is required, and its note now states the window excludes its endpoint. **Declined: moving FR-KIT-005 to milestone 3.** Expiry is not required for the submission, so the two departures resting on it moved to 5 instead — the dependency inversion resolved by moving the departures, not the requirement. |
| **Splitting a requirement is often the answer to a milestone conflict** | FR-KIT-001 was proposed for amendment to add a manual read of the kit identifier. Guy's answer: the manual route is a requirement of its own at milestone 5, and the automatic reading stays at 3. **One requirement cannot hold two dates**, and folding new scope into an existing requirement silently moves the whole thing. Reach for a new identifier before an amendment when the milestones differ. |
| **The switch-user route is conditional, and Guy was right** | Checked against both clients at his request: the option is offered only where the backend reports more than one patient against the phone number or the address. Otherwise support is the only route. It is future development for QACR (FR-AUT-020, FR-AUT-011, FR-AUT-015, all milestone 5), so support is what applies. |
| **Q-103, Q-104, Q-105 new; Q-30 widened** | **Q-103** FR-KIT-001 requires the software to prevent the user completing a scan where the code is missing; nothing does and nothing can, since the code is read during the scan. Left as written at Guy's direction — the brief records the product and the register carries the question. **Q-104** the kit-identifier template, a value needing kit manufacturing. **Q-105** no requirement demands prevention where the backend reports no unused kit remaining; left with SPEC-01, which owns FR-RDY-014. **Q-30** was scoped to the section-12 timing windows and now records that the FR-KIT-007 window is defeated by the same alterable clock. |
| **§8.5 could not be run for Rev 1.21** | No PDF renderer is installed in this environment, so the cover pages were not read as images. The risk that step exists to catch is a narrow column wrapping badly, and nothing new entered one: the three added rows put a single digit in `Pri.` and `F03.1`/`F03.2` in `Feat.`, the same shapes already rendering. **Run it in the environment that has a renderer before this revision is circulated.** |
| **The developers' behaviour review is a better input than research** | For E03 the team produced 86 behaviour lines against the shipped product and Guy marked each `correct`, `change` or `wrong`. Fourteen `change` marks became ten departures; two `wrong` marks became the entire research phase. **Its requirement mapping was against a pre-Rev-1.18 document**, so it read BL-04, BL-21, BL-22, BL-23, BL-24, BL-35 and BL-42 as deferred and proposed requirements that already exist. Six of its ten proposals did. **Always re-map such an input against the current revision before believing a gap.** |
| **No pre-scan kit-expiry check exists** | Established at the SPEC-03 draft, because the review claimed one. Expiry is read from the kit identifier, which is unreadable until the scan, so it cannot be checked earlier. What *can* block before a test is a **configured** blocked state whose reason set includes an expired-kit value — FR-CFG-006, milestone 3, SPEC-01's. One client also carries a block reason the backend has no way to send. **A block that appears to be a kit check may be a configuration state**; the two have different owners and different documents. |
| **The pre-test refusal set is now known** | SPEC-01 has been waiting on the closed set of backend refusals. Reading the shipped system gives six named reasons plus a repeat-testing block that is computed rather than configured. Not yet applied to SPEC-01, which is `ready` — it needs Guy, and it is FR-RDY-014's business. |
| **configs.js cites withdrawn requirements as live — 3 places** | Found by a probe written for the SPEC-03 draft: the configuration register discusses FR-KIT-006 twice and FR-CFG-007 once as though they were live requirements. FR-KIT-006 was withdrawn into FR-KIT-004; FR-CFG-007 is still withdrawn and still awaiting reinstatement. **The register ships inside the FR document**, so this is the same class of defect as the unswept backlog prose. Raised, deliberately not fixed: correcting a register note is a document edit. **The guard is ready to wire in once the prose is fixed** — narrowed to `configs.js`, `review.js`, `epics.js` and `spta.js`, because `appendices.js` is the withdrawn register and citing retired identifiers is its job. |
| **`appendices.js` `renumber` is not an issued-identifier list** | Its left column holds identifiers from a *superseded* numbering scheme — old FR-KIT-002 became FR-KIT-001, and so on down the section. It is not exported to any builder and does not ship: FR-KIT-008 appears there but zero times in the built document. **`id-manifest.json` is the authority on what has been issued**, and it was right. This was misread once as a reuse trap, which would have left a permanent gap in every renumbered section for no reason. FR-KIT-008 was free and is now issued. |
| Decisions now in the log | **Q-101** FR-AUT-012 stays as written; the control is guarded by the product manager, not the software. **Q-102** phone verification is not needed in the clinical studies, which settles both milestone questions about consent and the invite-code path arriving at 4. Both recorded at Rev 1.20. |
| Q-63 sharpened, still open | The session-token expiry period cannot be settled from the application — no lifetime is held client-side, so the backend enforces it entirely. The register now says so. It needs the backend SRS or the backend team. |
| F02.5's intent text | The epic map says the token "expires after twenty-four hours" as fact, while Q-63 records that value as wrong for this application. Raised, not changed: it is prose in the epic map and the note beside it already carries the doubt. |
| Specs to write | 10 of 13 remain. **SPEC-01 ready at Rev 1.3, SPEC-02 ready at Rev 1.0, SPEC-03 ready at Rev 1.0** — all three recreation briefs, none carrying a behaviour statement. SPEC-05 is drafted at Rev 0.7, not reviewed, and is still where the New/Changed shape gets settled. The board renders each document's state. |
| F02.5 was mis-triaged, the second time | `Changed` pending "the token inventory", which turned out to be research rather than a change: the session holds three credentials, none persisted, none behaving differently for QACR — so FR-SEC-008's no-persisted-credential control is already met by the design. Corrected to `Unchanged` at the source. **The inventory itself is implementation detail and was deliberately kept out of the spec**, which is the altitude rule catching something the PM had asked for in good faith. |
| Q-63 has the wrong owner | The session-token expiry period cannot be settled from the application: no lifetime is held client-side at all, so the backend enforces it entirely. The question needs the backend SRS or the backend team. |
| **SPEC-01's open items, mostly answered now** | **FR-CFG-006 is in scope at milestone 3** — the configured blocked state, restored to its own identifier. The set of backend refusals it demanded a reason for is now **Appendix I**. Still awaiting Guy: requirements for any refusal no section owns, block-versus-notify on FR-RDY-011, built-in defaults for configured thresholds — which needs FR-CFG-002 narrowed as well as FR-RDY-008's note corrected, since as written it forbids the defaults he asked for — and reinstating FR-CFG-007, whose identifier is being held vacant for exactly that. |
| **SPEC-03's three open items, all answered** | **U1** the kit-identifier template is still undecided and he does not want it waited on, so it stays open in a `ready` document — a value, not a behaviour, and that is an acceptable thing for a ready brief to carry. **U2** an alterable clock is accepted for the 24-hour window between tests and no requirement is wanted; Q-30 stays open only for the timing windows inside a test, where RA 4.18 relies on the timers. **U3** the no-unused-kit block needs no requirement of its own — it is one of the reasons the backend refuses a test, which FR-RDY-014 covers, and it belongs on the list. Q-105 and Q-106 closed at Rev 1.22. |
| **§8.5 is unrunnable here and Appendix I is new layout** | No PDF renderer is installed in this environment, so the cover pages and the new appendix were not read as images. Appendix I is a four-column table that has never been rendered; its widest unbreakable token is a requirement identifier, which fits, but that is reasoning rather than verification. **Read Appendix I as an image in the environment that has a renderer before Rev 1.22 is circulated.** |
| SPEC-01's requirements landed at Rev 1.19 | One new — **FR-RDY-014**, a message specific to each reason the backend refuses a test, at milestone 3, owned by F01.5. Six amendments: FR-RDY-011 declares block or notify, FR-RDY-009 covers a camera that cannot be started, FR-RDY-004 routes to the store with configuration deciding mandatory or dismissible, FR-CFG-001 separates retrieval in progress from failed, FR-CFG-002 keeps the no-fallback rule about the set rather than each value in it, and FR-CFG-004 loses its labelling clause per Q-100. One milestone move: **FR-CFG-003 from 5 to 3**, which is both where it is needed and the earliest it can sit. Declined: mandating a default for every configured threshold, reinstating FR-CFG-007, and a notify-once requirement — that last one is unchanged from Minuteful, so no requirement. |
| Register hygiene, carried over | FR-RDY-008's note still says the storage threshold is "fixed in the application rather than configuration-supplied", which does not match how configuration works. Raised, deliberately not changed: correcting a note is a document edit and the requirement is unaffected. |
| **Resolved at Rev 1.18** | The Appendix F prose that discussed FR-CFG-003, FR-CFG-004, FR-CFG-006 and FR-CFG-007 as absent is no longer wrong for the first three: they are live requirements again. FR-CFG-007 is still withdrawn and still proposed for reinstatement by SPEC-01. Appendices are now A to I, contiguous, and a guard fails the build if the document cites one it does not contain. |
| **Pilot review** | Both pilots are at Rev 0.4: tuned against the current product for accuracy, then brought back to the product-requirement level per the altitude rule in section 5. They carry thirteen new open items between them that need his answers, not values. Read the Open items section of each before writing a third spec — several are patterns every spec will inherit, notably support escalation by attempt and whether the requirements or the current product govern where they disagree. |
| Recreation method | The requirements say what must be checked; they do not say what the user meets when a check fails. That gap is where four blocking conditions and one escalation rule came from in SPEC-01, all of them already in Minuteful. **Diff every spec against the Minuteful content set, not only against the requirements.** Cite copy keys, never wording. |
| **Copy is not evidence of behaviour** | The shipped copy set disagrees with the shipped application, repeatedly, and always in the direction of sounding right — on durations, on thresholds, and on whether a screen blocks or merely warns. Four claims in the pilots' Rev 0.2 were taken from copy and three were wrong. **Copy tells you a behaviour exists; only the application tells you what it does.** Use copy to find the condition, then confirm the behaviour. The specific disagreements are in `git log` at `51a99b1`, deliberately not repeated here: they are research, and research does not belong in a spec or in this file. |
| Research context, never spec content | `gh` is installed. `gh api "repos/OwnHealthIL/iosDip/contents/<path>?ref=<sha>" -H "Accept: application/vnd.github.raw"` reads a file; `gh api "search/code?q=<term>+repo:OwnHealthIL/iosDip"` locates one. Do not clone — 2.6 GB. Useful starting points: the lobby view model holds the readiness gate in check order, the pre-login coordinator holds the integrity block, the shared utils hold battery and disk, and the chat test coordinator drives the timing. **Read these to make a requirement accurate, then leave them behind.** See the altitude rule in section 5. |
| Platform parity, checked | Both clients are readable (`OwnHealthIL/iosDip`, `OwnHealthIL/AndroidDip`) and every "unchanged" claim in the pilots was confirmed on both. Timing, thresholds, check order, the integrity block, the configured block states and the storage threshold's source all agree. One deviation was found — a charging device below the battery threshold — and Guy has settled it: see below. |
| **Parity verification is QA's, at the end** | Guy's decision when the parity deviation surfaced: cross-platform parity is verified as a QA process activity at the end, not built into development. **Do not raise it as a spec item or a development obligation, and do not propose a verification activity for F01.7.** It was raised once and closed; the answer is that this is exactly the kind of thing not to overcomplicate. |
| FR-TIM-005 | Reads as though both countdowns are shown for an active stage, while SPEC-05 shows one at a time and has them change meaning at the transition. Narrowing the requirement is regulatory-visible. |
| FR-TIM-014 | Covers only the about-to-expire notification. The UX study's primary re-engagement mechanism — a notification at the end of the wait, to bring the user back to act — has no requirement, nor do the study's SMS fallback or its iOS Live Activity / Android floating timer. New scope, his call. |
| FR-RDY-007 | **Decided:** the check is the minimum battery level and nothing else — a device below it is blocked whether or not it is charging. FR-RDY-007 as written already says that, so no requirement change is needed. Still open: what happens when the level cannot be read at all, where today's products let the test proceed. SPEC-01 S01.26. |
| The stage is the unit of timing | QACR needs two timed stages, each with its own minimum duration and completion window, each independently tracked, and each start time retained across the application not running — at milestone 1. Today's product has one wait inside one overall limit on the test, so this is finer-grained than anything that exists. **Whether that is met by extending what exists or by building again is the development team's call, not the spec's.** SPEC-05 S05.38. |
| Safety margin on the reaction | Is one wanted, and is it inside the minimum duration? Today's product keeps a margin by displaying more time than it enforces, which QACR cannot do once FR-TIM-005 requires the remaining time to be shown. If a margin is wanted it belongs in the duration, where the timing-flex study sets it and verification tests it. SPEC-05 S05.37. |
| F05.6 | Absorbed into SPEC-05 as the sad flow, though the triage marked it Changed in its own right. He may want it separate. |
| Derived notes | The seven Changed features above need his confirmation. |
| FR-TXT-001 | Still claims *all* user-facing text meets grade 6, while the check is scoped to the instructional flow. Narrowing it is a regulatory-visible change and goes through his review. Bears on Q-22. |
| Content pipeline | Parked pending developer feedback. |
| Q-99 | Whether the real-time capture guidance is recorded audio, as the instructional flow is. |
| **Closed at Rev 1.18** | BL-34 became FR-CFG-004 at milestone 1 and BL-35 became FR-CFG-006 at milestone 3, both at Guy's direction. The doubts recorded against Q-31 and against the two deferral notes are settled: the mechanism exists in Minuteful and both are now in scope. |
| **Q-100 — new** | FR-CFG-004's final clause requires the software to label a demonstration result as not a patient result, which FR-RES-006 already requires. One requirement, one idea: the clause should probably come out, leaving FR-CFG-004 a backend rule. Proposed, not applied. |
| FR-SUP-004, formerly BL-40 | In-app support chat is milestone 5, and Minuteful already has it, while telephone and email — FR-SUP-002 at milestone 3, assumed ready — are the part needing a spec. Both clients integrate Freshchat and GetStream. |
| F08.2 | How Minuteful handles algorithm version status. His to check. |
| F02.5 | The token inventory. His to provide. |
| **Milestone 5, new at Rev 1.18** | The backlog was dissolved into milestone 5. Two consequences worth watching: the epic map's fourth feature field is now always empty and should be removed as its own change, and `generator/build-conflicts.py` and `spec-triage.py` still contain BL identifiers from the era they were written in. Both are frozen one-off builders, so their references are historical rather than stale, but nothing guards that distinction. |
| Register wording | The consequence-of-deferral entries in `review.js` still read as consequences of deferring, which is still true — a milestone-5 requirement is not built for this submission — but the word "deferred" now means something the document no longer has. Worth a pass. |
| **Four table columns are too narrow for an identifier** | `FR-CAM-002` renders as `FR- / CAM-002` in the R.1 register, in Appendix D.1 and D.3, and in Appendix E.2 — and in D.1 the header itself breaks as `Requirem / ent`. Guy's call at Rev 1.23 was to leave them. It is cosmetic until a reviewer searches the PDF for a withdrawn identifier and does not find it, which is exactly what Appendix D is for. `generator/column-width-probe.py` finds all four and is **not** wired into `npm run check`; run it by hand against a built `.docx`. The body tables hold a ten-character identifier in 1150 twips; these four render at 932 to 1014. |
| **A citation can resolve and still be wrong** | Three requirements cited an appendix that exists but is not the one meant — `FR-LCM-018` pointed at Appendix H (the Priority Summary) meaning the Configuration Register, and `FR-RES-002` and `FR-SHR-011` pointed at Appendix E meaning the dissolved backlog appendix. All three passed every guard for five revisions, because the appendix guard asks whether a cited appendix *exists*. Fixed at Rev 1.23 by citing registers **by name**. Only two letter citations remain in the data, Appendix I and Appendix A, and both are correct. Prefer a name over a letter in any new requirement text. |
| **Appendix I is verified against the shipped configuration** | Every outcome was checked against `minuteful_kidney_us` rather than the copy set. `enabledQrBlock` is switched off in eight partner overrides and set explicitly true in another, which is why the already-used-kit row now says *where the check is switched on for the partner*. `blockSubsequentTests.timeLimit.enabled` is false everywhere, consistent with FR-KIT-010 being future development. Scheduled downtime has no row of its own by decision — it reaches the user as the configured blocked state, which now names it. Nothing was found missing: `minAge`/`maxAge`, `customBlockByFlow`, `blockFlow`, `blockMultipleExamsOnOrder`, `allowIpadForReview` and the maximum-OS keys are absent from every file in this product's configuration set. |
| **No fuller block list exists anywhere** | Searched independently at Rev 1.23 across both SRSs, both Risk Analysis drafts, the threat analysis, the development plan, the Minuteful description and the lobby spec. There is no enumerated set of refusal reasons in any of them; the closest remains `blockFlow`'s three configured values. **Appendix I is the first such list, not a restatement of one.** Two agreements worth keeping: the backend SRS validates expiry on *the scanned kit*, which independently confirms that no pre-scan expiry check exists, and the application SRS says the software shall prevent the user initiating a scan on a bad QR — the same impossibility Q-103 records. |
| **SPEC-01 now points at Appendix I** | Added at Rev 1.23. SPEC-01 owns the blocked-state pattern and traces the three requirements Appendix I exists to serve, and was the only brief that never mentioned it. The pointer strengthens the no-enumeration design rather than weakening it: the list exists, and it lives under document control rather than in a brief. **A list in a spec is still forbidden** — that rule is section 5 and it did not change. If it ever should, section 5 changes with it. |
| **SPEC-05's header is two revisions behind its content** | It reads *current to FR Rev 1.20* while tracing Rev 1.23. Nothing in Rev 1.21 or 1.22 was found to make one of its statements false — FR-KIT-007's text changed and SPEC-05 only traces it for the new-kit obligation — but the header is a claim and it has not been re-established. Settle it as part of the Rev 0.7 review. |
| **F05.2 was mis-triaged and the tripwire caught it** | It was `Unchanged` while its own product-manager note reads *"the timing and test steps are changed"*, and SPEC-05 section 3.7 carries behaviour statements for it. Corrected to `Changed` at Rev 1.23. Tallies are now **18 Changed, 40 Unchanged**. The lesson is the one already in section 5: when an `Unchanged` feature starts wanting behaviour statements, the status is wrong, not the statements. |

---

## 11. The shared repository — `qacr-spec`

This document set lives inside `qacr-spec`, which the development team also works in. That
is deliberate: the requirements and the code that implements them share one history, and a
developer starting a task can see what to build and what already exists without asking.

`product/` is **yours**. Everything beside it is **theirs**. That boundary is the whole
design and it is not a courtesy.

### The four layers

| | |
|---|---|
| `product/` | this document set. Read-only to them. To change a requirement, change the data and rebuild |
| `features/` | one generated file per specified feature: the spec's disposition, the requirements it owns, the evidence rows, and the requirements the spec is **silent** on |
| `evidence/` | what the code does **today**, one cited claim per row, `file:line`, against the commits pinned in `evidence/pins.yaml` |
| `decisions/` | `D-nn` — questions **they** raise against a spec, for you to answer |
| `tools/` | their parser, revision differ, citation checker and feature-file builder |

### What you never do

These are hard stops, in the same spirit as the ones in section 8.

1. **Do not edit anything outside `product/`.** Not `features/`, not `evidence/`, not
   `tools/`, not the root `README.md` or `SDLC.md`. If something out there is wrong, say so
   and let them fix it. A PM commit in `tools/` is indistinguishable from a developer's and
   nobody knows which half of the pipeline to trust afterwards.
2. **Do not restructure their directories.** The layout is load-bearing for their tooling:
   `tools/parse_product_docs.py` finds each document by looking for exactly one
   `QACR-APP-FR-01*.docx` in `product/FR-01/` and one `QACR-APP-EPIC-01*.docx` in
   `product/EPIC-01/`, and it *refuses to run* on a directory holding two.
3. **Do not run their skills.** `revision-intake` and `spec-intake` are theirs. Landing a
   document is your half; ingesting it is theirs, and their skill deliberately commits to a
   branch and stops without opening a pull request, because a revision is reviewed
   separately. Running it for them removes their review.
4. **Do not copy a `Q-nn` into `decisions/`.** Your review register is yours and is parsed
   out of the document every revision. A `D-nn` is a question they raised against a spec and
   moves under them. Merging the two id spaces loses which is which, and with it who is
   waiting on whom. `decisions/README.md` says this at length and it is right.
5. **Nothing under `local/` is ever committed.** It is in `product/.gitignore`, and the
   repository is public.

### `local/` — on your disk, not in git

Not tracked is not the same as not present. These sit right here in the working directory
and `/mind`, the specs and you all reach for them exactly as before; they are simply not
pushed:

`local/Source documents/` — the Risk Analysis, both SRSs, the SPTA, the product glossary,
the development plan, the Minuteful Kidney description, the UX studies.
`local/Reference/` — the Minuteful copy set and screenshots.
`local/` also holds the content project and the superseded spreadsheets.
`Previous revisions/` is likewise untracked: git history is the archive that ships.

### Their parse is a second, independent derivation — treat it as one

`tools/parse_product_docs.py` reads the built `.docx` and writes `product/FR-01/*.json` and
`product/EPIC-01/*.json`. **It never reads the data modules.** So where it agrees with
`generator/`, the document has been confirmed by something that did not build it — which is
the independent reader section 8 keeps asking for, and it is stronger than any guard in here
because it validates the document against *the document's own arithmetic*:

| | |
|---|---|
| Appendix H, Priority Summary | a 22-area by 6-milestone matrix, 132 cells, with a total per row and per column. It pins every requirement's milestone **by functional area**, so two errors in opposite directions cannot net out |
| Review Register front matter | open items per group, and their total |
| Appendix D.1–D.3 headings | each states its own row count |
| section 2 | "this revision contains N requirements across M functional areas" |
| per-epic headers, roadmap cells | requirements per epic, and per feature per milestone |

Those `.json` files are **theirs to regenerate**, not yours to produce. Leave them at
whatever revision they are at; the mismatch against a newly landed document is exactly what
their `diff_revisions.py` reports, and it is how they know a revision arrived.

### Spec naming, and the one rule that is new

`specs/QACR-APP-SPEC-nn Rev<major>.<minor>.md`. The revision is in the **filename** as well
as the header row, and `layout-check.py` fails the build if they disagree — the filename is
the only revision a reader of the directory sees.

> **A published revision is immutable.** Once it is committed, somebody has built against
> it. A change needs a **new number**, not new text under the old one.

Superseded revisions stay in the directory, because their rule is to keep every revision
built against and their `build_feature_files.py` cites a specific one. The **highest
revision is the live one**, and `spec-check.py` checks only that one — a superseded brief
cites the FR revision that was current when it was written, so checking it would fail it for
being exactly what it is.

Consequence for section 5: promoting a spec to ready is now also a **rename**. Bump the
number in the header row and the filename together, in one commit.

### `layout-check.py` — the seam guard

Runs first in `npm run check`, six checks:

1. exactly one `QACR-APP-FR-01*.docx` under `FR-01/`, at the revision `version.js` declares
2. the same for the epic map under `EPIC-01/`
3. no deliverable stranded at the `product/` root
4. every spec filename's revision equals the `Revision` row inside the file
5. one live revision per spec, and it is the highest
6. no already-committed spec revision has been edited in place — the one check that asks git,
   because git is the only thing that knows

Checks 4 and 5 catch a filename and a body that disagree. Only 6 catches the defect that
prompted all of this, and even 6 cannot catch a body edited *together with* its filename
left alone at a number nobody else has seen yet. **Bumping the revision is still a judgement
you make**; the guards only stop it being silently wrong afterwards.

### What comes back to you, and where to read it

Three things the shared repository tells you that this document set has no way to know:

| | |
|---|---|
| the **`silent`** list, in every feature file | a requirement a covered feature owns that its spec says nothing about. Nobody can build it — not because it is hard but because nobody has said what it should do. **Silence is not a decision and must never be read as as-is** |
| `decisions/D-nn` | a question they raised and cannot close. Answer it **verbatim** into the register or the requirement, not by picking the more likely reading |
| `evidence/context.tsv` | eleven `CTX-nn` rows: what a developer knows that no requirement states. CTX-03 records that result generation and fetching **do not exist**, on mobile or backend. CTX-04 that QACR's timing is a different shape, not ACR's with different numbers. CTX-02 that the QACR application was built for a usability study, not to ship. Read these before SPEC-05's review |

`evidence/behaviour.tsv` is also the honest answer to the recreation problem section 5
describes: it is what the code does today, cited, rather than what the copy set implies. Use
it the way section 8 says to use the copy set — to find the condition, then confirm the
behaviour. And read `evidence/coverage.tsv` before concluding anything from a missing row:
`no-evidence-found` means **nobody extracted evidence**, never *the code does nothing*.

### The altitude rule still applies, and this is where it is tested

`evidence/` is full of `file:line` citations, class names and implementation detail. It is
there for the development team. **None of it travels into a spec or a requirement.** Section
5's rule does not relax because the evidence now sits in the same repository — if anything
the temptation is larger, because it is one directory away instead of behind a `gh api` call.
Convert what you learn into product behaviour and leave the internals where they are.

---
