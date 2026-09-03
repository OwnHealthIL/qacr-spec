# QACR-APP-SPEC-05 — Timed waits and the reaction phase

| | |
|---|---|
| Document | QACR-APP-SPEC-05 |
| Revision | 0.11, draft for review — Guy's Rev 0.10 review applied; not yet re-reviewed |
| Epic | E05 Timing and the reaction phase |
| Features covered | F05.1, F05.2, F05.3, F05.4, F05.5, F05.6, and F04.8 |
| Milestones | 1, except the sample-freshness window at 3 and the expiry notification at 4 |
| Domains | iOS, Android |
| Traces to | QACR-APP-FR-01 Rev 1.25 · QACR-APP-EPIC-01 Rev 1.19 |

**F04.8, the waiting-time card, is an E04 feature specified here** because its only
use is inside a timed wait and its behaviour cannot be described apart from the
countdown it carries. E04's spec references this document rather than repeating it.

**Guy's review of Rev 0.10 is applied at this revision**, and it moved more than any review
before it. The waiting phase is no longer empty — the chat runs optional steps through it and
the flow skips whatever the user has not reached when the mandatory action falls due. The
transition is staged rather than instantaneous. The completion window is not shown to the
user at all. The flow does not run while the application is away. Section 3 changed in more
places than it did not.

**Two durations are now real numbers**: incubation 5 minutes, colour evolution 4 minutes.
The completion windows remain the timing-flex study's.

**Three requirements are needed and do not exist** — the notification set, background audio,
and the stage properties travelling with the exam. Section 8 carries them.

**Copy has been removed as a section.** Wording lives in the content set and is not this
document's business.

**`[UI placeholder]` blocks** mark where the document implies an interface that has not been
designed. They are not open items — nothing is undecided about the behaviour — they are notes
for whoever picks up the design.

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
| Length | 5 minutes | 4 minutes |
| Failing to act in time | invalidates the test | invalidates the test |

Each timed stage has four properties, fixed in the application build and not
configurable at run time:

| Property | Meaning |
|---|---|
| **Start event** | the user action or system event from which elapsed time is measured |
| **Minimum duration** | the period before which the next action is not permitted |
| **Completion window** | the period, beginning at the end of the minimum duration, within which the next action must be taken |
| **Expiry behaviour** | what happens when the completion window closes without the action |

So a wait has two phases the user experiences differently. **Waiting**, where the
required action is not yet permitted — but not empty: the chat carries steps through it,
and the user works through them. **Acting**, where the required action is available and a
clock is running against them. The whole design problem of this spec is the transition
between those two phases, and the fact that the user may be mid-step when it arrives.

**The stage is the unit, and that is a change.** Minuteful Kidney has one wait, and it is
short: a countdown the user is shown, inside a single overall limit on the test as a whole.
Nothing in it is described per stage, because there is only one.

QACR needs the stage to be the unit. Two stages, each with its own minimum duration and its
own completion window, each tracked in its own right. A single deadline covering the test as
a whole does not express that, and the requirements ask for the finer grain: FR-TIM-005 wants
both intervals shown for each active stage, FR-TIM-002 wants each stage's start time
persistently retained.

*Traces: FR-TIM-001. The two durations above are Guy's, set at the Rev 0.10 review; the
completion windows remain TBD from the timing-flex study, and milestone 1 enforces provisional
values. Together the waits run to about nine minutes against the predecessor's seventy-five
seconds, which is the reason so little of its timing design carries over.*

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

**S05.03** Backgrounding, screen lock, a phone call, an app kill or a device restart have
no effect on the **clock**: it is wall-clock time and it keeps running. They do stop the
**flow** — nothing is delivered while the application is away. On return, elapsed time is
recomputed, and the user works through the steps that remain for that stage in order,
provided time is left and the completion window has not closed. They may return into a phase
they never saw begin, and the flow picks up from the step they had reached rather than from
where the clock now is.

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

**S05.39** The four properties of each stage named in section 2 — the start event, the
minimum duration, the completion window and the expiry behaviour — are transmitted to the
backend with the test record, as the values that were actually in force for that test. A
result cannot be interpreted later without knowing the timing it ran under, and a
provisional value at milestone 1 is exactly the case where that matters.

*Traces: FR-TIM-001, FR-TIM-002, FR-TIM-003. FR-TIM-004, a hardened time
source, is future development at milestone 5, so elapsed time is derived from a clock the user
can change — see section 8. The
exposure is inherited rather than introduced: this is how the current product works too.*

### 3.2 Entering a wait

**S05.05** A wait begins in the chat, not on a screen of its own. The step that starts it
is an ordinary flow step. *What the chat then says, and the bubbles it posts, is the chat's
own content and is not specified here.*

**S05.06** From that moment the chat shows a countdown of the time remaining until
the next action is permitted. This is the primary countdown during the waiting
phase. The completion window is not counted down here and is not shown, because
nothing the user can do is yet at risk.

**S05.07** **The wait is not empty, and the flow runs through it.** The chat carries steps
during the waiting phase which the user works through at their own pace. Those steps are
**not mandatory**: they exist to fill and use the wait, not to gate it.

**S05.41** Each stage has a small number of **mandatory** steps, and they are the ones the
stage cannot complete without. In the incubation stage they are shaking and opening the
Transfer Valve; in the colour-evolution stage they are shaking and scanning.

**S05.40** When the moment arrives for a stage's final mandatory action, **the flow advances
to it, skipping any non-mandatory steps the user has not reached.** The user is never held
behind optional content when the action is due. Whether the completion window turns out long
enough to let a user finish the optional steps *and* still act is a question for the
timing-flex study; if it does, this statement softens from a skip to a choice, and that is
the one part of section 3 the study can still move.

> **[UI placeholder — the skip.]** What the user sees when the flow jumps past steps they had
> not reached is undesigned. It must not read as content lost or as an error.

> **[UI placeholder — the countdown.]** Its unit, format and where it sits during the wait
> are undesigned, as is its relocated position during the handover.

**S05.31** The countdown is a persistent element of the flow rather than a bubble in
the transcript, so it does not scroll away from the user. Its unit and format are a design
decision and are stated nowhere in this document, but they have to suit a wait measured in
minutes: the predecessor's countdown is labelled in whole seconds, which reads badly once
the number runs to four digits. Existing countdown wording is not assumed to carry over.

*Traces: FR-TIM-005, FR-TIM-008.*

### 3.3 During a wait — the waiting-time card

**S05.08** Where the wait is long enough **and every step before the final one has been
completed**, the flow opens a card within the chat. The user does not choose to open it,
cannot be relied on to have opened it, **and cannot close it**. The thresholds that decide
whether it opens are fixed in the application.

**S05.09** The card carries the countdown. While the card is open it is the place
the user looks for the time remaining, so the countdown must not be duplicated
behind it in a way that can disagree.

**S05.10** The card also carries content that changes as the wait elapses — currently a
sequence of tips, presented with an animation. That content is optional: not reading it can
affect neither the conduct nor the validity of the test.

> **[UI placeholder — the card.]** Its layout, how the countdown and the changing content sit
> together, and the animation are undesigned.

**S05.11** The card yields when the flow needs the user to act — see S05.13 for when that
is. It is never dismissed by the user, and it is not left on screen competing with the action
prompt.

**S05.32** Filling the wait is not itself new. The current product already spends its wait
on the scanning instruction — a demonstration and the framing and distance rules —
delivered as ordinary chat steps, because a short wait needs no container of its own. What
is new here is the container, and that its content advances with elapsed time. The
instruction delivered during a wait is **not** the card's optional content: it is
instruction, it sits inside the readability scope, and it is subject to S05.33.

**S05.12** During wait 1 only, the flow offers scan practice from within the wait. It is
**not** bounded by the wait that hosts it: FR-IMG-022 ends it on a limit of its own, which
will most likely outlast the wait because the completion window is long. Milestone 1 may run
it with no limit at all. See SPEC-04, F04.7.

*Traces: FR-FLW-009, FR-IMG-022. Card thresholds TBD. On provenance: the UX study
describes this as a static countdown screen, a waiting lobby of its own. FR-FLW-009
settled on a card presented within the instructional flow, and this spec follows the
requirement. Noted because the study is still the readable account of the intent, and a
reader should not take its screen for the current design.*

### 3.4 The transition from waiting to acting

This is the critical moment of the test and it happens twice.

**S05.13** The transition is staged, not instantaneous. **The card yields a few seconds
before the countdown reaches zero**, so that the chat can post a bubble saying the next step
is about to arrive. The countdown itself keeps running, relocated to the foot of the screen.
When it reaches zero there is a chime and a prominent visual emphasis, and the flow posts the
instruction for the action now required. The bubbles and the countdown are synchronised: the
instruction does not arrive before the user has been told it is coming.

> **[UI placeholder — the transition.]** The relocated countdown, the emphasis at zero, and how
> the card's departure reads are undesigned. This is the most-seen moment in the test and it
> happens twice.

**S05.14** The transition must be perceptible to a user who is not looking at the screen. It
is accompanied by the spoken delivery of the instruction and by the chime of S05.13. **The
chime sounds even where the user has silenced the chat**: silencing the narration is not a
request to miss the test.

**S05.42** Where the application is not in the foreground when a stage ends, a notification is
raised. See S05.36 for the full set.

**S05.43** The application continues to produce audio while it is not in the foreground, in
the manner of a media player, so that the chime and the spoken instruction reach a user who
has put the phone down. **No requirement covers this and it needs one** — see section 8. The
platforms will not implement it the same way.

**S05.15** The countdown does not change meaning at this moment, because **the completion
window is not shown to the user at all.** The countdown counts down to permission and then
stops. What replaces it is the instruction to act, not a second clock counting against them.
The window is enforced silently.

**S05.16** The instruction for the action carries the same weight in both waits, but
the actions differ: wait 1 ends with a physical action on the device (the coloured
release button) confirmed in the chat; wait 2 ends by entering the scan.

**S05.33** The order is time first, then instruction. The minimum duration elapses, and the
instruction bubble for the action is played after it — the instruction is not required to fit
inside the wait, and the wait is not extended to accommodate it. This is how the current
product behaves and it is what S05.13's staging is built around.

**S05.34** Shortly before the minimum duration elapses the flow tells the user that the
action is nearly due, so that the transition is anticipated rather than sprung. Two moments,
not one: a heads-up, then the transition itself. The current product does the same, so this
is a recreation rather than an addition.

*Traces: FR-TIM-007, FR-TIM-005, FR-FLW-008.*

### 3.5 The completion window

**S05.17** **The completion window is not shown.** No countdown to expiry is presented and
the user is not told a second clock is running, so that they are not hurried through the
action the window exists to protect. It is enforced silently, as S05.15 says.

**S05.18** The **incubation** window completes when the user confirms in the chat that the
coloured release button has been pressed. The confirmation is the recorded event; the
application cannot observe the physical action.

**S05.19** The **colour-evolution** window completes when a valid scan is captured, not when
the user enters the scan screen. A user who enters the scan screen inside the window but is still
framing when it expires has an expired test. **The deadline is judged on when the images were
captured, not on when analysis finished**: an analysis still running when the window closes does
not invalidate a test whose capture landed inside it.

**S05.20** Acting too early and acting too late are different failures. Too early is
prevented: the control is not there, and no test is lost. Too late is an
invalidation: the test is over.

*Traces: FR-TIM-008, FR-TIM-009, FR-TIM-011. These two are **completion windows**, not
waits — the wait is the minimum duration that precedes each. The document says which
throughout, because conflating them is how a reader ends up thinking the user is shown a
clock during the part of the stage where they are shown none.*

### 3.6 Expiry and invalidation — the sad flow

**S05.21** When a completion window closes without the action, the test is
invalidated at that moment. The invalidation does not wait for the user to return to
the application or to attempt the action.

**S05.22** The user is told, in the chat, that the test is no longer valid, why, and that a
new kit is required to test again. **Each stage has one timing failure, so the stage is the
reason** — there is nothing further to distinguish within it.

**S05.23** The invalidation message uses the blocked-state pattern (SPEC-01, F01.5) and
offers no retry, because no retry can succeed. It opens the troubleshooting conversation,
which ends at the option to contact support and obtain a new kit.

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

> **[UI placeholder — the sad flow.]** The invalidation alert and the troubleshooting
> conversation that follows it are undesigned. This is the moment a user has lost ten minutes
> and a kit, and it is the most likely source of a support call.

*Traces: FR-TIM-009, FR-TIM-011, FR-TIM-012, FR-RDY-013, FR-KIT-007.*

### 3.7 The sample-freshness window — milestone 3

**S05.26** The time from the user confirming sample collection to connecting the
Sample Pod is measured, but it is measured silently. No countdown is shown and the
user is not told a clock is running, so that they are not hurried through a step
where haste causes error.

**S05.27** If the limit is exceeded the test is invalidated, and the user is told when they
activate the control confirming the Sample Pod is connected — not merely held at the step. The message states the reason
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
spec does not specify the first, because no requirement carries it; see section 8. The
same section records two further mechanisms the study proposes and no requirement
carries: an SMS fallback where notification permission was refused, and a persistent
timer outside the application by way of an iOS Live Activity or an Android floating
timer.

> **[UI placeholder — the notifications.]** What each of the two notifications says and how
> it looks on each platform is undesigned, as is the permission explanation that precedes the
> platform prompt.

*Traces: FR-TIM-014, FR-COM-009, FR-COM-012.*

---

## 4. States and transitions

For each timed stage. **WAITING is not idle** — the chat runs optional steps through it —
and the move to ACTING is staged rather than instantaneous.

```
  [step that starts the stage confirmed]
        |
        v
  +---------------------------------------------+
  | WAITING                                     |
  |   countdown to permission, shown            |
  |   optional chat steps run                   |
  |   card opens once earlier steps are done    |
  |   scan practice offered (incubation only)   |
  +---------------------------------------------+
        |
        |  a few seconds before zero:
        |  card yields, bubble warns,
        |  countdown moves to foot of screen
        v
  +---------------------------------------------+
  | HANDOVER   (seconds)                        |
  |   any optional step not reached is skipped  |
  +---------------------------------------------+
        |
        |  countdown reaches zero: chime + emphasis
        v
  +---------------------------------------------+   window closes    +---------+
  | ACTING                                      | -----------------> | INVALID |
  |   instruction for the mandatory action      | (enforced silently)+---------+
  |   completion window running, NOT shown      |                         |
  +---------------------------------------------+                         |
        |                                              troubleshooting chat
        |  action taken                                  -> support, new kit
        v
  +------------+
  | NEXT STAGE |
  +------------+
```

| State | Entered when | The user can | Leaves when |
|---|---|---|---|
| WAITING | the step that starts the stage is confirmed | work through the optional chat steps, read the card, practise scanning (incubation only), leave the app | the handover begins, a few seconds before the minimum duration elapses |
| HANDOVER | the countdown nears zero | read the warning bubble | the countdown reaches zero |
| ACTING | the minimum duration elapses | take the required mandatory action | the action is taken, or the window closes |
| INVALID | the window closes without the action | read why, work through troubleshooting, reach support | — |

Every state is recoverable from the persisted start time alone. There is no state that
exists only because the application happened to be running — but note that the **flow** does
not advance while the application is away (S05.03), so a user returning mid-stage resumes at
the step they had reached, not at the step the clock implies.

---

## 5. Data requirements

*To be completed. Seeded with what the behaviour above already implies.*

| Field | Type | Written when | Persisted locally | On the test record | Notes |
|---|---|---|---|---|---|
| stage identifier | enum | stage starts | yes | yes | which timed stage |
| start event time | timestamp | stage starts | yes | yes | the authority for all elapsed time (S05.01) |
| minimum duration | duration | build | — | **yes** | the values actually in force travel with the exam (S05.39) |
| completion window | duration | build | — | **yes** | as above |
| action time | timestamp | action confirmed or captured | yes | yes | incubation: chat confirmation. colour evolution: capture |
| outcome | enum | stage ends | yes | yes | completed / expired |
| invalidation reason | enum | on expiry | yes | yes | the stage is the reason; one per stage (S05.22) |
| interruptions | TBD | on background / foreground | TBD | TBD | recorded where a window expired while the application was in the background — that case is worth knowing about |

**Settled at the Rev 0.10 review: the timing values in force are recorded with the test**, as
S05.39 requires. This is the same answer FR-CFG-003 gives for the configuration set, and for
the same reason — a result cannot be interpreted later without the values it ran under.

---

## 6. Analytics events

*Provisional, and to be validated before implementation.* No analytics discussion has been
held yet; these are seeded from what the behaviour implies so the section is not empty. They
are **superseded by the analytics specification when it is written** and nothing here should
be built to as it stands.

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

## 7. What differs from Minuteful Kidney

This section says whether a behaviour is the same as today's product, because that is what
decides how much has to be designed. It does not say how today's product works. The single
change that drives most of the rest is the length of the wait: seconds in Minuteful Kidney,
around ten minutes here.

| | |
|---|---|
| The stage as the unit of timing | **Changed.** Two stages, each with its own minimum duration and completion window, each tracked independently. The predecessor has one wait inside one overall limit on the test. Section 2, S05.38. |
| Displayed countdown states the enforced deadline | **Changed.** The predecessor shows more time than it enforces; QACR's countdown runs at real time. S05.37. |
| Backgrounding and interruption | Unchanged. Elapsed time is recomputed from the start time on return rather than restarted. |
| Invalidation independent of the user returning | **Changed.** Today invalidation effectively happens when the user is there to be told. S05.21 makes it independent of that. |
| Number of timed waits | **Changed.** Two, both blocking, both ending in an action the user must take. Minuteful has one. |
| Countdown presentation | **Changed by scale, not by intent.** Same job, same position in the flow. A wait measured in minutes cannot reuse wording built for seconds, and the two phases need visibly different treatments they did not need at that length. S05.15, S05.31. |
| Filling the wait with instruction | **Unchanged.** The wait already carries the scanning instruction today, and it plays after the minimum duration ends rather than inside it. S05.32, S05.33. |
| Waiting-time card | **New**, and required by FR-FLW-009. A container for time-driven content, which a short wait did not need. |
| Heads-up before the transition | Unchanged. One exists today. S05.34. |
| Scan practice during a wait | New. Only possible because the wait is long. |
| Invalidation on timing expiry | Mechanism exists. Additions: two timing failures rather than one, and **two routes out rather than one** — a lapsed reaction or scanning window opens the troubleshooting conversation, a stale sample goes straight to support. S05.25, S05.35. |
| Sample-freshness window | **Unchanged.** Same mechanism, same route — the alert goes to support with no troubleshooting step — and the predecessor invalidates the test too. Only the limit differs, and it remains open. S05.27. |
| Notification at the end of the wait | Proposed by the UX study, carried by no requirement. Not specified here. S05.36. |

---

## 8. Open items

| Ref | Question | Where it sits |
|---|---|---|
| — | Timing values: minimum durations, completion windows, card thresholds. From the timing-flex study, which completes before milestone 3. Milestone 1 runs provisional values. | FR-TIM-001 |
| FR-TIM-001 | **A suspected defect in the predecessor, to confirm with the development team.** A static reading of one platform suggests that after an analysis fails for a non-quality reason, the next test in the same application session may run with no expiry deadline scheduled at all — the previous clock is not cleared, so a fresh start skips scheduling. It is unconfirmed at runtime. It matters because the deadline is an assay control: without it a test can be scanned after the colour has evolved past its valid window and still produce a result. **S05.02 and S05.38 already prevent it here** — elapsed time is recomputed from a retained start time per stage rather than held in a live timer, and a design that recomputes cannot leak a stale one. Worth confirming so we know whether it is live in the shipping product. | Research, then dev |
| FR-CFG-003 | ~~Whether the timing values in force are recorded with the test.~~ **Answered: they are** — S05.39 sends all four stage properties with the exam. What remains is only whether FR-CFG-003's wording already covers them or needs widening. | FR doc, raise at review |
| S05.36 | **The notification set needs a requirement, and the shape is now settled.** Two per stage: one when the waiting period ends, and one a minute before the completion window closes. FR-TIM-014 covers only the second, and only as a warning — the first, which brings back a user who put the phone down, is carried by nothing. Amend FR-TIM-014 or add alongside it. | New requirement |
| S05.36 | ~~The study's SMS fallback where notification permission was refused.~~ **Not wanted at the moment; recorded as possible future development.** | Closed |
| S05.36 | ~~The study's iOS Live Activity and Android floating timer.~~ **Not for milestones 1 to 3.** Future development, with the Android form needing a second permission beyond notifications. | Closed |
| S05.33 | ~~Whether the scanning walkthrough plays inside the wait or after the countdown ends.~~ **As the predecessor: the instruction plays after the minimum duration ends.** S05.33 states it. | Closed |
| S05.43 | **The application producing audio while in the background has no requirement.** The chime and the spoken instruction have to reach a user who has put the phone down, which means the application keeps an audio session in the manner of a media player. iOS and Android will implement it differently and it may need a platform capability declared at release. | New requirement |
| FR-TIM-005 | The requirement reads as though both intervals are displayed for an active stage. **They are not: each stage shows its own waiting countdown and the completion window is never shown** (S05.15, S05.17). The requirement's wording needs narrowing to match, and that is regulatory-visible. | FR doc, raise at review |
| S05.37 | ~~Is a safety margin wanted on the reaction?~~ **Answered at the E05 review: the countdown runs at real time and states the deadline enforced.** No margin in the gap between displayed and enforced; if one is wanted it belongs in the minimum duration, where the timing-flex study sets it. | Closed |
| S05.27 | ~~Does the expiring sample route the user to support, or tell them a new kit is needed?~~ **Both, and the review settled the sequence:** the test is invalidated, the alert states the reason and that a new kit is needed, and its only route is support — no troubleshooting step. FR-TIM-006 amended accordingly at Rev 1.25. | Closed |

---

*Generated against QACR-APP-FR-01 Rev 1.25 and QACR-APP-EPIC-01 Rev 1.19. Every
S-statement traces to at least one requirement; every requirement in the features
covered is discharged by at least one S-statement.*
