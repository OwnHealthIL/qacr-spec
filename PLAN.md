# Execution plan

Six phases, one branch each, one session each. Master only ever receives a finished phase.

**Rule:** nothing partial or unverified lands on master. A phase that overruns gets cut down, not
merged half-done.

---

## State today

| | |
|---|---|
| `master` | committed (`aed9a80`), 15 files, **not pushed** |
| `product/` | done — 241 requirements, 22 areas, 15 epics, 82 features, all 46 self-stated counts validate |
| `evidence/pins.yaml` | done — 4 repos, all pinned commits still HEAD |
| `wip/evidence-extraction` | not yet committed. 2,859 extracted candidates with citations resolved |

### Data already collected (do not re-derive)

- **2,859 candidates** from 3 atlases + 87 spec notes, each with citation, sentence, product, vault line.
- **851 continuation citations** (bare `:2422`) resolved; **44 unresolvable** — listed in `wip-evidence/residual-unresolved.tsv`, a defect in the vault's writing.
- **450 compressed rows** — all atlas-scoped, **zero** carry a requirement id, so none apply to SPEC-01.
- **SPEC-01 scope:** 8 features, **28 requirements**. 88 candidates already cover **11** of them; **17 have no evidence at all**.

---

## Phase 1 — Base

**Branch:** `phase-1-base` → master, then push both.

- `PLAN.md` (this file).
- `tools/parse_product_docs.py` onto master — without it `requirements.json` has no generator and cannot be refreshed at Rev 1.20.
- Commit the extraction work to `wip/evidence-extraction`: extractor, `candidates.jsonl`, `NOTES.md`, `residual-unresolved.tsv`, the 450 compressed rows. **Drop** `batches/` (3.2 MB exact duplicate of `candidates.jsonl`) and both `resolver_patch*.py` (stale — patch2 matches 0 of 2 anchors).
- Push `master` and `wip/evidence-extraction`.

**Done when:** repo is on the remote, and someone can clone it and regenerate `requirements.json` from the `.docx`.
**Size:** minutes.

---

## Phase 2 — The instrument

**Branch:** `phase-2-citation-checker`

`tools/check_citations.py`. Ported from the vault's `Citation checker.py`, with its two known gaps fixed:

- its regex indexes `.pbxproj` and `.md` but cannot match them, so those citations are silently skipped
- it cannot see continuation citations at all

Reads a TSV of claims; resolves each citation against the four repos; confirms the file exists and
really has that line; prints a resolve rate and every failure.

**Done when:** it runs against `wip-evidence/candidates.jsonl`, reports a resolve rate, and every
failure is named. A failing citation is a finding, not a row to delete.
**Size:** ~1 hour.

Built before any evidence work because everything after it leans on it, and it turns the expensive
parts into a loop that runs in under a second.

---

## Phase 3 — Context table

**Branch:** `phase-3-context-table`

`evidence/context.tsv` from the vault's Context register — 11 `CTX-nn` rows:

```
id  fact  what_no_requirement_states  attributed_to  date  affects
```

Facts a human supplied that no requirement states. A note can be accurate against the requirements,
accurate about the code, and still wrong about QACR — this is where that gap is recorded.

**Done when:** 11 rows, each traceable to a named person and date.
**Size:** ~30 minutes. Independent of every other phase.

---

## Phase 4 — First evidence slice

**Branch:** `phase-4-evidence-spec01`

`evidence/behaviour.tsv`, scoped to SPEC-01's 28 requirements only — not the full table.

```
requirement  area  product  status  claim  citation  source
```

Method: run Phase 2's checker over the candidates first and fix what it reports; freeze; then one
compression pass. Never move a citation underneath a completed batch.

Also ships `evidence/coverage.tsv` — requirement id, extracted yes/no, scope. **Required**, because
in a partial table absence is ambiguous: a developer greps `FR-CFG-003`, gets nothing, and cannot
tell "nobody has looked at this in the code" from "not extracted yet". Those are opposite
conclusions.

**Done when:** each of the 28 either has cited rows for both ACR platforms, or is on the
zero-evidence list. Resolve rate reported.
**Size:** half a session.

---

## Phase 5 — First feature files

**Branch:** `phase-5-features-spec01`

Run SPEC-01 through the pipeline in `SDLC.md`, using the `spec-intake` skill.

- Trace its 28 requirements: departure / as-is / open / **silent**.
- For every as-is claim, compare `acr-ios` against `acr-android`. **Where they disagree, as-is is
  undefined** — that is the `FR-RDY-007` battery-check case, and it becomes a decision, not a guess.
- 8 feature files in `features/E01/`.
- One `decisions/D-nn.md` per unresolved question.

**Done when:** 8 feature files exist, and every platform disagreement is a decision file awaiting
Product.
**Size:** one session. **Generates work for Product** — this is the phase that asks you questions.

**This is the gate.** If the design is wrong it shows here, after two sessions, not after the full
table.

---

## Phase 6 — Full evidence table

**Branch:** `phase-6-evidence-full`

The remaining ~2,700 rows, so the next spec does not need Phase 4 again.

With Phase 2 in place this is mechanical: validate all 2,859 against the repos, iterate the
resolver against the checker alone until clean, freeze, compress once.

**Done when:** table complete, resolve rate reported, the 44 unresolvable citations filed back to
whoever maintains the vault.
**Size:** one session, mostly unattended.

---

## Why this order

Phases 1–3 are base: small, certain, independent. Phase 4 is the first slice of the hard thing,
scoped to the spec actually on the desk. Phase 5 proves the design. Phase 6 is the bulk, and it
goes last because its value depends on the design being right — and Phase 5 is what establishes
that.

## The lesson this order encodes

The first attempt used the compression pass as the citation validator, so every defect invalidated
completed batches and cost a full re-run. Validation must be cheap and must run **before** the
expensive pass. That is why Phase 2 exists and why it comes before Phase 4.
