# QACR-APP-SPEC-02 — Identity, authentication and consent

**RECREATION BRIEF.** Not a specification of behaviour.

|  |  |
| --- | --- |
| Document | QACR-APP-SPEC-02 |
| Revision | 1.0 — **ready**. Reviewed and settled; build from it. |
| Epic | E02 Identity, Authentication and Consent |
| Features covered | F02.1, F02.2, F02.3, F02.4, F02.5, F02.6, F02.7, F02.8 |
| Milestones | 3, except the OTP attempt limits, the invite-code path, consent acknowledgement and first-run onboarding at 4, and the multi-user cases at 5 as future development |
| Domains | iOS, Android, Backend |
| Traces to | QACR-APP-FR-01 Rev 1.20 · QACR-APP-EPIC-01 Rev 1.14 |

---

## How to read this

**All eight features are recreations. The current product is their specification.** Build them as  
Minuteful Kidney US behaves.

This brief does not describe that behaviour and must not be read as describing it. It records what  
**departs** from the current product, what is **still undecided**, and which requirement each  
feature answers to. Nothing else.

> **Where this brief and the current product disagree on anything not in the departures table,  
> the current product is right.** Raise it rather than implementing the brief.

Two of the eight features are triaged `Changed` and neither needs a behaviour section: F02.4's
change is a single configuration state, so it is a departure row, and F02.5 turned out to be a
recreation. So this document states no behaviour at all.

---

## 1\. Scope

**In scope.** Identifying the user and getting them authenticated, confirming who is testing at the  
start of a test, and obtaining the acknowledgements the product requires before it collects  
anything.

**Out of scope.** Readiness and eligibility, which is SPEC-01 — including the `unauthorized`  
refusal the backend may return, which SPEC-01 covers as one of the refusals the application must  
present. Results access and its PIN, which is SPEC-13.

---

## 2\. Departures from the current product

The only prescriptive part of this brief. Two rows.

| # | Feature | What changes | Driven by |
| --- | --- | --- | --- |
| **D1** | F02.1 | A backend that does not answer the registration lookup must not be reported to the user as an unregistered number. Today a non-response and an unregistered number produce the same message, which tells the user something about their number that has not been established. | FR-AUT-003 |
| **D2** | F02.4 | Configuration gains a third state for the date-of-birth step: today it can enforce the check or skip the validation, and the new state suppresses the step from the chat entirely. Intended for demonstration partners. | FR-AUT-012, unchanged — see Q-101 |

**Everything else across all eight features is recreated as-is.** No departures.

---

## 3\. Still undecided

| # | Question | Owner |
| --- | --- | --- |
| U1 | **Q-63.** The session-token expiry period is recorded as wrong as stated. It cannot be settled from the application: no expiry or lifetime is held client-side at all, so the period is enforced entirely by the backend. The question needs the backend SRS or the backend team, not this spec. | Guy · backend |

---

## 4\. Confirmed as-is at review

Each of these was asked and the answer was that the current product’s behaviour stands.

| Question | Answer |
| --- | --- |
| Sign-out while test data is still being transmitted? | **Refused, with an alert.** Keep it. Signing out at that moment deletes the test and it cannot be restored. |
| A backend with no identity for the patient? | **Re-verification.** The user verifies again. |
| Consent acknowledgement is at milestone 4 while phone entry is at 3 — is that a gap? | **No.** Phone verification is not needed in the clinical studies, so the acknowledgement gate arriving at 4 does not leave a study collecting data without it. |
| An unregistered number has no path until the invite code arrives at milestone 4 — is that a gap? | **No**, for the same reason. |
| The date-of-birth requirement says the user *shall* confirm, and D2 lets configuration remove the step | **The requirement stays as it is.** It is not enforced by the software but by the product manager, who guards which state a partner is given. |
| Which steps of the flow are conditional, and on what parameter? | **In this document, only the date-of-birth step.** The structure of the chat flow belongs to its own document, so Q-65 stays with E04 rather than reaching in here. |

---

## 5\. Traceability

Every requirement owed by a covered feature, and its disposition. `as-is` means the current product  
is the specification and there is nothing to design.

| Feature | Requirements | Disposition |
| --- | --- | --- |
| F02.1 Phone number entry and lookup | FR-AUT-001, FR-AUT-002, FR-AUT-003, FR-AUT-023 (M5) | as-is except **D1** |
| F02.2 One-time password verification | FR-AUT-004, FR-AUT-005 (M4), FR-AUT-018, FR-AUT-019, FR-AUT-024 (M4) | as-is |
| F02.3 Invite code for unregistered numbers | FR-AUT-006 (M4) | as-is |
| F02.4 Date-of-birth confirmation at test start | FR-AUT-008, FR-AUT-010, FR-AUT-012, FR-AUT-007 (M5), FR-AUT-011 (M5), FR-AUT-015 (M5), FR-AUT-020 (M5) | as-is except **D2** |
| F02.5 Session and token lifecycle | FR-AUT-013, FR-AUT-014, FR-AUT-021, FR-AUT-022, FR-SEC-008, FR-COM-010 | as-is · U1 open |
| F02.6 Authentication guidance and failure support | FR-AUT-016 | as-is |
| F02.7 Consent acknowledgement | FR-CNS-001 (M4), FR-CNS-002 (M4), FR-CNS-003 (M4), FR-CNS-005 (M5), FR-CNS-006 (M5), FR-CNS-007 (M5) | as-is |
| F02.8 First-run onboarding | FR-AUT-017 (M4) | as-is |

F02.4 and F02.5 also carry the multi-user cases at milestone 5 — more than one user against a phone  
number, switching user, and a second test on a shared number. The application already holds the  
state those need; the flow is future development.

---

## 6\. Not in this brief

Behaviour, flows, screens and values. What the session holds and how credentials are carried. And  
**copy** — no spec states, constrains or enforces user-facing wording.

Behaviour lives in the current product. What must be true lives in QACR-APP-FR-01. Wording lives in  
the content set.

Eight features, two departures, no behaviour statements.
