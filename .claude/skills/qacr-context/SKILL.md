---
name: qacr-context
description: Gather everything this repository records about one QACR feature — the brief's disposition for each requirement it owns, the departures and open items behind those dispositions, the answers already recorded in the decision log, ACR's behaviour where the feature recreates it, and the architectural guidelines for its domains — and emit it as one contract a spec writer can work from. Use when a QACR spec or feature is named, when /spec is run on a QACR-APP-SPEC id, or when asked what a QACR feature needs before it can be specified. Produces context, never a specification.
---

# Everything known about one QACR feature, in one object

**The output is context. It is not a specification, and it does not say how to build anything.**

A spec writer arriving at a QACR feature needs five things this repository holds and one it does
not: what the PM decided for each requirement, what those decisions rest on, which of its questions
were already asked and answered, what ACR does where the feature recreates it, and which
architectural rules apply. This skill assembles them and stops.

`spec-skill` consumes what it emits. Nothing here writes a spec, slices a task, or opens the QACR
application — those come after.

## What this skill is, and is not

It does **not**: decide a disposition, fill in a requirement the brief is silent on, resolve an open
value, answer a question the decision log has not, judge whether the PM is right, or read
`evidence/`. Producing a confident answer to any of those is the way this fails, because the
consumer is an agent that will specify whatever it is handed.

**Its one refusal is the important part.** A requirement the brief does not classify does not get a
classification here. It gets recorded as a stop, and the spec is written without it.

---

## Inputs — the only files read

| | |
|---|---|
| `features/<epic>/<feature>.md` | the feature file — read whole, section by section; see step 2 |
| `product/specs/QACR-APP-SPEC-nn Rev x.y.md` | the brief — departure text, open items, confirmed-as-is answers |
| `product/EPIC-01/features.json` | which features a brief covers, and what each owns |
| `product/FR-01/requirements.json` | requirement text, milestone, and the `note` field |
| `decisions/adr/DECISIONS.md` | answers already recorded for this feature's questions; an absent file is no answers, not an error — see step 3.5 |
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

**Lead with whatever changes the recommendation.** Before the list, say which covered features
already have a spec, and — the part that actually decides it — which of those have **recorded
answers their spec has not consumed yet**. A feature whose spec is waiting on answers that have
since arrived is a bounded update, cheap and immediately valuable; a feature with no spec is a
full extraction. Bury that under a flat list of eight and the menu reads as though no work has
been done yet, which is how a caller ends up starting from scratch beside a spec that already
exists.

> F01.1 already has a spec (round 2, approval pending) and **four recorded answers it has not
> taken up** — that one is a bounded update. The other seven have no spec yet.

Given a feature id, resolve its brief from the feature file's header link and go straight on —
no menu.

## Step 2 — Read the record

From the **feature file**: title, epic, milestones, domains, the requirements owned in their own
order, and the disposition against each. This file is generated and deterministic — it is the
record, not a summary of one.

### Read it by its sections, not by the fields you came for

`build_feature_files.py` writes a fixed set of sections. A run that reads the file looking only for
the fields the contract happens to name will not see a section added since, and will report nothing
missing — the file is well-formed and the contract validates. That is how a generator and its reader
drift apart in silence, and it is why this is a walk rather than a lookup.

**Walk the sections. Each one is carried or refused, and the refusal is recorded.**

| Section | What it holds | Where it goes |
|---|---|---|
| header line | epic, milestone, domains, the link to the brief | `feature` |
| `**Spec disposition:**` | the brief's feature-level wording | `feature.spec_disposition` |
| `## Requirements owned` | one row per requirement, with milestone and disposition | `requirements`, and the note pass |
| `## What the vault records about the code` | the analysis phase's evidence rows | **refused** — recorded in `excluded_deliberately` |
| `## Not covered by this spec` | requirements the feature owns that the brief never mentions | `not_covered_by_brief`, and a stop for each |
| `` ## Named by this spec, absent from `product/` `` | requirements the brief claims that `product/` has not exported | `named_but_absent` |
| `## Provenance` | the brief, and the document revisions actually rendered | `_contract.sources` |

A section present in the file and absent from this table is a defect in this skill, not in the
file. Do not drop it. Raise a `skill-behaviour` flag against `skill/step-2`, resolved by
`the skill author`, and put the section's heading and its body **verbatim** in that flag's `what` —
that field is the destination, so the text survives the run and the next author can see what the
table is missing. Nothing else in the contract takes arbitrary section text: `excluded_deliberately`
maps a refusal to its reason and is for sections this document already knows about, so an
unrecognised section does not belong there.

The last two sections are new to this reader and each has its own rule below.

### Named by this spec, absent from `product/`

A brief is written against a document revision; `product/` is exported from that document
afterwards. In between, a brief's traceability table names requirements `requirements.json` does
not hold. `spec-intake` declares those `pending`, and the generator renders them in their own
section — fixed heading, comma-separated ids, one reason paragraph:

    ## Named by this spec, absent from `product/`

    FR-AUT-021, FR-AUT-022

    Listed for this feature in the brief's traceability table, and not carried by EPIC-01 Rev 1.13 / FR-01 Rev 1.19. They render here once `product/` is re-exported.

A generator writes it, so the shape is stable. The section is **omitted entirely** when there are
none, which is the common case; absent means none, and `named_but_absent` is then empty.

**The reason paragraph is one paragraph, emitted unwrapped as a single line**, and it is carried
whole — not its first sentence, not a summary of it. This document says *reason paragraph*
throughout and means that same string every time.

**These requirements belong to the feature and cannot be specified.** No text, no milestone, no
note — `requirements.json` has nothing to read. That is the situation the refusal at the top of this
document already describes: a requirement the feature owns that the spec cannot cover. It travels
for the same reason stops travel, so the spec can say what it left out and why.

Carry them in `named_but_absent`, each with the section's reason paragraph **verbatim**. Not in
`requirements` — a consumer walks that array and specifies what it finds, and these have nothing to
specify from. Not in `stops` either: a stop is a decision this skill took about a requirement it
could read, and reading one of these as a stop invites someone to go and resolve it.

**This never halts the run.** The ids are genuinely unspecifiable and no amount of asking changes
that before the next export. The feature is specified from the requirements that did render, and the
contract states which ones did not. They also take **no note-pass row** — see the rule below.

### The provenance line — which revisions this contract stands on

The last section names the brief, then each product document **at the revision actually rendered**,
noting the brief's own claim only where the two diverge:

    QACR-APP-SPEC-02 Rev 1.0 · FR-01 Rev 1.19 (brief cites 1.20) · EPIC-01 Rev 1.13 (brief cites 1.14)

**The leading number is what `product/` holds; the parenthetical is what the brief cites.** Reading
those the wrong way round inverts the meaning of every divergence in the contract. Where no
parenthetical appears, the two agree.

**Take the revisions from this line, never from this document.** The schema in step 6 carries
example revisions to show the shape, and they go stale the moment an ingest lands. A contract whose
`sources` were copied from an example states which revisions the spec was written against, and is
wrong while looking exactly like a record. Carry the line itself verbatim in
`sources.provenance_line`, so the claim can be checked against its source.

**A divergence is carried, not smoothed over.** It runs in both directions and neither is an error:

| Direction | `divergence_direction` | What it means for this run |
|---|---|---|
| the two agree | `none` | nothing to carry |
| `product/` **behind** the brief | `product-behind-brief` | the brief classifies requirements that have not rendered — expect a `Named by this spec` section |
| `product/` **ahead** of the brief | `product-ahead-of-brief` | dispositions were decided against text that has since been re-exported: the disposition comes from one revision and the requirement text and `note` from another, and nothing here can tell whether either changed in between |
| the two documents diverge opposite ways | `mixed` | read each document's own row; the pair has no single direction |

The third row is the quiet one — nothing announces it but a parenthetical, and it was the live case
across every E01 feature file when this rule was written on 2026-08-19.

Set `diverges` on each document where the two differ, and record **one value from that closed set**
in `sources.divergence_direction`, every run, `none` included. It is a reading of a generated line,
so two runs over the same file record the same value. Naming it is the point: left unnamed, a run
that notices the consequence narrates it in prose of its own invention and the next run does not
mention it at all. The consumer rule below carries the obligation onward; this skill reports the
direction and does not try to reconcile it.

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

**"Every requirement the feature owns" means the `## Requirements owned` table — not the brief's
traceability list.** The two are the same set only while `product/` is level with the brief. A
`named_but_absent` requirement gets **no row**: a verdict is a reading of a `note` field, and there
is no record to read one from. Its absence from `note_pass` is correct, and `named_but_absent` is
where it is accounted for instead.

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
question (`PQ-nn`, per `decisions/README.md`), and record the stop.

**On the unclassifiable.** A requirement QACR needs that ACR never had has no disposition in the
brief's vocabulary yet. When one appears, stop. Do not read it as a departure, and do not invent a
label.

A stop removes that requirement from the spec. It does not stop the feature — the rest is specified
without it, and the stops travel in the contract so the spec can say what it left out and why.

## Step 3.5 — Recorded answers, from the decision log

**A question somebody already answered never reaches the spec as open.** Answers live in
`decisions/adr/DECISIONS.md` — append-only, one `## <id> — <question>` heading per entry, a yaml
block carrying every field (`n/a` when not applicable), prose after. Entries are never edited; an
entry is superseded exactly when a later entry names its id in `supersedes`. **An absent file is no
answers yet, not an error** — record the state and move on.

**Scope the log to this feature:** entries whose `feature` matches, or whose `affects` intersects
the ids in the `## Requirements owned` table. Nothing else is read into this contract.

For each in-scope entry, the first rule that applies wins:

1. **Superseded** → ignore it. Only the superseding entry is considered.
2. **`status: deferred`** → not an answer, and not this skill's to re-triage. It travels in
   `open_items` beside the brief's U-n items: `ref` is the entry id, the question verbatim, the
   entry's named owner, and the deferral reason. `blocks` comes from `affects` with
   `blocks_inferred` false — the log attaches its own ids, so that join is a record, not a
   reading. The spec writer lists it with its owner, and nobody triages it again from scratch.
3. **Stale** — `decided_against` names a revision that has since moved (compare against the
   revisions step 2 read off the Provenance line) → do **not** fold. Raise a `stale-decision`
   flag: `needs re-confirmation: decided against <old>, current is <new>`. A stale decision must
   never silently steer a new spec — but this is a flag, not a stop; the requirement still
   specifies.
4. **`status: accepted` and `decided_against` still current** → fold it into `confirmed_as_is`,
   whose semantics already fit: recorded so nobody re-asks. Carry the entry id, the answer,
   `decided_by` / `decided_on`, and what it `resolves` and `unblocks`. **Do not invent a new
   top-level field for it** — `spec-skill`'s disposal table has no destination for one, and an
   unknown field surfaces downstream as uncarried.

Record the log in `_contract.sources` — path, `read` or `absent`, and the in-scope entry ids — so
provenance names what the folds stand on.

**The refusal at the top of this document holds here unchanged.** This skill answers nothing; it
carries answers someone recorded. An entry missing any of its mandatory fields is malformed —
report it in `excluded_deliberately` with the fields it lacks, and do not fold it. A malformed
record is a defect in the log, not a license to reconstruct what it probably meant.

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

`decisions/` is then the only thing this skill writes into `qacr-spec`. It also *reads*
`decisions/adr/DECISIONS.md` (step 3.5), but the log is written elsewhere, never here — the
boundary above is about writes, and it has not moved.

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
      "A named_but_absent requirement belongs to this feature and cannot be specified yet — it is not in product/ at the revision read. State it in the spec as uncovered, with the reason given, and do not describe the feature as fully covered. Omitting it is how a spec gets signed off over requirements nobody knew were missing.",
      "Record the revisions from _contract.sources in the spec. Where a document diverges, say so: the dispositions were decided against the revision the brief cites, and the requirement text and notes were read from the revision product/ holds.",
      "Never choose a value for an open item, and never treat a silent requirement as as-is.",
      "ACR behaviour is evidence about a solved problem, not a requirement. Derive, do not copy.",
      "Every acceptance criterion names the requirement it proves; every derived test carries that id.",
      "Where the QACR application contradicts a requirement: present both and stop for a human. The requirement wins by default. Record it either way, and when it does not win, write the question to qacr-spec/decisions/ as a PQ-nn file.",
      "Questions the spec itself raises use the spec's own id spaces: Decisions-needed rows are SD-n, Open-Questions items are SQ-x, scoped to that spec — never bare D-n or Q-n, which collide with the PM's ids (SPEC-nn's Dn departures, the Q-nn register) and read as claims about the PM's records.",
      "Answers to this spec's open questions are recorded per <qacr-spec>/.claude/skills/adr-conventions/SKILL.md, and the spec's Decisions-needed section says so. The pointer travels into every spec, so an answer found later has somewhere to land.",
      "A criterion unblocked by a recorded answer cites the entry id. The entry names what it unblocks; the criterion names what unblocked it — traceability both ways.",
      "In a repository serving more than one product: additive only. Existing behaviour and existing consumers are untouched, and blast radius is checked with /mind. If the requirement cannot be met additively, that is a stop.",
      "A proposed guideline is unreviewed. Follow it for consistency, and flag in the spec that it is unapproved.",
      "Where a domain has no guideline and you infer one while specifying, write it to qacr-spec/architecture/<domain>.md marked proposed, with the feature and date. Inferring without recording is how eighty-two features acquire eighty-two architectures."
    ],
    "incomplete": false,
    "incomplete_why": "Set whenever a step was skipped or could not run. A skipped step 4 means ACR behaviour is absent by instruction — not evidence that ACR has no prior art.",
    // Read off the feature file's Provenance line — never copied from here. `read` is the
    // revision `product/` holds, `brief_cites` is what the brief claims to trace to, and
    // `diverges` is true when they differ. The values below show shape and are stale by the
    // next ingest; `provenance_line` is what makes the claim checkable.
    "sources": {
      "brief": "QACR-APP-SPEC-01 Rev 1.2",
      "requirements": { "read": "QACR-APP-FR-01 Rev 1.20", "brief_cites": "1.19", "diverges": true },
      "epic_map": { "read": "QACR-APP-EPIC-01 Rev 1.14", "brief_cites": "1.13", "diverges": true },
      "provenance_line": "<the feature file's Provenance line, verbatim>",
      "divergence_direction": "none|product-behind-brief|product-ahead-of-brief|mixed",
      // The decision log this run read (step 3.5). `absent` means no answers yet, not an error.
      "decision_log": { "path": "decisions/adr/DECISIONS.md", "state": "read|absent",
                        "in_scope": ["<entry ids>"] },
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

  // Named for this feature by the brief's traceability table, and not in `product/` yet.
  // They belong to the feature and cannot be specified — no text, no milestone, no note.
  // Deliberately outside `requirements` so nothing downstream mistakes them for specifiable,
  // and outside `stops` so nothing reads them as a decision this skill took. Empty is normal.
  "named_but_absent": [{ "id": "FR-AUT-021", "feature": "F02.5",
                         "why": "<the section's reason paragraph, verbatim>" }],

  "departures": [{ "ref": "D1", "what_changes": "<verbatim from the brief>", "driven_by": "FR-RDY-007" }],
  // Deferred decision-log entries ride here too (step 3.5): ref is the entry id, owner and
  // deferral reason from the entry, blocks from its `affects` with blocks_inferred false.
  "open_items": [{ "ref": "U1", "question": "<verbatim>", "owner": "...",
                   "blocks": ["FR-RDY-007"], "blocks_inferred": true,
                   "blocks_what": "<what is withheld — values, verification>",
                   "brief_verbatim": "<the brief's own words on what waits on it>" }],
  // Recorded so nobody re-asks — the brief's answers, and the decision log's accepted entries
  // (step 3.5), which also carry their entry id and trail.
  "confirmed_as_is": [{ "question": "<verbatim>", "answer": "<verbatim>" },
                      { "question": "<verbatim>", "answer": "<verbatim>",
                        "decision": "<log entry id>", "decided_by": "...", "decided_on": "<ISO date>",
                        "resolves": ["<spec question ids>"], "unblocks": ["<criterion ids>"] }],

  "stops": [{
    "requirement": "FR-XXX-nnn",
    "kind": "silent|unclassifiable|note-contradiction",
    "why": "...",
    "action": "raised in decisions/PQ-nn.md | awaiting the PM"
  }],

  "note_pass": [{ "requirement": "FR-XXX-nnn",
                  "verdict": "no-note|agrees|silent|contradicts|possible-undeclared-departure",
                  "note": "<verbatim, empty if none>", "why": "" }],

  "flags": [{
    "ref": "note/FR-RDY-008",
    "kind": "note-vs-brief|requirement-vs-requirement|needs-acr-behaviour|skill-behaviour|stale-decision",
    "requirements": ["FR-XXX-nnn"],
    "what": "...",
    "resolves_with": "step 4|the PM|the decider|the skill author"
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
| `stale-decision` | `decision/<log entry id>` |

Two runs that find the same thing then give it the same name, which is what makes flags comparable
across runs at all.

**`kind` and `resolves_with` are closed sets, not descriptions.** Write exactly one of the listed
values; the elaboration goes in `what`. A prose `kind` cannot be counted, filtered or checked, which
is most of why the field exists.

**`excluded_deliberately` records what was deliberately not carried**, so a reader can tell an
omission from an oversight. The feature file embeds the vault's evidence rows; they are excluded on
every run, and saying so is cheaper than the reader wondering.

`confirmed_as_is` is carried because the brief records those answers precisely so the next reader
does not ask them again. Dropping them here reintroduces the questions one layer down. The decision
log's accepted entries join it for the same reason — one field, one meaning, and the entry id keeps
the two sources distinguishable.

## Step 7 — Verify before handing over

- every requirement in the `## Requirements owned` table appears exactly once, either with a
  `build` or in `stops`
- no disposition was assigned that the feature file does not state
- no requirement text was paraphrased
- `acr_behaviour.called` is true if and only if at least one requirement recreates
- every departure referenced by a requirement has its row, verbatim
- every open item names what it blocks
- every silent requirement has a `PQ-nn` file in `decisions/`
- `_contract.incomplete` is true whenever any step was skipped, with the reason recorded
- every open-item link carries `blocks`, `blocks_inferred` and `blocks_what` — a link missing any
  of the three is an invalid contract, not a stylistic lapse
- every `flags[].kind` and `resolves_with` is exactly one of the listed values
- every flag names what resolves it
- `note_pass` holds exactly one row per requirement in the `## Requirements owned` table — none
  skipped, and no row for a `named_but_absent` id
- every flag's `ref` matches its content, per the derivation table
- every section of the feature file is carried, or named in `excluded_deliberately` — a section
  this skill does not recognise is a `skill-behaviour` flag against `skill/step-2` whose `what`
  holds that section's heading and body verbatim, never a silent drop
- where the feature file carries a `` ## Named by this spec, absent from `product/` `` section,
  every id in it reaches `named_but_absent` with the reason paragraph verbatim, and none of those
  ids appears in `requirements`, `stops` or `note_pass`
- `_contract.sources` agrees with the feature file's Provenance line and carries it verbatim in
  `provenance_line`; `diverges` is set wherever `read` and `brief_cites` differ. A revision that
  matches this document's schema example but not the Provenance line was copied, not read — that is
  a defect, not a coincidence
- `sources.divergence_direction` is present on every run and is exactly one of the four listed
  values, `none` included — it is never omitted, and never replaced by prose of the run's own
- every in-scope `accepted` entry from the decision log was folded into `confirmed_as_is` or
  explicitly refused with its reason recorded — never silently dropped
- no `deferred` entry was treated as an answer — each travels in `open_items` with its named owner
  and deferral reason
- no stale entry — one whose `decided_against` revision has moved — was folded; each carries its
  `stale-decision` flag naming the old and current revisions
- no question the log already answers is carried as open — an answered question reaching the spec
  as open is the failure step 3.5 exists to prevent
- `_contract.sources.decision_log` is present with its state, `read` or `absent` — absent meaning
  no answers yet, never an error
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
7. **Do not write to `decisions/adr/DECISIONS.md`.** The log is append-only and recorded
   elsewhere, per `adr-conventions`. This skill carries answers; it never records one. Its only
   writes into `decisions/` remain the `PQ-nn` question files.

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
- **Dropping the named-but-absent section** because those requirements have nothing to specify.
  Having nothing to specify is the finding, not a reason to omit it.
- **Filing a named-but-absent requirement in `requirements`**, where a consumer will try to specify
  a requirement with no text, or in `stops`, where it reads as a decision someone can go and resolve.
- **Halting the run on a named-but-absent section.** The export is not arriving today; specify the
  rest and say what is uncovered.
- **Copying the `sources` revisions out of the schema example.** The example goes stale at the next
  ingest; the Provenance line is the record.
- **Reading the Provenance line's parenthetical as the rendered revision.** It is the brief's claim.
  The leading number is what was read.
- **Narrating a divergence in an invented field** instead of recording `divergence_direction`. A
  field one run adds and the next omits is not a record of anything.
- **Folding a deferred entry because its prose sketches an answer.** Deferred is not decided. It
  travels as an open question with its named owner.
- **Folding a stale decision silently.** `decided_against` names what the decision was true
  against; once that moves, the answer needs re-confirmation, not reuse.
- **Treating an absent decision log as an error.** No file means nobody has answered anything
  yet, which is a state, not a failure.
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
- **Review of the feature-file reader, 2026-08-19, no run.** A brief is written against a document
  revision and `product/` is exported from that document afterwards, so a brief routinely names
  requirements `requirements.json` has not got. `spec-intake` declares those `pending` and the
  generator gives them their own section; step 2 never read it. Those requirements left the record
  entirely — a feature specified, approved as covering it, two requirements never in it and nothing
  to send anyone back when the export lands. The refusal at the top of this document already
  covered the case in principle ("a requirement the brief does not classify does not get a
  classification here … the spec is written without it") and could not reach it, because the reader
  could not see the section. Three corrections, and the third is the one that matters.
  (i) **`named_but_absent` is its own field.** Not a `requirements` entry, which a consumer would
  try to specify from nothing, and not a `stop`, which reads as a decision someone can go and
  resolve. It does not halt the run: these ids are genuinely unspecifiable — no text, no milestone,
  absent from `requirements.json` — so the feature is specified from what rendered and the contract
  states what did not. It travels for exactly the reason stops travel.
  (ii) **"Every requirement the feature owns" stopped being unambiguous** the moment a second list
  of ids existed for a feature. It means the `## Requirements owned` table. A `named_but_absent` id
  takes no `note_pass` row, because a verdict is a reading of a `note` and there is no record to
  read one from.
  (iii) **The reader was enumerating fields, not sections, and that is the actual defect.** The
  missing section was a symptom. `## Provenance` was missing too, and worse: nothing in this
  document said where `_contract.sources` came from, and the only revisions written anywhere in it
  were the schema example's. The first two runs emitted those strings exactly — indistinguishable
  from having read them, because `product/` happened to hold Rev 1.19 / Rev 1.13 that day. It now
  holds Rev 1.20 / Rev 1.14, so the same copy would state the wrong revisions while looking like a
  record. Step 2 now walks the generator's sections against a table, each carried or refused, so
  the next section added upstream is a named defect rather than a silent omission, and the
  Provenance line is read with `provenance_line` carried verbatim so the claim can be checked
  against its source.
  Also: **revision divergence is carried in `_contract.sources`, not as a flag.** It runs both ways.
  `product/` behind the brief produces the section above; `product/` ahead of it — which is every
  E01 feature file today, reading `FR-01 Rev 1.20 (brief cites 1.19)` — pairs a disposition decided
  against one revision with text and notes read from another, and said nothing at all. Only
  `FR-AUT-003` changed between Rev 1.19 and Rev 1.20 and it belongs to E02, so nothing E01 owns was
  affected; a reader of the old contract could not have known that, which is the point. A new flag
  `kind` was considered and dropped: the set is closed and checked, and a value read off a generated
  line is a record rather than a discovery.
  Then the F01.4 pair was re-run against the edited skill, and it caught one more thing.
  **`divergence_direction` is adopted from the run, which invented it unprompted — and only in one
  of the two runs.** Both runs read the revisions correctly and agreed on every schema'd field, but
  A felt the consequence needed saying, had no field to say it in, and wrote a paragraph of its own
  under a key B never produced. That is the second-run flag instability in miniature: a finding that
  exists in one run and not the next is not a record. The name is A's; the value is now a closed set
  of four, recorded every run including `none`, because the direction is a reading of a generated
  line and prose cannot be compared across runs. Open: whether `spec-intake` should refuse to render
  a brief against a `product/` export newer than the one it cites, which would remove the
  `product-ahead-of-brief` direction rather than reporting it.
- **F01.4 with step 4, 2026-08-19 — the first run with ACR behaviour actually attached.**
  Deliberately not given an ordinal: the entry above is a review that then re-ran the F01.4
  pair, so "third run" would have named two different things. **This run predates that entry's
  edits** and was gathered at `c80d686`, so its contract carries no `provenance_line`, no
  `divergence_direction` and no `named_but_absent` — those fields postdate it, and its `sources`
  block states the revisions from the feature file's Provenance line without the machinery that
  now makes the claim checkable. Re-run F01.4 against the current skill before trusting that
  block. What follows is unaffected by the change, because it comes from `product/` and from
  source. It changed what the contract is worth: every one of the six requirements recreates, so the
  extraction is the bulk of the output rather than an appendix. All 22 structural assertions passed.
  Four findings.
  (i) **The exhaustive note pass paid off exactly as designed, and the proof is a pair.** FR-RDY-007
  and FR-RDY-008 carry the *same note shape* — "threshold TBD, fixed in the application, not
  configurable" — and resolved in **opposite directions**. ACR hardcodes the battery minimum, so
  007's note describes what the product already does; ACR reads the storage minimum from
  `staticData.lowDiskSpaceSize` on both platforms, so 008's note prescribes a change the brief never
  declared. Neither note contradicts its requirement text, so a run that scanned for conflicts would
  have missed **both**, and a run that spot-checked would have had a 50% chance of picking the inert
  one. Enumerate; the value is in the pair, not the finding.
  (ii) **The `kind` closed set has no value for the most consequential thing step 4 produces:** a
  requirement whose text the current product does not satisfy while the brief dispositions it
  `as-is`. Three arose here (FR-RDY-005's iOS no-internet alert is dead code; FR-RDY-006 has no
  backend probe at all; FR-RDY-010 re-evaluates some conditions and caches others). `note-vs-brief`,
  `requirement-vs-requirement` and `needs-acr-behaviour` all misdescribe them. Carried in a new
  `requirement_vs_acr` field rather than forced into a wrong kind — the same move the first run made
  with `_contract.incomplete`. **Step 3's disposition table probably needs a fourth outcome**, and it
  is not a stop: the requirement still specifies, it just cannot be satisfied by recreation alone.
  (iii) **The open-item rule held.** U1 withholds the values behind two of the six requirements and
  neither stopped; both mechanisms are fully specifiable with the threshold stated as a threshold.
  The superseded `open`-stops rule would have deleted two of six requirements from the spec.
  (iv) `confirmed_as_is` earned its place a second time, and more sharply: two of the five answers are
  **contradicted on one platform** by source. "A camera that fails to start blocks" is true on
  Android and false on iOS, where nothing is shown at all. An answer recorded as settled can still be
  settled about only one platform — worth checking each against the extraction rather than carrying
  them as closed.
  Open: `requirement_vs_acr` needs a real home in the schema. And the 26 vault evidence rows are
  still embedded in the feature file and still refused on every run; deleting that section from
  `build_feature_files.py` would remove the temptation instead of policing it.
