# QACR-APP-SPEC-04 — Guided test flow engine

**RECREATION BRIEF, with one behaviour section.** The engine is a recreation. The flow it
runs is not this document's.

| | |
|---|---|
| Document | QACR-APP-SPEC-04 |
| Revision | 0.2 — draft; Rev 0.1 review answers applied, not yet re-reviewed |
| Epic | E04 Guided Test Flow Engine |
| Features covered | F04.1, F04.2, F04.3, F04.4, F04.5, F04.6, F04.7 |
| Not covered | F04.8 waiting-time card — specified in SPEC-05, because it cannot be described apart from the countdown it carries |
| Milestones | 1, except conditional steps and cancellation at 3 |
| Domains | iOS, Android |
| Traces to | QACR-APP-FR-01 Rev 1.23 · QACR-APP-EPIC-01 Rev 1.17 |

**What changed from Rev 0.1.** Six of the seven undecideds were answered at review and are
recorded in section 6. Two departures gained a row and three were rewritten. Two proposed
requirements were declined, two merged, and three moved from *raised* to *proposed* now that
the decision behind them exists. Four new undecideds opened, three of them from the review's
own answers.

---

## How to read this

**SPEC-04 recreates the chat flow engine** — how a step is presented, confirmed, retained and
resumed. Six of its seven features are recreations, and the current product is their
specification. Build them as Minuteful Kidney US behaves.

**It does not specify the flow that engine runs.** Which sections exist, in what order, what
each says, and what waits sit between them are QACR's own. The sections are built from
scratch: they are not Minuteful's seven, and there is no dipping step. Their content is E07's,
their waits are SPEC-05's, and the structure, flow logic and content are all set in the
`urine-bible` content repository.

That distinction is the whole document. The triage marks F04.1, F04.3 and F04.4 `Unchanged`
because there are no new controls or mechanics, and the review returned sixteen departures
because the flow changes throughout. Both are true of different objects. **The engine is
recreated; the flow is authored.**

This brief does not describe the engine's behaviour and must not be read as describing it. It
records what **departs**, what is **still undecided**, and which requirement each feature
answers to. One feature, F04.7, is new and has no predecessor to recreate, so it gets a
behaviour section in section 3 and nothing else does.

> **Where this brief and the current product disagree on anything not in the departures
> table, the current product is right.** Raise it rather than implementing the brief.

A brief that enumerated the engine's rules would be read as naming all of them, and a team
building to such a list would remove working capability. This document names only what
changes, and so cannot be read as a complete account of anything.

---

## 1. Scope

**In scope.** The mechanics of the guided flow: presenting one step at a time, confirming it,
holding what has been completed, surviving interruption, resuming, detecting a test that ended
without finishing, cancelling one deliberately, and the demonstration route through it. Plus
the practice scan, which is a step of the flow and exists nowhere in the predecessor.

**Out of scope.** The flow's own content and shape — see *Not in this brief*.

---

## 2. Departures from the current product

The only prescriptive part of this brief. Ten rows. Everything else across all seven features
is recreated as-is.

Four of them resolve a **platform disagreement**: where the two platforms differ today, they
record which behaviour QACR adopts. That is a product choice and belongs here. It is not the
parity question that was closed — verifying parity remains a QA activity at the end, and no
row here creates a development obligation to check one platform against the other.

| # | Feature | What changes | Driven by |
|---|---|---|---|
| **D1** | F04.1 | The flow is built from scratch. Its sections, their order and their number are QACR's own and are not the predecessor's; there is no dipping step. The engine's rules are unchanged and apply to whatever sections QACR defines. | FR-FLW-001, FR-FLW-005 |
| **D2** | F04.1 | *Platform disagreement — iOS.* The camera-permission request is presented after the explanation of it has been given, rather than after a fixed interval. | FR-RDY-009 |
| **D3** | F04.1, F04.2 | *Platform disagreement — a composition of both.* While the flow is playing, the view follows new content as it arrives, as iOS does. A user who has moved back to re-read an earlier instruction is left where they are, as Android does: the flow does not pull them away from what they are reading. | FR-FLW-004 |
| **D4** | F04.5, F04.3 | The point at which the sample is committed is the step confirming the Urine Collection Cup was used, not the dipping step. Everything that hangs off that point moves with it: what the exit warning says, and whether an absence resets the flow. | FR-STA-008, FR-STA-003 |
| **D5** | F04.5, F04.1 | The exit confirmation is not one message. It presents a message appropriate to the step it was invoked from — before the cup was used, and after — rather than a single warning for both. | FR-STA-008 |
| **D6** | F04.3 | *Platform disagreement — iOS.* Transmission of a captured test continues after the user leaves the application. Nothing is shown to the user about it, then or on return. | FR-STA-005 |
| **D7** | F04.3 | *Platform disagreement — iOS.* Once a timeout has been presented and dismissed, the absence window applies again from that moment. It does not stop applying for the rest of the run. | FR-STA-003 |
| **D8** | F04.4 | A recorded timeout survives the application dying. The user is shown the failure and continues into the troubleshooting flow. If the application was killed before the failure was presented, the user opens at the start-up state and is shown the failure there. | FR-STA-007, FR-TIM-012 |
| **D9** | F04.6 | The demonstration route advances to a chosen section of the flow, and also to the end of the current section, so that bubbles, audio and timers can be passed over. It may advance past anything the chat presents. | FR-FLW-007 |
| **D10** | F04.2 | An instruction video opens full screen. This is already how the QACR usability application behaves and it differs from the predecessor. | FR-FLW-002 |

**On D9 and the timing requirements.** FR-TIM-008 prevents progression past a time-dependent
stage before the minimum time has elapsed, and admits no exemption. The demonstration route
crosses it. There is no clinical conflict — a demonstration produces no result for a real
patient, so no assay timing is being defeated — but the requirement as written does not say
so, and that is a requirement to amend rather than a rule to bend in a spec. See section 5.

---

## 3. Behaviour — F04.7 Scan practice

The one feature here with no predecessor. What follows describes the **practice framing** — where
it sits, how it ends, and what it does not do. The scanning interaction it reproduces is E06's
and is deliberately not described here; the point of a practice scan is that the user meets
that interaction unchanged.

**S04.01** A practice scan is a step of the flow, not an optional detour. It occurs during a
timed waiting period, and the user passes through it in order to continue.

**S04.02** A practice scan presents the scanning interaction as a real scan does. Where the two
would differ, they do not: a user who struggles in practice is meeting the same difficulty they
would meet in the real scan, which is the reason for putting it there.

**S04.03** The scanning window that governs a real scan does not apply to a practice scan.

**S04.04** A practice scan that runs on past the end of the wait it began in has no consequence
for the assay. Whether it ends with that wait or continues under a longer limit of its own is
undecided — see U1.

**S04.05** A practice scan produces nothing. No result, no image on the test record, no kit
registered as used. A user who practises on the kit they are about to test with has not spent
it.

**S04.06** A user can tell throughout that they are practising, so that nobody leaves a
practice scan believing they have already scanned. How that distinction is made visible is a
design decision.

**S04.07** A practice scan occurs only within a wait long enough to accommodate one. Which
waits qualify, and how long they are, is SPEC-05's.

*Traces: FR-IMG-022.*

The requirement is milestone 1; the identifier-template validation it inherits arrives at
milestone 3 with FR-KIT-003, and the used-kit check with FR-KIT-004. S04.05 is what keeps the
second of those harmless in practice.

**S04.01 and S04.04 both depart from FR-IMG-022 as written**, which *allows* the user to start
a practice scan and requires it to *end when the waiting period ends*. Neither is a licence
this brief can grant itself; both are in section 5 as amendments.

---

## 4. Still undecided

| # | Question | Owner |
|---|---|---|
| **U1** | Whether a practice scan ends with the wait it began in, or continues under a longer limit of its own. Settled at review: either way there is no consequence for the assay. Amends FR-IMG-022, which currently requires the first. | Guy |
| **U2** | The absence allowance that applies on the doctor-notification stage, which differs from the one applying elsewhere. **The development team is asked for the context first**; the decision is Guy's after that. | Developers, then Guy |
| **U3** | Whether an abandoned test's captured images can reach analysis in the current product. Guy has decided they must not, and expects this already to be how the predecessor behaves; the behaviour review reports the opposite — that a part-captured test resumes transmitting at the next start and can reach a result. **The decision is not in doubt; how much of it is a change is.** | Research, then Guy |
| **U4** | Whether retained test state must survive an application update. The review answer was *"ok, same as ACR"*, and the two halves point opposite ways: the review reports that on one platform an update removes everything saved. One word settles it — is this a new obligation or a recreation? | Guy |

---

## 5. Requirements proposed

The developers' behaviour review offered fourteen candidate requirements, read against FR
Rev 1.20. **Re-mapped against Rev 1.23, every gap they report still stands**: of the seventeen
requirements this document owes, none changed text between those revisions, and the three
requirements added since — FR-KIT-008, FR-KIT-009, FR-KIT-010 — close none of them. The one
requirement in the neighbourhood that did change is FR-KIT-007, which no longer presents *an
alert stating that a new kit is required*.

**Propose, never edit.** Most of these are amendments to requirements that already exist
rather than new identifiers, and are proposed as such: reach for a new identifier only where
the milestones differ.

### 5.1 Proposed

| Amends or adds | What it would say | Proposed milestone | Where it came from |
|---|---|---|---|
| FR-STA-003 | Define the point at which a test becomes active — the user activating the start-test control — and state the reset that applies outside it. The prohibition on an inactivity timeout during a test says nothing about when a test begins, and a reset does apply before that point. | 1 | D4, U2 |
| FR-FLW-004 | Completed instructions remain available to the user while the flow continues. The flow follows new content as it arrives, and does not move the user's view away from an earlier instruction they have moved back to read. | 1 | D3 |
| FR-FLW-008 | Speech and any demonstration in progress stop when the user confirms a step or the application leaves the foreground, and neither resumes by itself. | 1 | Observation; both platforms already do it |
| New, FLW | Each element of the flow is presented after a defined interval, and where an element carries recorded audio that interval is the audio's duration. The same on both platforms. **The interval is the engine's and holds wherever the content comes from**, so it is not deferred to the content set. | 1 | D2, and the pacing of the wait |
| New, STA | The screen is prevented from dimming or locking while the flow is displayed. | 1 | Observation; no requirement asks for it |
| FR-FLW-007 | Demonstration mode is evident within the flow, and the demonstration route may advance past anything the chat presents, including timing windows and confirmation steps. **This is the exemption FR-TIM-008 does not currently admit**, and it is safe because a demonstration produces no result for a real patient. | 1 | D9 |
| FR-FLW-006 | Every parameter governing the inclusion or omission of a section has a value applied when it is not supplied: the default held in the application where one exists, and where none exists the software reports the condition rather than proceeding silently. | 3 | Review answer |
| FR-IMG-022 | A practice scan is a step of the flow the user passes through rather than one they may start; and the limit that ends it is its own rather than the wait's. | 1 | S04.01, S04.04, U1 |
| FR-STA-007 | Data captured for a test that is invalidated on reopening is discarded, the invalidation is reported, and a result later returned for that test is not presented. **The decision is made: an abandoned test's images are not analysed.** Whether this is new or a recreation is U3. | 1 | Review answer |
| FR-KIT-007 | The message is presented on every attempt within the window until the user confirms it, and the confirmation closes the window. | 3 | Review answer |

**On FR-FLW-006.** FR-CFG-002 already requires that *where a retrieved and valid set does not
supply an individual value, the software shall apply the default defined in the application for
that value*, and it did so at Rev 1.20 too. The first half of this proposal is therefore
already carried if a flow parameter is a configuration value. **The second half is not carried
anywhere**: no requirement says what happens when no default exists, and the review's answer is
that the software reports the condition. That is the part worth writing.

**On FR-KIT-007.** The review's answer is a third behaviour, and cleaner than either reading
that preceded it. Today the message is shown once and the window keeps running without it; the
candidate requirement said the message must be shown on every attempt regardless. Neither is
what is wanted: **the confirmation ends the window rather than merely suppressing the message.**
A user who confirms they hold a new kit is not asked again, and is not silently inside a window
whose only signal has been switched off.

### 5.2 Raised, not yet proposed

Three candidates rest **entirely** on behaviours marked `correct` at review — meaning the
current behaviour is what QACR should do — while each describes a requirement the product does
not carry. Under the review's own rule they should be dropped. They are recorded rather than
dropped because for a Class B submission an unstated capability is a gap rather than a
preference. **This is a decision, not a defect to fix here.**

| Amends | What it would say | Proposed milestone |
|---|---|---|
| FR-STA-007 | Something is written down at the point a test becomes active by which an incomplete test can be identified on reopening, and it is examined before the start-up state is presented. | 1 |
| FR-STA-002 | Flow content is not delivered while the application is not in the foreground, and on return delivery resumes from the point reached. | 1 |
| FR-STA-003 | Retained state survives an application update, and where it cannot be read back the user is told a test could not be recovered rather than shown the start-up state. **Held pending U4.** | 1 |

### 5.3 Declined at review

Recorded so that they are not proposed again by the next reader of the same export.

| What was proposed | Why not |
|---|---|
| New, COM — the user is told when a transmission has not completed, and told when it does | Transmission finishes silently in the background and the user does not need to be aware, as today. Consistent with the same answer already recorded in SPEC-01. |
| FR-STA-007 — the user is told that data was discarded and a new kit is required | Already carried. The requirement tells the user the test is invalid and a new kit is required; nothing needs adding to it. |
| FR-FLW-007 — the requirement enumerates which timing windows and confirmation steps the demonstration route does not apply | The demonstration route may affect the whole chat, so there is no list to state. Replaced by the general permission in section 5.1. |
| FR-TXT-004 — the flow's intervals are part of the versioned content set, at milestone 3 | The timing of bubbles is part of the chat engine and belongs at milestone 1, and it holds wherever the text comes from. Merged into the FLW row in section 5.1. |

### 5.4 A capability to exclude explicitly

Nothing found here. Recorded so that the absence is a finding rather than an omission.

---

## 6. Answered at review

### 6.1 Undecideds closed at the Rev 0.1 review

| Was | Answer | Where it went |
|---|---|---|
| U1 · what the video UX changes are | The video opens full screen. Already the QACR usability application's behaviour, and it differs from the predecessor. | **D10** |
| U2 · a missing section parameter | Fall back to a default held in the application where one exists; where none exists, report the condition. | FR-FLW-006 proposal, section 5.1 |
| U4 · a timeout recorded before the application died | A recorded timeout survives. The user sees the failure and continues into the troubleshooting flow; if the application was killed first, the failure is shown at the start-up state on reopening. | **D8** |
| U5 · whether D2 sits with FR-RDY-013 | **No conflict.** Where the platform offers a further attempt at the permission, it is offered; normally it does not, and the route is the phone's settings. That is what FR-RDY-013 already requires — a retry where retrying resolves it, and otherwise only the route that applies. | Closed. D2 narrowed to the pacing question |
| U6 · fast-forwarding past a wait and its audio | In scope, for demonstration partners only. The fast-forward and skip-to-section controls may skip all timing windows; no real result is produced, so assay timing is unaffected. | **D9**, and the FR-FLW-007 proposal |
| U7 · who owns the QACR section list | The `urine-bible` content repository, along with the whole structure, flow logic and content of the chat flow. | Closed. *Not in this brief* |

### 6.2 Confirmed as-is

Each of these was put to review and the answer was that the current product's behaviour
stands. They are recorded because otherwise the next reader asks them again. This is not a list
of everything that is unchanged — it is the list of what was asked.

| Question | Answer |
|---|---|
| Do the parameters that decide what the flow opens with carry over? | **Yes, as today.** Only what happens when one is missing changes. |
| Does the confirmation model change? | **No.** One step, one control, nothing advancing without it. |
| Does a call, a notification, a screen lock or backgrounding end a test? | **No**, as today. What the app switcher shows is also unchanged. |
| What happens when the application is killed mid-test? | **As today**, including where the user lands, what survives, and that the absence reset stops applying once the sample is committed. |
| What happens when retained state cannot be read back? | **As today.** U4 asks only about an application update. |
| What happens when the device clock is moved? | **As today.** |
| Does the used-kit gate change? | **No.** Its content does — that is E07's, not a departure here. |
| Is the user told a transmission is still finishing? | **No.** It completes silently in the background, as today. |
| Is every instruction video replayable? | **No, and that is correct.** FR-FLW-003 already reads *where the demonstration for a step is designated replayable*; which steps those are is defined per step in the content set. The transcript, not the replay control, is what lets a user return to a text instruction. |

---

## 7. Traceability

Every requirement owed by a covered feature, and its disposition. `as-is` means the current
product is the specification and there is nothing to design.

| Feature | Requirements | Disposition |
|---|---|---|
| F04.1 Step sequencer and confirmation model | FR-FLW-001, FR-FLW-004, FR-FLW-005, FR-FLW-006 (M3) | as-is except **D1, D2, D3, D5** |
| F04.2 Instruction media, replay and spoken delivery | FR-FLW-002, FR-FLW-003, FR-FLW-008 | as-is except **D3, D10** |
| F04.3 State retention and interruption tolerance | FR-STA-002, FR-STA-003, FR-STA-005 | as-is except **D4, D6, D7** · U2, U4 open |
| F04.4 Termination detection and invalidation | FR-STA-006, FR-STA-007 | as-is except **D8** · U3 open |
| F04.5 Cancellation | FR-STA-008 (M3), FR-STA-009 (M3), FR-STA-010 (M3) | as-is except **D4, D5** |
| F04.6 Demonstration navigation | FR-FLW-007 | as-is except **D9** |
| F04.7 Scan practice | FR-IMG-022 | **New** — section 3 · U1 open |

F04.5 is triaged `Changed`, and the change is D4: the committed-sample point. FR-STA-008
already places the cancellation cut-off at cup fill, so the requirement does not move; what
moves is which step in the QACR flow that is.

---

## 8. Not in this brief

**The flow itself.** Which sections exist, in what order, and how many — together with the
structure, flow logic and content of the chat flow. All of it is set in `urine-bible`.

**Content, copy and media.** E07's. No spec states, constrains or enforces user-facing
wording, and none quotes it.

**Timed waits and the waiting-time card.** SPEC-05's, which also carries F04.8. Where this
document names a wait it names it as a boundary, never as a duration.

**The scanning interaction.** E06's. Section 3 describes the practice framing around it and
deliberately not the interaction itself.

Behaviour lives in the current product. What must be true lives in QACR-APP-FR-01. Waits live
in SPEC-05. Wording and flow structure live in the content set.

Seven features, ten departures, seven statements. Six recreations and one thing that did not
exist before.
