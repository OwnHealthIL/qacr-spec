# Behaviour evidence extraction — work in progress

Stopped deliberately on 2026-08-13 so the repo could ship. Nothing here is on `master`.
Everything needed to resume is in this directory.

The goal was `evidence/behaviour.tsv`: one row per cited claim about what the ACR and QACR code
does, in the columns `requirement · area · product · status · claim · citation · source`.

---

## Where this got to

| | |
|---|---|
| Candidates extracted | **2,859** — mechanical extraction is **complete** |
| Compression batches done | **3 of 20** (`out/batch_01`, `02`, `06` — 450 rows) |
| Current extractor | `tools/extract_behaviour_candidates.py`, resolver revision 6 (see below) |
| Rows still needing compression | ~2,409 |

`candidates.jsonl` is the artefact to protect. 2,859 rows, 3.4 MB, each carrying the citation, the
sentence and paragraph it came from, the vault file and line it came from, the product, and the
section status. Regenerating it means re-running the whole extraction and re-doing six rounds of
resolver work.

The 17 batches under `batches/` are the same data split for the compression pass. `out/` holds the
three completed ones. **The 20 batch files are current; the three outputs match them.** Earlier
outputs for batches 03–05 and 07–10 were discarded, not lost by accident: the resolver changed
their citations underneath them, and a compressed claim written against a wrong citation is worse
than no row at all.

Candidate breakdown: 1,610 rows from `03 Specs/*.md` (all carry a requirement id), 1,249 from the
three atlases. By product: acr-ios 820, acr-android 692, qacr-ios 687, qacr-android 657, 3
unresolved. 22 negative `NOT FOUND` rows.

---

## The continuation-citation problem

This was the whole of the difficulty, and it is the thing to understand before touching the code.

Android-side vault prose writes a filename once and then refers to further lines in the same file
as a bare `` `:2422` ``. There are **851** of these across the extracted scope — the vault's own
citation checker cannot see them at all, so they have never been validated by anything.

A bare `:2422` is only meaningful relative to a filename that must be recovered from the
surrounding prose. Recovering it wrongly attaches a *true claim* to the *wrong file*, which is
worse than dropping the claim, because it looks correct.

### The rule that was settled on

Resolution is scoped to a **segment** — one bullet, one table row, or one sentence — with the
paragraph and then the section behind it. In order:

1. **Symbol match.** If a symbol is named next to the citation — "polled by
   `SyncManager.getOrderStatus` (`:463-524`)" — and a file of that name is cited somewhere in the
   same section (then the same document), that file wins. The symbol may sit up to 160 characters
   *before* the citation but only 16 characters *after* it: a wide forward window steals the base
   from the next sentence. **The match is scoped to the citation's product** — see the collision
   class below.
2. **Nearest earlier file mention in the segment whose real file on disk is long enough to have
   that line.** The line-count check is what separates a code file from a passing mention of a
   one-line asset. It reads the actual repositories; it is used only to *reject* a candidate,
   never to invent one.
3. Nearest earlier file mention, unverified; then the last file named in the paragraph; then in
   the section.
4. Nothing → the row is **kept** with the citation exactly as the vault wrote it (`:403-541`), so
   the checker fails it. A citation that cannot be resolved is a finding, not something to delete.

Resulting distribution of the 851: verified 515, symbol 144, paragraph 117, section 25, nearest 6,
**unresolved 44**.

A file mention with no line number (`` `ExamSenderHandler.swift` `` … "at `:14-71`") also
establishes a base. Extensionless build files count: `Jenkinsfile`, `Dangerfile`, `Fastfile`,
`Podfile`, `Gemfile`, `Makefile`, `Appfile`, `Matchfile`, `Dockerfile`.

---

## Error classes found, each with the example that exposed it

Every one of these was found by a compression subagent noticing that a citation contradicted its
own sentence — and every one cost a re-run of the batches already done. That is the design defect;
see the lesson at the end.

### 1. Wrong-file inheritance from a passing asset mention

`acr-android.md:296`

> Four lobby screens keyed by Lottie asset (`LobbyContainerViewModel.kt:40-45`): `Welcome`
> (`lobby1_welcome.json`), … `WelcomeResults` (`lobby4_results.json`). Selection logic at
> `:194-215`.

Resolved to **`lobby4_results.json:194-215`**. The source means `LobbyContainerViewModel.kt`. A
Lottie asset has no selection logic. Fixed by the line-count check plus segment scoping.

Same class: `store_debug.json:86-94` for `PersistenceService.kt`; `trace.json:455-470` for
`Server.kt`; `podTemplates/androidJava17Builder.yaml:70` and `shared_module_versions.json:198` for
`AndroidDip/Jenkinsfile` (that one because `Jenkinsfile` has no extension and was invisible to the
file-mention regex).

### 2. Cross-platform and cross-product symbol collision

`CameraViewModel` exists as a Swift file **and** a Kotlin file, in ACR **and** in QACR — four real
files, one name. An Android sentence —

> **Android decouples text from voice.** `CameraViewModel.handlePreviewFrame` updates the text
> state at `MIN_TEXT_UPDATE_INTERVAL = 750L` … `:547`

— resolved onto **`iosDip/Dip/Infra/Camera/CameraViewModel.swift:547`**. Now
`ui/screens/camera/CameraViewModel.kt:547`.

Fixed by scoping symbol lookup to the passage's full product (family *and* platform), not just the
platform. A second bug hid behind this one: the symbol index kept only **one** path per basename,
so `SyncManager.kt` (which exists in both `AndroidDip` and `AndroidQacr`) resolved to whichever
was seen first and then failed the product filter. The index now keeps every path per basename and
lets the product filter choose.

Related, and fixed the same way: the vault's own rule that **an explicit repository path the author
wrote outranks the surrounding label** — a spec's `**QACR Android today.**` paragraph legitimately
cites the iOS file when comparing the two. Rows like candidate 1486 were labelled `qacr-android`
while citing `Quant.xcodeproj/project.pbxproj`.

### 3. Inheritance leaking across a product boundary — the batch 07–10 residue

This is the class the spec-note batches surfaced, and it was the largest. In `03 Specs/*.md` the
evidence block is divided by run-in labels `**ACR today.**` / `**QACR iOS today.**` /
`**QACR Android today.**`. The carry-over filename was **not** being reset at those boundaries, so
a QACR Android paragraph inherited a `Quant/…swift` path from the QACR iOS paragraph above it.

Concretely, `FR-COM-003`: seven bare citations in the `**QACR Android today.**` block
(`:268-277`, `:303-310`, `:210`, `:122-124`, `:133-139`, `:486-525`, `:90-112`) were resolving to
iOS `ChatFlowViewController.swift`. The sentences are about `SyncManager.kt`.

**Verified.** The carry-over is now cleared whenever the run-in label or the `**iOS.**` /
`**Android.**` sub-label changes. Those seven rows are now honestly *unresolved* rather than
confidently wrong — the citation is left as the vault wrote it and the checker will fail it.

I re-checked every case the subagents flagged in batches 03–10 against the data rather than taking
their word for it. Of 23 tracked cases, 21 now resolve correctly; the remaining 2 are in the list
below. The subagents were right on essentially every call — worth trusting next time, but still
worth verifying, since one report (`Camera2Extensions.kt`) was a case where an earlier "fix" of
mine had made things worse.

### 4. Also fixed along the way

- `.pbxproj` and `.md` citations: the vault's checker indexes both extensions but its regex never
  lists them, so **every such citation is silently skipped** by the vault's own validation. The
  extractor matches them.
- Citations with several ranges in one backtick (`build.gradle.kts:87-89, 267-283`) were matched by
  nothing and dropped.
- Glob patterns (`` `*.yml` ``) were being treated as filenames and became inheritance bases.
- Paths containing spaces (`…/MinutefulUS + Minuteful UK/…`) were not matched.

---

## Residual ambiguous rows — a defect in the vault, not in the resolver

**44 citations cannot be resolved by any rule**, because the source prose does not contain the
information. They are listed in full in `residual-unresolved.tsv` with their candidate number, the
citation exactly as written, the vault file and line, and the sentence.

These should go back to whoever maintains the vault rather than being silently dropped. Each is a
place where a reader cannot tell which file a line number refers to either.

Named examples, with the vault line:

| Candidate | Vault source | Written as | The problem |
|---|---|---|---|
| 1273 | `FR-CAM-001` | `:305-314` | "Execution: `CameraViewModel.requestNextFrame(settings:)` (`:305-314`)" — QACR's `CameraViewModel.swift` is never cited with a path anywhere in the note, so there is nothing to inherit from. |
| — | `FR-RDY-002:104` | `:403-541` | "not among the 44 fields of `AppSettingsNetworkService.InitResponseData` (`:403-541`)" — the file is never cited, only the type. |
| — | `FR-COM-003:147` ×6 | `:268-277` etc. | The `**QACR Android today.**` block refers to line ranges whose file is named only in the iOS block above. |

Four rows resolve to a *plausible but probably wrong* file and no rule fixes them. They are the
ones to re-read by hand:

| Candidate | Resolved to | The source appears to mean |
|---|---|---|
| 381 | `dip/order/OrderManager.kt:130-137` | `FlowStartManager.kt` — a table row `\| 11 \| Demo-flow warning \| :130-137 \|` whose subject is the table's, not the previous row's |
| 549 | `Server.kt:19-23` | `Requests.kt` — "`Requests.kt` … deliberately separated from `Server.kt` … (comment at `:19-23`)"; both files are long enough, both are code, nearest-mention picks the wrong one |
| 1046 | `Quant/Scripts/download_algo.sh:83` | `AlgorithmService.swift` — the same `fatalError` string is cited correctly at candidate 959 |
| 1275 | `UIDevice+Extensions.swift:582-587` | QACR's `CameraViewModel.swift` — same cause as 1273 |

---

## The design lesson

**The compression pass was acting as the citation validator.** Every defect above was found by a
subagent reading a sentence, noticing it did not match its citation, and saying so — which meant
each finding invalidated batches already compressed and cost a full re-run. Three rounds of that
consumed most of the effort and is why only 3 of 20 batches are complete.

The two stages were coupled for no reason. They are independent:

**Next attempt, in this order:**

1. **Resolve and validate all 2,859 mechanically, first, alone.** Every citation gets checked
   against the real repositories: the file exists, and it really has that line. Every continuation
   citation reports which rule resolved it and what it resolved to.
2. **Iterate on that until it is clean** — it runs in under a second and costs nothing. Diff each
   resolver change against the previous run and read the rows that moved; that is how every one of
   the classes above was actually caught, and it did not need a model at all.
3. **Add a cheap consistency check** the subagents were performing by hand: if the sentence names a
   symbol `Foo.bar()` and the resolved citation is not `Foo.<ext>`, flag the row. That single check
   would have surfaced classes 1, 2 and 3 in one mechanical pass.
4. **Only then compress, once.** Feed the frozen, validated candidates to the compression pass and
   never move a citation underneath a completed batch again.

Also worth keeping: the compression prompt in the batch runs was good and needs no change — one
line per citation, present tense, no markdown, run long rather than lose meaning, never merge two
claims, never add an implication. The three completed outputs are a fair sample of what it
produces.

---

## Data already collected (do not re-derive)

Recorded on master in `PLAN.md`, which was retired once its six phases were done. Moved here,
where the artefacts it describes actually live.

- **2,859 candidates** from 3 atlases + 87 spec notes, each with citation, sentence, product, vault line.
- **851 continuation citations** (bare `:2422`) resolved; **44 unresolvable** — listed in `wip-evidence/residual-unresolved.tsv`, a defect in the vault's writing.
- **450 compressed rows** — all atlas-scoped, **zero** carry a requirement id, so none apply to SPEC-01.
- **SPEC-01 scope:** 8 features, **28 requirements**. 88 candidates already cover **11** of them; **17 have no evidence at all**.
