# E03 behaviour review — where every item went

The development team read Minuteful Kidney US (iOS `develop` @ `e0636af31`, Android `develop`
@ `a50d8b0`) and produced 86 behaviour lines across F03.1 and F03.2, each mapped to a
requirement. Guy marked each line `correct`, `change` or `wrong`. This file records the
disposition of every marked line, so the review is traceable after the JSON leaves the
conversation.

The source is `Reference/acr-behaviour-review-E03.json`, exported 18 August 2026. It records
84 of the 86 lines as reviewed. The two unmarked ones are `F03.2-expired-6` and
`F03.2-expired-7`, both describing a pre-scan expired-kit block — the thing Guy asked to have
surfaced to him, and the thing the research established does not exist. They are unmarked
because they were the question, not an answer.

> **Its requirement mapping is against a pre-Rev-1.18 document.** It treats BL-04, BL-21,
> BL-22, BL-23, BL-24, BL-35 and BL-42 as deferred backlog items. All seven are live
> requirements now. That is why six of its ten proposed requirements turned out to exist
> already. Read its `relation: "unlisted"` verdicts against Rev 1.20, not as written.

## The fourteen `change` lines → ten departures

| Line | Guy's comment | Went to |
|---|---|---|
| F03.1-qrabsent-1 | keep the configuration gate; keep the rectified-image fallback; **add a manual scan fallback** | **D1** + P1 |
| F03.1-format-2 | align platforms | **D2** + U1 (the template is a value) |
| F03.1-mismatch-1 | show the general error | **D3** + P3 |
| F03.1-edge-3 | no known reason → general error | **D4** + P3 |
| F03.1-expired-3 | expiry should route to troubleshooting | **D5** (with F03.2-expired-3) |
| F03.2-expired-3 | QACR should have a troubleshooting flow | **D5** |
| F03.2-soon-5 | no second tap; continuing starts the chat | **D6** |
| F03.2-soon-6 | "No" dismisses the warning | **D7** |
| F03.2-kits-2 | should be like Android | **D8** (with F03.2-kits-3) |
| F03.2-kits-3 | should be like Android | **D8** |
| F03.2-resume-6 | should be like Android — **corrected at the Rev 0.1 review:** an expired kit should *not* count as a completed test, because the user has been told it is expired and would be refused again | **D9**, inverted, at M5 |
| F03.2-bound-1 | should be like iOS | **D10** |
| F03.2-bound-7 | consider a clock the user cannot change | **U2**, and Q-30 widened to record it |
| F03.1-edge-7 | Spanish should align between platforms | **content set.** No spec states or constrains wording |

## The two `wrong` lines → answered from the shipped system

| Line | Guy's doubt | Answer |
|---|---|---|
| F03.1-qrabsent-2 | "not sure if the backend is rejecting it — I think it is on the device" | **The backend refuses it, and only where a per-partner configuration value says to.** The device establishes that no identifier was read and reports it; it does not stop the scan. Both of Guy's comments are consistent once the flag's location is separated from the refusal's. |
| F03.1-edge-5, F03.2-expired-6, F03.2-expired-7 | "not familiar with a pre-scan block — surface it to me" | **There is no pre-scan expiry check.** Expiry is established from the identifier, which is unreadable until the scan. What can block beforehand is a **configured** blocked state whose reason set happens to include an expired-kit value — FR-CFG-006, milestone 3, already SPEC-01's. The JSON mislabelled a configuration state as a kit check. One client also carries a block reason the backend cannot send. |

## The ten proposed requirements → one is new

| | Proposed | Disposition |
|---|---|---|
| CN-01 | kit expiry | **exists**: FR-KIT-005 at milestone 5. Moving it to 3 was **declined** — expiry is not required for the submission, so D5 and D9 moved to 5 instead |
| CN-02 | reason enumeration and a safe fallback | **new** → **FR-KIT-008**, milestone 3 |
| CN-03 | wrong product's kit | folded into **FR-KIT-008** — same outcome, so one rule, not two |
| CN-04 | no unused kit remaining | **No requirement of its own.** It is one of the reasons the backend refuses a test, which FR-RDY-014 covers, and it is now a row in **Appendix I** |
| CN-05 | a verdict arriving while backgrounded | **Q4** — the outcome is not lost; it surfaces at the next start attempt |
| CN-06 | tamper-resistant clock | **Declined for this window.** An alterable clock is accepted for the interval between tests and no requirement is wanted. Q-30 stays open only for the timing windows inside a test |
| CN-07 | confirmation on every attempt | partly settled: the acknowledgement stays, the second tap goes → **D6** |
| CN-08 | two recency messages | **P4** amends FR-KIT-007, which describes one |
| CN-09 | connectivity threshold and escalation | **another document.** FR-COM-006's subject, and it applies to every upload step, not the kit check |
| — | the manual read of the identifier, from Guy's D1 comment | **FR-KIT-009**, milestone 5, split out rather than folded into FR-KIT-001 |
| — | the backend's minimum interval between tests | **FR-KIT-010**, milestone 5, at Guy's direction rather than an exclusion |
| CN-10 | supported languages | **content set** |

Everything the JSON marked `correct` and did not propose a requirement for is a recreation and
carries no departure. Nine of those became rows in *Confirmed as-is at review*, because a reader
who has seen the JSON will otherwise ask about them again.

## What was not swept

The sweep was bounded to the conditions and states inside F03.1 and F03.2 — kit reading,
validation, refusal, reuse and the start-of-test gate. It did not cover the scan itself, its
guidance or its image checks (SPEC-06); the practice scan (SPEC-05); the upload and connectivity
behaviour every step shares (FR-COM-006); or the pre-test refusals the backend raises before a kit
is involved (SPEC-01).
