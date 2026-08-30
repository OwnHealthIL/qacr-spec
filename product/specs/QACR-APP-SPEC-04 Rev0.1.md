# QACR-APP-SPEC-04 — Guided test flow engine

**RECREATION BRIEF, with one behaviour section.** The engine is a recreation. The flow it
runs is not this document's.

| | |
|---|---|
| Document | QACR-APP-SPEC-04 |
| Revision | 0.1 — draft for review; not yet reviewed |
| Epic | E04 Guided Test Flow Engine |
| Features covered | F04.1, F04.2, F04.3, F04.4, F04.5, F04.6, F04.7 |
| Not covered | F04.8 waiting-time card — specified in SPEC-05, because it cannot be described apart from the countdown it carries |
| Milestones | 1, except conditional steps and cancellation at 3 |
| Domains | iOS, Android |
| Traces to | QACR-APP-FR-01 Rev 1.23 · QACR-APP-EPIC-01 Rev 1.17 |

---

## How to read this

**SPEC-04 recreates the chat flow engine** — how a step is presented, confirmed, retained and
resumed. Six of its seven features are recreations, and the current product is their
specification. Build them as Minuteful Kidney US behaves.

**It does not specify the flow that engine runs.** Which sections exist, in what order, what
each says, and what waits sit between them are QACR's own. The sections are built from
scratch: they are not Minuteful's seven, and there is no dipping step. Their content is E07's
and their waits are SPEC-05's.

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
the practice scan, which is offered from inside the flow and exists nowhere in the predecessor.

**Out of scope.** The flow's own content and shape — see *Not in this brief*.

---

## 2. Departures from the current product

The only prescriptive part of this brief. Nine rows. Everything else across all seven features
is recreated as-is.

Four of them are **parity directions**: where the two platforms disagree today, they record
which behaviour QACR adopts. That is a product choice and belongs here. It is not the parity
question that was closed — verifying parity remains a QA activity at the end, and no row here
creates a development obligation to check one platform against the other.

| # | Feature | What changes | Driven by |
|---|---|---|---|
| **D1** | F04.1 | The flow is built from scratch. Its sections, their order and their number are QACR's own and are not the predecessor's; there is no dipping step. The engine's rules are unchanged and apply to whatever sections QACR defines. | FR-FLW-001, FR-FLW-005 |
| **D2** | F04.1 | *Parity direction — iOS.* Where the two platforms differ in the camera-permission step, QACR follows iOS: both in the route offered when permission is refused, and in the request being presented after the explanation of it has been given rather than after a fixed interval. **See U5 — this may need FR-RDY-013 amended.** | FR-RDY-009, FR-RDY-013 |
| **D3** | F04.1, F04.2 | *Parity direction — Android.* A user who scrolls back to re-read an earlier instruction is left where they are. The flow does not move their view away from what they are reading in order to show something newer. | FR-FLW-004 |
| **D4** | F04.5, F04.3 | The point at which the sample is committed is the step confirming the Urine Collection Cup was used, not the dipping step. Everything that hangs off that point moves with it: what the exit warning says, and whether an absence resets the flow. | FR-STA-008, FR-STA-003 |
| **D5** | F04.5, F04.1 | The exit confirmation is not one message. It presents a message appropriate to the step it was invoked from — before the cup was used, and after — rather than a single warning for both. | FR-STA-008 |
| **D6** | F04.3 | *Parity direction — iOS.* Transmission of a captured test continues after the user leaves the application. | FR-STA-005 |
| **D7** | F04.3 | *Parity direction — iOS.* Once a timeout has been presented and dismissed, the absence window applies again from that moment. It does not stop applying for the rest of the run. | FR-STA-003 |
| **D8** | F04.4 | A timeout recorded while the application was running must reach the user. If it was recorded but not yet presented when the application died, it is presented when the application is reopened. If it was presented and the application then died, the user returns to the start-up state. **Research attached — see U4.** | FR-STA-007, FR-TIM-012 |
| **D9** | F04.6 | The demonstration control advances to a chosen section of the flow, not only to the end of it. | FR-FLW-007 |

---

## 3. Behaviour — F04.7 Scan practice

The one feature here with no predecessor. What follows describes the **practice framing** — when
it is offered, how it ends, and what it does not do. The scanning interaction it reproduces is
E06's and is deliberately not described here; the point of a practice scan is that the user
meets that interaction unchanged.

**S04.01** A practice scan is offered from within the instructional flow during a timed wait,
as something the user may do rather than must. Declining it has no effect on the test and no
consequence the user has to recover from.

**S04.02** A practice scan presents the scanning interaction as a real scan does. Where the two
would differ, they do not: a user who struggles in practice is meeting the same difficulty they
would meet in the real scan, which is the reason for offering it.

**S04.03** The scanning window that governs a real scan does not apply to a practice scan. The
user may take as long as the wait allows.

**S04.04** A practice scan ends when the wait during which it was started ends, finished or
not, and returns the user to the flow at the point the wait has reached. It never holds the
flow back.

**S04.05** A practice scan produces nothing. No result, no image on the test record, no kit
registered as used. A user who practises on the kit they are about to test with has not spent
it.

**S04.06** A user can tell throughout that they are practising, so that nobody leaves a
practice scan believing they have already scanned. How that distinction is made visible is a
design decision.

**S04.07** A practice scan is offered only during a wait long enough to accommodate one.
Which waits qualify, and how long they are, is SPEC-05's.

*Traces: FR-IMG-022.*

The requirement is milestone 1; the identifier-template validation it inherits arrives at
milestone 3 with FR-KIT-003, and the used-kit check with FR-KIT-004. S04.05 is what keeps the
second of those harmless in practice.

---

## 4. Still undecided

| # | Question | Owner |
|---|---|---|
| **U1** | What the changes to the video UX are. The triage records that they are small and that they belong in this document; nothing states what they are, and no behaviour can be written for F04.2 until they are. | Guy |
| **U2** | What the software does when a parameter governing the inclusion or omission of a section is not supplied. Today the two platforms answer differently. Raised at review as an open question rather than a decision. **See also the proposal register — FR-CFG-002 may already answer this.** | Guy |
| **U3** | The absence allowance that applies on the doctor-notification stage, which differs from the one applying elsewhere. Raised at review as needing more context. | Guy |
| **U4** | What the current product does when a timeout is recorded and the application dies before it is presented. D8 states the intent and does not rest on the answer, but the answer decides how much of D8 is a change. | Research, then Guy |
| **U5** | Whether D2 is consistent with FR-RDY-013, which requires a retry to be offered where retrying can resolve the condition. Where the operating system still permits a second request, retrying can resolve it — which is the behaviour D2 declines in favour of the other platform's route. Either the requirement needs amending or the route to Settings is the applicable route to resolution. | Guy |
| **U6** | Whether fast-forwarding past a wait and its audio is in scope, and if so which timing windows it may skip. FR-TIM-008 admits no exemption from a minimum duration. **This is new scope with no requirement and no owner.** | Guy |
| **U7** | Which document owns the QACR section list and its order. It is out of this brief by decision, and nothing else currently carries it. | Guy |

---

## 5. Confirmed as-is at review

Each of these was put to review and the answer was that the current product's behaviour
stands. They are recorded because otherwise the next reader asks them again. This is not a
list of everything that is unchanged — it is the list of what was asked.

| Question | Answer |
|---|---|
| Do the parameters that decide what the flow opens with carry over? | **Yes, as today**, for now. What they are is unchanged; U2 covers only what happens when one is missing. |
| Does the confirmation model change? | **No.** One step, one control, nothing advancing without it. |
| Does a call, a notification, a screen lock or backgrounding end a test? | **No**, as today. What the app switcher shows is also unchanged. |
| What happens when the application is killed mid-test? | **As today**, including where the user lands, what survives, and that the absence reset stops applying once the sample is committed. |
| What happens when retained state cannot be read back? | **As today.** |
| What happens when the device clock is moved? | **As today.** |
| Does the used-kit gate change? | **No.** Its content does — that is E07's, not a departure here. |
| Is every instruction video replayable? | **No, and that is correct.** FR-FLW-003 already reads *where the demonstration for a step is designated replayable*; which steps those are is defined per step in the content set. The transcript, not the replay control, is what lets a user return to a text instruction. |

---

## 6. Requirements proposed

The developers' behaviour review offered fourteen candidate requirements, read against FR
Rev 1.20. **Re-mapped against Rev 1.23, every gap they report still stands**: of the seventeen
requirements this document owes, none changed text between those revisions, and the three
requirements added since — FR-KIT-008, FR-KIT-009, FR-KIT-010 — close none of them. The one
requirement in the neighbourhood that did change is FR-KIT-007, which no longer presents *an
alert stating that a new kit is required*, so the candidate written against that wording needs
rewording before it can be considered.

**Propose, never edit.** Nine of the fourteen are amendments to requirements that already
exist rather than new identifiers, and are proposed as such: reach for a new identifier only
where the milestones differ.

### 6.1 Earned by a departure — propose these

| Amends or adds | What it would say | Proposed milestone | Where it came from |
|---|---|---|---|
| FR-STA-003 | Define the point at which a test becomes active, and state the reset that applies outside it. The prohibition on an inactivity timeout during a test says nothing about when a test begins, and a reset does apply before that point. | 1 | D4, U3 |
| FR-FLW-004 | Completed instructions remain available to the user while the flow continues, and the flow does not move the user's view away from what they are reading. | 1 | D3 |
| FR-FLW-008 | Speech and any demonstration in progress stop when the user confirms a step or the application leaves the foreground, and neither resumes by itself. | 1 | Observation; both platforms already do it |
| New, FLW | Each element of the flow is presented after a defined interval, and where an element carries recorded audio that interval is the audio's duration. The same on both platforms. | 1 | D2, and the pacing of the wait |
| FR-TXT-004 | The intervals above are part of the versioned content set. | 3 | Follows FR-TXT-004's own milestone |
| New, STA | The screen is prevented from dimming or locking while the flow is displayed. | 1 | Observation; no requirement asks for it |
| New, COM | Where a transmission has not completed, the user is told when the application is next brought to the foreground, and told when it completes. | 3 | D6 |
| FR-FLW-007 | Demonstration mode is evident within the flow, and the requirement states which timing windows and confirmation steps do not apply in it. **Needs reconciling with FR-TIM-008, which admits none.** | 1 | D9, U6 |
| FR-FLW-006 | Every parameter governing the inclusion or omission of a section has a value applied when it is not supplied, and the same value on every platform. | 3 | U2 |

**On the last row.** FR-CFG-002 already requires that *where a retrieved and valid set does not
supply an individual value, the software shall apply the default defined in the application for
that value* — and it did so at Rev 1.20 too, so this is not a revision the review missed but an
existing requirement it did not reach. **If a flow parameter is a configuration value, U2 is
already answered and no amendment is needed.** That is the question to settle before proposing
anything.

The two audio rows are split deliberately. The pacing rule is needed at milestone 1, because
the flow is built then; putting it in the content set alone would leave a milestone-1
obligation resting on a milestone-3 requirement.

### 6.2 Raised, but the behaviour they rest on was marked correct

Five further candidates, plus two more, rest **entirely** on behaviours marked `correct` at
review — meaning the current behaviour is what QACR should do. Under the review's own rule they
should be dropped. They are recorded rather than dropped because each describes a requirement
the product does not carry, and for a Class B submission an unstated capability is a gap rather
than a preference. **This is a decision, not a defect to fix here.**

| Amends | What it would say | Proposed milestone |
|---|---|---|
| FR-STA-007 | Something is written down at the point a test becomes active by which an incomplete test can be identified on reopening, and it is examined before the start-up state is presented. | 1 |
| FR-STA-007 | Data captured for a test that is invalidated on reopening is discarded, the invalidation is reported, and a result later returned for that test is not presented. **Needs a product decision first: may an abandoned test's images ever be analysed?** | 1 |
| FR-STA-007 | Where data is discarded because a test cannot be completed, the user is told that it was discarded and that a new kit is required. | 1 |
| FR-STA-003 | Retained state survives an application update, and where it cannot be read back the user is told a test could not be recovered rather than shown the start-up state. | 1 |
| FR-STA-002 | Flow content is not delivered while the application is not in the foreground, and on return delivery resumes from the point reached. | 1 |
| FR-KIT-007 | The message is presented on every attempt within the window, and a confirmation applies only to the attempt on which it was given. **Reword: FR-KIT-007 no longer presents an alert.** | 3 |

The sharpest of these is the last. The review's evidence for it is that the warning is shown
once and every later attempt in the window starts without it — which was marked `correct`,
while the candidate exists to say that defeats FR-KIT-007. Both readings are available and
neither is mine to pick.

### 6.3 A capability to exclude explicitly

Nothing found here. Recorded so that the absence is a finding rather than an omission.

---

## 7. Traceability

Every requirement owed by a covered feature, and its disposition. `as-is` means the current
product is the specification and there is nothing to design.

| Feature | Requirements | Disposition |
|---|---|---|
| F04.1 Step sequencer and confirmation model | FR-FLW-001, FR-FLW-004, FR-FLW-005, FR-FLW-006 (M3) | as-is except **D1, D2, D3, D5** · U2, U5 open |
| F04.2 Instruction media, replay and spoken delivery | FR-FLW-002, FR-FLW-003, FR-FLW-008 | as-is except **D3** · U1 open |
| F04.3 State retention and interruption tolerance | FR-STA-002, FR-STA-003, FR-STA-005 | as-is except **D4, D6, D7** · U3 open |
| F04.4 Termination detection and invalidation | FR-STA-006, FR-STA-007 | as-is except **D8** · U4 open |
| F04.5 Cancellation | FR-STA-008 (M3), FR-STA-009 (M3), FR-STA-010 (M3) | as-is except **D4, D5** |
| F04.6 Demonstration navigation | FR-FLW-007 | as-is except **D9** · U6 open |
| F04.7 Scan practice | FR-IMG-022 | **New** — section 3 |

F04.5 is triaged `Changed`, and the change is D4: the committed-sample point. FR-STA-008
already places the cancellation cut-off at cup fill, so the requirement does not move; what
moves is which step in the QACR flow that is.

---

## 8. Not in this brief

**The flow itself.** Which sections exist, in what order, and how many. Out of scope by
decision, and U7 records that nothing yet owns it.

**Content, copy and media.** E07's. No spec states, constrains or enforces user-facing
wording, and none quotes it.

**Timed waits and the waiting-time card.** SPEC-05's, which also carries F04.8. Where this
document names a wait it names it as a boundary, never as a duration.

**The scanning interaction.** E06's. Section 3 describes the practice framing around it and
deliberately not the interaction itself.

**Dedicated demonstration controls.** Wanted in a document of their own; none is planned. D9
and U6 record the part that has a requirement and the part that does not.

Behaviour lives in the current product. What must be true lives in QACR-APP-FR-01. Waits live
in SPEC-05. Wording lives in the content set.

Seven features, nine departures, seven statements. Six recreations and one thing that did not
exist before.
