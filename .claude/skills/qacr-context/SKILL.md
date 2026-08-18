---
name: qacr-context
description: Gather everything this repository records about one QACR feature — the brief's disposition for each requirement it owns, the departures and open items behind those dispositions, ACR's behaviour where the feature recreates it, and the architectural guidelines for its domains — and emit it as one contract a spec writer can work from. Use when a QACR spec or feature is named, when /spec is run on a QACR-APP-SPEC id, or when asked what a QACR feature needs before it can be specified. Produces context, never a specification.
---

# Everything known about one QACR feature, in one object

**The output is context. It is not a specification, and it does not say how to build anything.**

A spec writer arriving at a QACR feature needs four things this repository holds and one it does
not: what the PM decided for each requirement, what those decisions rest on, what ACR does where the
feature recreates it, and which architectural rules apply. This skill assembles them and stops.

`spec-skill` consumes what it emits. Nothing here writes a spec, slices a task, or opens the QACR
application — those come after.

## What this skill is, and is not

It does **not**: decide a disposition, fill in a requirement the brief is silent on, resolve an open
value, judge whether the PM is right, or read `evidence/`. Producing a confident answer to any of
those is the way this fails, because the consumer is an agent that will specify whatever it is
handed.

**Its one refusal is the important part.** A requirement the brief does not classify does not get a
classification here. It gets recorded as a stop, and the spec is written without it.

---

## Inputs — the only files read

| | |
|---|---|
| `features/<epic>/<feature>.md` | the feature file — requirements owned, disposition each, milestones, domains |
| `product/specs/QACR-APP-SPEC-nn Rev x.y.md` | the brief — departure text, open items, confirmed-as-is answers |
| `product/EPIC-01/features.json` | which features a brief covers, and what each owns |
| `product/FR-01/requirements.json` | requirement text, milestone, and the `note` field |
| `architecture/<domain>.md` | the guidelines, where they exist |

**Not `evidence/`.** `behaviour.tsv` is the analysis phase's secondhand index, mined from vault
prose. ACR behaviour comes fresh from source through `acr-behaviour-reference`. Do not read it, and
do not fall back to it when a lookup is thin.

**Not the QACR application.** Reading what the new app does today is `spec-skill`'s job, after this.

---

## Step 0 — Find this repository

`spec-skill` runs in the application repository, not here. Locate `qacr-spec` as a sibling of the
current repository's parent. If it is not there, **ask once** and use the answer — do not search the
filesystem, and do not proceed without it.

## Step 1 — Resolve the target feature

The caller gives a spec id (`QACR-APP-SPEC-01 Rev1.2`) or a feature id (`F01.4`).

**A feature is the unit of work.** A brief covers eight of them; a spec written across all eight is
not a spec anyone can build or review. So given a spec id, read its *Features covered* row, present
them as a numbered list with titles, and **wait for a choice**. Do not pick one, even if only one is
covered.

> QACR-APP-SPEC-01 Rev 1.2 covers eight features:
>   1. F01.1 — Store distribution and install-time compatibility
>   2. F01.2 — Supported-device policy and run-time eligibility
>   ...
> Which one are you specifying?

Given a feature id, resolve its brief from the feature file's header link and go straight on.

## Step 2 — Read the record

From the **feature file**: title, epic, milestones, domains, the requirements owned in their own
order, and the disposition against each. This file is generated and deterministic — it is the
record, not a summary of one.

From the **brief**: for each departure the feature carries, the row from the departures table
verbatim — its reference, what changes, and the requirement driving it. The feature file names
`departure D1`; only the brief says what D1 *is*. Also take the open items and the
confirmed-as-is answers.

From **`requirements.json`**: each requirement's text, milestone, and `note`.

### The note pass — every requirement, every run

A `note` records a configuration reality the requirement text does not, and the two can disagree — a
requirement refusing an unregistered phone number while its note says registration is enabled. These
are the highest-value findings this skill produces and they are **enumerated, never noticed.**

**Walk every requirement the feature owns, in order, and record one verdict for each.** Not the ones
that look interesting. All of them, including the ones with an empty note, which get `no-note`. A
requirement absent from this list is a defect in the run, not a requirement without a note.

| Verdict | When |
|---|---|
| `no-note` | the note field is empty |
| `agrees` | the note elaborates the text and they are consistent |
| `silent` | the note addresses something the text does not speak to — no conflict |
| `contradicts` | text and note cannot both hold. A Product question. Record both verbatim, add a stop |
| `possible-undeclared-departure` | the note prescribes a change the brief does not carry as a departure. A flag, resolved by step 4 |

**Never resolve a `contradicts` by preferring one side.** Both go to Product, verbatim.

`possible-undeclared-departure` is the subtle one and it is why the pass is exhaustive. The brief
states that everything outside its departures table is recreated as-is. A note saying a value was
"unlinked from configuration at review" prescribes a change the brief never declared — which is
either a departure missing its D-row, or a note describing what the current product already does.
Step 4 settles which. Neither the text nor the note contradicts the other, so nothing here trips a
`contradicts`, and a run that scans for conflicts rather than enumerating will pass straight over it.

The verdicts travel in the contract as `note_pass`, one row per requirement.

**Never paraphrase a requirement.** Text is copied verbatim with its id, or referenced by id alone.
A restated requirement is a second requirement, and the two drift.

## Step 3 — Partition, by reading the label

The disposition is already recorded. This step is a lookup and a set difference — **not an
inference.** If a requirement's classification is unclear, that is a stop, not a judgement call.

**A disposition comes from one place: the per-requirement column of the feature file.** It holds
`as-is`, `departure D-n`, or nothing. It never holds `open` — the brief's open items (`U-n`) sit at
**feature** level, and a feature-level question is not a per-requirement classification.

| Disposition | What it means | Result |
|---|---|---|
| `as-is` | the current product is the specification | `recreate` — ACR behaviour needed |
| `departure D-n` | QACR differs, and the brief says how | `recreate-with-departure` — ACR behaviour needed, plus the D-row |
| `silent` | the feature owns it; the brief never mentions it | **stop** |
| unclassifiable | including a capability ACR never had, which has no label yet | **stop** |

**On open items.** An open item withholds a *value*, not a behaviour, so it is carried as context and
**never stops a requirement on its own.** Stopping one would delete a check from a feature whose
subject is that check, and would block a departure the PM wrote prescriptively for it.

Build the mechanism, withhold the value, and **never choose one.** The spec states the criterion in
terms of the threshold rather than a number, and names the open item it waits on.

Where an open item names a value a requirement turns on, record the link. **Every such link carries
three required keys** — the contract is invalid without them:

| | |
|---|---|
| `blocks` | the requirement ids |
| `blocks_inferred` | `true` unless the brief itself attaches the item to those ids. It does not today, so this is `true` |
| `blocks_what` | what is actually withheld — values, verification — in the brief's own words |

The brief lists its questions without attaching them to requirement ids, so that join is a reading,
not a record. A link without `blocks_inferred` reads as something the brief stated.

**This flips the moment the PM labels a requirement `open`.** If the per-requirement column ever
carries it, an `open` requirement stops, and the question of what a developer does with it comes
back. He has not answered it yet.

**On `silent`.** Silence is not a decision and must never be read as `as-is`. Today the set is
empty — every requirement of every covered feature appears in SPEC-01 — so a silent requirement
means something slipped, and it goes back to the PM. Write it to `decisions/`, one file per
question, and record the stop.

**On the unclassifiable.** A requirement QACR needs that ACR never had has no disposition in the
brief's vocabulary yet. When one appears, stop. Do not read it as a departure, and do not invent a
label.

A stop removes that requirement from the spec. It does not stop the feature — the rest is specified
without it, and the stops travel in the contract so the spec can say what it left out and why.

## Step 4 — ACR behaviour, when the feature recreates anything

**If any requirement resolved to `recreate` or `recreate-with-departure`, call
`acr-behaviour-reference` once for the feature.** Once — not per requirement. It takes a feature
named in plain words; give it the feature's title and boundary, and pass the requirement ids as
scope.

If every requirement stopped, or the feature is entirely new capability, **do not call it.** There is
no prior art to read, and running it produces a document about a feature ACR does not have.

Nest its contract inside this one rather than flattening it. Its rules for the consumer — derive
don't copy, never specify a `not_derivable`, never carry over a `do_not_copy` — must survive intact.

## Step 5 — Architectural guidelines, by domain

The feature file names its domains. For each, read `architecture/<domain>.md`.

**Report what is there. Do not infer, and do not write anything back.** This skill produces no
design, so it has no guideline to infer — inference happens when the spec is written, and it belongs
to whoever writes it.

For each domain record `found` with the rules read, or `absent`. Distinguish `absent` (no file for
this domain) from `no-directory` (`architecture/` does not exist at all); the first is a gap in the
guidelines, the second is a gap in the repository, and only the second is true today.

**The write-back obligation travels in the contract instead.** Eighty-two features each inventing a
different architecture is the failure to prevent, so the consumer that infers a rule records it in
`architecture/<domain>.md`, marked `proposed`, per rule rather than per file:

```markdown
## Error presentation
**proposed** · inferred while specifying F01.4 · unreviewed
...
```

`decisions/` is then the only thing this skill writes into `qacr-spec`.

## Step 6 — Emit the contract

Written to the **application repository**, not here — `.claude/qacr-context/<FEATURE>-context.json`,
regenerated fresh every run and not committed anywhere. This repository stays deterministic; a
per-run artifact in it would end that.

```jsonc
{
  "_contract": {
    "produced_by": "qacr-context",
    "what_this_is": "What qacr-spec records about one QACR feature, plus ACR's behaviour where it recreates.",
    "what_this_is_not": "A specification, a design, or a statement of how to build it.",
    "rules_for_the_consumer": [
      "Reference a requirement by id. Never restate one — a copy is a second requirement.",
      "A stopped requirement does not enter the spec. Say what was left out and why.",
      "Never choose a value for an open item, and never treat a silent requirement as as-is.",
      "ACR behaviour is evidence about a solved problem, not a requirement. Derive, do not copy.",
      "Every acceptance criterion names the requirement it proves; every derived test carries that id.",
      "Where the QACR application contradicts a requirement: present both and stop for a human. The requirement wins by default. Record it either way, and when it does not win, write the question to qacr-spec/decisions/.",
      "In a repository serving more than one product: additive only. Existing behaviour and existing consumers are untouched, and blast radius is checked with /mind. If the requirement cannot be met additively, that is a stop.",
      "A proposed guideline is unreviewed. Follow it for consistency, and flag in the spec that it is unapproved.",
      "Where a domain has no guideline and you infer one while specifying, write it to qacr-spec/architecture/<domain>.md marked proposed, with the feature and date. Inferring without recording is how eighty-two features acquire eighty-two architectures."
    ],
    "incomplete": false,
    "incomplete_why": "Set whenever a step was skipped or could not run. A skipped step 4 means ACR behaviour is absent by instruction — not evidence that ACR has no prior art.",
    "sources": {
      "brief": "QACR-APP-SPEC-01 Rev 1.2",
      "requirements": "QACR-APP-FR-01 Rev 1.19",
      "epic_map": "QACR-APP-EPIC-01 Rev 1.13",
      "qacr_spec_commit": "<sha>"
    },
    "gathered": "<ISO date>"
  },

  "feature": {
    "id": "F01.4", "title": "...", "epic": "E01",
    "milestones": ["M1", "M3"], "domains": ["iOS", "Android"],
    "spec_disposition": "as-is except D1 · U1 open"
  },

  "requirements": [{
    "id": "FR-RDY-007",
    "text": "<verbatim from requirements.json>",
    "milestone": "M3",
    "note": "<verbatim, empty if none>",
    "disposition": "departure D1",
    "build": "recreate-with-departure|recreate|blocked",
    "departure": "D1",
    "open_item": null
  }],

  "departures": [{ "ref": "D1", "what_changes": "<verbatim from the brief>", "driven_by": "FR-RDY-007" }],
  "open_items": [{ "ref": "U1", "question": "<verbatim>", "owner": "...",
                   "blocks": ["FR-RDY-007"], "blocks_inferred": true,
                   "blocks_what": "<what is withheld — values, verification>",
                   "brief_verbatim": "<the brief's own words on what waits on it>" }],
  "confirmed_as_is": [{ "question": "<verbatim>", "answer": "<verbatim>" }],

  "stops": [{
    "requirement": "FR-XXX-nnn",
    "kind": "silent|unclassifiable|note-contradiction",
    "why": "...",
    "action": "raised in decisions/<file>.md | awaiting the PM"
  }],

  "note_pass": [{ "requirement": "FR-XXX-nnn",
                  "verdict": "no-note|agrees|silent|contradicts|possible-undeclared-departure",
                  "note": "<verbatim, empty if none>", "why": "" }],

  "flags": [{
    "ref": "note/FR-RDY-008",
    "kind": "note-vs-brief|requirement-vs-requirement|needs-acr-behaviour|skill-behaviour",
    "requirements": ["FR-XXX-nnn"],
    "what": "...",
    "resolves_with": "step 4|the PM|the skill author"
  }],

  "acr_behaviour": {
    "called": true,
    "why": "3 of 6 requirements recreate",
    "contract": { }
  },

  "guidelines": [{ "domain": "iOS", "path": "architecture/ios.md",
                   "state": "found|absent", "proposed_written": [] }],

  "not_covered_by_brief": [],

  "excluded_deliberately": { "<what was not carried>": "<why>" }
}
```

**`stops` and `flags` are not the same thing.** A stop removes a requirement from the spec. A flag
leaves it in and names something a human or a later step must resolve. Collapsing them loses the
distinction between "cannot be specified" and "specify it, but look at this."

**A flag's `ref` is derived from its content, never from the order it was found.** `F1` meaning one
thing in one run and something else in the next makes "look at F2" a dangerous sentence. Build it
from what the flag is about:

| Kind | `ref` |
|---|---|
| `note-vs-brief` | `note/<requirement>` |
| `requirement-vs-requirement` | `xref/<requirement>+<requirement>`, ids ascending |
| `needs-acr-behaviour` | `acr/<feature>` |
| `skill-behaviour` | `skill/step-<n>` |

Two runs that find the same thing then give it the same name, which is what makes flags comparable
across runs at all.

**`kind` and `resolves_with` are closed sets, not descriptions.** Write exactly one of the listed
values; the elaboration goes in `what`. A prose `kind` cannot be counted, filtered or checked, which
is most of why the field exists.

**`excluded_deliberately` records what was deliberately not carried**, so a reader can tell an
omission from an oversight. The feature file embeds the vault's evidence rows; they are excluded on
every run, and saying so is cheaper than the reader wondering.

`confirmed_as_is` is carried because the brief records those answers precisely so the next reader
does not ask them again. Dropping them here reintroduces the questions one layer down.

## Step 7 — Verify before handing over

- every requirement the feature file lists appears exactly once, either with a `build` or in `stops`
- no disposition was assigned that the feature file does not state
- no requirement text was paraphrased
- `acr_behaviour.called` is true if and only if at least one requirement recreates
- every departure referenced by a requirement has its row, verbatim
- every open item names what it blocks
- every silent requirement has a file in `decisions/`
- `_contract.incomplete` is true whenever any step was skipped, with the reason recorded
- every open-item link carries `blocks`, `blocks_inferred` and `blocks_what` — a link missing any
  of the three is an invalid contract, not a stylistic lapse
- every `flags[].kind` and `resolves_with` is exactly one of the listed values
- every flag names what resolves it
- `note_pass` holds exactly one row per requirement the feature owns — none skipped
- every flag's `ref` matches its content, per the derivation table
- nothing was written into `qacr-spec` except `decisions/`
- the contract was written to the application repository, not here

## Do not

1. **Do not read `evidence/`.** It is the analysis phase's index. ACR behaviour comes from source.
2. **Do not open the QACR application.** That is `spec-skill`'s next step, and its rules differ.
3. **Do not infer a disposition**, including by reading an unclassified requirement as `as-is`
   because everything around it is.
4. **Do not resolve an open value**, even when one reading is obviously more likely. A question
   answered by picking the likely reading is buried, not answered, and it resurfaces during
   verification where it is expensive.
5. **Do not write a feature file.** `spec-intake` owns `features/`.
6. **Do not edit `product/`.** It is read-only. A requirement changes by the document changing.

## Anti-patterns

- **Returning context for all eight features of a brief.** The unit is one feature.
- **Auto-picking a feature** because only one looked relevant. Ask.
- **Flattening the ACR contract**, which drops its consumer rules and lets its evidence read as
  requirement.
- **Calling `acr-behaviour-reference` per requirement.** Once per feature.
- **Calling it for a feature with no recreation.** It has nothing to read.
- **Stopping a requirement because the brief carries an open item.** The item withholds a value;
  the behaviour is still specifiable. Only the per-requirement column stops anything.
- **Recording an inferred open-item link as though the brief stated it.** Mark it inferred.
- **Silently dropping a stopped requirement.** The spec must be able to say what it left out.
- **Inferring a guideline here.** This skill reports what exists; the spec writer infers, and the
  contract tells it to record what it inferred.
- **Scanning the notes instead of enumerating them.** A note pass that looks for conflicts misses
  the undeclared departure, which is the finding worth most.
- **Numbering flags by discovery order.** The ref is derived from content or it is not stable.
- **Resolving a note-vs-text contradiction.** Both go to Product, verbatim.
- **Committing a run's contract.** It is transient and belongs in the application repository.

## Refinement log

Append what each run corrected, so the next feature is cheaper.

- **Written 2026-08-18, not yet run.** Decisions taken while writing, worth revisiting after the
  first use: (i) **the caller may pass a spec id, but the unit is a feature** — a brief covers eight,
  so a spec id lists and asks rather than returning all of them; (ii) ~~**`open` stops** rather than
  building the mechanism with the value deferred~~ — **superseded by the first-run entry below.
  Open items never stop a requirement.** Left here as history, not as guidance; (iii) **the `note` field is carried and checked against the requirement text**,
  after `feature-definition` found notes that contradict what the requirement says; (iv) ~~**inferred
  guidelines are written back as `proposed`**~~ — **superseded by the second-run entry below. This
  skill produces no design and so infers nothing; the obligation moved to the consumer.**
- **First run — F01.1 and F01.4, 2026-08-18, step 4 skipped.** Both produced valid contracts and
  every mechanical assertion passed. Four corrections came out of it, in order of weight:
  (i) **The `open` stop was a rule for a value the input never produces.** A disposition comes from
  the feature file's per-requirement column, which holds `as-is`, `departure D-n`, or nothing —
  `open` sits at feature level in the brief. So the rule could not fire, the case that actually
  occurs was uncovered, and the run had to reason its way to an answer. It reached the right one
  (build the mechanism, withhold the value) but a rule an agent can reason past is not a rule. Step 3
  now says where a disposition comes from, and open items never stop a requirement by themselves.
  (ii) **`_contract.incomplete` was missing** — a skipped step 4 leaves ACR behaviour absent, and a
  downstream reader would take that for "ACR has no prior art" and invent behaviour. Adopted from the
  run, which invented it unprompted. (iii) **`stops` alone was too coarse.** The run needed to say
  "specify this, but look at it" and had nowhere to put it, so `flags` is now first-class — a stop
  removes a requirement, a flag does not. (iv) **`excluded_deliberately`** records what was refused,
  so an omission reads differently from an oversight. Also: an open-item-to-requirement link is now
  marked `blocks_inferred`, because the brief lists its questions without attaching them to ids.
  `confirmed_as_is` earned its place on the first run — two of F01.4's five answers bear directly on
  the feature — so that open question is closed. Open: the feature file embeds 26 vault evidence
  rows that this skill refuses on every run; removing that section from `build_feature_files.py`
  would delete the temptation rather than police it. And consistency is still unmeasured — one run
  per feature, no repeat.
- **Second run — F01.4 twice from cleared sessions, 2026-08-18, step 4 skipped.** The schema fixes
  held: every structural check passed. Two findings, and the second is the important one.
  (i) **Step 5 told this skill to infer a guideline and write it back, which it cannot do.** It
  produces no design, so it has nothing to infer — inference happens when the spec is written. The
  run flagged the instruction rather than following it. Step 5 now reports `found` / `absent` /
  `no-directory` and the write-back obligation travels as a consumer rule, leaving `decisions/` as
  the only thing written here.
  (ii) **Flag discovery was unstable, and that was a real defect.** Run A found five flags, run B
  found two; across five runs the storage-threshold undeclared-departure surfaced in four. An 80%
  catch rate on undeclared departures is not a process, and the cause was structural — flags were
  open-ended noticing with nothing enumerated. Notes are an enumerable set, so the note pass is now
  exhaustive: one verdict per requirement, every run, `no-note` included. This is the same move
  `acr-behaviour-reference` makes with the alert catalogue, and for the same reason.
  `possible-undeclared-departure` exists as its own verdict because that finding trips no
  contradiction — text and note agree — and a run scanning for conflicts passes straight over it.
  Also: flag `ref` is now derived from content, because `F2` naming different findings in different
  runs makes "look at F2" a dangerous sentence. Open: whether the open-ended flag kinds
  (`requirement-vs-requirement`) can be enumerated too, or whether they stay discovery.
