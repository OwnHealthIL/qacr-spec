# QACR-APP-SPEC-04 — Guided test flow engine

**RECREATION BRIEF, with one behaviour section.** The engine is a recreation. The flow it
runs is not this document's.

| | |
|---|---|
| Document | QACR-APP-SPEC-04 |
| Revision | 1.1 — **ready**. Reviewed and settled; build from it. |
| Epic | E04 Guided Test Flow Engine |
| Features covered | F04.1, F04.2, F04.3, F04.4, F04.5, F04.6, F04.7 |
| Not covered | F04.8 waiting-time card — specified in SPEC-05, because it cannot be described apart from the countdown it carries |
| Milestones | 1, except conditional steps and cancellation at 3 |
| Domains | iOS, Android |
| Traces to | QACR-APP-FR-01 Rev 1.24 · QACR-APP-EPIC-01 Rev 1.18 |

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

The only prescriptive part of this brief. Twelve rows. Everything else across all seven features
is recreated as-is.

Four of them resolve a **platform disagreement**, and all four resolve it the same way: where
the two platforms differ today, QACR takes iOS's behaviour. That is a product choice and
belongs here. It is not the parity question that was closed — verifying parity remains a QA
activity at the end, and no row here creates a development obligation to check one platform
against the other.

| # | Feature | What changes | Driven by |
|---|---|---|---|
| **D1** | F04.1 | The flow is built from scratch. Its sections, their order and their number are QACR's own and are not the predecessor's; there is no dipping step. The engine's rules are unchanged and apply to whatever sections QACR defines. | FR-FLW-001, FR-FLW-005 |
| **D2** | F04.1 | *Platform disagreement — iOS.* The camera-permission request is presented after the explanation of it has been given, rather than after a fixed interval. | FR-RDY-009 |
| **D3** | F04.1, F04.2 | *Platform disagreement — iOS.* While the flow is playing, the view is carried to each new bubble as it is displayed. There is no exception for a user who has moved back through the transcript. The transcript itself remains available; it is the view that follows the flow. | FR-FLW-004 |
| **D4** | F04.5, F04.3 | The point at which the sample is committed is the step confirming the Urine Collection Cup was used, not the dipping step. Everything that hangs off that point moves with it: what the exit warning says, and whether an absence triggers the UI reset. | FR-STA-008, FR-STA-003 |
| **D5** | F04.5, F04.1 | The exit confirmation is not one message. It presents a message appropriate to the step it was invoked from — before the cup was used, and after — rather than a single warning for both. | FR-STA-008 |
| **D6** | F04.3 | *Platform disagreement — iOS.* Transmission of a captured test continues after the user leaves the application. Nothing is shown to the user about it, then or on return. | FR-STA-005 |
| **D7** | F04.3 | *Platform disagreement — iOS.* Once a timeout has been presented and dismissed, the absence window applies again from that moment. It does not stop applying for the rest of the run. | FR-STA-003 |
| **D8** | F04.4 | A recorded timeout survives the application dying. The user is shown the failure and continues into the troubleshooting flow. If the application was killed before the failure was presented, the user opens at the start-up state and is shown the failure there. | FR-STA-007, FR-TIM-012 |
| **D9** | F04.6 | The demonstration route provides **two controls**, not one: a navigator that moves between sections of the flow, and a fast-forward that runs to the end of the current section. Between them they may pass over any bubble, any audio and any timer the chat presents. | FR-FLW-007 |
| **D10** | F04.2 | An instruction video opens full screen. This is already how the QACR usability application behaves and it differs from the predecessor. | FR-FLW-002 |
| **D11** | F04.6 | **Demonstration mode is determined in the build at milestone 1**, and by configuration retrieved before a test starts **from milestone 2**, where it will carry more than demonstration. The predecessor determines it from the backend throughout; the QACR application has no configuration channel yet. | FR-FLW-007 |
| **D12** | F04.2 | A silenced flow stays silent **for the current test session** and no longer. The predecessor remembers the choice across tests. | FR-FLW-008 |

**On D9 and the timing requirements.** Both demonstration controls cross a time-dependent stage.
There is no clinical conflict — a demonstration produces no result for a real patient, so no assay timing is being defeated — but the requirement as written does not say so,
so FR-TIM-008 was amended at FR Rev 1.24 to admit it. A demonstration produces no result for a patient.

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

**S04.04** A practice scan ends on a limit of its own, not on the end of the wait it began in. It
may run past that wait, and doing so has no consequence for the assay. The length of that limit is
a value to be set, with the other timing values.

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

FR-IMG-022 was amended at FR Rev 1.24 to say both of these: the practice scan is a step of the
flow the user passes through, and it ends on a limit of its own rather than on the end of the
wait. **The document and the requirement agree.**

---

## 4. Still undecided

**Both of these are questions the development team has to answer before Guy can.** They are facts
about the current product, not decisions, and putting them to Guy first is what stalled each of
them at least once. Nothing in this document waits on either.

**The numbering starts at U2 on purpose.** U1 closed at Rev 1.1 and the survivors keep the
identifiers they were reviewed under. Renumbering an open-item list is what produced three of the
four defects the development team found in Rev 1.0 — a reference to a `U4` that no longer existed,
and two rows describing the wrong question. **Identifiers here are not renumbered when one
closes.**

| # | Question | Owner |
|---|---|---|
| **U2** | The absence allowance that applies on the doctor-notification stage, which differs from the one applying elsewhere. **What that stage is and why its allowance differs is the developers' to explain**; the decision is Guy's after that. | Developers, then Guy |
| **U3** | What the two current behaviours actually amount to when a parameter governing the inclusion or omission of a section is not supplied — **what an alternative section is, and what a user meets when a section drops entirely.** The developers' to establish first; the decision is Guy's after that. Behaviour is as the current product's and no requirement changes, but *same as today* does not pick between two different things, and one of them is how a section that is required to exist stops being presented. | Developers, then Guy |

---

## 5. Answered at review

### 5.1 Questions closed

| Was | Answer | Where it went |
|---|---|---|
| whether a practice scan ends with its wait, or under a limit of its own | **A limit of its own.** It may run past the wait it began in with no consequence for the assay. FR-IMG-022 was amended at FR Rev 1.24 to require it, so the requirement and S04.04 agree. The length of the limit is a value to be set. | Closed |
| what the video UX changes are | The video opens full screen. Already the QACR usability application's behaviour, and it differs from the predecessor. | **D10** |
| a timeout recorded before the application died | A recorded timeout survives. The user sees the failure and continues into the troubleshooting flow; if the application was killed first, the failure is shown at the start-up state on reopening. | **D8** |
| whether D2 sits with FR-RDY-013 | **No conflict.** Where the platform offers a further attempt at the permission, it is offered; normally it does not, and the route is the phone's settings. That is what FR-RDY-013 already requires — a retry where retrying resolves it, and otherwise only the route that applies. | Closed |
| fast-forwarding past a wait and its audio | In scope, for demonstration partners only, and as **two** controls rather than one. They may skip all timing windows; no real result is produced, so assay timing is unaffected. | **D9** |
| who owns the QACR section list | The `urine-bible` content repository, along with the whole structure, flow logic and content of the chat flow. | Closed |
| whether retained state must survive an application update | **It already does**, on both platforms. The wipe that exists on one is opt-in per release rather than a consequence of updating, and has never been used on this variant. Where stored data is discarded the user is not told, and that is to stay as it is. | Closed |
| which requirement delivers configuration at milestone 2 | The configuration channel moves to milestone 2, where it stops being demonstration-only and carries a real test partner. Milestone 1 may determine demonstration mode in the build. **Milestone moves authorised**, SPEC-01's re-issue included. | Closed |
| whether an abandoned test's images can reach analysis | **The case was misread, and the line is now drawn.** A capture that succeeded and awaits only transmission is not an abandoned test: it and its images wait to be sent, the software keeps trying across a kill, and the test reaches a result — as today, and the mechanism is not to be touched. Invalidation is what happens when the capture *failed*. | Closed |

### 5.2 Confirmed as-is

Each of these was put to review and the answer was that the current product's behaviour
stands. They are recorded because otherwise the next reader asks them again. This is not a list
of everything that is unchanged — it is the list of what was asked.

| Question | Answer |
|---|---|
| Do the parameters that decide what the flow opens with carry over? | **Yes, as today.** U3 asks only which of two current behaviours applies when one is missing. |
| Does the confirmation model change? | **No.** One step, one control, nothing advancing without it. |
| Does a call, a notification, a screen lock or backgrounding end a test? | **No**, as today. What the app switcher shows is also unchanged. |
| What happens when the application is killed mid-test? | **As today**, including where the user lands, what survives, and that the UI reset stops applying once the sample is committed. |
| What happens to a test the application never finished sending? | **It depends on whether the capture succeeded, and this is the line to build to.** Where the capture succeeded and only transmission remains, the exam and its images sit waiting to be transmitted; the software goes on trying across a kill and a reopen, and the test reaches a result. As today, and the mechanism is not to be touched. **Where the capture itself failed, the software invalidates the test.** |
| What happens when retained state cannot be read back? | **As today.** The application-update case was asked and closed at review — see 5.1. |
| What happens when the device clock is moved? | **As today.** |
| Does the used-kit gate change? | **No.** Its content does — that is E07's, not a departure here. |
| Is the user told before a demonstration run begins? | **Yes, as today.** The predecessor presents a disclaimer before the test starts when demonstration mode is on, and QACR keeps it. So the mode being evident is a recreation, not something to require. |
| Is the user told a transmission is still finishing? | **No.** It completes silently in the background, as today. |
| Is every instruction video replayable? | **No, and that is correct.** FR-FLW-003 already reads *where the demonstration for a step is designated replayable*; which steps those are is defined per step in the content set. The transcript is what lets a user return to a text instruction. |

---

## 6. Traceability

Every requirement owed by a covered feature, and its disposition. `as-is` means the current
product is the specification and there is nothing to design.

| Feature | Requirements | Disposition |
|---|---|---|
| F04.1 Step sequencer and confirmation model | FR-FLW-001, FR-FLW-004, FR-FLW-005, FR-FLW-006 (M3) | as-is except **D1, D2, D3, D5** · U3 open |
| F04.2 Instruction media, replay and spoken delivery | FR-FLW-002, FR-FLW-003, FR-FLW-008, FR-FLW-010 | as-is except **D3, D10, D12** |
| F04.3 State retention and interruption tolerance | FR-STA-002, FR-STA-003, FR-STA-005, FR-STA-012 | as-is except **D4, D6, D7** · U2 open |
| F04.4 Termination detection and invalidation | FR-STA-006, FR-STA-007 | as-is except **D8** |
| F04.5 Cancellation | FR-STA-008 (M3), FR-STA-009 (M3), FR-STA-010 (M3) | as-is except **D4, D5** |
| F04.6 Demonstration navigation | FR-FLW-007 | as-is except **D9, D11** |
| F04.7 Scan practice | FR-IMG-022 | **New** — section 3 |

**FR-FLW-010 and FR-STA-012 were added at FR Rev 1.24**, out of this document's own sweep:
the pace at which the flow presents each element, and keeping the screen awake while it is
displayed. Both are capabilities the current product already has and no requirement asked for,
so both are recreations like everything else here and neither is a departure.

F04.5 is triaged `Changed`, and the change is D4: the committed-sample point. FR-STA-008
already places the cancellation cut-off at cup fill, so the requirement does not move; what
moves is which step in the QACR flow that is.

---

## 7. Not in this brief

**The flow itself.** Which sections exist, in what order, and how many — together with the
structure, flow logic and content of the chat flow. All of it is set in `urine-bible`.

**Content, copy and media.** E07's. No spec states, constrains or enforces user-facing
wording, and none quotes it.

**Timed waits and the waiting-time card.** SPEC-05's, which also carries F04.8. Where this
document names a wait it names it as a boundary, never as a duration.

**The scanning interaction.** E06's. Section 3 describes the practice framing around it and
deliberately not the interaction itself.

**The transmission mechanism.** Unchanged, and deliberately untouched by this brief.

Behaviour lives in the current product. What must be true lives in QACR-APP-FR-01. Waits live
in SPEC-05. Wording and flow structure live in the content set.

Seven features, twelve departures, seven statements. Six recreations and one thing that did not
exist before.
