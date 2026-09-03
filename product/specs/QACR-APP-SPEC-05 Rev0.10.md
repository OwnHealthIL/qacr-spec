# QACR-APP-SPEC-05 — Timed waits and the reaction phase

| | |
|---|---|
| Document | QACR-APP-SPEC-05 |
| Revision | 0.10, draft for review — the E05 behaviour review applied; not yet re-reviewed |
| Epic | E05 Timing and the reaction phase |
| Features covered | F05.1, F05.2, F05.3, F05.4, F05.5, F05.6, and F04.8 |
| Milestones | 1, except the sample-freshness window at 3 and the expiry notification at 4 |
| Domains | iOS, Android |
| Traces to | QACR-APP-FR-01 Rev 1.25 · QACR-APP-EPIC-01 Rev 1.19 |

**F04.8, the waiting-time card, is an E04 feature specified here** because its only
use is inside a timed wait and its behaviour cannot be described apart from the
countdown it carries. E04's spec references this document rather than repeating it.

**The E05 behaviour review is applied at this revision.** It was exported in `baseline` mode —
one behaviour, one mark — against FR Rev 1.24, and re-mapped here against Rev 1.25, which matters
because FR-TIM-006 moved in between.

Four open items closed on Guy's answers: the two routes out of a timing failure (S05.25, S05.27,
S05.35), whether a capture in progress may finish (S05.19), and whether a safety margin sits in
the gap between displayed and enforced time (S05.37 — it does not). One opened: a suspected
stale-timer defect in the predecessor, which this document's design already prevents.

**The review also confirmed what this document is not.** Most of its `change` marks say only
that the comparison does not apply — *no dipping in QACR*, *different timings*, *different flow*
— because these features are new rather than changed. That is the right answer and it is why
this is a full specification rather than a recreation brief with a departures table. Section 8
records which **mechanisms** carry over, not which behaviours differ.

The functional requirements referenced throughout are traceability anchors, not the
behaviour itself. They are written for regulatory review and say what must be true;
this document says what the product does.

Where this document says a behaviour is unchanged from Minuteful Kidney, that was checked
against the current product **on both platforms** — its content set, the waiting-time UX study,
and the shipped applications — rather than assumed. The two platforms agree on everything in
this document, including the margin between displayed and enforced time in S05.37, which is a
deliberate product decision on both rather than a quirk of one. **How the current product achieves any of it is not
recorded here and is not this document's business.** Whether the existing implementation
serves a requirement or has to be built again is for the development team to judge from the
requirement.

Values are open items until the timing-flex study or Guy sets them. None is inherited from
the predecessor.

---

## 1. Scope

**In scope.** Everything between the moment the user completes the step that starts
a timed stage and the moment they are permitted to take the next action, including
what the chat shows while they wait, how the wait ends, and what happens when it
ends badly.

**Out of scope.** The chat engine and the step sequencer itself (SPEC-04). The scan
and its real-time guidance (SPEC-06). Scan practice (SPEC-04, F04.7), which is
*offered* during the first wait but specified with the other capture behaviour. The
assay chemistry and the values of the windows themselves, which come from the
timing-flex study.

---

## 2. Concepts

QACR has two timed waits and they are not the same shape.

| | **Wait 1 — incubation** | **Wait 2 — colour evolution** |
|---|---|---|
| Starts when | the user confirms the Sample Pod is connected and the sample has entered the Incubation Wells | the user confirms the coloured release button has been pressed |
| The user is waiting for | the reagent to incubate | the colour to develop in the Detection Wells |
| Ends with the action | press the coloured release button, which opens the Transfer Valve | scan the Test Board |
| Length | the longer of the two | shorter |
| Failing to act in time | invalidates the test | invalidates the test |

Each timed stage has four properties, fixed in the application build and not
configurable at run time:

| Property | Meaning |
|---|---|
| **Start event** | the user action or system event from which elapsed time is measured |
| **Minimum duration** | the period before which the next action is not permitted |
| **Completion window** | the period, beginning at the end of the minimum duration, within which the next action must be taken |
| **Expiry behaviour** | what happens when the completion window closes without the action |

So a wait has two phases the user experiences differently. **Waiting**, where there
is nothing to do and nothing can be done. **Acting**, where the action is available
and a clock is running against them. The whole design problem of this spec is the
transition between those two phases.

**The stage is the unit, and that is a change.** Minuteful Kidney has one wait, and it is
short: a countdown the user is shown, inside a single overall limit on the test as a whole.
Nothing in it is described per stage, because there is only one.

QACR needs the stage to be the unit. Two stages, each with its own minimum duration and its
own completion window, each tracked in its own right. A single deadline covering the test as
a whole does not express that, and the requirements ask for the finer grain: FR-TIM-005 wants
both intervals shown for each active stage, FR-TIM-002 wants each stage's start time
persistently retained.

*Traces: FR-TIM-001. Values TBD from the timing-flex study; milestone 1 enforces provisional
values. The UX study works to a wait of roughly ten minutes, which is an order of magnitude
longer than the predecessor's — the reason so little of its timing design carries over.*

---

## 3. Behaviour

### 3.1 The timer framework

**S05.01** Each timed stage records the wall-clock time of its start event and retains it
immediately, before any UI reflecting the wait is shown. The record has to survive the
application not running.

**S05.02** All elapsed time is computed as the difference between now and the
retained start time. Nothing accumulates a separate count that could become the authority
instead. A displayed countdown is a rendering of that computation, refreshed at least once
per second while visible.

**S05.03** Backgrounding, screen lock, a phone call, an app kill or a device restart
have no effect on a timed stage. On return, elapsed time is recomputed and the flow
resumes in whichever phase that computation puts it, which may be a phase the user
never saw begin.

**S05.04** If the recomputation on return shows that the completion window closed
while the application was away, the test is invalid and the user is told so
immediately on return, not left in a waiting state that has already expired.

**S05.37** The countdown the user is shown states the deadline the software enforces. There
is no hidden margin between them. Where a safety margin is wanted — and for a reaction it
may well be — it belongs in the minimum duration itself, set by the timing-flex study and
testable at design verification, not in the gap between what is displayed and what is
enforced. A user who waits until the countdown reaches zero has waited long enough.

**S05.38** Each timed stage is tracked in its own right. Its start time, its minimum
duration and its completion window belong to that stage, and the two stages are independent:
neither the elapsed time nor the outcome of one is derivable from the other. A single
deadline covering the test as a whole does not satisfy this document.

*Traces: FR-TIM-001, FR-TIM-002, FR-TIM-003. FR-TIM-004, a hardened time
source, is future development at milestone 5, so elapsed time is derived from a clock the user
can change — see section 9. The
exposure is inherited rather than introduced: this is how the current product works too.*

### 3.2 Entering a wait

**S05.05** A wait begins in the chat, not on a screen of its own. The step that
starts it is an ordinary flow step; when the user confirms it, the flow posts a
bubble that says the wait has started and what the user is waiting for.

**S05.06** From that moment the chat shows a countdown of the time remaining until
the next action is permitted. This is the primary countdown during the waiting
phase. The completion window is not counted down here and is not shown, because
nothing the user can do is yet at risk.

**S05.07** The flow does not advance past the bubble that starts the wait. The user
cannot scroll or tap their way forward, and no confirmation control for the next
step is present until the minimum duration has elapsed.

**S05.31** The countdown is a persistent element of the flow rather than a bubble in
the transcript, so it does not scroll away from the user. Its unit and format are a design
decision and are stated nowhere in this document, but they have to suit a wait measured in
minutes: the predecessor's countdown is labelled in whole seconds, which reads badly once
the number runs to four digits. Existing countdown wording is not assumed to carry over.

*Traces: FR-TIM-005, FR-TIM-008.*

### 3.3 During a wait — the waiting-time card

**S05.08** Where the wait is long enough, the flow opens a card within the chat. The
user does not choose to open it and cannot be relied on to have opened it. The
thresholds that decide whether it opens are fixed in the application.

**S05.09** The card carries the countdown. While the card is open it is the place
the user looks for the time remaining, so the countdown must not be duplicated
behind it in a way that can disagree.

**S05.10** The card also carries content that changes as the wait elapses —
currently a sequence of tips. That content is optional: not reading it can affect
neither the conduct nor the validity of the test. It is therefore out of scope of the
grade-6 readability gate applied to instructional content, though it is authored in
the same content set.

**S05.11** The card yields the moment the flow needs the user to act. It is not
dismissed by the user having read it, and it is not left on screen competing with
the action prompt.

**S05.32** Filling the wait is not itself new. The current product already spends its wait
on the scanning instruction — a demonstration and the framing and distance rules —
delivered as ordinary chat steps, because a short wait needs no container of its own. What
is new here is the container, and that its content advances with elapsed time. The
instruction delivered during a wait is **not** the card's optional content: it is
instruction, it sits inside the readability scope, and it is subject to S05.33.

**S05.12** During wait 1 only, the flow offers scan practice from within the wait.
Practice is bounded by the wait that hosts it and ends when that wait ends,
regardless of what the user is doing. See SPEC-04, F04.7.

*Traces: FR-FLW-009, FR-IMG-022. Card thresholds TBD. On provenance: the UX study
describes this as a static countdown screen, a waiting lobby of its own. FR-FLW-009
settled on a card presented within the instructional flow, and this spec follows the
requirement. Noted because the study is still the readable account of the intent, and a
reader should not take its screen for the current design.*

### 3.4 The transition from waiting to acting

This is the critical moment of the test and it happens twice.

**S05.13** When the minimum duration elapses, the flow makes an unmissable
transition. The waiting presentation ends, the card yields, and the flow posts the
instruction for the action now required.

**S05.14** The transition must be perceptible to a user who is not looking at the
screen. It is accompanied by the spoken delivery of the instruction, per the
instructional flow's recorded audio, and by whatever non-visual signal the design
settles on. A user who set the phone down during a ten-minute wait must be brought
back by something other than a change of pixels.

**S05.15** The countdown changes meaning at this moment. It stops counting down to
permission and begins counting down to expiry. Because the two mean opposite things
to the user — one is patience, the other is urgency — they are not the same
component with a different number in it. The design distinguishes them.

**S05.16** The instruction for the action carries the same weight in both waits, but
the actions differ: wait 1 ends with a physical action on the device (the coloured
release button) confirmed in the chat; wait 2 ends by entering the scan.

**S05.33** The transition has **two** conditions, not one. The minimum duration must
have elapsed *and* the instructions preceding the action must have been completed. Time
alone does not release the action. The consequence is a constraint on content: every
instruction the user needs in order to act must fit inside the minimum duration. Content
that overruns does not extend the wait — it delays the action instruction past the moment
the user is permitted to act, and so is taken out of the completion window. Minuteful
satisfies this by spending the whole wait on the scanning instruction and reaching the
action with nothing left to say.

**S05.34** Shortly before the minimum duration elapses the flow tells the user that the
action is nearly due, so that the transition is anticipated rather than sprung. Two moments,
not one: a heads-up, then the transition itself. The current product does the same, so this
is a recreation rather than an addition.

*Traces: FR-TIM-007, FR-TIM-005, FR-FLW-008.*

### 3.5 The completion window

**S05.17** During the completion window the flow shows the time remaining before the
window expires. This countdown is prominent and continuous.

**S05.18** Wait 1 completes when the user confirms in the chat that the coloured
release button has been pressed. The confirmation is the recorded event; the
application cannot observe the physical action.

**S05.19** Wait 2 completes when a valid scan is captured, not when the user enters
the scan screen. A user who enters the scan screen inside the window but is still
framing when it expires has an expired test. **The deadline is judged on when the images were
captured, not on when analysis finished**: an analysis still running when the window closes does
not invalidate a test whose capture landed inside it.

**S05.20** Acting too early and acting too late are different failures. Too early is
prevented: the control is not there, and no test is lost. Too late is an
invalidation: the test is over.

*Traces: FR-TIM-008, FR-TIM-009, FR-TIM-011.*

### 3.6 Expiry and invalidation — the sad flow

**S05.21** When a completion window closes without the action, the test is
invalidated at that moment. The invalidation does not wait for the user to return to
the application or to attempt the action.

**S05.22** The user is told, in the chat, that the test is no longer valid, why, and
that a new kit is required to test again. The reason distinguishes the two timing
failures in language the user can act on: the window for the release button was
missed, or the window for scanning was missed.

**S05.23** The invalidation message uses the blocked-state pattern (SPEC-01, F01.5)
and offers no retry, because no retry can succeed. It offers the route that does
apply: obtain a new kit.

**S05.24** An invalidated test still uploads its record. The test is over for the
user, not for the data.

**S05.25** **A timing failure has two routes out, and which one applies depends on which
window was missed.** A reaction or scanning window that lapses is a failure the user may have
caused and may be able to explain, so it opens the troubleshooting conversation. A sample that
has gone stale is not: nothing the user can say changes it, so it states the reason and goes
straight to support without a troubleshooting step. The twenty-four hour new-kit gate applies
to the next attempt in both cases, as it does after a completed test.

**S05.35** The guided exit is kept, and it is kept for the reaction and scanning windows
specifically. The alert states that the kit is spent, and the troubleshooting conversation that
follows establishes what happened before it ends at support. It matters more here than in the
predecessor: a QACR user has lost ten minutes and a kit, and the difference between being handed
to support and being returned to a home screen is the difference between a resolved and an
unresolved support case.

*Traces: FR-TIM-009, FR-TIM-011, FR-TIM-012, FR-RDY-013, FR-KIT-007.*

### 3.7 The sample-freshness window — milestone 3

**S05.26** The time from the user confirming sample collection to connecting the
Sample Pod is measured, but it is measured silently. No countdown is shown and the
user is not told a clock is running, so that they are not hurried through a step
where haste causes error.

**S05.27** If the limit is exceeded the test is invalidated, and the user is told when they
attempt to connect the Sample Pod — not merely held at the step. The message states the reason
and that a new kit is needed, and its route out is **support, with no troubleshooting step in
between**: a stale sample is not something the user can explain away, so asking them about it
would waste the one interaction they have left.

*Traces: FR-TIM-006. Limit TBD, currently specified as 30 minutes. The mechanism is a
recreation: the current product measures between the user's confirmation of collection and
their confirmation of the next physical step and blocks at the second of those, which is
what S05.26 describes. The limit differs — the predecessor's is shorter, and the value here
is Guy's to set. **What is no longer inherited is the outcome:** FR-TIM-006 was amended at FR
Rev 1.25 to invalidate the test rather than block the step, and FR-TIM-012 carries what the
user is told and that a new kit is needed. The current product blocks and routes to support;
QACR does not.*

### 3.8 Expiry notification — milestone 4

**S05.28** When a completion window is about to expire and the application is in the
background, the software raises a local device notification. It is raised only when
the application is in the background; a user looking at the countdown is not
notified about it.

**S05.29** The notification is local and does not depend on connectivity, so that a
user who loses signal mid-test is still warned.

**S05.30** The permission required is requested behind an explanation of our own, so
that the platform prompt is not the first thing the user sees. Refusing it does not
prevent a test being started, completed or reported — the on-screen countdown
carries the obligation either way.

**S05.36** The requirement behind this section covers one notification: the warning that
a window is about to expire. The UX study asks for a different one and treats it as
central — a notification at the end of the wait, to bring back a user who put the phone
down, whose job is to get the action taken rather than to warn that time is running out.
Those are two notifications at two moments, and only the second is required today. This
spec does not specify the first, because no requirement carries it; see section 9. The
same section records two further mechanisms the study proposes and no requirement
carries: an SMS fallback where notification permission was refused, and a persistent
timer outside the application by way of an iOS Live Activity or an Android floating
timer.

*Traces: FR-TIM-014, FR-COM-009, FR-COM-012.*

---

## 4. States and transitions

For each timed stage:

```
        ┌─────────────────────────────────────────────┐
        │                                             │
   [step confirmed]                                   │
        │                                             │
        ▼                                             │
   ┌─────────┐  minimum duration    ┌──────────┐      │
   │ WAITING │ ───────────────────► │  ACTING  │      │
   └─────────┘       elapses        └──────────┘      │
        │                            │        │       │
        │ card opens / yields        │        │ window │
        │ practice offered (wait 1)  │        │ closes │
        │                            │        ▼        │
        │                     [action taken]  ┌───────────┐
        │                            │        │ INVALID   │
        │                            ▼        └───────────┘
        │                     ┌────────────┐        │
        └────────────────────►│ NEXT STAGE │        │
                              └────────────┘   [new kit required]
```

| State | Entered when | The user can | Leaves when |
|---|---|---|---|
| WAITING | the step that starts the stage is confirmed | read the card, practise scanning (wait 1), leave the app | the minimum duration elapses |
| ACTING | the minimum duration elapses | take the required action | the action is taken, or the window closes |
| INVALID | the window closes without the action | read why, reach support, return home | — |

Every state is recoverable from the persisted start time alone. There is no state
that exists only because the application happened to be running.

---

## 5. Data requirements

*To be completed. Seeded with what the behaviour above already implies.*

| Field | Type | Written when | Persisted locally | On the test record | Notes |
|---|---|---|---|---|---|
| stage identifier | enum | stage starts | yes | yes | which timed stage |
| start event time | timestamp | stage starts | yes | yes | the authority for all elapsed time (S05.01) |
| minimum duration | duration | build | — | TBD | fixed in build; recording it makes a record self-describing |
| completion window | duration | build | — | TBD | as above |
| action time | timestamp | action confirmed or captured | yes | yes | wait 1: chat confirmation. wait 2: capture |
| outcome | enum | stage ends | yes | yes | completed / expired |
| invalidation reason | enum | on expiry | yes | yes | distinguishes the two timing failures (S05.22) |
| interruptions | TBD | on background / foreground | TBD | TBD | open: is interruption behaviour worth recording |

Open for this section: whether the timing values in force are recorded with the test,
which is the same question FR-CFG-003 asks about the configuration set.

---

## 6. Analytics events

*To be completed.*

| Event | Fires when | Properties | Notes |
|---|---|---|---|
| `timed_stage_started` | a stage starts | stage | |
| `timed_stage_ready` | the minimum duration elapses | stage, whether app was foregrounded | tells us whether the transition was seen |
| `timed_stage_completed` | the action is taken | stage, time into the window | how close to expiry users act |
| `timed_stage_expired` | the window closes | stage, whether app was foregrounded | the failure we most need to size |
| `waiting_card_opened` | the card opens | stage | |
| `waiting_card_content_advanced` | content changes | stage, index | |
| `expiry_notification_raised` | M4 only | stage | |

The question these events exist to answer: how often do users miss a window, and were
they looking at the phone when it happened. That determines whether the M4
notification is a nice-to-have or a must.

---

## 7. Copy

All wording lives in the content set, not here. Keys below are engine-derived from
the sheet, following the `urine-bible` convention; the QACR content set does not
exist yet, so these are the items required rather than confirmed keys.

| What | Sheet | Key shape | Status |
|---|---|---|---|
| Wait started, per stage | Bubbles | `chat bubble {section}` | not authored |
| Scanning instruction delivered during the wait | Bubbles | `chat bubble {section}` | not authored |
| Waiting-card content, per tip | Bubbles | `chat bubble {section}` | not authored · no equivalent exists today |
| Heads-up before the transition, per stage | Bubbles | `chat bubble {section}` | not authored (S05.34) |
| Action instruction, per stage | Bubbles | `chat bubble {section}` | not authored |
| Confirmation control, wait 1 | Bubbles | `chat bubble {section} btn` | not authored |
| Countdown label | General | TBD | not authored · existing wording is seconds-only and does not carry over (S05.31) |
| Timing invalidation, too late to release | Alerts | `alert {scenario} title` / `text` / `btn` | not authored |
| Timing invalidation, too late to scan | Alerts | `alert {scenario} title` / `text` / `btn` | not authored |
| Sample no longer fresh | Alerts | `alert {scenario} …` | not authored |
| Expiry notification | General | TBD | not authored |

Countdown formatting is not copy. It is a display rule and belongs in design.

The instructional bubbles in this spec are inside the readability scope (test start
through the results chat). The waiting-card tips are not, per S05.10.

---

## 8. What differs from Minuteful Kidney

This section says whether a behaviour is the same as today's product, because that is what
decides how much has to be designed. It does not say how today's product works. The single
change that drives most of the rest is the length of the wait: seconds in Minuteful Kidney,
around ten minutes here.

| | |
|---|---|
| The stage as the unit of timing | **Changed.** Two stages, each with its own minimum duration and completion window, each tracked independently. The predecessor has one wait inside one overall limit on the test. Section 2, S05.38. |
| Displayed countdown states the enforced deadline | **Changed.** The predecessor shows more time than it enforces. S05.37. |
| Backgrounding and interruption | Unchanged. Elapsed time is recomputed from the start time on return rather than restarted. |
| Invalidation independent of the user returning | **Changed.** Today invalidation effectively happens when the user is there to be told. S05.21 makes it independent of that. |
| Number of timed waits | **Changed.** Two, both blocking, both ending in an action the user must take. Minuteful has one. |
| Countdown presentation | **Changed by scale, not by intent.** Same job, same position in the flow. A wait measured in minutes cannot reuse wording built for seconds, and the two phases need visibly different treatments they did not need at that length. S05.15, S05.31. |
| Filling the wait with instruction | **Unchanged intent.** The wait already carries the scanning instruction today. S05.32. |
| Waiting-time card | **New**, and required by FR-FLW-009. A container for time-driven content, which a short wait did not need. |
| Heads-up before the transition | Unchanged. One exists today. S05.34. |
| Scan practice during a wait | New. Only possible because the wait is long. |
| Invalidation on timing expiry | Mechanism exists. Additions: two timing failures rather than one, and **two routes out rather than one** — a lapsed reaction or scanning window opens the troubleshooting conversation, a stale sample goes straight to support. S05.25, S05.35. |
| Sample-freshness window | Unchanged mechanism, and **unchanged route** — the alert goes to support with no troubleshooting step, as today. **Changed outcome:** expiry invalidates the test rather than blocking the step. The limit differs and remains open. S05.27. |
| Notification at the end of the wait | Proposed by the UX study, carried by no requirement. Not specified here. S05.36. |

---

## 9. Open items

| Ref | Question | Where it sits |
|---|---|---|
| FR-TIM-004 | Elapsed time is derived from a clock the user can change. A hardened time source is future development at milestone 5, so until it is built, changing the device clock mid-test alters what the application believes about the windows. Milestone 5 carries no date, so this exposure stands through the submission. | FR doc, milestone 5 |
| — | Timing values: minimum durations, completion windows, card thresholds. From the timing-flex study, which completes before milestone 3. Milestone 1 runs provisional values. | FR-TIM-001 |
| FR-TIM-001 | **A suspected defect in the predecessor, to confirm with the development team.** A static reading of one platform suggests that after an analysis fails for a non-quality reason, the next test in the same application session may run with no expiry deadline scheduled at all — the previous clock is not cleared, so a fresh start skips scheduling. It is unconfirmed at runtime. It matters because the deadline is an assay control: without it a test can be scanned after the colour has evolved past its valid window and still produce a result. **S05.02 and S05.38 already prevent it here** — elapsed time is recomputed from a retained start time per stage rather than held in a live timer, and a design that recomputes cannot leak a stale one. Worth confirming so we know whether it is live in the shipping product. | Research, then dev |
| S05.14 | What the non-visual signal for the wait-to-act transition is, on each platform, and whether it survives silent mode. | New, raise at review |
| Q-99 | Whether the capture guidance is recorded audio as the instructional flow is. Bears on S05.14. | FR doc register |
| FR-CFG-003 | The configuration set in force is now recorded with the test record at milestone 3, so a test's configuration can be reconstructed. Whether the **timing values** in force are part of what is recorded is the part that bears on this spec and is not settled. | FR doc, raise at review |
| S05.36 | **The notification that brings the user back to act has no requirement.** FR-TIM-014 covers only the about-to-expire warning. The UX study's primary re-engagement mechanism is a notification at the end of the wait, which is a different notification at a different moment. Adding it is a new requirement, so it goes through review. | New, raise at review |
| S05.36 | The study's SMS fallback where notification permission was refused. No requirement carries it, and FR-COM-012 currently states the opposite intent: refusal is tolerated and the on-screen countdown carries the obligation. SMS is also a backend capability, adjacent to FR-COM-013. | New, raise at review |
| S05.36 | The study's iOS Live Activity and Android floating timer. No requirement, and the Android form needs a second permission beyond notifications. | New, raise at review |
| S05.33 | Whether the scanning walkthrough plays inside the wait, as Minuteful's does, or after the countdown ends as the study proposes. The study's placement spends about a minute of the completion window on instruction, which is the window the user needs in order to act. | New, raise at review |
| FR-TIM-005 | The requirement reads as though both countdowns are displayed for an active stage, while S05.06 shows only one at a time and S05.15 has them change meaning rather than coexist. The behaviour here is deliberate; the requirement's wording may need narrowing to match it, which is regulatory-visible. | FR doc, raise at review |
| S05.37 | ~~Is a safety margin wanted on the reaction?~~ **Answered at the E05 review: the countdown runs at real time and states the deadline enforced.** No margin in the gap between displayed and enforced; if one is wanted it belongs in the minimum duration, where the timing-flex study sets it. | Closed |
| S05.27 | ~~Does the expiring sample route the user to support, or tell them a new kit is needed?~~ **Both, and the review settled the sequence:** the test is invalidated, the alert states the reason and that a new kit is needed, and its only route is support — no troubleshooting step. FR-TIM-006 amended accordingly at Rev 1.25. | Closed |

---

*Generated against QACR-APP-FR-01 Rev 1.25 and QACR-APP-EPIC-01 Rev 1.19. Every
S-statement traces to at least one requirement; every requirement in the features
covered is discharged by at least one S-statement.*
