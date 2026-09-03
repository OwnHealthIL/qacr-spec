# QACR-APP-SPEC-03 — Kit identification and eligibility

**Two features, both recreated.** Authority is per feature — see below.

|  |  |
| --- | --- |
| Document | QACR-APP-SPEC-03 |
| Revision | 1.3 — **ready**. Reviewed and settled; build from it. |
| Epic | E03 Kit Identification and Eligibility |
| Features covered | F03.1, F03.2 |
| Milestones | 3, except reading the kit identifier manually, expiry validation, and a backend refusal on a minimum interval between tests, all at 5 as future development |
| Domains | iOS, Android, Backend |
| Traces to | QACR-APP-FR-01 Rev 1.24 · QACR-APP-EPIC-01 Rev 1.18 |

---


## What this document defines

For each feature, **the source named below is authoritative.** Where this document and that
source disagree, the source wins — raise it rather than resolving it yourself.

| Feature | Behaviour defined by |
|---|---|
| F03.1 QR capture and kit validation | **recreated** — Minuteful Kidney, except departures D1 to D4 |
| F03.2 Reuse detection and new-kit gating | **recreated** — Minuteful Kidney, except departures D5 to D10 |

**Neither is new**, so the precedence rule below applies to both without exception.

## How to read this

**Both features are recreations. The current product is their specification.** Build them as
Minuteful Kidney US behaves.

This brief does not describe that behaviour and must not be read as describing it. It records what
**departs** from the current product, what is **still undecided**, and which requirement each
feature answers to. Nothing else.

> **Where this brief and the current product disagree on anything not in the departures
> table, the current product is right.** Raise it rather than implementing the brief.

Ten departures is more than either brief before this one, and none of them describes behaviour that
is being kept. Each was decided by Product against a specific behaviour of the current product,
which the development team read and reported.

**Three of the ten are future development.** D1, D5 and D9 are not built for this submission, and
each says so in its row, because a departure with no date reads like scope otherwise.

---

## 1\. Scope

**In scope.** Establishing that the kit in the user's hands is the right one, is authentic, and has
not been used — and what the user meets when it is not. Plus the forward-looking control at the
start of a test, where the software can only ask rather than verify, because the kit identifier is
not readable until the scan.

**Out of scope.** Everything the backend may refuse *before* a test starts, which is SPEC-01: the
configured blocked state, the unauthorised patient, the order that cannot be found, the end-of-service
refusal, and the block raised where no unused kit remains. Where a refusal originates there, this
brief records only that the application must present it. Appendix I of the requirements holds the
whole set, this document's kit conditions included. The scan itself, its guidance and its image
checks, which are SPEC-06. The practice scan, which is SPEC-04 — see below.

**The practice scan needs nothing from this brief.** The triage note against both features reads
*"adding this check to the scan practice as well"*, and that is already a requirement: FR-IMG-022
requires a practice scan to include QR-code validation, and to run the kit checks read-only so that
practising on the kit under test cannot spend it. It is owned by SPEC-04, with the rest of F04.7. No departure is needed
here.

---

## 2\. Departures from the current product

The only prescriptive part of this brief. Ten rows.

**Today** is Minuteful Kidney's behaviour, which is what the row departs from. **In QACR** is what is being asked for. Every row is readable without the behaviour review it was written against.

| # | Feature | Today | In QACR | Milestone | Driven by |
| --- | --- | --- | --- | --- | --- |
| **D1** | F03.1 | The automatic reads are all there is. Where the software cannot read the kit identifier, there is no second route and the test is invalidated. | **The user may present the kit identifier for reading.** Where the software cannot read it automatically, it asks the user to present the code, and invalidates the test only once that has also failed. Whether a missing identifier refuses the test at all stays configuration-determined, as it is today. | **5** | FR-KIT-009 |
| **D2** | F03.1 | Each platform enforces a different rule for what counts as a well-formed kit identifier, so a code one accepts the other rejects. | **One kit-identifier template, applied identically on both platforms.** The template itself is a value, not a departure — see U1. | 3 | FR-KIT-003, FR-PLT-006 |
| **D3** | F03.1 | A kit that is not this product's is handled differently on each platform: one names the condition, the other presents an empty message. | **The general failure**, on both. QACR states nothing specific about the kit, because nothing specific has been established about it. | 3 | FR-KIT-008 |
| **D4** | F03.1 | A refusal the software cannot attribute is reported as an already-used kit, which may be untrue and sends the user to the wrong troubleshooting route. | **The general failure.** The software never asserts a reason it has not been given. | 3 | FR-KIT-008 |
| **D5** | F03.2 | An expired kit is the one kit failure with no guided conversation. | **An expired kit routes to troubleshooting**, as the other kit failures do. | **5** | FR-KIT-005 |
| **D6** | F03.2 | The new-kit notice returns the user to the lobby, and they must start the test again with a second tap that asks nothing — so nothing is confirmed at the moment the flow begins. | **Confirming the new-kit notice starts the test**, which is what the requirement asks for. | 3 | FR-KIT-007 |
| **D7** | F03.2 | Declining a new test opens a results history screen on one platform. The other dismisses the warning. | **Dismisses the warning and does nothing else.** A results history screen is future development for QACR, so there is nowhere for it to go. Recorded as a departure rather than left implicit, so nobody recreates the route by default. | 3 | FR-PRT-015 (M5) |
| **D8** | F03.2 | Where the user has no unused kit left, one platform opens a switch-user screen with no message first. | **The message comes first, and support is the only route offered unless the backend reports more than one patient.** Switching user is offered only where the backend reports more than one patient against the phone number or the address, and that case is future development for QACR, so support is the route that applies. | 3 | FR-RDY-014, FR-AUT-020 (M5) |
| **D9** | F03.2 | One platform records an expired kit as a completed test and warns on the next attempt within the gate; the other does not. | **An expired kit does not count as a completed test** for the twenty-four-hour gate. The user has been told the kit is expired and will not reasonably try it again; if they do, they are refused again on the same grounds. | **5** | FR-KIT-007, FR-KIT-005 |
| **D10** | F03.2 | The platforms disagree at exactly twenty-four hours: one warns, one does not. | **The twenty-four-hour window excludes its endpoint**, identically on both platforms. Now stated in FR-KIT-007. | 3 | FR-KIT-007, FR-LCM-006 |

**Everything else across both features is recreated as-is.** No departures.

Six of these ten — D2, D3, D7, D8, D9 and D10 — exist because the two platforms disagree today. Each
names the behaviour QACR takes rather than instructing anyone to compare the platforms. Verifying
parity remains a QA activity at the end and is not a development obligation.

---

## 3\. Still undecided

One item, and it is a value rather than a behaviour.

| # | Question | Owner |
| --- | --- | --- |
| U1 | The kit-identifier template: what constitutes a well-formed identifier. Undecided, and deliberately not waited on. Nothing in this brief waits on it except D2 and design verification. Register: **Q-104**. | Guy · kit manufacturing |

---

## 4\. Confirmed as-is at review

Each of these was asked and the answer was that the current product's behaviour stands. They are
recorded because otherwise the next reader asks them again.

| Question | Answer |
| --- | --- |
| Is the kit identifier read during the scan rather than as a step of its own? | **Yes.** The user has already run the assay by the time it is read, which is why reuse is detected and not prevented. |
| Is the refusal for a missing identifier the backend's or the device's? | **The backend's**, and it is configuration-determined. The device establishes that no identifier was read and reports it; whether that refuses the test is decided against a per-partner value. Both halves of that stay as they are. |
| Is there a check on kit expiry before the test starts? | **No.** Expiry is established from the identifier, which is not readable until the scan. What can block before a test is a *configured* blocked state, and that is SPEC-01's — not a kit check. |
| Is expiry validation in scope for the submission? | **No.** It stays future development at milestone 5, and D5 and D9 go with it. |
| Should the automatic reading of the identifier and the manual route be one requirement? | **No.** The automatic reading stays at milestone 3 and the manual route is a requirement of its own at 5, so that one does not carry the other's date. |
| Must the twenty-four-hour window be judged against a time source the user cannot alter? Changing the device clock defeats it today. | **No.** An alterable clock is accepted for this window and no requirement is wanted for it. The timing windows inside a test are a separate matter and stay open as Q-30. |
| Does the block raised where no unused kit remains need a requirement of its own? | **No.** It is one of the reasons the backend refuses a test, which FR-RDY-014 already covers. It is recorded in Appendix I of the requirements, with the rest of that set. |
| Does a kit refusal interrupt the on-screen explanation, or wait for it? | **It waits.** Kept. |
| Is a kit rejection ever judged on the device? | **No.** Reuse is the backend's answer against its own register, so an unreachable backend yields no verdict rather than a guess. Kept. |
| Does the recency warning need re-acknowledging on a second attempt in the same window? | **No.** One acknowledgement stands until the next test completes, as today. FR-KIT-007 was amended at FR Rev 1.24 to require the message on every attempt **until it is confirmed**, which is the same behaviour stated from the other side and changes nothing here. |
| Are there two different recency messages, one for a previous test that produced a result and one for a test that was invalidated? | **Yes, and both stay.** They say different things and lead different places. FR-KIT-007 described one and has been corrected. |
| Does scanning the same used kit repeatedly escalate? | **No.** The same message every time, no attempt counter, no lockout. Kept. |
| Is the kit checked when the scan has already failed the on-device image checks? | **No**, as today — so a kit problem stays hidden until a scan passes locally. Kept. |
| Is the backend's own refusal on a minimum interval between tests wanted? | **Yes, as future development**, so that a capability the backend has is in the record rather than reached by configuration alone. |

---

## 5\. Traceability

Every requirement owed by a covered feature, and its disposition. `as-is` means the current product
is the specification and there is nothing to design.

| Feature | Requirements | Disposition |
| --- | --- | --- |
| F03.1 QR capture and kit validation | FR-KIT-001, FR-KIT-002, FR-KIT-003, FR-KIT-008 · future development at M5: FR-KIT-009 | as-is except **D1 (M5), D2, D3, D4** · U1 open |
| F03.2 Reuse detection and new-kit gating | FR-KIT-004, FR-KIT-007 · future development at M5: FR-KIT-005, FR-KIT-010 | as-is except **D5 (M5), D6, D7, D8, D9 (M5), D10** |

FR-KIT-002 and FR-KIT-004 carry no departure: the kit identifier is transmitted and checked against
the backend's register exactly as required, and both conditions FR-KIT-004 names invalidate the test
with their own message every time. FR-KIT-006 was withdrawn and its subject folded into FR-KIT-004.

Two register items belong to requirements this brief traces to, and neither is resolved by it.
**Q-15**: the Risk Analysis states that reuse is prevented, where the software can only detect it at
the scan. **Q-103**: FR-KIT-001 requires the software to prevent the user from completing a scan
where the code is missing or damaged, which nothing does and nothing can, since the code is read
during the scan. The requirement was left as written at review; this brief records the product's
behaviour and the register carries the question.

---

## 6\. Not in this brief

Behaviour, flows, screens, thresholds and values. Which refusals a given partner's configuration
raises. How the identifier is read, or by what mechanism. And **copy** — no spec states, constrains
or enforces user-facing wording, in any language.

Behaviour lives in the current product. What must be true lives in QACR-APP-FR-01. The conditions
that refuse a test are Appendix I of that document. The identifier template is U1. Wording lives in
the content set.

Two features, ten departures, no behaviour statements.
