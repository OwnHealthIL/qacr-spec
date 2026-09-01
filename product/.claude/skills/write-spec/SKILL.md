---
name: write-spec
description: Writes a QACR spec document for the features of one epic, as a draft for Guy's review, then implements his approvals across the requirements, the epic map, the review register and the board, and promotes the document to ready. Use when asked to write, draft, or continue a spec — "write SPEC-02", "do the readiness spec", "next spec" — or to promote an existing draft spec to ready. Covers features triaged Unchanged or No spec directly. For a Changed or New feature it asks Guy for his brief first: a one-liner becomes a departure row inside the brief, anything larger needs a behaviour section and a shape not yet settled.
---

# Writing a QACR spec

## What this produces, and what it does not

This skill produces **a draft for Guy to review**, then implements what he approves. It does not
replace his review and it never decides for him.

Read `CLAUDE.md` first — it is the standing law of this document set, and this skill assumes it.
Where the two disagree, `CLAUDE.md` wins and this file is wrong.

**Coverage.** Features triaged `Unchanged` or `No spec` get a **recreation brief**, which is what
this skill knows how to write.

**For a `Changed` or `New` feature, ask Guy for his brief before writing anything about it.** His
answer decides the shape, and it is not predictable from the triage:

- **A one-liner, and the rest of the feature is unchanged** — then it is a *departure row* and the
  recreation brief absorbs it. No behaviour section. This is the common case and the triage note
  often already contains it.
- **More than that** — then it needs a behaviour section, and that shape has not been through a
  review cycle yet. Say so and agree the approach with him rather than inventing it.

Never assume which. A `Changed` status says only that something differs, not how much.

**Hard boundaries, all learned the expensive way:**

- Never edit a requirement, a note, or a milestone without Guy's explicit approval. Propose.
- Never write behaviour for a recreation. The current product is its specification.
- Never enumerate conditions, checks or reasons. State the rule; the product supplies the cases.
- Never state, constrain or enforce copy.
- Never source a value from copy, a note, or a register. Only the shipped application.
- Never hand-edit a `.docx`, `.html` or `.xlsx`. Edit the data module and rebuild.
- **The spec's revision lives in its filename as well as its header row, and the two must
  agree**: `specs/QACR-APP-SPEC-nn Rev<major>.<minor>.md`. Promoting a draft to ready is
  therefore a rename as well as an edit — bump both, in one commit.
- **A published revision is immutable.** Once a revision is committed, the development team
  may have built against it, so a change needs a new number rather than new text under the
  old one. The superseded file stays in `specs/`; the highest revision is the live one.
- **`evidence/behaviour.tsv` is a better input than research**, and `evidence/coverage.tsv`
  tells you whether anyone has looked at all — `no-evidence-found` means nobody extracted
  evidence, never that the code does nothing. Neither one's `file:line` citations, class
  names or internals may appear in a spec: the altitude rule does not relax because the
  evidence now sits one directory away. See section 11 of CLAUDE.md.
- **Never write outside `product/`.** `features/`, `evidence/`, `decisions/` and `tools/`
  belong to the development team, and `decisions/` in particular is where *they* raise
  questions — a spec's open items stay in the spec and the review register.

---

## Phase 0 — Scope and status. **Blocking.**

Do this before any research and before writing a line. It is two minutes of work and it decided
two wasted revisions of SPEC-01.

```bash
cd product && node -e '
const E=require("./generator/epics.js"), spec=require("./generator/spec-status.js"),
      D=require("./generator/domains.js").DOMAIN;
const e=E.find(x=>x.code==="E0N");              // ← the epic
console.log(e.title||e.name);
e.features.forEach(f=>{ const r=spec(f[0], e.code, D[f[0]]);
  console.log(`\n${f[0]} | ${f[1]}\n  ${r.status} (src: ${r.src}) -> ${r.doc||"no doc"} | ${r.state}`);
  console.log(`  FR: ${f[2].join(", ")||"none"}`);
  if(r.note) console.log(`  note: ${r.note}`); });
console.log("\nepic open items:", e.open.join(" | "));'
```

**The status chooses the document shape, so it has to be right before anything else.**

Then read `features/` for every covered feature, if the development team has built the files
yet. The **`silent` list** is a requirement the feature owns that its spec says nothing about —
nobody can build it, not because it is hard but because nobody has said what it should do. It is
the one input that tells you what the *last* revision missed, and it costs one `cat`.

Then ask Guy, in one message, before proceeding:

1. **Every feature whose `src` is `derived`** — the *status* is derived too, not just the note, and
   it may be wrong. "`spec-status.js` says F0n.n is Changed because ⟨note⟩. Is it actually changed,
   or does it work as it does today?" F01.9 was Changed on one derived sentence and was a
   recreation; two revisions of SPEC-01 described a working product before that surfaced.
2. **His brief on every `Changed` or `New` feature**, per the coverage note above. Quote the
   triage note back to him and ask whether that is the whole of it. A one-liner keeps the document
   a brief; anything larger changes the process.
3. **Which document carries which feature**, if the epic's features do not map one-to-one — see
   `DOC_OVERRIDE` in `spec-status.js`.

If the answer moves a feature to `Unchanged`, correct `spec-status.js` at the source so the epic
map and board follow, and say what the tallies became.

**When a brief lands, work out what it implies for the requirements before you reply.** SPEC-02
took three rounds where one would have done: the brief, then the research it asked for, then the
consequences — that a configuration state suppressing a step contradicts a requirement saying the
user *shall* do it, and that a platform-only affordance brushes against the parity requirement.
Both were predictable from the brief itself. Ask the question and propose the answer in the same
message.

---

## Phase 1 — Research. Bounded, with a stopping condition.

Research answers exactly three questions. **Never research in order to describe** — that has no
stopping condition and is what made SPEC-01 expensive.

1. Is the triage right? (Phase 0 asked Guy; here you check it against the product.)
2. Is the departures list complete?
3. **What does the product do that no requirement covers?** — the sweep, below.

### Where to look, cheapest first

| Source | For |
|---|---|
| `generator/reqs-part*.js` | what is already required, and at which milestone |
| `generator/id-manifest.json` | every identifier ever issued and its disposition |
| `generator/m5-map.js` | where each former backlog item went |
| `generator/configs.js` | the configuration register — flags, defaults, dispositions |
| `reviews/acr-behaviour-review-E0n.json` | the team's behaviour export for this epic, with Guy's `pm_mark` per line. Read `reviews/README.md` first: `checked_against` is behind, `change` marks are departures, `wrong` marks are research, and `platforms: differs` is nobody's |
| `evidence/behaviour.tsv` | **what the code does today, cited, one claim per row.** Cheaper and more reliable than reading the clients yourself, and it is the sweep's best starting point. Convert to product behaviour; the `file:line` never travels |
| `evidence/coverage.tsv` | whether anyone has looked at a requirement at all. `no-evidence-found` means **nobody extracted**, never that the code does nothing |
| `evidence/context.tsv` | `CTX-nn` — what a developer knows that no requirement states. CTX-02, CTX-03 and CTX-04 all bear on what the QACR build can be assumed to have |
| `features/*` — the `silent` list | a requirement a covered feature owns that its spec says nothing about. **Silence is not a decision and must never be read as as-is** |
| `decisions/PQ-nn` | questions *they* raised against a spec. Answer verbatim into the register or the requirement |
| `local/Reference/Minuteful copy/` | which conditions and screens **exist**. Never for values |
| `local/Source documents/` | Risk Analysis, both SRSs, the SPTA, UX studies |
| `/mind` | topology: which services and clients, what talks to what |
| the shipped clients | **the only source for how it behaves and what a value is** |

### Reading the shipped clients

`gh` is authenticated. Both clients are readable. Do not clone — `iosDip` is 2.6 GB.

```bash
gh api "repos/OwnHealthIL/iosDip/contents/<path>?ref=<sha>" -H "Accept: application/vnd.github.raw"
gh api "search/code?q=<term>+repo:OwnHealthIL/iosDip" --jq '.total_count, (.items[]?.path)'
gh api "repos/OwnHealthIL/AndroidDip/git/trees/develop?recursive=1"   # code search is not indexed
```

Useful anchors: the lobby view model holds the start-test gate in check order; the pre-login
coordinator holds the integrity block; shared device utils hold battery and disk; the chat test
coordinator drives timing; `.natrium.yml` and `app/gradle-scripts/variant-build-configs/` hold the
per-flavour build values. The QACR flavour is `minuteful_kidney_us` / `minutefulus`.

> **Never source a value from copy.** The shipped copy disagrees with the shipped build repeatedly,
> and always in the direction of sounding right — the wait, the battery floor and the timeout were
> each wrong in the copy set. Copy tells you a condition *exists*; only the application tells you
> what it does. Four claims in one revision came from copy and three were wrong.

**Check both platforms** for anything you will call unchanged. They agreed on everything in E01
except one battery rule — which was a real parity defect nobody had noticed.

### The sweep: capability the requirements do not cover

This is the highest-value output of the phase, and it is **research, not a question for Guy.** He
cannot be expected to know what is unspecified without being shown it.

**Start from the alert and message set, then verify against source.** `local/Reference/Minuteful copy/`
gives a finite list of the conditions the product actually raises, which is a far better bound than
"everything inside the covered features" — for E02 it turned the sweep from an open-ended trawl
across two clients and a backend into seven conditions to check against the requirements. Use the
copy set to enumerate the conditions and the source to establish what each one does. Never the
other way round, and never the copy for a value.

For the features in scope, compare what the product does against what the requirements require, and
produce one table. Each row gets your recommendation, because he is reviewing a judgement rather
than generating one:

| Disposition | Means | Goes to |
|---|---|---|
| **keep** | wanted, and no requirement covers it | a proposed requirement |
| **change** | exists, but QACR needs it differently | a departure |
| **exclude** | exists, and QACR must *not* keep it | a departure **and** an explicit exclusion, so nobody recreates it by default |

**Say what you swept and what you did not.** "Everything the product does" is unbounded, so bound
it to the conditions and states inside the covered features and state the edges. A list that looks
complete and is not is the failure this whole format exists to prevent.

**Before proposing any requirement, search for it.** Twice in SPEC-01 the thing to be written
already existed — FR-CFG-006 as a deferred backlog item, and FR-CFG-003 saying verbatim what was
wanted while sitting at milestone 5. A promotion or a milestone move is a far cheaper thing to ask
for than a new requirement.

```bash
cd product && node -e '
const s=[...require("./generator/reqs-part1.js"),...require("./generator/reqs-part2.js")];
const term=/configuration set.*test record/i;                       // ← what you would write
s.forEach(x=>x.reqs.forEach(r=>{ if(term.test(r[1])) console.log(r[0],"M"+r[4],r[1]); }));
const m=require("./generator/id-manifest.json").issued;                        // retired ideas live here too
Object.entries(m).filter(([,v])=>!/in scope/.test(v)).slice(0,5).forEach(x=>console.log(x.join(" -> ")));'
```

---

## Phase 2 — Draft the brief

Copy the shape from the live revision of `specs/QACR-APP-SPEC-01`. It is the worked
example and it is `ready`.

```
# QACR-APP-SPEC-nn — <name>
**RECREATION BRIEF.** Not a specification of behaviour.

header table   Document · Revision (0.1, draft for review) · Epic · Features covered ·
               Not covered · Milestones · Domains · Traces to <current FR and EPIC revisions>

How to read this   all features are recreations; the current product is their specification.
                   THE PRECEDENCE RULE, verbatim:
                   > Where this brief and the current product disagree on anything not in the
                   > departures table, the current product is right. Raise it rather than
                   > implementing the brief.
1. Scope           in scope / out of scope, by feature
2. Departures      the only prescriptive section. Table: # | feature | what changes | driven by
                   "No departures" is a complete and valid answer
3. Still undecided # | question | owner
4. Confirmed as-is question | answer — every question asked whose answer was "as today"
5. Traceability    feature | requirements | disposition, where `as-is` means nothing to design
6. Not in this brief
```

While the spec is in draft it also carries **Requirements proposed** — the sweep's output, with
milestones. That section is removed when the document becomes ready (Phase 5).

Rules for the draft:

- **No behaviour statements for a recreation.** SPEC-01 ended with eight features and zero, which
  is what finished looks like. If a feature starts wanting them, it is mis-triaged: stop and ask.
- Cite the current FR and EPIC revisions in `Traces to`; the guard fails a stale one.
- Every requirement owed by a covered feature must appear in the traceability table — the coverage
  guard fails otherwise. Get the owed set from `epics.js`, not from memory.
- A trace must resolve to a live requirement. A retired identifier may be discussed in prose but
  never traced to.
- No `S0n.nn` statements unless a `New`/`Changed` feature earns them; zero is valid and passes.

---

## Phase 3 — Hand over for review

Post in the conversation, not in the document:

1. **One numbered question set.** Not waves — SPEC-01's open items arrived seven, then three, then
   one, because they were raised as found. Each question answerable in a sentence, each saying what
   changes depending on the answer.
2. **The sweep table** with keep / change / exclude recommendations.
3. **Requirements proposed**, each with a proposed milestone and its dependency check (Phase 4).
4. **What was not swept**, so he knows the list's edges.
5. **Any `decisions/PQ-nn` raised against this spec**, answered. Those are the development
   team's questions and they cannot close them.

**Give him a redline for anything past the first revision.** From SPEC-04 Rev 0.2 onwards the
handover was a published page grouping every change by *the mark that caused it*, with a separate
section for the changes he did not ask for. That second section is the point: it separates your
judgement from his instruction, and it is what got both of the remaining calls answered in a
single pass instead of three. He edits the file in place and adds comments in `<angle brackets>`,
so expect the document back through an editor — straight quotes become curly, headings pick up
`\.` escapes, and tables get respaced. **Normalise that away before reading, or the real edits
are three in a diff of two hundred lines.**

Then stop. Do not implement anything until he answers.

---

## Phase 4 — Implement his approvals

Only what he approved, and nothing adjacent.

### Milestones: check both directions before proposing one

Requirements here do not cross-reference each other, so dependencies are logical and you have to
reason them out. For each requirement:

- **what it needs** — it may not sit earlier than anything it depends on;
- **what needs it** — it may not sit later than anything that depends on it;
- then the rule from `CLAUDE.md` section 4: milestones 3 and 4 share a date, so **a must-have may
  not depend on a nice-to-have**, and **milestone 5 has no date at all** — a milestone-3 departure
  resting on a milestone-5 requirement is the worst form of it. That was exactly SPEC-01's D2, and
  moving FR-CFG-003 to 3 is what fixed it.

State the earliest legal milestone and the one where it is needed. If they differ, say so.

### Order, and it matters

1. `reqs-part*.js` — new requirements and amendments. New identifiers take the next free number in
   the section; **never reuse one**, including the gaps left by withdrawals.
2. `epics.js` — a feature must own every new requirement or the build fails. Update the
   per-milestone `split` if a requirement's milestone moved.
3. `review.js` — close what the decisions close, moving items to `exports.closed` with the revision
   that closed them. Never leave an item asserting something the change just made false.
4. `version.js` — bump `FR`, and `EPIC` with it. Both, always.
5. `npm run build && npm run check`, from `product/`.
6. **Then** refresh the specs — **all of them, and each one costs a revision.** The bump
   invalidates every spec's cited revision, and a new requirement makes its feature's spec owe a
   trace it does not have. Both fail the build.

> **In the shared repository a published revision is immutable, so refreshing a spec's citation
> is not an edit — it is a new revision of that spec.** That used to mean one FR bump re-issued
> every live spec, ready documents included, because `layout-check.py` check 6 refuses an
> in-place edit to anything committed.
>
> **`spec-impact.py` is what removed that cost, and it runs inside `npm run check` — every
> time, on nothing but the files in the tree.** Nothing triggers it and nothing has to remember
> it. A spec may now cite a superseded FR revision; what fails the build is a spec that lags
> **and traces to a requirement that actually moved** — text, milestone, or gone. Anything else
> prints the lag and passes.
>
> So the answer to "which specs does this bump re-issue" is a machine's, not a judgement:
> re-issue what it names. When SPEC-04's pass amends nine requirements, it names SPEC-05 and
> nothing else, because SPEC-01, SPEC-02 and SPEC-03 own none of them.
>
> Two consequences worth holding on to. **The citation now carries information** — allowed to
> lag, it records what the document was last verified against, which is the thing a reader
> actually wants and which a forced-current citation can never say. And **batching approvals
> still helps**, just less: it is re-reading the affected specs that costs, not the numbering.

Note the difference between *citing* a requirement and *tracing* to one, because the guard
depends on it. A trace is a traceability-table row or a `*Traces:*` line and claims coverage;
prose may mention any requirement it likes. SPEC-04 discusses FR-TIM-008 in a departure without
tracing to it, so an amendment to FR-TIM-008 does not re-issue SPEC-04 — it re-issues SPEC-05,
which owns it.

### Verify — `CLAUDE.md` section 8, in full

`npm run check` is necessary and not sufficient. Also: validate the XML of every part of both
`.docx`; extract with python-docx and confirm counts and distribution; **diff priorities against
the previous revision and prove the drift is exactly what was intended**; render and read the
cover pages — `python3 generator/render-pages.py .`, which needs LibreOffice and poppler and is
no longer a step to be skipped for want of a renderer; run the board in a DOM and confirm no
script errors. Prove any new guard by running
it against the artefact that carries the defect, before fixing it.

---

## Phase 5 — Promote to ready. The last step.

Ready comes **after** the requirements land, not before. SPEC-01 was marked ready and then the
requirement pass bumped the revision, which immediately made the ready document cite a superseded
one.

1. Remove the **Requirements proposed** section. A ready document is what a developer builds from,
   and a list awaiting a product decision is not — and it dates the moment one is approved.
   **Before deleting it, check every decision in it survives somewhere.** SPEC-04's section 5
   held nine, and five lived nowhere else: when a test becomes active, that speech stops on
   confirm, that the screen does not dim, the flow's pacing, and that the used-kit confirmation
   closes the window. Deleting the section without landing them as requirements loses them
   silently. That is the whole reason ready comes second.
2. Fold answered questions into **Confirmed as-is**; keep only what is genuinely still open.
   A draft may carry its own review history — a *closed at review* table, a *what changed*
   note; a ready document carries neither.
3. Refresh the cited FR and EPIC revisions, and the traceability table's milestones.
4. Strip the archaeology. Notes about what earlier revisions got wrong belong in `CLAUDE.md`, not
   in a delivery document. **This includes the revision's own changelog paragraph** — useful while
   he is reviewing successive drafts, wrong the moment the document is delivered.
5. Set the document's state to `ready` in `spec-status.js` — `STATE` — so the board shows it. That
   is what tells a developer the document is not still moving under them.
6. **Rename the file and bump the header row together, in one commit**: `Rev0.n` becomes `Rev1.0`
   in the filename *and* in the Revision row. The superseded draft stays beside it. Then rebuild
   the board — `spec-status.js` is the only data module it reads, so neither `.docx` moves and
   neither should be committed dirty.
7. `npm run check`. **Checks 7 and 8 of `layout-check.py` are steps 1 and 5 of this list**, and
   they are the only two a machine can make. They exist because this step was got backwards once.
8. Report: what he approved, what landed where, and what remains open.

> **Open items do not block ready.** SPEC-01 went ready carrying one. What blocks ready is a
> requirement the document's own prescriptive half contradicts — SPEC-04's section 3 stated a
> practice scan the user passes through while FR-IMG-022 said the software *shall allow* one to be
> started, and its D9 let the demonstration controls cross a timing window FR-TIM-008 admits no
> exemption from. **No guard catches that**: `spec-check.py` asks whether a traced identifier is
> live, never whether the spec and the requirement agree. Read the requirements a departure or a
> behaviour statement traces to, and check them by hand, before promoting.

---

## Failure modes, in the order they cost the most

| | |
|---|---|
| Writing behaviour for a recreation | Every statement is noise or a defect: right, it restates the product; slightly wrong, it silently instructs a change. 35 statements became 4, then 0. |
| A list read as complete | Thirteen conditions named where the product has more than twenty. A team building to it removes working capability. **Enumeration in a spec fails by subtraction.** |
| Not confirming a `derived` status | Two revisions describing a feature that turned out to be a recreation. |
| Sourcing a value from copy | Three of four claims wrong in one revision. |
| Over-specifying | Happened three times at descending altitudes — behaviour, then spec prose, then requirement text. Each time the fix was to state the rule and drop the mechanism. Assume you are doing it. |
| Proposing what already exists | Search the requirements, the manifest and the milestone-5 map first. |
| Leaving proposals in a ready document | They date immediately and nobody builds from them. |
| Marking ready before the requirements land | The revision bump makes the ready document stale on the spot — and deleting the proposals section first loses every decision that lived only there. Five of SPEC-04's nine did. |
| Not reading this file | It lives under `product/`, so the harness never lists it and nothing offers it. SPEC-04 was written and reviewed through four revisions from `CLAUDE.md` alone; section 5 carries the reasoning but not the sequence, so the promotion came out backwards. `CLAUDE.md`'s preamble now points here. |
| Promoting a spec whose own content contradicts a live requirement | No guard asks whether a spec and its requirements agree, only whether the identifier is live. Check by hand. |

Two of Guy's standing instructions that reach beyond specs, both easy to trip over:

- **Some risk controls are guarded by the product manager**, not by the software — the
  configuration-driven ones especially. A requirement may say configuration determines behaviour
  without that weakening the control. Do not build a mechanism to make a configured control
  tamper-proof.
- **The requirement states the rule; the product supplies the cases.** This is why FR-RDY-014 does
  not list the refusals it covers and FR-RDY-011 does not say which conditions block.
