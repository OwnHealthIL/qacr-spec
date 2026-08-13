# QACR-APP-SPEC-01 — Readiness and eligibility

**RECREATION BRIEF.** Not a specification of behaviour.

| | |
|---|---|
| Document | QACR-APP-SPEC-01 |
| Revision | 1.2 — **ready**. Reviewed and settled; build from it. |
| Epic | E01 App Foundation and Device Readiness |
| Features covered | F01.1, F01.2, F01.3, F01.4, F01.5, F01.6, F01.8, F01.9 |
| Not covered | F01.7 cross-platform parity — a constraint every spec inherits, not a feature with behaviour of its own |
| Milestones | 3, except the camera check and server-side demonstration enforcement at 1, exclusive store distribution at 4, and two configuration items at 5 as future development |
| Domains | iOS, Android, Backend |
| Traces to | QACR-APP-FR-01 Rev 1.19 · QACR-APP-EPIC-01 Rev 1.13 |

---

## How to read this

**All eight features are recreations. The current product is their specification.** Build them
as Minuteful Kidney US behaves.

This brief does not describe that behaviour and must not be read as describing it. It records
what **departs** from the current product, what is **still undecided**, and which requirement
each feature answers to. Nothing else.

> **Where this brief and the current product disagree on anything not in the departures
> table, the current product is right.** Raise it rather than implementing the brief.

That rule matters more than anything else here. A brief that named readiness conditions would
be read as naming all of them, and the product has more than twenty — so a team building to
such a list would remove working capability. This document names only what changes, and so
cannot be read as a complete account of anything.

---

## 1. Scope

**In scope.** Whether this user, on this phone, with this build, holding this kit, may start a
test — and what they meet when the answer is no.

**Out of scope.** Authentication and kit validation, which are SPEC-02 and SPEC-03. Where a
refusal originates there, this brief records only that the application must present it.

---

## 2. Departures from the current product

The only prescriptive part of this brief. Two rows.

| # | Feature | What changes | Driven by |
|---|---|---|---|
| **D1** | F01.4 | The battery check is the level and nothing else. A device below the minimum is blocked whether or not it is charging, because a cable can be pulled out during a ten-minute wait. Today one platform exempts a charging device and the other does not. | FR-RDY-007 |
| **D2** | F01.9 | The configuration set that was in force travels with the test data to the backend, so a completed test carries the configuration it ran under. Not recorded today. | FR-CFG-003 |

**Everything else across all eight features is recreated as-is.** No departures.

---

## 3. Still undecided

One item, and it is a set of values rather than a behaviour. Nothing in this brief waits on it
except design verification.

| # | Question | Owner |
|---|---|---|
| U1 | Minimum battery level (Q-01), available storage (Q-02), supported OS range (Q-03), minimum hardware specification (Q-04). | Guy · IVTS qualification |

---

## 4. Confirmed as-is at review

Each of these was asked and the answer was that the current product's behaviour stands. They
are recorded because otherwise the next reader asks them again.

| Question | Answer |
|---|---|
| Does a recent previous test, or demonstration mode, block or notify? | **Notify.** It makes no difference whether the previous test was real or a demonstration: after a successful test the user is told before a new one starts, and is not blocked. |
| What happens when the battery level cannot be read at all? | **The test proceeds**, as today. |
| Is a camera that fails to start recoverable? | **No — it blocks.** The user cannot proceed with the flow. |
| Is the user told a previous result is still uploading? | **No.** Nothing is shown. |
| Do built-in defaults exist behind configuration-supplied values? | **For some values, not all**, as today. Not to be restricted either way. |

---

## 5. Traceability

Every requirement owed by a covered feature, and its disposition. `as-is` means the current
product is the specification and there is nothing to design.

| Feature | Requirements | Disposition |
|---|---|---|
| F01.1 Store distribution and install-time compatibility | FR-PLT-001, FR-PLT-002, FR-PLT-003, FR-PLT-004 | as-is |
| F01.2 Supported-device policy and run-time eligibility | FR-PLT-005, FR-RDY-002, FR-RDY-003, FR-RDY-004 | as-is |
| F01.3 Device integrity check | FR-RDY-001 | as-is |
| F01.4 Pre-test resource and permission checks | FR-RDY-005, FR-RDY-006, FR-RDY-007, FR-RDY-008, FR-RDY-009, FR-RDY-010 | as-is except **D1** · U1 open |
| F01.5 Blocked-state pattern | FR-RDY-011, FR-RDY-013, FR-RDY-014, FR-SUP-003 | as-is |
| F01.6 Deferred-upload recovery at start-up | FR-RDY-012 | as-is |
| F01.8 Device and version telemetry on the test record | FR-PLT-008 | as-is |
| F01.9 Run-time configuration | FR-CFG-001, FR-CFG-002, FR-CFG-003, FR-CFG-006, FR-CFG-004 (M1) · future development at M5: FR-CFG-008, FR-LCM-018 | as-is except **D2** |

FR-CFG-004 and FR-CFG-006 came into scope at Rev 1.18 — server-side enforcement of
demonstration behaviour, and the application's response to a configured blocked state. Both are
capabilities the current product already has, so both are recreations like everything else
here.

---

## 6. Not in this brief

Behaviour, flows, thresholds and values. Which checks a given partner has switched on. And
**copy** — no spec states, constrains or enforces user-facing wording.

Behaviour lives in the current product. What must be true lives in QACR-APP-FR-01. Values are
U1. Wording lives in the content set.

Eight features, two departures, no behaviour statements. For a set of recreations that is what
finished looks like.
