---
name: acr-behaviour-reference
description: Establish how the shipping ACR application actually behaves for a named feature, read from source with a citation on every line, and emit it as a structured reference another agent can reason about. Use when asked "how does ACR do X", "what is the current behaviour of X", "get the ACR reference for X", when a QACR feature is described as the same as or similar to the current product, or when a specification must be derived from an existing implementation rather than invented. Produces reference material, never a specification.
---

# Reading ACR's real behaviour, for an agent to reason about

**The output is reference material. It is not a specification, and it is not a design to copy.**

Everything here serves one downstream question: *what must the new product do, given what the old
one does?* That question is answered by **understanding** ACR — its behaviour, and where derivable
its intent — not by transplanting it. A consumer that copies this document produces a clone,
including the bugs. Say so in the output itself; do not rely on the consumer being careful.

## What this skill is, and is not

It takes **a feature or capability, named in plain words** — optionally with whatever ids, notes or
scope statement the caller already holds — and emits **one self-describing file** describing ACR's
current behaviour for it.

It is deliberately **agnostic about what produced its input and what consumes its output.** It does
not require a specification to exist, does not read a requirements corpus, and assumes nothing about
a wider workflow. Anything the consumer must know travels *inside* the output, in `_contract`.

It does **not**: write a specification, decide what the new product should do, judge whether ACR is
right, or describe the new product's current state. Those are other jobs. Producing a confident
answer to a question outside this boundary is the main way this skill fails.

---

## The variant lock — read this before opening a file

**ACR means Minuteful Kidney US, and only that.** A behaviour line read at any other target or
flavour is a defect, not a detail, because the flavours genuinely differ in flow, copy and gating.

| | In scope |
|---|---|
| iOS | `iosDip/Dip/TargetFiles/Acr/MinutefulKidneyUS/` |
| Android | flavour `acrFda` × `minutefulUs` — declared at `AndroidDip/app/build.gradle.kts:128` and `:201`; sources in `app/src/acrFda/`, `app/src/minutefulUs/`, combined variant dir `app/src/acrFdaMinutefulUsStagingDebug/` |

**The trap that has to be named: there are two US targets.** `Acr/AcrUs` (iOS) and `acryd`/`acrydUs`
(Android) are *also* US builds, sit in the same directory listing, and are **out of scope**. So is UK
`Minuteful` / `minuteful`, and every non-ACR flavour (`boots`, `clalit`, `dip`, `maccabi`…). "The US
target" is ambiguous in this repository; `MinutefulKidneyUS` is not.

Shared code reached *from* the in-scope target is in scope — that is where most behaviour lives. What
is banned is reading a **sibling flavour's** override and reporting it as ACR's behaviour.

Both repositories are **read-only**. Never write to them. Exclude `iosDip/.claude/worktrees/` from
every search or you will get duplicate hits from a nested worktree.

### Getting at the repositories

Local clones are preferred and are not required. In order:

1. **Local clone**, if `iosDip` / `AndroidDip` are present. Pin with `git rev-parse HEAD`.
2. **`gh api` at a pinned commit**, for a repo you can access but have not cloned:
   `gh api "repos/OwnHealthIL/<repo>/contents/<path>?ref=<commit>" -H "Accept: application/vnd.github.raw"`
3. **`/mind`**, when you need to find *where* something lives before you can read it — see below.

A developer without the ACR repositories cloned can still run this skill.

---

## `/mind` — extends a trace, never starts one

Most ACR behaviour reaches beyond `iosDip` and `AndroidDip` — into shared modules, and into the
backend. Use `/mind` to follow it.

**The rule: start inside the locked variant, then follow.** Take a citation you already hold in the
in-scope target and use `/mind` to trace where it goes. Never use `/mind` to search for ACR behaviour
cold.

This is not caution for its own sake. The variant lock is enforced by *directory paths inside
iosDip and AndroidDip*. A shared module has no variant concept — it serves every flavour — and a
backend service serves every product. Asked cold, `/mind` cannot tell you whether what it found is
ACR's behaviour or a sibling's. Asked to follow a call you have already located inside the lock, it
can.

Use it for:

- **The trail leaving the two repositories.** A call into a shared module, an event, a database.
- **`not_derivable: backend`.** The apps only send and react, so a requirement about what the
  *server* decides is invisible from the app — the read stops at the network boundary. `/mind` traces
  the endpoint to the service that owns it, and some of those admissions become findings.
- **Locating a code surface** you cannot find from the target's own directory tree.

Do not carry a hardcoded list of repositories in this skill or in a brief. `/mind` already knows what
exists and how it connects; a list goes stale and a stale list is read as fact.

---

## Step 1 — Turn the feature into a code surface

Write one sentence first: *"from X to Y"*. If it needs two sentences it is two features, and the
extraction should be split — the register in Step 3 collapses under a feature that has two subjects.

Then locate the surface from what already exists, rather than grepping cold:

1. **`/mind`** — resolve the components the feature names and see what they connect to, so the search
   starts from the real topology rather than a guess.
2. **The flow is script-driven, so steps are enumerable rather than guessed.** ACR's guided flow is a
   bundled JSON of `{"itemGroups": {group: [items]}}`, the same schema on both platforms, with
   `headlessButton` and `conditional` as the control items. Read the script and you have the happy
   path as data.
3. **The alert catalogues give you the failure paths without inventing them.** Android:
   `app/src/main/java/io/healthy/dip/alert/AppAlert.kt` (a sealed hierarchy, ~85 subclasses, each with
   a `Type`) reached through `AlertController.kt`. iOS: `Dip/Features/Alert/AlertCoordinator.swift`
   plus the target's own `AcrMinutefulKidneyAlertsGenerator.swift` and its `Localizable.strings`;
   Android's user-facing copy is `app/src/minutefulUs/res/values/client_strings.xml`.
4. **A prior atlas, if the caller supplies one.** Some projects keep a secondhand reading of the
   repositories. Treat it as an index into the source, **never as the source** — a passing citation
   proves a line exists, not that it says what was claimed. Optional; the skill runs without one.

Enumerating the alert catalogue is what turns "the error cases" into a finite, checkable list. Do it
before writing any scenario, and record the ones that turned out to be unreachable.

## Step 2 — Extract in parallel, one agent per feature area

Fan out one agent per feature area, capped at **4–5 concurrent**. Each agent:

- **writes its findings to a file and replies in three or four sentences.** A large reply dies with
  "Connection closed mid-response" and the work is lost. This is not a style preference.
- carries the variant lock verbatim in its brief, including the two-US-targets trap. An agent that
  has not been told will read `AcrUs`, because the directory sits right beside the right one.
- carries the `/mind` rule verbatim — extends a trace, never starts one.
- is told to return **"not derivable"** rather than a plausible answer. This is the single most
  important instruction in the brief, because the consumer is an agent that will specify whatever it
  is handed, and a guess is indistinguishable from a reading once it is written down.

Then run **one reconciliation pass across the whole feature**, never per area. Divergences, duplicate
lines and behaviour that no scenario claimed are only visible with every line in view.

## Step 3 — The register: one line, one behaviour, no implementation

Every behaviour line is **present tense, user-visible, and ≤ 25 words.**

> ✅ `After the scan the user sees "The kit has expired" instead of results.`
> ✅ `This is the only kit failure offering two choices: "I HAVE A NEW KIT" and "SUPPORT".`
> ❌ `validateColorboardQR parses the 412 body and routes to the expiry alert.`

The rule holds even though the consumer is an agent — for a sharper reason than readability. **The
line is what the consumer may reason about; the evidence is how it verifies.** Mixing them lets ACR's
implementation enter the reasoning as if it were a requirement, and the derived specification
inherits a class name as a constraint. Keep behaviour in `text`, implementation in `evidence`.

**Both platforms, every line, no exceptions.** A line checked on one platform only is not a finding.
Each line carries an `ios` and an `android` reading and one `divergence` verdict:
`same` · `differs` (both sides stated, and they must actually read differently) · `ios-only` ·
`android-only`. Divergence is signal: on E03, 10 of 86 lines differed, and two were live defects.

## Step 4 — Evidence is first-class, and every citation carries its own provenance

**Every line carries at least one citation, `repo/path:line`, naming what it shows.** A line without
evidence does not ship.

This is the deliberate inversion of the human-facing variant of this work, where a leak guard
*refused to render* a file path so the document stayed readable. Here the consumer needs to verify,
quote and re-read, so evidence is promoted into the record beside each line — while the behaviour
prose stays free of it, per Step 3.

Cite the **narrowest thing that proves the claim**.

**Provenance belongs on the citation, not on the file.** A single file-level "read at these two
commits" block is a promise that holds only while nothing leaves `iosDip` and `AndroidDip` — and it
breaks *silently* the moment a line comes from anywhere else. Each citation therefore states how it
was established and what it was read against:

| Field | |
|---|---|
| `via: "source"` | someone opened the file and read it — locally, or via `gh api` at a pinned commit |
| `via: "map"` | the architecture map states it; no file was opened |
| `read_at` | the commit for a `source` citation; the map's version/date for a `map` one |

A file read through `/mind` at a pinned commit is exactly as solid as one read locally, and says so.
A line resting on a map summary says that instead. `_contract.read_at` is then **derived** from the
citations — every repo and commit this file actually touched — rather than asserted in advance.

## Step 5 — Capture intent where it is derivable, and only there

Behaviour alone tells the consumer *what* to consider, not *why*, and "why" is what separates
deriving from copying. Where the source shows intent — a comment, a guard's condition, a
configuration flag's name, a deliberate ordering — record it in `intent`.

**Where it does not, leave `intent` empty.** Inferred intent is the most dangerous field in this
document: it reads as authoritative and is unfalsifiable. Empty is a valid, common answer.

## Step 6 — Confidence is derived, never asserted

The consumer is a spec writer, and it needs to know which lines it may specify from directly. So
every line carries a confidence — but a hand-assigned one is a self-report, which is the thing this
skill exists to eliminate. **Compute it from the record:**

| | Condition |
|---|---|
| `high` | every citation `via: source` · both platforms read · all citations resolve |
| `medium` | at least one citation `via: map`, or only one platform has a reading |
| `low` | no `source` citation at all — the line rests on the map alone |

Same evidence always produces the same value, which is what makes it worth carrying. Add one short
`confidence_why` naming the reason for anything below `high` — the level tells the consumer to be
careful, the reason tells it what to be careful about.

```jsonc
"confidence": "medium",
"confidence_why": "android reading came from the map, not from source"
```

## Step 7 — The three honesty sections

These matter *more* for an agent consumer than a human one. A human queries a gap; an agent fills it.

**`not_derivable`** — what cannot be known, named and typed, never guessed:
`backend` (the apps only send and react) · `binary` (compiled framework, e.g. the image-processing
engine) · `needs-a-run` (in-memory or timing-dependent state) · `config` (server-supplied at runtime).
E03 produced ten of these across two features. An empty list is almost always a failure to look.

**Try `/mind` on every `backend` entry before keeping it.** That kind exists because the read stopped
at the network boundary, and that is precisely the boundary `/mind` crosses. An entry that survives a
trace is a real admission; one that was never traced is laziness wearing an honesty label.

**`do_not_copy`** — ACR behaviour that exists and should **not** be reproduced. This is the section
that makes "understand, don't copy" operational rather than aspirational, and it must be populated by
looking, not by waiting for something to be obvious. Real examples found on E03: iOS accepts only a
6–7 character kit identifier while Android accepts any length; and for a wrong kit type Android shows
an alert with **empty title, body and buttons**. Both are shipping behaviour. Both would be defects if
recreated. Record what it is, why it should not carry over, and its evidence.

**`open_behaviour`** — behaviour ACR has that the feature description never mentions. Do not skip this
because the input looked complete. On E03, 16 of 86 lines were behaviour nothing had asked for, and
the largest cluster of them was kit expiry — a whole capability believed unhandled, handled all along.
That was the single most valuable output of the pilot.

## Step 8 — Emit the contract

One file per feature. **The caller names the output path**; absent one, write
`.claude/acr-behaviour/<FEATURE>-acr-behaviour.json` in the repository the skill was invoked from.
The file is regenerated fresh on every run and is not intended to be committed.

Self-describing, because the consumer may be an agent with no context beyond this file.

```jsonc
{
  "_contract": {
    "produced_by": "acr-behaviour-reference",
    "what_this_is": "How the shipping ACR application behaves today for this feature, read from source.",
    "what_this_is_not": "A specification, a design, or a statement of what the new product should do.",
    "rules_for_the_consumer": [
      "Derive, do not copy. ACR's behaviour is evidence about a solved problem, not a requirement.",
      "Never specify anything listed in not_derivable — it is not knowable. Ask instead.",
      "Never carry over anything listed in do_not_copy.",
      "A line's `text` is the behaviour. Its `evidence` is how to verify it — not a design constraint.",
      "`intent` is recorded only where the source shows it. Empty means unknown, not absent.",
      "confidence high — specify directly from this line.",
      "confidence medium — specify, and flag in the spec that it rests on weaker evidence.",
      "confidence low — do not specify from this alone. Treat it as a question.",
      "Every citation names what it was read against. Older readings may have rotted."
    ],
    "variant": {
      "name": "Minuteful Kidney US",
      "ios_target": "Dip/TargetFiles/Acr/MinutefulKidneyUS",
      "android_flavour": "acrFda x minutefulUs",
      "out_of_scope": ["Acr/AcrUs", "acryd / acrydUs", "Minuteful (UK)", "all non-ACR flavours"]
    },
    "read_at": { "<repo>": "<commit>", "architecture-map": "<version or date>" },
    "extracted": "<ISO date>"
  },

  "feature": { "name": "...", "boundary": "from X to Y", "in_scope": [], "out_of_scope": [] },

  "scenarios": [{
    "id": "happy", "title": "...", "kind": "happy|failure|interruption|boundary",
    "lines": [{
      "id": "<feature>-<scenario>-<n>",
      "text": "one present-tense, user-visible sentence, <= 25 words",
      "ios": "what iOS does", "android": "what Android does",
      "divergence": "same|differs|ios-only|android-only",
      "intent": "why, only where the source shows it — otherwise empty",
      "confidence": "high|medium|low",
      "confidence_why": "required below high; empty at high",
      "evidence": [{
        "platform": "ios|android",
        "cite": "repo/path:line",
        "via": "source|map",
        "read_at": "<commit> | map @ <date>",
        "shows": "..."
      }]
    }]
  }],

  "user_visible_strings": [{ "where": "...", "en": "..." }],
  "not_derivable":  [{ "what": "...", "why": "...", "kind": "backend|binary|needs-a-run|config",
                       "mind_traced": true }],
  "do_not_copy":    [{ "what": "...", "why": "...", "evidence": [] }],
  "open_behaviour": [{ "what": "...", "why_it_matters": "...", "lines": [] }]
}
```

**Scenario taxonomy, fixed** so two features are comparable: `happy` · one `failure` per named failure
· `interruption` (including resume) · `boundary`. E03 ran 18 scenarios across two features.

## Step 9 — Gate it before anyone reads it

No human reviews this output, so the gate is the only thing between a wrong line and a specification.

**Mandatory — every citation resolves.** This is the check that guards truth. Run it and fix what it
reports; do not hand over a file that fails it.

```bash
python3 - "<output.json>" <<'PY'
import json, os, sys
doc = json.load(open(sys.argv[1]))
ROOT = os.path.expanduser("~/Documents/Healthy.io")   # parent of the repo checkouts
bad = []
for sc in doc["scenarios"]:
    for ln in sc["lines"]:
        for ev in ln["evidence"]:
            path, _, rng = ev["cite"].rpartition(":")
            start = int(rng.split("-")[0].split(",")[0])
            local = os.path.join(ROOT, path)
            if os.path.exists(local):
                n = sum(1 for _ in open(local, errors="ignore"))
                if start > n:
                    bad.append((ln["id"], ev["cite"], f"file has {n} lines"))
            else:
                bad.append((ln["id"], ev["cite"],
                            f"not local — verify with gh api at {ev.get('read_at','?')}"))
print("\n".join(f"  {b}" for b in bad) if bad else "all citations resolve")
PY
```

A citation the script cannot reach locally is not automatically wrong — verify it with `gh api` at
its recorded commit. A citation that resolves to a file too short for its line number is wrong.

**Also mandatory, and mechanical:**

- every line has at least one citation
- `confidence` matches the Step 6 rule for that line's evidence
- `confidence_why` is present on every line below `high`
- `_contract.read_at` lists exactly the repos and commits the citations name
- `differs` lines actually read differently on the two sides
- every `not_derivable` entry of kind `backend` records whether `/mind` was tried

**Quality, not correctness — run if a linter is available.** Line length, present tense, implementation
language in `text`, the both-platform rule. Its calibration is hard-won — do not relearn it:

- **`iOS` matches a camelCase identifier pattern.** Platform and device names are legitimate
  vocabulary and must be whitelisted; this was the first false positive it produced.
- **ALL-CAPS is not automatically a constant.** `SUPPORT` and `I HAVE A NEW KIT` are real ACR button
  labels and exactly what must survive into the output. Require an underscore before calling
  something a constant.

Then check by hand: no scenario is missing its failure cases from the alert catalogue ·
`not_derivable` is non-empty or its emptiness is defended · `do_not_copy` and `open_behaviour` were
actively looked for, not left blank by default.

---

## Anti-patterns

- **Reading a sibling flavour.** `AcrUs` and `acrydUs` are US builds and are not ACR-as-we-mean-it.
- **Asking `/mind` cold.** It cannot apply the variant lock. Follow a trace out; never start one there.
- **A line with no citation.** The entire value of this document is that it cannot be hallucinated.
- **Guessing instead of returning `not_derivable`.** The consumer cannot tell the difference, and will
  specify the guess.
- **Keeping a `backend` not-derivable without tracing it.** That is the one `/mind` was added for.
- **Asserting `confidence` by feel.** It is derived from the evidence or it is a self-report.
- **A file-level provenance block covering citations from many repositories.** It reads as a promise
  and is false for exactly the lines that came from furthest away.
- **Empty `do_not_copy` and `open_behaviour` because nothing jumped out.** They are findings you go
  looking for. Both were populated on the pilot and both changed the answer.
- **Implementation nouns in `text`.** They become requirements downstream.
- **Inferring `intent` from behaviour.** Unfalsifiable and authoritative-sounding; leave it empty.
- **One-platform lines.** Not a finding.
- **A hardcoded list of repositories.** It goes stale and is then read as fact. Ask `/mind`.
- **A subagent replying with its findings inline.** The reply dies and the work is lost.
- **Treating an atlas as source.** It is an index; a passing citation proves a line exists, not
  that it says what was claimed.

## Refinement log

Append what each run corrected, so the next feature is cheaper.

- **E03 — Kit Identification and Eligibility, 2026-08-13. The pilot this skill is derived from.**
  Two features, 18 scenarios, 86 lines, every line cited, lint 0/0, 10 platform divergences. What it
  taught, in order of value: (i) **`open_behaviour` is where the money is** — 16 of 86 lines were
  behaviour nothing had asked for, and the biggest cluster was kit expiry, which the new product
  believed was unhandled and had deferred. It was handled all along, and three days later the
  requirement was formally restored — the extraction had reconstructed it from behaviour first.
  (ii) **A prediction was wrong and the evidence corrected it** — the 24-hour re-test gate was assumed
  absent; it exists on both platforms, but it *asks* rather than *requires*: every branch ends with
  the test proceeding, it never states the window, and it runs on the device clock. "Present" and
  "enforced" are different findings. (iii) **Two shipping defects surfaced** and became the first
  `do_not_copy` entries. (iv) The extraction agents produced **no per-line intent or requirement
  hint**, forcing an entire extra cold pass over all 86 lines — hence `intent` being captured during
  extraction here, not after.
- **Output medium, 2026-08-16.** The human-facing artifact was validated in real use — the PM went
  through it comfortably — so it stays for human review, and an alternative that would have traded
  away its affordances was dropped. This skill is the **agent-facing** sibling of that work, and the
  split is deliberate: the human version hides evidence to stay readable, this one promotes evidence
  because the consumer must verify.
- **Relocation and `/mind`, 2026-08-17.** Moved out of a single project and into the shared toolkit so
  it installs on a developer's machine and runs during `/spec`. Five changes, in order of weight:
  (i) **`/mind` added, with the extends-never-starts rule** — roughly a third of ACR's cited code
  areas lie outside `iosDip` and `AndroidDip`, and the `backend` kind of `not_derivable` exists
  precisely at a boundary `/mind` crosses. (ii) **Provenance moved from the file to the citation**
  (`via` + `read_at`), because a two-commit block silently over-promises once a line comes from a
  third repository. (iii) **`confidence` kept but derived**, with a stated reason and consumer rules
  in `_contract` — the open question from the pilot, answered by making it computable rather than
  dropping it. (iv) **Citation resolution promoted to the mandatory gate** and the linter demoted to
  quality; with no human reviewer, the citation is what guards truth and the linter only guards
  shape. (v) **Local clones no longer required** — `gh api` at a pinned commit reads a repository the
  developer does not have. Open for the first run: whether `confidence_why` proves worth its width,
  and whether `mind_traced` belongs on every `not_derivable` kind or only on `backend`.
- **F01.4 — Pre-test resource and permission checks, 2026-08-19.** Called by `qacr-context`; five
  areas, 34 scenarios, 138 lines, 353 citations, 124 `high` / 14 `medium` / 0 `low`, 27 `do_not_copy`,
  42 `open_behaviour`, 28 `not_derivable` with all five `backend` entries `/mind`-traced. Five
  corrections, and the first is the one to keep.
  (i) **The reconciliation pass caught a citation that did not say what its line claimed — in this
  skill's own output.** One area asserted, at `high`, that iOS readiness alerts cannot be dismissed by
  tapping away, citing `AlertViewModel.swift:78-84`. Opened during reconciliation, that range is
  `isExistingAlertIdentical(type:)` — duplicate-alert *suppression*, not dismissal policy. Two other
  areas had independently **refused** to state the same thing. The anti-pattern "a passing citation
  proves a line exists, not that it says what was claimed" was written about a caller-supplied atlas;
  it applies just as much to a subagent's own evidence, and **the only thing that caught it was
  opening the cited line.** Reconciliation must re-read the citations behind any line where two areas
  disagree, not merely notice that they disagree.
  (ii) **Confidence must be a ceiling derived from coverage, never an assignment.** Recomputing Step 6
  mechanically first *undid* the correction in (i) (both platforms are cited, so the rule said `high`)
  and *wiped* a substantive runtime caveat on another line. Order matters: derive the coverage ceiling,
  let a substantive caveat cap it lower, apply reconciliation corrections last as authoritative.
  A content judgement is invisible to a coverage rule and must outrank it.
  (iii) **Step 6's "both platforms read" is ambiguous for an `ios-only` / `android-only` line.** The
  platform without the behaviour still gets read and its absence still gets cited. Applied here as:
  `high` when both sides carry a citation, a cited absence counting; `medium` when only one does.
  Eight lines moved to `medium` under it. Worth stating in Step 6 rather than re-deciding per run.
  (iv) **Citations come in three shapes and they do not prove equally much** — 341 line-ranges, 7
  whole-file (flow scripts and string catalogues, where line numbers carry no stable meaning), and 4
  directory-scope. A directory-scope cite backs an *absence* claim: it records where someone looked,
  not what the product does, and the absence claims it supports are the weakest lines in the document.
  The Step 9 gate script only understands `path:line` and reports the other two as unresolved — it
  needs to classify them instead of failing them.
  (v) **A sibling repo reached through SPM must be read at the pin, not at the working copy.**
  `ios-camera`'s local checkout differed from the revision `iosDip` pins by 115 insertions and 149
  deletions in the very file three lines cited; the ranges were re-read at the pin and confirmed.
  `ios-foundations` happened to be byte-identical, which is luck, not method. Take the pin from
  `Package.resolved` and cite that — and note the highest-value line in this whole extraction (iOS's
  no-internet alert being unreachable) rests on exactly such a read.
