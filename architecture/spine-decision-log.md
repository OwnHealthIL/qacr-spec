# Decision log — QACR backend architecture spine

Append-only. One line per decision, constraint, version, assumption and open question.
The spine (`architecture/spine.md`) is distilled from this file, not written alongside it.
This file is the authority on what was decided; resume from here, never from the rendered spine.

Sources: `architecture/data_model.md`,
`architecture/QACR-Software-Cybersecurity-Considerations.md`, `product/FR-01/requirements.json`, and
two inputs now **absorbed into this file and deleted** — the answered-questions document (14 answers,
8 open items, 7 OZ comments) and the investigation handoff. Everything either of them carried that
anything here cites is in **L12**: evidence `E-1`–`E-14`, corrections `C-1`–`C-7`, gaps `G-1`–`G-6`,
the verbatim answers and OZ comments, and where each of the fourteen answers landed.

---

## Legend · epistemic tags used throughout

Every finding, decision and gap below carries one of these. They describe the *basis* for the
claim, not the reader's confidence in it.

| Tag | Asserts |
|---|---|
| `[OBSERVED]` | Read directly from a cited source — code, config, a document, a query result. Verifiable by re-reading the citation. |
| `[ADOPTED]` | Settled by the user's own words, or by existing production reality this method treats as binding until changed. Not derived — decided. |
| `[INFERRED]` | Derived by the method from `[OBSERVED]`/`[ADOPTED]` facts already on record. Follows from evidence already established, not asserted independently. |
| `[UNKNOWN]` | A gap. Nobody has read the source, asked the question, or chosen a value yet. |
| `[REPORTED]` | Stated by the user as fact, not independently verified against a source. |

## Table of contents

| Section | Date | Covers |
|---|---|---|
| [L0](#l0--framing-established-before-elicitation) · Framing established before elicitation | pre-2026-08-19 | Why the backend has no requirements document of its own; what the absorbed inputs and the compliance note carry |
| [L1](#l1--adopted--settled-by-the-user-or-by-existing-reality-not-open-for-re-litigation) · Adopted — settled by the user or by existing reality | 2026-08-19 | The six answered open items, plus four facts about the live estate; none open for re-litigation |
| [L2](#l2--contradictions-between-the-oz-comments-and-the-answered-questions) · Contradictions between the OZ comments and the answered questions | — | Four collisions surfaced, not resolved here (resolved later in L8) |
| [L3](#l3--still-open-from-the-prior-investigation) · Still open from the prior investigation | — | Seven unresolved items carried forward (five later closed by L11) |
| [L4](#l4--notifications--investigated-2026-08-23-in-response-to-why-not-copy-the-notification-worker) · Notifications | 2026-08-23 | Why consuming notifications-worker's store was wrong; the proposed thin-SMS alternative |
| [L5](#l5--why-notifications-worker-is-complex-and-what-dropping-its-store-would-cost) · Why notifications-worker is complex | 2026-08-23 | What its 21 migrations actually buy; the attempt-record proposal that replaces L4's answer |
| [L6](#l6--cross-cluster-consumption-of-um-and-notifications-worker--investigated-2026-08-23) · Cross-cluster consumption of UM and notifications-worker | 2026-08-23 | The OTP chain traced end to end; the one real mismatch (UM requires `fullName`/`email`, QACR collects neither) |
| [L7](#l7--decision--consume-the-existing-services-defer-change-or-copy-to-a-dedicated-feature) · Decision — consume the existing services | 2026-08-23 | The user's decision on UM/notifications-worker; items not deferrable now; revisit conditions |
| [L8](#l8--user-answers-2026-08-23) · User answers | 2026-08-23 | Verbatim answers to OZ-2 (PII), OZ-5 (extension points), OZ-1/6/7 (security, monitoring, management plane) |
| [L9](#l9--stack-ratified-from-the-existing-repo--and-two-end-of-support-findings) · Stack, ratified from the existing repo | 2026-08-23 | Brownfield stack table; two end-of-support findings (PostgreSQL 14, RabbitMQ 3.11) |
| [L10](#l10--finalize-pass-2026-08-23) · Finalize pass | 2026-08-23 | First `spine.md` write — 19 ADs, 10 open questions; checks run; two items left outstanding |
| [L11](#l11--review-pass-2026-08-23--thirteen-items-raised-against-the-spine) · Review pass — thirteen items raised against the spine | 2026-08-23 | 13 `AQ-*` questions worked and landed one by one (`L11.1`–`L11.15`); adds AD-20–AD-27, OQ-11–OQ-17 |
| [L12](#l12--absorbed-source-material-2026-08-26) · Absorbed source material | 2026-08-26 | Evidence base (`E-1`–`E-14`), corrections (`C-1`–`C-7`), gaps (`G-1`–`G-6`), verbatim inputs folded in and deleted |
| [L13](#l13--message-broker-choice-for-qacr-backend-one-broker-not-two) · Message broker choice | 2026-08-30 | Why `behealthy` runs RabbitMQ and GCP Pub/Sub side by side; lands AD-29, one broker for `qacr-backend` |
| [L14](#l14--the-algorithm-execution-runtime-one-artefact-two-deployments) · The algorithm execution runtime | 2026-09-02 | The algorithm is fetched at runtime, not baked into the worker image (C-8), so who builds the image was never settled; proposes AD-30 plus OQ-19/OQ-20, unadopted |

## Index · where each decision currently stands

A decision is frequently amended in a later, non-adjacent section. This table is the shortcut: given
an id, where it was landed and everywhere it was touched again. **Landed** is where the id first
appears; **Amended / touched again in** lists every section that revises it or leans on it as a
premise — not every passing citation. Read the current state from the section listed last.

### Architecture decisions

| # | Landed | Amended / touched again in | Status | Current state |
|---|---|---|---|---|
| AD-1 | L10 (Q5, Q7 — L12.8) | — | Decided | Modular monolith; module boundaries mechanically enforced in CI (L11.6d) |
| AD-2 | L10 (Q6 — L12.8) | L11.1c | Decided | Single PostgreSQL + RLS is the only isolation mechanism, scoped to "per deployment" |
| AD-3 | L10 | L11.4c | Decided | `idempotency_key` — Rule now states plainly it is not replay protection |
| AD-4 | L10 (Q2 — L12.8) | — | Decided | Insert-only tables; binding `consent_ack` was considered, not taken (L11.13g) |
| AD-5 | L10 (Q10 — L12.8) | — | Decided | Kit consumed in the same transaction as the exam write |
| AD-6 | L10 (Q13 — L12.8); decision made L7 | L11.2i, L11.14a | Decided | UM owns auth; M1 static-token exception named (AD-21); session TTL is UM's value — open, **OQ-16** |
| AD-7 | L10 (from L7 "AD candidates") | — | Decided | No notification capability in `qacr-backend` before M5 |
| AD-8 | L10 (from L8.1) | L11.3g, L11.3h, L11.11 | Decided — amended more than any other AD in this log | Declared PII register, not segregation; outbound payloads carry only what the recipient exists to receive; no pseudonym mapping issued or held here |
| AD-9 | L10 (Q11 + L12.5) | — | Decided | Transactional outbox for all event publishing |
| AD-10 | L10 (Q8 — L12.8) | — | Decided | Per-partner adapter interface + null adapter |
| AD-11 | L10 (Q3 — L12.8) | L11.3h | Decided | Production→research one-way feed; scope of what may cross tightened alongside AD-8 |
| AD-12 | L10 (Q9 — L12.8) | L11.5c | Decided | Client polling, no server-driven progress; poll interval restated as advisory, not a control |
| AD-13 | L10 | L11.7e | Decided | Exam configuration snapshot; AD-25's version-floor named as the one exemption |
| AD-14 | L10 (Q14.3 + L12.5) | — | Decided | Digest pinning, SBOM, image signing — universal; underwrites AD-19's deferred freeze |
| AD-15 | L10 (Q8 — L12.8) | — | Decided | Provider delivery detail, paired with AD-10 |
| AD-16 | L10 (Q12 — L12.8) | — | Decided | No commercial implementation now; extension seams kept |
| AD-17 | L10 | L11.4e, L11.4f | Decided | `worker-api` callback surface; gap closed by AD-23's single-use grant |
| AD-18 | L10 (L12.5) | L11.2f, L11.9e | Decided | No patient data outside the production namespace; extended to cover M1; one named exception for restore rehearsal |
| AD-19 | L10 (Q4 — L12.8) | L11.1 (whole section) | Decided, narrowed | "Own database" claim withdrawn as contradicting AD-2; frozen-study deployment is now a Deferred item gated on OQ-7 |
| AD-20 | L11.2c, L11.2d (AQ-10) | — | Decided | Demonstration mode is a `partner` property; the gate is an absent outbox row |
| AD-21 | L11.2f–i (AQ-10) | — | Decided | M1's protection is absence of patient data plus a credential with mandatory expiry |
| AD-22 | L11.3b–d (AQ-02) | L11.9d | Decided | One region per deployment (`us-central1`); dual/multi-region permitted if every region is in-jurisdiction |
| AD-23 | L11.4 (AQ-03) | L11.5, L11.6, L11.12, L11.14a, L11.14b | Decided — amended by multiple independent sessions; flagged at L11.15b as the exact pattern the method watches for | Ingest contract: integrity/authenticity/replay/idempotency separated; patient-entitlement check; single-use callback credential |
| AD-24 | L11.6 (AQ-04) | — | Decided | States the release-gate set — KEV blocks, secret-scan blocks on any finding, suppressions named/owned/dated |
| AD-25 | L11.7 (AQ-11) | L11.14d (absorbs Q-03, no new id) | Decided, but resting on an invariant no requirement obliges | Version-floor / rollback-block / live-read admission gate — **OQ-13** |
| AD-26 | L11.9 (AQ-01) | — | Decided | Directional durability guarantee — DB never ahead of object storage; RPO/RTO figures open — **OQ-14** |
| AD-27 | L11.10 (AQ-05) | — | Decided, invariant half only | Exactly one component normalises; *where* is genuinely undecided — **OQ-15** |
| AD-28 | never created | L11.12a | — | Considered and explicitly rejected — the finding landed as an AD-23 amendment instead, to avoid one concern with two governing ADs |
| AD-29 | L13 | — | Decided | One message broker (RabbitMQ); a boundary AMQP cannot cross is bridged by HTTP behind AD-10's port, not by adding GCP Pub/Sub |
| AD-30 | L14 | — | **Proposed — awaiting review** | Algorithm execution runtime promoted as one digest-pinned image research → production; `worker-api` stays per-deployment. Not in `spine.md`; L14.6 holds the text |

### Open questions and decisions/ files

| # | Landed | Amended / touched again in | Status | Current state |
|---|---|---|---|---|
| OQ-1 | L10 (original spine) | L11.6f, L11.7h | Open | Independent penetration testing (procurement); fielded-version risk-assessment ownership |
| OQ-2 | L10 (original spine) | content in L9 | Open | PostgreSQL 14 / RabbitMQ 3.11 end-of-support upgrade path |
| OQ-3 | L10 (original spine; content L3.3) | L11.9c, L11.10f | Open | Retention period for frames/traces — blocked on L3.3 (ACR's retention never read) and on OQ-15 |
| OQ-4 | L10 (original spine; content L8.3) | — | Open | Per-feature log schema — mandatory fields, PHI-exclusion checklist |
| OQ-5 | — | — | — | Not referenced anywhere in this log — check `spine.md` directly rather than assume it here |
| OQ-6 | L10 (original spine; content L3.1, L12.6 item 7) | — | Open, owner Product | `FR-KIT-005` kit valid-use period — withdrawn or deferred, never answered |
| OQ-7 | L10 (original spine; content L3.4, L12.6 item 4) | L11.1f | Open | ACR's board→lot encoding never read; gates the kit-register import and study kit-lot partitioning |
| OQ-8 | L7.3, L7.4 (findings); id assigned L10 | L8.1 (confirms L6.8 as a violation) | Open | The two inherited UM exposures — PII in logs; OTP-bypass |
| OQ-9 | L10 (original spine; content G-1) | L11.10f | Open | Algorithm wall-clock latency / autoscaling targets; the workload itself depends on OQ-15 |
| OQ-10 | L10 (original spine; content C-3, L3.5) | — | Open | `NEW_BACKEND_PLAN.md` on an unmerged branch, never read |
| OQ-11 | L11.3f (AQ-02) | — | Open, owner QMS | Cross-border transfer basis for a second-market deployment |
| OQ-12 | L11.3i (AQ-02) | L11.11e | Open, owner Product | Patient-level linkage in research; the two pseudonyms must never be the same value |
| OQ-13 | L11.7a (AQ-11) | L11.14d (absorbs Q-03) | Open, owner Product + QMS | No requirement obliges a minimum admissible application build |
| OQ-14 | L11.9f (AQ-01) | — | Open, owner Backend owner + DevOps | RPO/RTO figures and restore-rehearsal cadence; gates the `dr` Deferred row |
| OQ-15 | L11.10a (AQ-05) | — | Open, owner Algorithm owner + Backend owner | Where image normalisation happens — device or backend |
| OQ-16 | L11.14b, L11.14c (AQ-13) | — | Open, owner Backend owner + QMS | Session token TTL value — SRS's 24h flagged wrong, no replacement chosen |
| OQ-17 | L11.14e, L11.14f (AQ-13) | — | Open, owner Product | Q-81: screenshot capture vs. results-PDF save/email |
| OQ-18 | L11.12g, L11.12h (AQ-06) | — | Open, owner Product | Results-centre content: invalidated tests, household visibility |
| D-01 | L11.12g, L11.12h (AQ-06) | — | Open, owner Product | Household/shared-handset results-centre visibility; `FR-PRT-001` left unspecified |
| D-02 | L11.14e–g (AQ-13) | — | Open, owner Product | Q-81 contradiction between `FR-SEC-007` and `FR-SHR-015`/`FR-PRT-009` |

---

## L0 · Framing established before elicitation

| # | Finding | Tag | Consequence |
|---|---|---|---|
| L0.1 | `QACR-APP-FR-01 Rev1.19` is a mobile-application requirements document. Every `FR-SEC-*` is device-side except `FR-SEC-008` (auth server-side) and `FR-SEC-013` (report to backend). 44 of 241 requirements mention the backend. | [OBSERVED] `product/FR-01/requirements.json` | There is no backend requirements document. Every backend obligation is derived, so the spine must fix *how* it is derived, not just what it is. |
| L0.2 | The answered-questions input carries 14 answers with ~60 recommendations at mixed altitude — invariants, tuning values and build tasks interleaved. | [OBSERVED] absorbed answers, L12.8 | Distillation, not authorship. Most items are backlog or Deferred. |
| L0.3 | No backend requirement covers observability, logging content, or an operations/admin plane. | [OBSERVED] `requirements.json`, all 22 groups | OZ-6 and OZ-7 have no requirement source. They are architecture decisions with no upstream, which is exactly where a spine has to carry the weight. |
| L0.4 | `compliance/` exists and was consulted by neither absorbed input. It names the FDA Premarket Cybersecurity Guidance (3 Feb 2026) and classes QACR as a "cyber device". | [OBSERVED] `architecture/QACR-Software-Cybersecurity-Considerations.md` | This is the source OZ-1 points at. It is mobile-centric; its backend-side obligations need deriving. |
| L0.5 | `architecture/` is entirely untracked on `master`. | [OBSERVED] `git status` | Placement decision outstanding. Spine and log are being written into `architecture/` pending it. **Closed 2026-08-26 — L12.9a**: the directory is tracked and stays here. |

## L1 · Adopted — settled by the user or by existing reality, not open for re-litigation

| # | Item | Tag | Source |
|---|---|---|---|
| L1.1 | Order is out of scope this phase; when it arrives it is decoupled as far as possible from kit and exam. | [ADOPTED] | Open item 1 `[A]`, 2026-08-19 — verbatim in L12.6 |
| L1.2 | Backend retention matches ACR plus applicable regulation. **Not yet buildable** — ACR's actual retention was never read. | [ADOPTED] + [UNKNOWN] | Open item 2 `[A]` — L12.6 |
| L1.3 | Which provider integration ships first at M3: deferred. | [ADOPTED] | Open item 3 `[A]` — L12.6 |
| L1.4 | Board→lot encoding follows ACR, simplified where possible. **Not yet buildable** — ACR's encoding was never read. | [ADOPTED] + [UNKNOWN] | Open item 4 `[A]` — L12.6 |
| L1.5 | EDC export: deferred, status quo stands. Production backend does not own it. | [ADOPTED] | Open item 5 `[A]` — L12.6 |
| L1.6 | `FR-ALG-003` and `FR-SHR-011`: both deferred. Interim — `algorithm_approval` written and referenced but enforced nowhere; per-partner config surface kept, no post-result branch built. | [ADOPTED] | Open item 6 `[A]` — L12.6 |
| L1.7 | `backend.q-acr` has never been deployed to production; `helmfile.d/qacr.yaml` declares `production` and `dr` with no releases in them. | [ADOPTED] reality | E-1 |
| L1.8 | Every route in `backend.q-acr` sits behind one shared static token (`RESEARCH_APP_TOKEN`, defaulting to empty); `worker-api` and `utility-service` mount no auth and are publicly ingressed. | [ADOPTED] reality | E-2 |
| L1.9 | The QACR iOS app's *Production* environment points at the research namespace. | [ADOPTED] reality | E-3 |
| L1.10 | ACR has no server-driven progress of any kind. Pure client polling. | [ADOPTED] reality | E-4 |

## L2 · Contradictions between the OZ comments and the answered questions

The 7 OZ comments at the foot of the answers document — quoted verbatim in L12.7 — postdate both
reconciliation passes (L12.5, L12.6) and were never folded into the answers.
Four of them collide with an answered question. Surfaced, not resolved.

| # | OZ comment | Collides with | Nature of the collision |
|---|---|---|---|
| L2.1 | OZ-3 — "user management and notification worker … we will copy them" | Q5.1, Q13 — "Consume both unchanged. Build none of it." | [CONTRADICTION] Load-bearing. Q13 is the entire authentication answer and rests on UM already implementing every `FR-AUT-*`/`FR-ACC-*` mechanism with both apps' hosts compiled in. Copying inverts it. |
| L2.2 | OZ-5 — "keep current solution only to the point, do not prepare infra for extension or implement what is not required" | Q12 (emit domain events day one; named nullable reference columns; keep the per-partner config surface), Q8 (ship the adapter interface + null adapter now) | [CONTRADICTION] Partial. Some of what Q8/Q12 build is required now (`FR-CFG-004`, `FR-SHR-005`/`006` at M3); the rest is speculative ring. The rule that separates them is undecided. |
| L2.3 | OZ-2 — "Save all PII in a dedicated table" | `data_model.md` §3 Alternative A — `patient` holds phone number and date of birth inline | [CONTRADICTION] Alternative A as written has no PII segregation. Interacts with §7.8 (pseudonym→patient mapping), `FR-ANL-003`, and L1.2 retention/erasure. |
| L2.4 | OZ-7 — "enable different management backdoors — to maintain the product effectively without external exposure" | Q5 names a `backoffice-api` role but never decides its exposure or authorisation model | [CONTRADICTION] Gap rather than conflict. In a regulated clinical system an admin plane is the primary privilege-escalation surface and a PHI-read path; leaving its model undecided is a silent dimension. |

| # | OZ comment | Status |
|---|---|---|
| L2.5 | OZ-1 — apply all cybersecurity regulation | Dimension. Source identified (L0.4). Backend-side derivation outstanding. |
| L2.6 | OZ-4 — simplest possible, align with SOLID | Design principle. Reinforces Q5 (modular monolith) and OZ-5. |
| L2.7 | OZ-6 — a monitoring guideline per feature: which logs, with what information | Dimension, no requirement source (L0.3). Spine fixes the contract; each feature fills it in. |

## L3 · Still open from the prior investigation

| # | Question | Tag | Gates |
|---|---|---|---|
| L3.1 | `FR-KIT-005` (kit valid-use period) — withdrawn or deferred? Its risk-analysis line was removed. | [UNKNOWN] Open item 7 | Whether `kit.valid_until` is built at all |
| L3.2 | Dedicated `qacr-prod` GCP project vs existing `healthyio-prod`. | [UNKNOWN] Open item 8 | Q14.2, and reopens Q14.1 (cluster) if dedicated |
| L3.3 | ACR's actual data retention — no period, GCS lifecycle rule or purge job was ever found. | [UNKNOWN] from L1.2 | Frame and trace storage sizing |
| L3.4 | ACR's board→lot encoding — never read. | [UNKNOWN] from L1.4 | The kit-register import |
| L3.5 | `NEW_BACKEND_PLAN.md` on `backend.q-acr` branch `docs/qacr-existing-map-and-plan` — the one substantial input never consulted. May already answer or contradict parts of the absorbed answers (L12.8). | [UNKNOWN] C-3 | Unknown until read |
| L3.6 | Algorithm wall-clock latency — no figure exists in source. | [UNKNOWN] G-1 | Q7 autoscaling targets |
| L3.7 | Q-63 session token expiry, Q-03 minimum OS versions, Q-81 screenshot vs results-PDF-to-gallery — security decisions still open in the requirements document. **Closed by L11.14** (AQ-13): Q-63 → AD-6 amended plus OQ-16; Q-03 → absorbed by AD-25 and OQ-13; Q-81 → OQ-17. | [UNKNOWN] compliance note → dispositioned | Auth implementation; `FR-PLT-005` config |

## L4 · Notifications — investigated 2026-08-23 in response to "why not copy the notification worker?"

The question was put to a recommendation that said consuming notifications-worker "costs nothing".
Investigation showed that claim was wrong, and that the alternative was also wrong.

| # | Finding | Tag |
|---|---|---|
| L4.1 | `NotificationEvents` persists `target` (phone/email) as `ARRAY(TEXT)` under a BTREE index `NotificationTargetIndex`, plus the message `payload` as JSONB. `NotificationEventAudits` adds `extraData` JSONB per status transition. No tenant or partner scoping column exists. | [OBSERVED] `be-infra/projects/notifications-worker/db-migrations/20201108103600-create-notification-event.js`, `20201116103600-target-to-array.js`, `20240814153100-create-notification-event-audit.js` |
| L4.2 | Retention exists — `jobs/removeOldNotificationsEvents.js`, `DAYS = 90`, overridable by `DAYS_TO_DELETE_RECORDS`. It is one global knob shared by every consuming product; there is no per-tenant retention. | [OBSERVED] `jobs/removeOldNotificationsEvents.js` |
| L4.3 | Consuming it therefore puts indexed QACR patient phone numbers and message payloads in a shared multi-product Postgres, outside any QACR PII boundary, on a retention period QACR cannot set — and puts an auth-critical delivery path (`FR-AUT-004` OTP) on another product's release train. | [INFERRED] from L4.1, L4.2 |
| L4.4 | The service carries 21 migrations and channels QACR has no requirement for at any milestone: SMS brands, outgoing-number pools, blocked carriers, forwarding rules, unsubscribed targets, delivery-receipt status machine, email (Mailgun, Paubox, nodemailer, NHS SMTP), postal (PostGrid). | [OBSERVED] `db-migrations/`, `lib/`, `package.json` |
| L4.5 | **QACR's entire backend notification obligation at M3 is one SMS carrying a six-digit OTP** (`FR-AUT-004`). Push is `FR-COM-013` at **M5**. `FR-COM-009` and `FR-TIM-014` are local device notifications explicitly independent of backend connectivity. No requirement at any milestone asks for email, NHS, postal, delivery receipts or unsubscribe handling. | [OBSERVED] `product/FR-01/requirements.json` |
| L4.6 | Providers in use: Twilio (SMS), APNs + Firebase (push), Mailgun/Paubox/nodemailer/NHS SMTP (email), PostGrid (postal). | [OBSERVED] `lib/`, `package.json` |

**Proposed, pending confirmation.** Neither consume nor fork: own a thin SMS send inside
`qacr-backend` — one Twilio adapter, **no notification store**. The phone number lives only in the
OZ-2 PII table and the `auth_challenge` row `FR-AUT-005` already forces (code, expiry, attempt
count, lockout window). Delivery receipts, unsubscribes and carrier state do not exist because no
requirement asks for them. M5 adds a push adapter (APNs + FCM) for `FR-COM-013`.

This is less code than forking, keeps PII inside the QACR boundary, and puts OTP delivery on QACR's
own release train and version pin.

**Consequence for an existing answer.** The absorbed Q9 answer (L12.8) recommends firing
`notifications-worker.create-notification` with `type: pushNotification` on terminal transitions.
Under L4.5 that builds an M5 capability (`FR-COM-013`) at M3, which OZ-5 forbids. Flagged as a
conflict, not silently dropped.

**Version discipline outstanding.** `twilio@4.23.0` is what the estate runs; current major is 5.x.
Nothing is bound until verified at draft time.

## L5 · Why notifications-worker is complex, and what dropping its store would cost

Investigated 2026-08-23 in response to: does this affect debugging and monitoring, and why did they
build the more complex thing? Read chronologically, the migrations are an operational history, not
gold-plating. [OBSERVED] throughout — `be-infra/projects/notifications-worker`.

| When | What was added | The problem it answers |
|---|---|---|
| 2020-11 | `NotificationEvents(target, payload, status, type)`, BTREE index on `target` | "Did we ever try to message this person?" — support searches by phone number |
| 2020-12 | `provider`, `providerLookupIds` | Correlation with the provider's own message id. Without it you cannot cross from your logs into Twilio's. The single most load-bearing debugging column |
| 2021-04 | `subscriptions` JSONB | The calling service declares a routing key and learns the delivery outcome asynchronously |
| 2021-05 | `dryRun` | Exercising the path without sending real messages |
| 2022-06 | `BlockedCarriers(code, countryCode)` | Learned operationally — specific carriers in specific countries reject or black-hole traffic |
| 2023-05, then 2024-06 | statuses `delivered`, `undelivered` — two separate migrations | They began with `sent` (handed to the provider) and twice needed finer truth about whether it reached the handset |
| 2024-08 | `NotificationEventAudits` | A single mutable `status` column loses the sequence. Same append-only-beats-mutable-state argument `data_model.md` makes for `exam_event` |
| — | `routes/webhooks.js`, `handlers/webhooks` | Receives provider status callbacks — the loop that populates the two rows above |
| — | `jobs/requeuePendingEvents.js` | Rows stuck in `pending` because the process died between the DB write and the provider call, swept by cron |
| — | `SmsBrands`, `outgoingNumbers`, `forwardingRules` | Multi-brand, multi-country sender identity |

### Findings

| # | Finding | Tag |
|---|---|---|
| L5.1 | The complexity is overwhelmingly a **delivery-observability and reliability** story, not feature breadth. Only the channel families (email, NHS, postal, push) and the brand/carrier machinery are things no QACR requirement asks for. | [INFERRED] from the table above |
| L5.2 | `jobs/requeuePendingEvents.js` exists because the service writes its row, then calls the provider, and a crash in between leaves `pending` forever. That is precisely the failure a transactional outbox prevents. | [OBSERVED] `jobs/requeuePendingEvents.js` |
| L5.3 | **L4's "no notification store" was too strong.** Dropping the attempt record breaks four concrete operations: (a) "the patient never got the code" is unanswerable without the provider's message id; (b) "OTP delivery rate dropped" has no denominator; (c) `FR-AUT-019` resend-interval conformance cannot be verified without attempt history; (d) sends stuck between the write and the provider call cannot be swept. | [INFERRED] from L5.1 |
| L5.4 | Logs cannot substitute. `FR-SEC-005`-style rules push PII out of logs — correctly — so the phone number will not be there, which means logs alone cannot answer "which numbers failed". The record has to be a row, not a log line. | [INFERRED] |

### Revised proposal — the attempt record, not the service

QACR needs the *attempt record*, not the *service*. The shape already exists in the architecture
twice: `auth_challenge` is required regardless by `FR-AUT-005` (code, expiry, attempt count, lockout,
resend interval — `data_model.md` §1.2), and `provider_delivery_attempt` is already the
append-only-attempt pattern for result delivery, justified in Q8 with this same argument — it makes
`FR-SHR-006`/`FR-SHR-007` a query rather than a state machine.

So: one append-only `otp_send_attempt` table plus one provider-webhook endpoint, carrying
`challenge_id` (the phone number stays in the OZ-2 PII table, referenced not duplicated),
`provider`, `provider_message_id`, and append-only status transitions from the Twilio callback.
`FR-SEC-013` audit events carry the attempt and its outcome with no PII.

One table and one endpoint, against 21 migrations — and every OTP debugging capability that matters
is preserved. What is still declined: email, NHS, postal, push-before-M5, SMS brands, outgoing-number
pools, blocked carriers, forwarding rules, unsubscribe management.

### Two consequences beyond notifications

- **The outbox earns its place under OZ-5.** L5.2 is in-estate evidence of the exact bug it prevents,
  so it is a correctness mechanism rather than extension infrastructure. Strengthens Q11 fix 5.
- **This is the worked example OZ-6 needs.** A spine-level invariant falls out: *any outbound
  third-party call records the provider's own correlation id on an append-only attempt row.* Its
  absence is what makes a whole class of support question permanently unanswerable, and two features
  would otherwise decide it independently. Candidate AD for the observability dimension.

## L6 · Cross-cluster consumption of UM and notifications-worker — investigated 2026-08-23

Prompted by: keep notifications as-is, we plan to change nothing in UM or notifications-worker,
we will run in a different cluster and GCP project — is that really the case, copy or consume, and
does it complicate Twilio and Auth0?

### The OTP chain, established

`QACR app → UM POST /send-verification-code (public HTTPS, accounts-*.healthy.io) → messenger.publish
on routing key notifications-worker.create-notification → notifications-worker → Twilio`
[OBSERVED] `user-management/handlers/phone-verification/{sendVerificationCode.js,helpers.js}`,
`notifications-worker/routes/index.js`.

| # | Finding | Tag |
|---|---|---|
| L6.1 | **QACR has no direct integration with notifications-worker at M1–M4.** The OTP SMS is published by UM, over AMQP, inside the existing project. QACR never touches the exchange, the service or Twilio. | [OBSERVED] `helpers.js:sendVerificationCodeSms` |
| L6.2 | **Consuming UM eliminates Twilio from QACR entirely** — no account, credentials, webhook endpoint, sender numbers or delivery-status handling. The provider relationship stays wholly in the existing project. This inverts the concern raised in L4/L5: the attempt record and provider correlation id are UM's and notifications-worker's problem, not QACR's. | [INFERRED] from L6.1 |
| L6.3 | **Auth0 is a non-issue for QACR.** It is 1 of 13 `authProviderTypes` inside UM (`auth0`, `auth0_passwordless`, `epic`, `cerner`, `maccabi*`, `clalit`, `google`, `dr_chrono`, `innovive`, `single_use_token`, `testing`, `phone_verification`), serving staff and EHR SSO for other apps. QACR's path is `phone_verification`, native to UM. Consuming UM does not touch Auth0. | [OBSERVED] `user-management/enums.js`, `utils/authProviders/` |
| L6.4 | UM is reached over public HTTPS at `accounts-{staging,production}.healthy.io`, and both QACR apps already have the host compiled in. Cross-project, cross-cluster consumption is the normal case for every consumer, at zero integration cost. **Consume, do not copy.** | [OBSERVED] E-5; L1.8 context |
| L6.5 | UM implements more of `FR-AUT-005` than previously credited: per-app `verificationCodeExpirationInSeconds`, `allowedPhonePrefixes`, a blocked-phone-number list, carrier lookup, and two independent rate limits (`generateVerificationCodeRateLimit`, `addPhoneNumberToBlockedListRateLimit`). | [OBSERVED] `enums.js:configKeys`, `helpers.js:blockMultipleRetries` |
| L6.6 | **`Users.phone` is nullable and NOT unique** (unique indexes are on `email`, `username`, and `(authProvider, authProviderId)`). So M5's `FR-AUT-011` many-users-per-phone-number is already supported by the schema. A previously suspected M5 blocker is not one. | [OBSERVED] `user-management/lib/models/core/user.js` |

### The one real mismatch — "change nothing" is not quite true

| # | Finding | Tag |
|---|---|---|
| L6.7 | UM's `Users` requires `fullName` (`allowNull: false`) and `email` (`allowNull: false, unique: true`). **QACR collects neither.** Identity is phone number + date of birth + invite code; no `FR-AUT-*`/`FR-ACC-*`/`FR-CNS-*` requirement mentions a name or an email address. Registering a QACR patient in UM therefore forces synthesising both, and the unique-email constraint becomes a synthetic key generator. | [OBSERVED] `lib/models/core/user.js` vs `product/FR-01/requirements.json` |

Three ways out, none free: synthesise both values (no UM change; junk identity data in a shared
store that other products' support tooling reads); relax the columns for the `phone_verification`
provider (a code and migration change to a shared service — contradicts "change nothing"); or own
patient identity in `qacr-backend` and use UM for less.

### Costs that survive consumption — the remaining case for owning auth

| # | Finding | Tag |
|---|---|---|
| L6.8 | **UM writes the patient phone number to application logs** — `logger.info('sending verification code message', { phoneNumber })`. PII in the logs of a shared service QACR cannot change. Collides with OZ-2 and with the compliance note's "no patient data in logs". | [OBSERVED] `handlers/phone-verification/sendVerificationCode.js` |
| L6.9 | `isPhoneWhitelisted` returns `{ ok: true }` without sending a code — a bypass on the OTP path. Under the FDA premarket guidance, which explicitly expects a hunt for hardcoded credentials and backdoors, this needs a documented justification rather than inheritance. | [OBSERVED] same file |
| L6.10 | Pre-send validation failures are deliberately swallowed — "Do not block the patient in case of a failure in one of the validations". Availability chosen over the security control. A deliberate trade-off QACR would inherit, not decide. | [OBSERVED] same file |
| L6.11 | UM's `VerificationCodes` table holds `phoneNumber`; QACR patient PII would live in UM's shared database under UM's retention. | [OBSERVED] `lib/models/phone-verification/verificationCode.js` |

L6.8–L6.11 are the entire remaining case for owning patient auth. They are far narrower than
"fork UM", and none of them is about capability — UM does the job. They are about whose compliance
surface the controls sit on.

### Consequence of the different-project decision

| # | Finding | Tag |
|---|---|---|
| L6.12 | A different GCP project means a different RabbitMQ broker. So at M5, `FR-COM-013` push — the one place QACR would integrate with notifications-worker directly — cannot use AMQP. It must use `POST /event` behind `basicAuthMiddleware` on the public ingress. The `subscriptions` delivery-receipt mechanism is AMQP-based, so QACR would not receive push delivery receipts by that route. | [OBSERVED] `notifications-worker/routes/index.js`, `db-migrations/20210407164500-add-subscriptions-to-event.js` |
| L6.13 | The user's statement that QACR runs in a different cluster and a different GCP project appears to **answer open item 8** (`L3.2`), which the handoff recorded as still open and as gating Q14.1 (cluster) — L12.6, item 8. Needs confirming as a decision rather than a plan. | [REPORTED] user, 2026-08-23 |

## L7 · Decision — consume the existing services; defer change-or-copy to a dedicated feature

**Decided by the user, 2026-08-23.** [ADOPTED] Consume UM and notifications-worker as they are.
Whether to change them or copy them into QACR is deferred to a dedicated feature. This resolves
L2.1 (the OZ-3 / Q13 contradiction) in favour of Q13, with the OZ-3 instinct preserved as a
scheduled reconsideration rather than discarded.

Consistent with OZ-4 (simplest possible) and OZ-5 (do not build what is not required), and it keeps
`FR-SHR-001`-style single-enforcement-point discipline: patient identity has one home, not two.

### AD candidates arising

- **Patient identity and OTP are UM's.** `qacr-backend` implements no OTP, no JWT minting, no PIN
  credential. It validates bearer tokens per request through `@ownhealthil/um-client`. Prevents a
  second identity store and a second set of auth limits from appearing. Retires the shared static
  `RESEARCH_APP_TOKEN` (L1.8).
- **`qacr-backend` owns only what UM has no concept of:** invite code (`FR-AUT-006`), date-of-birth
  confirmation at test start (`FR-AUT-012`, `FR-AUT-010`), and phone→patient resolution
  (`FR-AUT-007`, `FR-AUT-011`, `FR-AUT-015`, `FR-AUT-020`).
- **No notification capability in `qacr-backend` before M5.** Prevents a second SMS path and a
  second Twilio credential from existing.

### Not deferrable — decided now by default

| # | Item | Why it cannot wait |
|---|---|---|
| L7.1 | **Synthetic `fullName` and `email` for QACR patient users** (L6.7). A UM user cannot be created without them, so consuming unchanged *is* choosing to synthesise. Must be deliberate: a documented, non-resolvable placeholder scheme, never a value that could be mistaken for real contact data, and never used as a delivery target. | You cannot register the first patient without it |
| L7.2 | Reversibility decays with patient volume. Unwinding later means migrating patient rows out of a shared `Users` table, so the revisit trigger must fire **at M5**, not at an open-ended "when we feel like it". | The cost of the deferral grows monotonically |

### Not deferrable — compliance findings needing an owner now

These do not block consuming, but they are live exposures from the moment M3 ships, not
revisit-time topics. Per `SDLC.md` they go to `decisions/`, one file each.

| # | Finding | Why now |
|---|---|---|
| L7.3 | UM writes patient phone numbers to application logs (L6.8). | PII in a shared service's logs is an exposure the day M3 ships. Either UM changes, or QACR documents and accepts it with a named owner. |
| L7.4 | `isPhoneWhitelisted` bypasses OTP entirely (L6.9). | The FDA premarket guidance expects backdoors and default credentials to be hunted and justified. Inheriting it silently is the failure mode. |

### Revisit conditions for the deferred feature

Any one of these reopens change-or-copy:

1. **M5 is scheduled** — `FR-AUT-011` (many users per phone) and `FR-COM-013` (push, which forces
   the cross-project `POST /event` path, L6.12). This is also the volume ceiling from L7.2.
2. **QACR needs a code change in UM or notifications-worker** — the "change nothing" premise is
   then already gone, and the question reopens on its own. Self-executing trigger.
3. **A per-tenant retention or erasure obligation is settled** (L1.2 / L3.3) — UM's and
   notifications-worker's retention become QACR's problem at that point.
4. **The submission's security traceability is assembled** — threat → requirement → code → test →
   evidence for every `FR-AUT-*`/`FR-ACC-*` control, where those controls live in a service QACR
   does not version.

## L8 · User answers, 2026-08-23

### L8.1 — PII (OZ-2, L12.7). Verbatim: "do not bite hard, we just need to know where the PII exist and that is not spread into too many tables"

[ADOPTED] **Not** a mandate to segregate PII into one dedicated table. The invariant is
*locatability and containment*, not relocation. Consequences:

- `data_model.md` Alternative A survives intact — `patient` may hold phone number and date of birth
  inline. L2.3 is **withdrawn as a contradiction**; it was my over-reading of the comment.
- What replaces it is weaker and more enforceable: a **declared PII register** — the set of tables
  and columns that hold personal data is enumerated in one place, and PII is *referenced from*
  elsewhere, never copied into it. A new PII-bearing column is a deliberate act, not a side effect.
- This retroactively confirms L6.8 (UM logging patient phone numbers) as a violation of the intent —
  PII spreading into logs is exactly the proliferation this rule exists to stop. It also keeps the
  `FR-SEC-013` audit channel and `FR-ANL-003` pseudonym rules on the right side of the line.
- L7.1 (synthetic `fullName`/`email` in UM) stands, but is now a containment matter rather than a
  segregation one.

### L8.2 — Extension points (OZ-5, L12.7). Verbatim: "keep the extenation points for partners, this is a good place that will be extended soon and i do not want to rebuilt it"

[ADOPTED] **Partner extension points are kept.** OZ-5 does not bite on them. So from Q8, all of:
the adapter interface `resolve(partner) → {transport, endpoint, credentialsSecretName,
payloadBuilder, ackParser}`; the per-partner config namespace with schema and `overrides/` layer;
the append-only `provider_delivery_attempt` table; and the null adapter. Most of this is required at
M3 by `FR-SHR-004`, `FR-SHR-005`, `FR-SHR-006`, `FR-SHR-008` regardless.

**Scope of the answer, read narrowly.** The user said extension points *for partners*. Q12's three
nullable reference columns — `external_payment_ref`, `fulfillment_ref`, `prescription_ref` — are
commercial and operational seams, not partner seams, and no requirement names any of them. They are
**dropped**. Billing does not exist anywhere in the org (E-10), so `external_payment_ref`
in particular anticipates a system with no design.

**One judgment call, flagged for reversal.** Q8 point 1 proposes emitting `testCompleted` carrying
ACR's AMQP headers `healthy-partner-name` / `healthy-entity-id`, so that
`urine.com.services.backend/services/send-results` becomes reachable for free. Decision: **emit the
completion event on QACR's own versioned schema through the outbox, and do not adopt ACR's header
contract.** Reasoning: the extension point the user wants preserved is the adapter interface and the
per-partner config, which is retained in full; adopting ACR's wire contract instead couples QACR to
the estate Q6 explicitly declines to join, and it is the cheap half to add later — an adapter
translates if `send-results` is ever wanted. Reversible either way; flagged rather than buried.

### L8.3 — Cybersecurity, monitoring, management plane (OZ-1, OZ-6, OZ-7, L12.7). Verbatim: "please keep those as open questions that need to be resolved"

[ADOPTED] These are **not** to be decided or invented. They go to the spine's Open Questions with an
owner and an unblock condition, and to `decisions/` per `SDLC.md`.

**Proposed refinement, needs confirming.** Leaving all three wholly silent would leave the spine with
an undecided security, observability and operations dimension — which the method treats as a defect.
So each is split:

| | Already settled by a source — records as decision or seed, not a question | Genuinely open — goes to Open Questions |
|---|---|---|
| `:936` cybersecurity | Obligations already stated in `compliance/` and already recommended in Q14.3: machine-readable SBOM with maintenance status and end-of-support per component (`FR-LCM-004`); image signing; deploy by digest; TLS-and-pinning enforced as a release gate (`FR-SEC-014`); server-side enforcement of all auth limits; no PHI in logs | Which SIEM; log retention period and location; who owns vulnerability disclosure and postmarket monitoring; whether penetration testing is contracted; the threat-model owner |
| `:941` monitoring | The one invariant L5 already produced: any outbound third-party call records the provider's own correlation id on an append-only attempt row | The per-feature log schema itself — mandatory fields, levels, what constitutes a security event, the PHI-exclusion checklist |
| `:942` management plane | That it is not internet-reachable, and that privileged reads of patient data are audited through the `FR-SEC-013` channel | The access mechanism (VPN, IAP, bastion, cluster-internal only); who holds it; break-glass procedure and its review |

Nothing in the left column is invented — each is cited to `compliance/` or to an existing answer.
If the user wants the left column open as well, say so and it moves.

## L9 · Stack, ratified from the existing repo — and two end-of-support findings

Brownfield ratification rather than fresh choice. All [OBSERVED] at
`backend.q-acr` HEAD via read-only `gh api`, 2026-08-23.

| Component | Observed | Where |
|---|---|---|
| Language / runtime | TypeScript 6.0.3, Node 22 (`@tsconfig/node22`, `@types/node` 22.19.21); base image `node:${NODE_VER}-bullseye-slim`, version supplied as a build arg | `package.json`, `Dockerfile` |
| ORM / DB client | Prisma 7.9.0 (`prisma`, `@prisma/client`, `@prisma/adapter-pg`), `pg` 8.22.0 | `package.json` |
| Database | PostgreSQL **14** | `docker-compose.yaml` |
| Broker | RabbitMQ **3.11** (`rabbitmq:3.11-management-alpine`) | `docker-compose.yaml` |
| Algorithm runtime | `us.gcr.io/smiling-diode-638/algo-base:5.0-node-${NODE_VER}` — separate image, Python/native | `Dockerfile.algo-worker` |
| Monorepo | npm workspaces: `common/**`, `jobs/**`, `research/services/*`, `user/services/*` | `package.json` |

### Two components are at or past end of support

| # | Finding | Tag |
|---|---|---|
| L9.1 | **PostgreSQL 14 reaches end of life on 12 November 2026** — under three months from today. The project supports a major version for five years, then issues one final minor release. | [OBSERVED] postgresql.org versioning policy |
| L9.2 | **RabbitMQ 3.11 is already outside community support** — 3.12.x and older no longer receive patches; patches for older series are commercial-licence only. Current release is 4.3.5. | [OBSERVED] rabbitmq.com release information |
| L9.3 | **Scope caveat.** Both versions are observed in `docker-compose.yaml`, which is the local and CI substrate — `backend.q-acr`'s own CI uses it as the test substrate. Production versions are unverified: the database is Cloud SQL and the broker is cluster-hosted, both configured outside the repo. If CI validates against PostgreSQL 14 while production runs a different major, that divergence is itself an `FR-LCM-003` finding ("validated within the complete device software system before release"). | [UNKNOWN] |

**Why this is not merely hygiene.** `FR-LCM-004` requires a controlled inventory of off-the-shelf
component versions with continuous dependency scanning; `FR-LCM-005` requires vulnerabilities and
supplier notifications to be monitored throughout the lifecycle; and `compliance/` records that a
cyber device must supply, per component, **who maintains it, whether it is still maintained, and its
end-of-support date**, with CISA KEV entries designed out rather than risk-accepted. Starting a new
regulated product on a database that goes EOL inside a quarter, and a broker already outside
community support, is a submission finding waiting to be written.

**Consequence for the spine.** The Stack table is seed and records what is ratified, not what is
aspirational. These two versions are therefore recorded with their end-of-support dates attached, and
the upgrade decision becomes an Open Question with an owner — not a silent inheritance.
Production-version verification (L9.3) is a prerequisite for closing it.

## L10 · Finalize pass, 2026-08-23

Spine written to `architecture/spine.md` — 19 ADs, 11 conventions, 3 diagrams, 10 open questions,
11 deferred items. Checks run:

- **No placeholders, no template residue, no `[ASSUMPTION]` tags.** Every claim is `[OBSERVED]`,
  `[ADOPTED]` or `[UNKNOWN]`. The method treats a surviving assumption as a blocker; there are none.
- **Inputs reconciled.** All 14 answered questions (L12.8), `data_model.md`, `compliance/`
  and the seven OZ comments were checked against the spine. Three gaps were found and closed:
  branching strategy (Q14.4) was missing → added to Conventions; SBOM and image signing (Q14.3 plus
  the compliance note) were missing → folded into AD-14; the supersession of Q14.1 by the dedicated
  project decision was implicit in a diagram → made explicit in Structural Seed.
- **Most of the source document did not become an AD, by design.** Roughly sixty recommendations in
  the absorbed answers reduced to 19 invariants. Tuning values (CPU requests, KEDA thresholds,
  `USE_QUORUM_QUEUES`) are a build backlog, not architecture; where they gate a real decision they
  became Open Questions (OQ-9) or Deferred rows rather than being dropped.
- **Dimensions accounted for:** deployment, environments, infra and provider strategy, operations,
  security, observability, data, tenancy, app-facing contract, CI and release. None silent.
- **One inherited contradiction stands open, deliberately.** AD-8 forbids personal data in logs;
  the inherited user-management behaviour writes patient phone numbers to logs. Surfaced as OQ-8
  rather than resolved locally, per the rule that a conflict with a binding parent is escalated, not
  overridden.

### Outstanding, not blocking

- `decisions/` files not yet written. Candidates: the two user-management exposures (OQ-8), the
  end-of-support upgrade (OQ-2), and the monitoring guideline (OQ-4). `decisions/` currently holds
  only its README.
- **Repository-rule tension.** `README.md:49` forbids restating or paraphrasing a requirement, and
  `README.md:64` says this repository holds no reasoning. The spine references requirements by id and
  uses their own vocabulary ("practice scan", "kit identifier") without copying wording, and
  `data_model.md` already set that precedent. The decision log, however, is reasoning by
  construction, and by the letter of `README.md:64` belongs in the vault. Placement was directed to
  `architecture/` by the user; the rule tension is recorded rather than resolved.

## L11 · Review pass, 2026-08-23 — thirteen items raised against the spine

A review of `spine.md` against its four sources — the two now absorbed as L12, `data_model.md` and
`architecture/QACR-Software-Cybersecurity-Considerations.md` — found gaps in three
distinct shapes. They are recorded one file per question in `architecture/questions/`, `AQ-nn.md`,
each with its evidence, its default-if-unanswered, and where its answer lands. This section is where
the answers come back — one `L11.n` row per settled question, appended as it settles.

| Shape | Items | What it means |
|---|---|---|
| **Silent dimension** | AQ-01 backup/restore/DR, AQ-02 region and residency, AQ-03 upload integrity and replay, AQ-10 demonstration mode and M1 protection, AQ-11 security-patch path, AQ-12 public-surface abuse resistance | A dimension this altitude owns, neither decided nor deferred nor logged as open. The method treats these as defects. L10 claimed "dimensions accounted for… none silent"; that claim was too strong. |
| **Dropped question** | AQ-05 normalisation, AQ-06 results-centre scope, AQ-07 consent timing, AQ-08 pseudonym mapping, AQ-13 residual Q-63/Q-03/Q-81 | Raised in a source, never carried into the spine. `data_model.md` §7 held nine questions; three were answered on 2026-08-19 and of the six remaining only two reached the spine (OQ-3, OQ-6). L3.7 was logged here and then not carried forward at all. |
| **Reconciliation miss / internal conflict** | AQ-04 `FR-SEC-014` release gate, AQ-09 AD-2 versus AD-19 | AQ-04: L8.3's left column listed `FR-SEC-014` as already settled and recording as a decision; AD-14 took SBOM, signing and digest from that list and left it. AQ-09: AD-2 says one database and RLS is the only isolation mechanism; AD-19 gives a frozen study its own database. Both cannot stand as written. |

**Correction to L10.** The finalize pass recorded "Dimensions accounted for: deployment,
environments, infra and provider strategy, operations, security, observability, data, tenancy,
app-facing contract, CI and release. None silent." Deployment and environments were covered for
*where things run* but not for *durability, recovery or region*; security was covered for access and
supply chain but not for ingest integrity, replay or the patch path. The list was checked at the
level of the heading rather than the dimension.

### Answers

Append `L11.n` rows here as each `AQ` settles — one row per question, carrying the rationale, the
tag, and the `AQ` it closes.

### L11.1 — AQ-09, AD-2 versus AD-19. Contradiction removed; the deployment model deferred

**Where the contradiction came from.** AD-19's "its own database" was imported from the absorbed
Q4.1 answer, which *describes* how ACR's FDA studies run on the research
cluster — own namespace, own logical database and credentials on the shared research Cloud SQL
instance, pinned image tag. That paragraph is a description of a borrowed pattern, not an answer.
Q4.1's actual answer was narrower — the pattern is fine, what ACR lacks is the freeze — and its four
prescriptions are all pinning (digest, algorithm blob, configuration set, release verification); not
one is a database. Q4.2 then answered the tenancy half in the opposite direction: "`partner` stays
the single tenancy scope … One isolation mechanism, one set of RLS policies, one thing to verify."
AD-19 fused the two. [OBSERVED] absorbed answers Q4.1–Q4.2 (L12.8)

**No requirement asks for a frozen data plane.** `FR-LCM-009` and `FR-LCM-010` require verification
that the approved algorithm versions and configuration were deployed. AD-14 delivers exactly that.
Nothing in `product/FR-01/requirements.json` names a study database. [OBSERVED] requirements.json

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.1a | The user's ratio for a frozen study, verbatim in substance: **support the FDA requirements, keep freedom to move fast on the production version while the clinical study stays untouched, and expect more than one version of the clinical study to exist.** Recorded so the deferred decision resumes from here rather than from zero. The user's lean is a dedicated database and storage, and an additional cluster if needed | [ADOPTED] user, 2026-08-23 | Session on AQ-09 |
| L11.1b | **Deferred, not decided.** The user withdrew the dedicated-deployment decision on the ground that it depends on the colour boards and the kit QR scan — where that data is held — which is OQ-7, and OQ-7 has never been read. Deferred with a revisit condition rather than answered | [ADOPTED] user, 2026-08-23 | New Deferred row in `spine.md` |
| L11.1c | **The contradiction itself cannot be deferred.** AD-2 declaring RLS the only isolation mechanism while AD-19 grants a study its own database is the one defect that guarantees divergence, because each unit cites the AD that supports what it was going to do. AD-2's Rule now reads "one PostgreSQL database **per deployment** of this backend, and today there is exactly one" — the reading L11's correction says was intended — and AD-19's closing sentence points at the Deferred item instead of asserting a database | [ADOPTED] method | Amendments in place to AD-2 and AD-19; ids unchanged |
| L11.1d | **AD-19 also loses its namespace-and-digest claim.** A pinned digest is a property of a *deployment*. If a study is a partner inside the production deployment, its code is not frozen — production moves underneath it. So no coherent interim delivers a code freeze without answering the deployment question, and claiming one would have been worse than the contradiction. AD-14 makes digest pinning universal, so whichever model is chosen inherits the freeze | [INFERRED] from AD-14's binding scope | AD-19 Rule |
| L11.1e | **A clinical study is one partner, not one partner per site.** Sites collapse into the study setting, which is what ACR already does — `StudySetting(studyIdentifier, site, …)` and no `Site` model, site being a string. This tightens AD-19's title claim (it said *site* is a partner) and reduces the deferral's cost: all study data under a single `partner_id` makes a later move to a dedicated database a scoped extraction. It does not address the code freeze | [ADOPTED] user, 2026-08-23; [OBSERVED] absorbed answers Q4 (L12.8) | AD-19 title, Prevents and Rule |
| L11.1f | Three downstream items AQ-09 raised are answered by the deferral rather than left open. **Kit register:** AD-5's same-transaction consume is unaffected while there is one deployment; partitioning kit identifiers by lot before issue becomes a precondition of the dedicated-deployment branch, and is why OQ-7 gates it. **Research feed:** unchanged — one one-way channel, AD-11 intact. **Provider delivery:** unchanged and never actually in conflict, since the null adapter is per-partner configuration under AD-10 | [INFERRED] | AQ-09 §"What it leaves undecided downstream" |
| L11.1g | Two consequences recorded now because they bite only in the dedicated-deployment branch and are easy to lose: the **research consumer's `schema_version` window** would be bounded by the oldest live study deployment rather than by production, and a study's **pinned algorithm artefact must live in the study's own storage**, or a lifecycle rule on production's `algorithms` bucket (OQ-3) silently un-freezes the study | [INFERRED] | Carried into the Deferred item's scope, not into an AD |
| L11.1h | Whether a study deployment consumes the shared user-management, and who allocates kit lots to a study, were asked and are **not** answered — they fold into the deferred decision. AD-6 forbids a second identity store, so the shared answer is the presumption unless the deferred decision overturns it, which would be a conflict to surface | [UNKNOWN] | Deferred item |

### L11.2 — AQ-10, demonstration mode and what protects M1. Two new ADs

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.2a | **M1 is being built.** Confirmed by the user, which is what makes both halves of AQ-10 live rather than academic. The words "demonstration", "demo" and "M1" appeared zero times in the spine before this entry, while `FR-CFG-004` and `FR-RES-006` are both milestone-1 requirements | [ADOPTED] user, 2026-08-23 | AQ-10 |
| L11.2b | A **dummy partner** and **demonstration mode** were being conflated, and are separated here. A dummy partner runs real exams, real algorithm, real results that are simply not transmitted — already covered by AD-10's per-partner adapter and needing no new decision, and it is what the clinical study uses. Demonstration mode fabricates the result and runs no algorithm. Only the second carries risk | [INFERRED] from `FR-RES-006` and AD-10 | Clarified in session; the user's near-term plan is a dummy partner, then the clinical study comparing app results against actual lab results |
| L11.2c | **AD-20.** The demonstration designation is a property of the `partner`, resolved server-side, stamped on the exam at creation, never read from the request. `FR-CFG-004` is explicit: "irrespective of any value supplied by the application." A demonstration exam runs no algorithm — `FR-RES-006`'s note confirms "in demonstration mode no algorithm version is exercised" | [ADOPTED] requirement text | `product/FR-01/requirements.json`, `FR-CFG-004`, `FR-RES-006` |
| L11.2d | **The gate is the outbox, and it is an absence rather than a check.** A demonstration exam writes **no outbox row at all**. The alternative — a flag each consumer inspects — puts the same check in `partner-delivery-worker` and the outbox relay, two units built at different times, and one of them will disagree; the failure is a fabricated result delivered to a real provider. Writing nothing means a consumer built later is safe without knowing the concept exists. `FR-RES-006`'s note is why this matters more than it looks: demonstration mode is "a state the backend returns with the configuration… so the same artefact that ships to patients can be placed in it" | [ADOPTED] method | AD-20; AQ-10 option 1, taken |
| L11.2e | AQ-10's option 3 — a demonstration partner with a null delivery adapter — **rejected**. It stops provider delivery but not the research feed, as the file itself notes. It is also a worse fit after L11.1: the null adapter is what a study partner uses, and overloading it makes "sends nothing" mean two unrelated things | [ADOPTED] method | AQ-10 options |
| L11.2f | **AD-21, the M1 half.** The reframing that decided it: `FR-SEC-014` requires that a build whose `FR-COM-001`/`FR-COM-002` transport controls are not implemented "shall be used only with data that did not come from a patient". M1 *is* that build — TLS enforcement and certificate pinning are M3. So M1's protection is not primarily a credential, it is the **absence of patient data**, which is AD-18's rule extended to cover M1 | [ADOPTED] requirement text | `FR-SEC-014`; AD-18 Binds amended in place |
| L11.2g | M1 remains publicly reachable and has no authentication, so a credential is still needed. The invariant that matters is not which credential but that it **cannot outlive M1**, since inertia is exactly how `RESEARCH_APP_TOKEN` reached publicly ingressed production-adjacent code with an empty-string default (L1.8). Two mechanical end conditions, both required: the credential **carries its own expiry**, lifetime at most 90 days, renewal a recorded act; and **CI fails the build** if the M1 credential path is present once the AD-6 authentication path is enabled | [ADOPTED] user, 2026-08-23 — recommendation accepted | AD-21 |
| L11.2h | The expiry is a **rolling 90-day bound rather than a literal calendar date**, because no milestone schedule exists anywhere in `product/` or `architecture/` — searched, nothing found. A fabricated date would have been worse than a bound that self-enforces regardless of the schedule | [UNKNOWN] the M1→M3 calendar | Searched `product/`, `architecture/` for milestone dates; none recorded |
| L11.2i | **AD-6 amended in place** to name the exception rather than be silently contradicted: "No route is protected by a shared static credential. The milestone-1 demonstration is the single bounded exception, governed by AD-21." An unnamed exception to AD-6 is how the rule erodes | [ADOPTED] method | AD-6 |
| L11.2j | Asked and **not** answered, deliberately: whether Product ever wants a demonstration *exam* inside a real partner — a sales demo on a live account, a training run at a clinic. `FR-CFG-004` reads as partner-only and partner-only is far cheaper to verify, so AD-20 fixes partner-only. If Product wants per-exam demonstration, AD-20 has to be rewritten rather than extended | [UNKNOWN] | Product; raise if it arises |

### L11.3 — AQ-02, region and residency. One region per deployment, `us-central1`; AD-8 amended as a consequence

> **Renumbered from `L11.2` to `L11.3` on 2026-08-23** by the session that landed AQ-03, AQ-04,
> AQ-11 and AQ-12. AQ-02 and AQ-10 were worked concurrently and both claimed `L11.2`, the collision
> the `questions/README.md` predicted for parallel sessions. AQ-10 landed first and keeps the id;
> AQ-02's rows move to `L11.3a`–`L11.3i`. Nothing decided here changed. Citations updated in
> `spine.md`, `architecture_points.md` and `questions/AQ-02.md`.

**Where the silence came from.** Q14.1 answered the cluster question as "new namespaces on the
existing production clusters — `qacr-production` on `production-uk` **and/or** `qacr-production-us`
on `production-us`" [OBSERVED] absorbed answers Q14.1 (L12.8). The dedicated-project decision voided
that answer's *cluster* half, as the handoff predicted (L12.5), but nothing replaced the region — and the
"and/or" carried an unresolved two-market assumption through into a spine where the word *region*
never appeared. The estate around it is genuinely split: research is `us-central1-c`, `qacr-develop`
targets `dev-stg` while still naming `be-staging-uk` hosts, and the release tool promotes
`production-us` and `production-uk` separately.

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.3a | **Market: US only for now, UK plausible later.** The repo could not answer this — `product/FR-01/requirements.json` names no market, residency or jurisdiction, and the only regulatory anchor is the FDA 2026 premarket guidance in `compliance/`, which fixes a submission and not a service location | [ADOPTED] user, 2026-08-23 | Session on AQ-02 |
| L11.3b | **The 1-versus-2 fork dissolves rather than resolving.** Applying L11.1c's move — scope the invariant to a *deployment* — makes "one region for everything" and "region per market" the same rule read at two times: one region per deployment, and today there is exactly one. A UK market is then a second deployment, not an amendment to the invariant, and it composes with the deferred study-deployment model instead of colliding with it | [ADOPTED] method | AD-22 |
| L11.3c | **The region is `us-central1`**, co-regional with the research cluster. The AD-11 feed and the algorithm-artefact promotion are the only standing production↔research paths; co-locating makes both cross a project boundary and not a regional one, at no cost to AD-11's separation, which is about credentials and direction rather than distance | [ADOPTED] user, 2026-08-23 | AD-22 Rule; Structural Seed diagram |
| L11.3d | **A violation already exists and is named in the Rule rather than left for an audit.** Both QACR environments point `ALGORITHMS_BUCKET` at `be-staging-algorithms` — another product's staging bucket, on the path that carries promoted clinical algorithms. This is the "invisible until someone looks" failure the invariant exists for, so the AD cites it as a violation to correct before production | [OBSERVED] absorbed answers Q3 (L12.8) | AD-22 Rule |
| L11.3e | **Non-production region is unconstrained, deliberately.** AD-18 means no patient data is there, so residency does not bind it. The one-region-per-deployment clause still binds *inside* each environment, which is what keeps a develop database and a develop bucket from drifting apart | [INFERRED] from AD-18 | AD-22 Rule |
| L11.3f | **The cross-border half largely dissolves, and that is recorded rather than glossed.** With production and research both `us-central1`, the standing exam feed is not a cross-border transfer. What survives splits in two: research *use* of clinical data needs a basis regardless of geography, which is live today; and the transfer question becomes a **precondition of provisioning a second-market deployment** rather than an open blocker. Both are OQ-11, owner QMS — the question was explicitly not resolved in this session | [UNKNOWN] | OQ-11 |
| L11.3g | **No patient identifier crosses to research.** `Exam.prodId` is `String? @unique` and `MetadataSchema` already accepts `prodSource`, `prodPatientId`, `prodExamId`, `prodExamOrderSession`, `prodPartnerName` — reserved scaffolding that nothing writes. `prodPatientId` stays unwritten: the exam key crosses, clinical content crosses, and reconciliation is on the study kit identifier, which is what ACR already does per Q4.3. A pseudonym production can map back would make the research row attributable and would make AQ-08 blocking rather than session-4 work | [ADOPTED] user, 2026-08-23; [OBSERVED] absorbed answers Q3 and Q4.3 (L12.8) | AD-8 Rule |
| L11.3h | **AD-8 was defective, found here rather than by the review pass, and is amended in place.** Its Rule ended "no personal or health data appears in … outbound event payloads" — which, read literally, forbids the AD-11 research feed from existing at all, since moving exam data *is* its purpose, and forbids AD-10 provider delivery, since `FR-SHR-001` requires an identified result to reach a provider. The first three sinks in that list are diagnostic channels where the prohibition is right; the fourth was written as though it belonged with them. Two units one level down could each cite AD-8 to justify opposite things — the AQ-09 failure shape. The amended Rule separates the two kinds of channel: **neither personal nor health data in logs, the audit channel or analytics, ever**; an outbound payload carries **only what its recipient exists to receive**, spelled out for AD-10 and AD-11. Recorded as a consequence of AQ-02, not as a new question | [ADOPTED] method | AD-8 Rule amended in place; id unchanged |
| L11.3i | **Patient-level linkage in research is routed to Product rather than assumed.** L11.3g's answer costs research the ability to group exams by patient; that is sufficient for per-exam validation against a reference device and insufficient for anything longitudinal. At the user's direction this becomes a question to Product rather than an architecture call | [ADOPTED] user, 2026-08-23 | OQ-12 |

### L11.4 — AQ-03, upload integrity and replay protection. One ingest contract; the callback gets a single-use credential

**Session 3 of the `questions/README.md` order: AQ-03, AQ-12, AQ-04, AQ-11 in one pass.**

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.4a | **`FR-COM-004` and `FR-COM-005` are milestone-1 backend requirements, not future work**, and appeared zero times in the spine. `FR-COM-005`'s own note is the sharper half: it is "the compensating control for a modified or instrumented application" — product has already assumed a tampered app and named the backend as the thing standing in the way | [OBSERVED] `product/FR-01/requirements.json`, `FR-COM-004`, `FR-COM-005` | AD-23 Rule |
| L11.4b | **Four properties were collapsing into one and are separated here:** integrity (did the bytes arrive whole), authenticity (who sent this), replay resistance (is this the first submission), and idempotency (does a repeat converge). The spine held only the fourth | [ADOPTED] method | AD-23; AD-3 amended |
| L11.4c | **AD-3's `idempotency_key` is not and cannot be replay protection**, and the AD now says so in place. It is derived from `clientCreatedAt` + `colorBoardId` + install reference — client-supplied values — so a captured request replays to the same key *by design*. That is the feature `FR-COM-006` and `FR-RDY-012` retransmission needs. A reader would have conflated the two and the spine did nothing to stop them | [OBSERVED] `data_model.md:253-254` | AD-3 Rule amended in place; id unchanged |
| L11.4d | **A blanket nonce was rejected in favour of "provably idempotent or single-use, stated per route."** Worked through what a replay actually buys on each path: exam creation hits the unique key and no-ops; a frame or trace replay re-sends the same bytes to the same exam and converges. On those paths the prize in a captured request is the **bearer token**, which a nonce does nothing about and token lifetime does — that is Q-63, and it stays with AQ-13. A nonce ledger with TTL and clock tolerance on the expensive frame path buys nothing | [ADOPTED] user, 2026-08-23 — AQ-03 option 1 | AD-23 Rule |
| L11.4e | **The callback failure is not the one AQ-03 named.** The file expected a replayed callback to *overwrite* a result. It cannot: `exam_result` is one row per exam, insert-only. The real failure is the opposite — **first-writer-wins**. `worker-api` is unauthenticated by AD-17 with network position as its only control, so a forged or replayed callback arriving *first* becomes the clinical result and the genuine one is then rejected by the very constraint that looked protective. Nothing has to break for that to happen | [OBSERVED] `data_model.md:262`; [INFERRED] from AD-17 | AD-23 Rule; AD-17 amended in place |
| L11.4f | **The grant is the nonce.** The callback carries a credential minted at job dispatch, bound to that exam and algorithm run, bounded lifetime, accepted at most once. One mechanism buys authenticity and non-replayability with no separate nonce store, and it closes AD-17's gap rather than restating it. Rejected: a shared cluster credential — it fixes "who" but not "first time", and reintroduces exactly the long-lived shared secret shape of `RESEARCH_APP_TOKEN` (L1.8) | [ADOPTED] user, 2026-08-23 | AD-23 Rule |
| L11.4g | **The digest is stated as *not* a security control**, per the compliance note's explicit warning that a checksum catches noise and not attackers. The operative consequence: the checksum stored against a frame or trace must be the **client-supplied digest the server verified**, never one the server computed after arrival — a server-computed checksum proves nothing about transit and satisfies `FR-COM-004` on paper only. `data_model.md:220` said only "keys and checksums", which is a storage note and admitted either reading | [OBSERVED] `architecture/QACR-Software-Cybersecurity-Considerations.md:78-79` | AD-23 Rule; Consistency Conventions "Ingest integrity"; `data_model.md` updated |
| L11.4h | **`FR-COM-010` was found in this session and folded in — no AQ raised it.** M3, backend, from the threat analysis: the backend "shall reject any request that is unauthenticated, unauthorised for the resource addressed, or **attempting to act on a patient record other than the one associated with the verified user**." Zero occurrences in the spine. AD-6 covers *is this a valid token*; AD-2's RLS covers *is this the right partner*. **Nothing covered *is this the right patient*** — so patient A's token acting on patient B's exam was blocked by no stated invariant. It is the AD-2 failure class reached by a different route, and it belongs in the ingest AD because that AD is already about what every inbound request must satisfy | [OBSERVED] `product/FR-01/requirements.json`, `FR-COM-010` | AD-23 Rule |
| L11.4i | Replay protection is **not** a product requirement and is recorded as compliance-only: the note says outright "the spec does not currently say this; the guidance asks for it." Kept visible so nobody later looks for the requirement id behind it | [OBSERVED] `compliance/…:75-77` | AD-23 |

### L11.5 — AQ-12, abuse resistance on the public surface. The ingress is the one enforcement point

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.5a | **Product asks for nothing here.** Searched the requirements: the only limits anywhere are `FR-AUT-005` (OTP attempt count and lockout) and `FR-ACC-005` (PIN failure counter), and under AD-6 both belong to user-management and cover the login path only. Nothing covers `client-api`. The whole obligation is one line of the compliance note — "be robust to a hostile network: outages, denial of service, junk traffic, scanning" | [OBSERVED] `product/FR-01/requirements.json`; `compliance/…:141` | AD-23; Consistency Conventions |
| L11.5b | **The decision is *where*, not *how much*.** Figures are tuning and tuning is build backlog. The architectural half is that a limit in application middleware for one route and at the ingress for another means the two disagree under load and no owner can say which fired. **Abuse controls sit at the ingress; an application-code limit is an exception requiring a stated reason**, mirroring how AD-2 treats an application-level partner filter | [ADOPTED] user, 2026-08-23 — AQ-12 option 1 | Consistency Conventions "Abuse controls" |
| L11.5c | **AD-12's poll interval was a control in appearance only**, and the AD now says so. A server-supplied interval is a cooperation mechanism: a client ignoring it is indistinguishable from an attacker unless something enforces it, and after L11.5b that something is the ingress | [INFERRED] from AD-12 | AD-12 Rule amended in place; id unchanged |
| L11.5d | **The request body-size limit stays a per-environment Helm value, with the consequence stated rather than left implicit.** The recommendation was one shared limit, on the ground that `FR-LCM-017` release testing assumes staging and production behave alike; the user chose to keep the estate's existing arrangement. Recorded honestly: staging and production can therefore carry different limits, and a size-related rejection can appear only in production. Not a defect — a knowing acceptance of a tuning value's blast radius | [ADOPTED] user, 2026-08-23 — recommendation declined; [OBSERVED] absorbed answers Q14 (L12.8) | Consistency Conventions "Abuse controls" |
| L11.5e | Ranked minor by AQ-12 and it stays minor: it lands as one convention row plus a clause in AD-23, not an AD of its own | [ADOPTED] method | — |

### L11.6 — AQ-04, security release gates. AD-24 states the gate set and what each gate does

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.6a | **AQ-04's premise was stale and is corrected.** The file records `FR-SEC-014` as appearing zero times in the spine; L11.2f had since landed it in AD-21. But it landed as a **data** rule — no patient data in the M1 build — and not as a **pipeline** rule, so AQ-04's substance stood untouched: nothing stopped a build lacking TLS and pinning from being promoted | [OBSERVED] `spine.md` AD-21 | AD-24 Rule |
| L11.6b | **Product does oblige most of this, and tags all of it "Process"** — `FR-LCM-002` through `FR-LCM-005`. That tag is the whole problem, and it is what the compliance note is answering when it says `FR-SEC-014` "is a CI/release-gate control, not a code comment. Enforce it in the pipeline." A procedure that names no pipeline step is how these get skipped | [OBSERVED] `product/FR-01/requirements.json`, `FR-LCM-002`–`005`; `compliance/…:195-197` | AD-24 |
| L11.6c | **The cadence did not have to be invented.** `FR-LCM-004`'s own note carries it: SPTA 8.1 requires scanning **weekly and on every update to an off-the-shelf component**. `FR-LCM-005`'s note names the CISA KEV catalogue subscription. Both are quoted into AD-24 rather than replaced with a chosen number | [OBSERVED] requirement notes | AD-24 Rule |
| L11.6d | **One release-gate AD, not an amendment to AD-14.** The spine already named four things CI must enforce — AD-1 module boundaries, AD-2 cross-partner reads, AD-4 insert-only, AD-12 contract tests — each buried inside the AD it serves, so "what must be green to release" required reading twenty-two ADs and gate five would be added ad hoc or not at all. The four stay in their own ADs and are referenced, not moved | [ADOPTED] user, 2026-08-23 — AQ-04 option 1 | AD-24 |
| L11.6e | **The blocking line: KEV and above-severity block, below reports.** Any CISA KEV entry blocks and is designed out, never risk-accepted. Secret and hardcoded-credential scanning blocks on **any** finding, since there is no benign hardcoded credential. Rejected "block on every finding" — strictest on paper and closest to the guidance's "you cannot wave away a low-impact security bug", but it stops the pipeline on unreachable transitive advisories with no fix available, and the predictable outcome is a blanket suppression, which is worse than a stated threshold. Hence the countermeasure in the Rule: **a suppression is named, owned and dated** | [ADOPTED] user, 2026-08-23 | AD-24 Rule |
| L11.6f | **Fuzz, abuse cases, dynamic analysis and attack-surface/chaining analysis report on a cadence rather than blocking per commit.** They are the submission's evidence obligations, and per-commit fuzzing is not what makes them credible; accumulating them is. Independent penetration testing stays with **OQ-1**, correctly — it is a procurement question, not a pipeline one | [ADOPTED] method; [OBSERVED] `compliance/…:145-163` | AD-24 Rule; OQ-1 unchanged |

### L11.7 — AQ-11, the security-patch path. AD-25; the admission gate is live-read and AD-13 gains its one exemption

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.7a | **AQ-11's premise is corrected, and this is the session's most consequential finding.** The file, following the compliance note, treats `FR-PLT-005` and `FR-CFG-006` as giving "the hooks" for a version kill switch. Read: `FR-PLT-005` is "a backend-configurable list of supported **operating-system** versions and minimum hardware characteristics"; `FR-CFG-006` is the **blocked state** — prevent a test starting, state the reason, give support contact. Together they give the *delivery mechanism* — the server can say "you are blocked, here is why" — but **no requirement anywhere obliges a minimum admissible application build.** Searched the whole requirements document | [OBSERVED] `product/FR-01/requirements.json`, `FR-PLT-005`, `FR-CFG-006` | **OQ-13**, owner Product + QMS |
| L11.7b | Consequence of L11.7a, recorded rather than papered over: AD-25 builds the floor because the compliance note requires the capability, but **an invariant with no requirement behind it is not verified under `FR-LCM-017`**. That is why it goes to Product as OQ-13 rather than being quietly absorbed. Also: both hooks are **M3**, so no build can be blocked at M1 or M2 at all | [INFERRED] | OQ-13; AD-25 |
| L11.7c | **Rollback blocking and the version floor are one control, not two.** The guidance asks to "block version rollback — let the app be updated, never downgraded to an older, weaker build." A normal user cannot downgrade on either store, so the only real defence is the server refusing to admit a build below the floor. Stated in AD-25 rather than assumed from the stores | [ADOPTED] method; [OBSERVED] `compliance/…:106-114` | AD-25 Rule |
| L11.7d | **The load-bearing call, and it dissolves rather than resolving.** AQ-11 framed it as whether the floor is *exempt* from AD-13's snapshot rule. It is not really an exemption: the floor is **admission control evaluated before an exam exists**, and AD-13 governs the configuration in force *for an exam* (`FR-CFG-003`). A build that is refused never runs a test, so there is nothing to reconstruct — the gate is upstream of AD-13's scope, not carved out of it. Snapshotting it would make the kill switch only as fast as the next publication plus cache expiry, which is the opposite of the obligation | [ADOPTED] user, 2026-08-23 — AQ-11 options 1 and 3, which converge | AD-25 Rule; AD-13 amended in place |
| L11.7e | AD-13 nonetheless names the exemption **in place**, because an unnamed exception is how a rule erodes — the same move L11.2i made for AD-6. Its Rule now reads that one namespace is exempt, that AD-25 names it, and that **there is no other exemption**. Reconstruction is preserved by recording the floor in force on the exam's configuration snapshot | [ADOPTED] method | AD-13 Rule; id unchanged |
| L11.7f | **A hotfix skips the train and never a gate.** The estate's tool cuts a release branch to staging on the first Sunday of the sprint and to production on the second, so a fix landing on the wrong day waits up to two weeks; the tool already has `prod-hotfix`. The trap is `FR-LCM-017`, which requires release testing before *each* release — if a hotfix needs the full cycle it is not fast and the capability exists on paper only. Resolved by scoping: **release testing for a hotfix is the change plus a regression set named in advance**, never scoped in the moment by whoever is in a hurry, and every AD-24 blocking gate still applies | [ADOPTED] user, 2026-08-23; [OBSERVED] absorbed answers Q14.4 (L12.8) | AD-25 Rule; Consistency Conventions branching row amended |
| L11.7g | **The patch metrics need no new telemetry.** The guidance says we will be asked for time from discovery to patch and from patch to phones. `exam.device_snapshot` already carries application and operating-system version on every exam, so version distribution across the fielded estate is a query. Stated in AD-25 so nobody builds a second pipeline for it | [OBSERVED] `data_model.md:255-256` | AD-25 Rule |
| L11.7h | Not answered, and deliberately: **who owns the fielded-version risk assessments** the guidance asks for per released version, and how long the build environment and test suite for each release are kept alive. Both are QMS lifecycle process rather than architecture, and they fold into OQ-1's owner list rather than earning an id | [UNKNOWN] | OQ-1 |

### L11.8 — Housekeeping: an `L11` id collision, repaired

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.8a | **AQ-02 and AQ-10 both claimed `L11.2`** — the exact collision `questions/README.md` predicts for concurrent sessions, and it had already reached four citing documents. AQ-10 landed first and keeps `L11.2`; AQ-02's section and its nine rows are renumbered to `L11.3`, with citations updated in `spine.md`, `architecture_points.md` and `questions/AQ-02.md`. Nothing decided in either section changed. Recorded because the log is the authority and a duplicate id in the authority is worse than a renumber | [OBSERVED] two `### L11.2` headings | Renumber applied; a note sits under the `L11.3` heading |
| L11.8b | The AD ids did **not** collide only by luck of ordering — AQ-02 took AD-22 before this session wrote anything. Session 3's ADs are therefore **AD-23, AD-24, AD-25** and its open question is **OQ-13**, after AQ-02 took OQ-11 and OQ-12. Confirms the README's guidance: concurrent sessions should stop after step 1 and land together | [ADOPTED] method | `questions/README.md` §"Running sessions in parallel" |

### L11.9 — AQ-01, backup, restore and disaster recovery. Durability made directional rather than synchronised

**Ids taken.** `AD-26`, `OQ-14`, one Deferred row. Amendments in place to `AD-18`, `AD-22` and the
`OQ-3` row. Session 3 had taken AD-23–AD-25 and OQ-13 while this question was being worked (L11.8b),
so the ids continue from there.

**The premise the AQ started from could not be delivered.** AQ-01 leaned toward "one recovery point
across both stores, stated as an invariant". No mechanism gives a consistent point-in-time across
Cloud SQL and GCS, so that AD would have been an invariant nobody could implement — worse than the
silence, because a stated-but-unimplementable rule stops the question being asked again.

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.9a | **The guarantee is directional, not synchronised.** A row referencing an object is written only after that object is durably stored, so the database is always **behind or equal to** object storage and never ahead; an object is never deleted while a live row references it; and there is no bucket-wide rollback — object loss is recovered per-object from a version. A database restored to an earlier point therefore references only objects that still exist. The two stores do not need a shared recovery point; they need a guaranteed direction | [ADOPTED] method | AD-26 Rule |
| L11.9b | **The upload lifecycle already almost gives it.** The device sequence is `notStarted → sendExam → uploadTrace → validateColorboardQR → getResults → userStepsEnded → uploadFrames → runEnded`, so the object lands before anything references it. AD-26 turns an incidental ordering into a rule, which is what makes it reviewable rather than a property that survives until someone reorders a handler | [OBSERVED] `data_model.md:117-119` (`Progress.swift:25-34`) | AD-26 Rule |
| L11.9c | **The lifecycle-rule trap is named because it is live.** A rule deleting record-bearing objects by age deletes half the record while AD-4 keeps the row. So no lifecycle deletion independent of the record: a purge is one joint operation across both stores and OQ-3 owns the period. This is the same trap L11.1g recorded for the `algorithms` bucket silently un-freezing a study, which is why `algorithms` is inside AD-26's binding scope | [INFERRED] from AD-4 and L11.1g | AD-26 Binds and Rule; OQ-3 row amended |
| L11.9d | **Record-bearing buckets may be dual-region or multi-region, in-jurisdiction.** AD-22 as written forbade the single largest available durability win, and worse, someone could have chosen a multi-region `US` location believing the invariant was satisfied. AD-22 now permits a dual- or multi-region location provided every constituent region is inside the deployment's jurisdiction. Geo-redundancy is a durability instrument, not a residency exception | [ADOPTED] user, 2026-08-23 | AD-22 Rule amended in place; id unchanged |
| L11.9e | **AD-18 keeps its absoluteness; the rehearsal moves instead.** Restoring a production backup into staging would breach AD-18, and an unrehearsed restore is not a durability contract. The rehearsal runs in an ephemeral restore-verification environment **inside the production deployment** — same project, region and IAM boundary — destroyed when it ends, evidenced under `FR-LCM-010`. AD-18's prohibition list is enumerated and this is none of those entries, but it had to be *said*: otherwise AD-18 reads as "anywhere but the production namespace". The alternative — carving an exception into AD-18 — was rejected because AD-18's force is that it admits none, and the per-branch seeding mechanism would then have a precedent to cite | [ADOPTED] user, 2026-08-23 | AD-18 Rule amended in place; id unchanged |
| L11.9f | **No figure is invented.** The RPO and RTO figures, and the rehearsal cadence, are OQ-14, owner Backend owner + DevOps. The tolerance input is recorded with the question because it is sharper here than usual: AD-5 consumes the kit in the same transaction as the exam write, so data lost after commit is a **spent kit plus a record AD-4 forbids repairing** — the patient needs a new physical kit and the result cannot be reconstructed for `FR-ALG-004`. Data loss is not "re-run the pipeline" | [UNKNOWN] | OQ-14 |
| L11.9g | **`dr` stays declared, and becomes a Deferred row rather than a deletion.** The user declined both removing the declaration and building a warm standby. Deferred is the method's answer to "decide later", and the dependency is real: whether a warm standby is worth a second estate is a function of the RTO figure, so the Deferred row is gated on OQ-14. The false affordance is neutralised in the document instead of the repository — the Structural Seed environment list now states there is no DR environment, and AD-26 states that nothing is built on `dr` until OQ-14 states an RTO | [ADOPTED] user, 2026-08-23; [OBSERVED] absorbed answers Q14 (L12.8) | New Deferred row; Structural Seed; AD-26 Rule |
| L11.9h | **`data_model.md:333`'s objection is answered rather than left standing.** Alternative C was rejected partly because "the regulatory record now spans two systems with two backup and restore stories, which `FR-LCM-010` has to verify as one." Alternative A reduced that but did not remove it — frames and traces still live outside the database. AD-26 is what makes the two stories verifiable as one: not by synchronising them, but by making one of the two orderings impossible | [OBSERVED] `data_model.md:333-338` | Source annotated |


### L11.10 — AQ-05, where normalisation happens. The placement stays open; the invariant that holds either way is landed

**Ids taken.** `AD-27`, `OQ-15`. Amendments in place to the `OQ-3` and `OQ-9` rows and to the
Capability → Architecture Map. Re-read before landing: sessions 1–3 and AQ-01 had taken AD-23–AD-26
and OQ-13–OQ-14 while this question was being worked, so the ids continue from there.

**The placement was not answerable in this session, and that is the correct outcome rather than a
stall.** The user stated plainly that they do not hold the context to decide it. `FR-IMG-016`'s own
note agrees — it records both halves as undecided — so there was no answer to elicit, and inventing
one would have been the `SDLC.md` failure the AQ file names: filling a QACR intent by inference from
what ACR does.

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.10a | **The placement is OQ-15, owned by the algorithm owner with the backend owner.** Unblocked by an IVTS specification revision stating the representation and where the transform runs — not by a backend preference. What architecture asks for back is deliberately narrow, and is written into the OQ so the question put to the algorithm owner is answerable: **which artefacts cross the algorithm port, and which of them are retained** | [UNKNOWN] | `FR-IMG-016` note, "whether normalisation happens on the device or in the backend, is undecided… See review register Q-24"; OQ-15 |
| L11.10b | **AD-27: exactly one component normalises, and the algorithm port names which.** This is the half that is architecture's regardless of placement, and it is the reason the question could not simply be parked. The divergence is not the placement but the *duplication*: the device normalises for capture guidance under `FR-IMG-002` and `FR-IMG-009` while the backend normalises again for colorimetry, and the Detection Well values derive from a twice-transformed image. Neither unit's own tests see it, because each is individually correct | [ADOPTED] method | AD-27 Prevents and Rule |
| L11.10c | **The record half is stated as a conditional that binds both branches**, rather than left to the branch that wins: if the backend normalises, the raw or raw-equivalent input **and** the normalisation version are retained; if the device normalises, the normalised frames plus the `FR-CAM-003` camera parameter set and the application version are, and the backend never re-normalises. Without this, `FR-ALG-004` reconstruction is satisfiable on paper while the artefact the algorithm actually consumed cannot be reproduced | [ADOPTED] requirement text | `FR-ALG-004`, `FR-CAM-003` ("Required for IVTS traceability"); AD-27 Rule |
| L11.10d | **A correction to `data_model.md` §7.2.** It reads "If backend, raw or raw-equivalent frames must be retained and the frame table grows accordingly", which presents retention as an existing obligation. `FR-ALG-004`'s "raw results" is **algorithm output, not raw frames**, and no requirement obliges raw-frame retention. It is a consequence of choosing backend normalisation under AD-27's record rule, not a requirement already in hand. Stated so the storage-sizing conversation is not held against an obligation that does not exist | [OBSERVED] `product/FR-01/requirements.json`, `FR-ALG-004`; `data_model.md` §7.2 | Source annotated |
| L11.10e | **The seam with AD-23 is named because it would otherwise be read wrongly.** AD-23's convention says a stored checksum is always the client-supplied digest the server verified, never a server-computed one. If the backend normalises, the normalised object has no client digest at all. AD-27 states that a backend-produced normalised object is record-bearing under AD-26 but is **not an ingest**, so the AD-23 rule does not reach it | [INFERRED] from AD-23 and AD-26 | AD-27 Rule |
| L11.10f | **The knock-on is recorded on the two items that wait, not only in the OQ.** `OQ-3` cannot size frame storage until this is answered — raw frames are materially larger — and `OQ-9`'s percentiles measure a different workload depending on it, so the same figure means a different thing. Both rows amended in place | [INFERRED] | `OQ-3`, `OQ-9` rows |

### L11.11 — AQ-08, the pseudonym-to-patient mapping. No mapping; the derived identifier ruled out; the M5 proxy caught

**Ids taken.** None. `AD-8` amended in place, id unchanged, as the AQ file directed.

**Answerable from evidence without the context the user did not have.** Reading the requirements
changed the question's shape: `FR-ANL-001` (M3) has the *software* transmit events to the analytics
service, and `FR-ANL-003` requires only that the analytics service cannot resolve the identifier. The
backend is **not on the analytics path at all** before M5. So "does the backend hold the mapping"
resolves to "does the backend issue the pseudonym", and nothing asks it to.

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.11a | **Option 1 taken: no mapping. The pseudonym is generated on the device and is never issued, received or stored by this backend.** Not chosen on preference but because a backend-issued pseudonym would require inventing a route no requirement asks for — the method's "never invent to fill a gap", pointing at absence for once | [ADOPTED] requirement scope | `FR-ANL-001`, `FR-ANL-003`, `FR-ANL-004` (M5, proxy is future development); AD-8 Rule |
| L11.11b | **The derived identifier is ruled out in writing, which was the point of the question.** A `hash(patient_id)` is resolvable by anyone holding the patient identifier and the salt, so the mapping exists whether or not a table does — a disclosure surface with no artefact anyone would think to register, and the default outcome of nobody deciding. AD-8 now says a derivation *is* a mapping | [ADOPTED] method | AD-8 Rule |
| L11.11c | **Option 2 is not foreclosed; it is priced.** The user's context for whether support needs event-to-patient resolution was not available, so the rule makes the absence the default and any mapping a deliberate act on AD-8's existing terms — a named row in the register with a stated retention, and every read an `FR-SEC-013` privileged read under AD-17. This is the L8.1 pattern ("locatability and containment", a new PII-bearing column being a deliberate act) applied rather than a new mechanism. If support later states a need, it is a registered addition, not a redesign | [ADOPTED] method, extending L8.1 | AD-8 Rule |
| L11.11d | **A silent dimension the AQ file did not carry: `FR-ANL-004`.** At M5 analytics events travel "through the configured proxy endpoint rather than directly to the analytics provider". A QACR-operated proxy sees the authenticated session and the pseudonym **in the same request** — that is the mapping, materialised in logs, arriving by a route AD-8 did not cover. The word "proxy" appeared nowhere in the spine in this sense. AD-8 now binds it as a pass-through: no event body, and no session-to-pseudonym correlation, in application or access logs | [OBSERVED] `product/FR-01/requirements.json`, `FR-ANL-004`; spine text before this entry | AD-8 Rule |
| L11.11e | **The two pseudonyms must not be one value.** OQ-12 records that research reconciles on the study kit identifier. Were that value and the Mixpanel pseudonym ever the same, a research row joins analytics data and both containment arguments fail at once — and each would still look correct read on its own. AD-8 states they are never the same value | [INFERRED] from AD-8's research clause and OQ-12 | AD-8 Rule |
| L11.11f | **What this costs, named rather than buried:** support cannot answer "which patient is this analytics event", and a device-generated pseudonym is per-install, so under `FR-AUT-011` (M5) two registered users on one phone are one subject in the analytics funnel. Neither is a clinical or safety concern, and both are visible to Product if either turns out to matter | [INFERRED] | Recorded here, not in the spine |

### L11.12 — AQ-06, results-centre scope. AD-23 amended; the Product half goes to OQ-18

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.12a | **AQ-06's premise expired between raising and answering, and that changed the landing.** The file proposed a new AD on the ground that nothing in the spine protected the boundary between two patients sharing a handset. True when written; by the time it was worked, session 3's **AD-23** already carried `FR-COM-010` — "every request is checked for entitlement to the record it addresses… acting on a patient record other than the verified user's is rejected". So this lands as an **amendment to AD-23**, not AD-28. A second AD on one concern is the AQ-09 failure shape: each unit cites the AD that supports what it was going to do | [OBSERVED] AD-23 Rule, landed under L11.6 | AD-23 amended in place; id unchanged |
| L11.12b | **The backend half was never a lean — it is an M3 requirement.** AQ-06 offered it as "lean: yes, it costs nothing to hold now". `FR-COM-010` *requires* it: reject any request "attempting to act on a patient record other than the one associated with the verified user". Recorded because the distinction matters for `FR-LCM-017` — an invariant with a requirement behind it is verified, an architectural preference is not | [OBSERVED] `product/FR-01/requirements.json`, `FR-COM-010`, milestone 3 | AD-23 |
| L11.12c | **A source correction, and the reason the clause needed landing at all.** The absorbed Q13 answer listed `FR-COM-010` in its "already in user-management" column beside the `exchange-session-nonce`/`validate` keypair JWT pair. Only the token half is inherited: user-management verifies *who the bearer is* and has no concept of an exam, a result or a results centre, so it cannot decide whether a request touches a patient record other than yours. Upstream asserting the obligation was met elsewhere is why it went un-carried for so long | [OBSERVED] absorbed answers Q13 (L12.8); `be-infra` user-management has no exam or result model | Corrected in the source at the time; the source is now absorbed — L12.9c |
| L11.12d | **The load-bearing clause is the one about the phone number, not the one about entitlement.** "Check entitlement" is advice; a unit can satisfy it by scoping a query to the phone number and calling that the verified user's records. The invariant is therefore stated as a single key — the resolved patient identifier is the only accepted scope, a **required argument** of the read rather than a filter the caller applies, resolved in one place — and the phone number is **never** a scope, query key or lookup path. Mechanically checkable: no repository method accepts one | [ADOPTED] method — AQ-06's stated invariant, sharpened | AD-23 Rule |
| L11.12e | **This is what makes M5 an addition rather than an amendment.** `FR-AUT-011` permits many patients per number and `FR-AUT-015` adds switch-user, both M5; the inherited `Users.phone` is already nullable and not unique, so the schema permits it today. Under the single-key rule, switching user re-resolves the subject and does not widen the scope, so no AD is revisited when M5 lands. AQ-06's "what gets built if nobody answers" — scoping that silently becomes scoping-by-phone — is closed | [OBSERVED] `FR-AUT-011`, `FR-AUT-015`; Inherited Invariants | AD-23 Rule |
| L11.12f | Also stated, because AD-17 would otherwise look contradicted: **privileged cross-patient reads exist**, on the management plane only, each emitting an `FR-SEC-013` audit event. An unnamed exception is how a rule erodes — the same move L11.2i made for AD-6 and L11.7e for AD-13 | [ADOPTED] method | AD-23 Rule |
| L11.12g | **The Product half was not answered, and could not be.** `FR-PRT-001`'s own note says whether invalidated tests appear and whether another registered user's results are excluded "**are to be specified**". A requirement that says it has not been written yet cannot be read more carefully. Raised as **OQ-18**, owner Product, both bits in one question | [OBSERVED] `FR-PRT-001` note; `SDLC.md`:99 | OQ-18 |
| L11.12h | Recorded in OQ-18 so the default is not mistaken for a decision: AD-23 makes the shipping behaviour **strict per-user scoping**, so household visibility is a **new rule** with an explicit partner-configured opt-in and never a relaxation of AD-23. Evidence that this is the likely product intent — `FR-AUT-015` switch-user and `FR-AUT-020` blocking a second test on a shared number until the user switches — is recorded as evidence and **not** treated as the answer, per `SDLC.md`. The invalidated-test half has **no safe default** and OQ-18 says so | [INFERRED] evidence only | OQ-18 |

### L11.13 — AQ-07, consent timing. No conflict to resolve; the requirement already closed it

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.13a | **The session's finding: there is no conflict, and three documents described one.** AQ-07, `data_model.md` §7.5 and the questions README all frame this as a live conflict between the requirements document and the backend SRS, to be surfaced and not resolved. `FR-CNS-007`'s own note resolves it and names the direction: the SRS "makes consent recording mandatory before a test starts as SRS-BE CON.1, **so that document is to be relaxed to match**". `product/` governs the wording per `SDLC.md`, so this is reading the governing document, not picking the more likely reading. None of the three quoted the sentence | [OBSERVED] `product/FR-01/requirements.json`, `FR-CNS-007` note | AQ-07; `data_model.md` §7.5 corrected |
| L11.13b | **The M3 question dissolves for a second, independent reason.** `consent_ack` could not move to M3 even if the SRS position had held, because the acknowledgement it records does not exist at M3: `FR-CNS-002`/`FR-CNS-003`, the mandatory-checkbox gate, are **M4** by recorded product decision — "users do not go through phone verification at milestone 3, so no personal information is collected before the acknowledgement gate exists". Earliest acknowledgement M4, earliest recording M5 | [OBSERVED] `FR-CNS-002` note | AQ-07 |
| L11.13c | **Landed as a Deferred row, not an AD.** The decision is that no mechanism is built: exam creation acquires **no consent precondition at M3 or M4**, and AD-3's idempotency key and AD-5's kit consumption keep the transaction they have. Stated rather than defaulted, because the SRS is still readable and a developer following it would add a check to the most contended write path in the system | [ADOPTED] `product/` governs | New Deferred row in `spine.md` |
| L11.13d | **What survives is narrower than AQ-07's framing and is genuinely open.** `FR-CNS-007` says only "record, and transmit… the identity and version of each policy document acknowledged, together with the time of acknowledgement" — recording, with **no statement either way** about whether a recorded acknowledgement is a precondition of a test at M5. That one bit is the Deferred row's revisit condition. A yes puts a third check inside the AD-5 transaction, which is why it is worth asking before M5 rather than during it | [UNKNOWN] | Deferred row |
| L11.13e | **A QMS traceability defect, named so it has somewhere to be found.** "To be relaxed" is an intent in a review note, not a document change; SRS-BE CON.1 still mandates consent before a test starts. A submission whose SRS requires behaviour the product deliberately does not implement is a traceability finding. Not architecture's to fix, and not architecture's to leave unnamed either | [OBSERVED] `FR-CNS-007` note, unrelaxed as of 2026-08-23 | Deferred row; QMS |
| L11.13f | **No `decisions/D-nn` raised, against the kickoff prompt's instruction.** The prompt directed this to `decisions/` on the premise of an unresolved conflict. The premise did not hold, and raising it would spend Product's attention re-deciding what `product/` already records. Recorded explicitly because declining a directed action needs a reason on file: if the SRS relaxation turns out not to be drafted as recorded, this reopens | [ADOPTED] method | AQ-07 |
| L11.13g | Considered and **not** taken: naming `consent_ack` in AD-4's insert-only Binds list now, so the M5 table cannot be built as a mutable "current consent" row — which would destroy the ability to show what was acknowledged at the time of a given exam. AD-4's list names tables that exist, and binding one that does not is the sort of forward claim this method avoids. The constraint is instead stated in the Deferred row's revisit condition, where whoever builds the table will read it | [ADOPTED] method | Deferred row |

### L11.14 — AQ-13, the three residual security items. L3.7 closed

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.14a | **Q-63, session token expiry — AD-6 amended in place, value to OQ-16.** Under AD-6 the TTL is user-management's to enforce, set per tenant via `Apps.tags.expirationTimeInSeconds` with values checked in at `partnerTokenExpirations.json`. So it is a value **QACR chooses and does not host**: changing it is a configuration change in a repository QACR does not own, which is worth stating rather than leaving implied, because a dimension living in someone else's file is exactly the kind that reads as forgotten | [OBSERVED] absorbed Q13 table (L12.8); values at `configurations/configFiles/userManagement/partnerTokenExpirations.json` | AD-6 Rule amended; id unchanged |
| L11.14b | **AQ-13 mis-graded Q-63 as bookkeeping, and L11.4d is why.** AQ-03's session declined a nonce on the frame and trace paths on the explicit ground that what a captured request is worth is bounded by **token lifetime** rather than replay protection — and assigned Q-63 here while doing it. The TTL is therefore a mitigation AD-23 leans on, not a preference. AD-6 states the qualitative bound: short enough that `FR-SEC-008`'s "a retained session token shall not by itself grant access" is a real bound | [OBSERVED] L11.4d | AD-6 Rule; OQ-16 |
| L11.14c | **The number was not picked, against the compliance note's instruction to "pick a value now".** `FR-AUT-013`'s note records the SRS's 24 hours as "flagged at review as incorrect for this application" with no replacement chosen. A session lifetime for a patient holding a kit mid-test is a clinical-workflow and security judgement with a named owner; inventing a figure to close a row is how the 24 hours got there. OQ-16, owner backend owner + QMS | [UNKNOWN] | OQ-16 |
| L11.14d | **Q-03, minimum OS versions — absorbed, no new id.** AQ-13 predicted it belonged with AQ-11; AQ-11 has since landed **AD-25**, which puts the `FR-PLT-005` supported operating-system and hardware list into a narrow control-plane namespace read **live** at the eligibility exchange. That satisfies the note's own instruction — "this will move, so do not hardcode against the low numbers" — structurally rather than by discipline: iOS 13 and Android 8 become values to change, not constants to edit. The residual AQ-11 found is already **OQ-13** | [OBSERVED] AD-25 Rule, landed under L11.7 | No new id; disposition recorded |
| L11.14e | **Q-81, screenshot versus the results PDF — OQ-17.** Two requirements contradict outright, so `SDLC.md` forbids resolving it by reading. `FR-SEC-007` (M3) bars capture of any screen holding personal, health or result information and its note records it as **"the sole control for SPTA 4.14, gross score 12"**; `FR-SHR-015`/`FR-PRT-009` (M5) require the letter to be savable to the phone and emailable | [OBSERVED] `FR-SEC-007`, `FR-SHR-015` notes; `compliance/…:192-194` | OQ-17 |
| L11.14f | **Why Q-81 did not simply go back as device-side.** `FR-SHR-015`'s note records that "the backend SRS requires letter generation and transmission as SRS-BE COM.10" — the letter is generated **backend-side** at M5. If Product resolves toward saving, QACR owns generation and transport and `FR-SEC-007`'s control has to be restated rather than silently narrowed at a developer's desk. The choice is Product's, via OQ-17; the consequence — restating `FR-SEC-007`'s control — is the spine's | [OBSERVED] `FR-SHR-015` note | OQ-17 |
| L11.14g | Recorded in OQ-17 and deliberately **not** chosen: a letter emailed from the backend to a patient-supplied address never enters device storage and would leave both requirements intact. It is a different product behaviour from the one `FR-SHR-015` describes, and substituting it would be architecture answering a Product question with a design | [INFERRED] | OQ-17 |
| L11.14h | **AQ-13 called itself minor; it was right about the decisions and wrong about the cost.** Two of three were not the spine's to decide, but all three were recorded as open in L3.7 and silent in the artefact — indistinguishable from forgotten, which is the condition the log exists to prevent. The spine now says for each where it lives: `partnerTokenExpirations.json` under AD-6, the live-read namespace under AD-25, Product under OQ-17. **L3.7 is closed** | [ADOPTED] method | L3.7 annotated in place |

### L11.15 — All thirteen `AQ` items landed; the finalize checklist is now due

| # | Decision | Tag | Evidence / rationale |
| --- | --- | --- | --- |
| L11.15a | Sessions 1 to 5 are complete: `AQ-01`–`AQ-13` all carry `status: landed`. The spine gained AD-20 through AD-27, amendments in place to AD-2, AD-6, AD-8, AD-13, AD-18, AD-19 and AD-23, OQ-11 through OQ-17, and Deferred rows for the study deployment model and for consent | [OBSERVED] `spine.md` | |
| L11.15b | Per `questions/README.md`, the spine's **finalize checklist is now due** against the amended document — the review pass, the input reconciliation and the `[ASSUMPTION]` sweep. Two known inputs for it: this session corrected the absorbed Q13 answer (L12.9c) and `data_model.md` §7.4 and §7.5, so the input reconciliation has fresh material; and the review pass should check whether the eight new ADs introduced any pair of the AQ-09 shape, since AD-23 alone was amended by two different sessions | [ADOPTED] method | Not yet run |
| L11.15c | Session 5 confirmed the README's own warning about concurrency from the other side. Sessions 3 and 4 landed **while session 5 was reading**, which is why AQ-06's new AD became an AD-23 amendment (L11.12a) and Q-03 needed no id at all (L11.14d). Both are better outcomes than the AQ files predicted, and both were only visible because the spine was re-read before writing. Recorded as evidence for the README's "stop after step 1, land together" guidance | [OBSERVED] AD-23, AD-25 present on disk after the initial read | `questions/README.md` §"Running sessions in parallel" |

## L12 · Absorbed source material, 2026-08-26

`HANDOFF.md` (the investigation's provenance, 2026-08-17/19) and `architecture_points.md` (14
answered questions, 8 open items, 7 OZ comments, 2026-08-17/19) were **folded into this log and
deleted**, at the user's direction, reducing `architecture/` toward four documents: the spine, this
log, `architecture_plan.html` and `data_model.md`.

Nothing above is re-argued here. What follows is the part of those two documents that other rows
cite, or that only they recorded: the evidence the adopted findings rest on (`E-1`–`E-14`), the
provenance caveat that qualifies it, the corrections that stop the next session chasing dead
references (`C-1`–`C-7`), the gaps left open deliberately (`G-1`–`G-6`), the user's answers verbatim,
the seven OZ comments verbatim, and where each of the fourteen answers ended up.

Citations that read `HANDOFF §3.n` in this file and in `spine.md` now read `E-n`.

### L12.1 — The evidence base (`E-1`–`E-14`)

The facts the adopted findings rest on. If one is stale, the row above it changes. Every citation is
a path read at repository HEAD on 2026-08-17 — see L12.2 for how, and for what qualifies it.

| # | Finding | Tag |
| --- | --- | --- |
| E-1 | **`backend.q-acr` has never been deployed to production.** `helmfile.d/qacr.yaml` contains only `qacr-develop` (GKE `dev-stg`, EU) and `qacr-research` (GKE `research-us`); it declares `production` and `dr` with **no releases in them**; there is no `qacr` file under `values/healthyio-prod/`; `ROLLBACK.md` records prod as "(separate deploy) — —". The single most load-bearing fact in the investigation | [OBSERVED] `helm-charts/helmfile.d/qacr.yaml`, `values/healthyio-prod/`, `backend.q-acr/ROLLBACK.md` |
| E-2 | **Every route sits behind one shared static token.** `user/services/user-app/src/app.ts` (and `research-app`, `utility-service`) mount `basicAuth({ token: process.env.RESEARCH_APP_TOKEN \|\| '' })` — a literal base64 string compare, defaulting to the empty string. `worker-api` and `utility-service` mount **no auth at all** and are publicly ingressed. There is no per-patient identity anywhere in the repo; the `users` table has no reader and there is no login endpoint | [OBSERVED] `backend.q-acr/user/services/*/src/app.ts`, `be-infra/packages/middleware/lib/basicAuth.js` |
| E-3 | **The QACR iOS app's *Production* environment points at the research namespace** — `flowURL = https://user-app.qacr-research.research-us.healthy.io/`. Consumer traffic lands in the research realm through a public ingress. That is the workaround production replaces | [OBSERVED] the iOS app's *Production* environment `flowURL` |
| E-4 | **ACR has no server-driven progress of any kind.** `getOrderStatus` collapses the 30 statuses in `beenums/src/orderStatus.ts` onto `pending \| has_results \| dry_stick \| error` (26 of 30 become `error`); no `socket.io`, `EventSource` or `text/event-stream` anywhere in `behealthy`; the algorithm run is scheduled *after* the HTTP response; push exists but every sender is in the outreach/back-office plane and nothing in the scan path emits one | [OBSERVED] `behealthy/infra/beenums/src/orderStatus.ts`, org-wide search |
| E-5 | **`be-infra` user-management already implements every mechanism `FR-AUT-*`/`FR-ACC-*` name** — phone + OTP with attempt/expiry limits and lockout, per-user-keypair JWT with per-tenant TTL and per-request validation, 4-digit PIN → `secure` claim, `Apps` + `Users.tags[app]` multi-tenancy — it is reached over public HTTPS at `accounts-{staging,production}.healthy.io`, **both QACR apps already carry the host compiled into their build config**, and it serves end-user (patient) auth across the estate, not just staff | [OBSERVED] `be-infra/projects/user-management/handlers/phone-verification/`, `lib/models/core/`, `enums.js`; both app build configs |
| E-6 | **There is no ArgoCD, Flux or Kustomize anywhere in the org.** The `argo` in `helm-charts/charts/argo-tunnel` is Cloudflare Argo Tunnel. The GKE standard is Jenkins → `yq`-patch the tag into `helm-charts` → commit → `helmfile sync`, adopted by `backend.q-acr` in 2025. The 2026 GHA→Cloud Run track (`data-platform`, `internal-healthy-broker`) is real but **no 2026 repo deploys to GKE** | [OBSERVED] org-wide search; `helm-charts/charts/argo-tunnel`; `backend.q-acr/Jenkinsfile` |
| E-7 | **Deployed tags are mutable.** Both QACR values files pin `tag: main-355` — `main-<jenkinsBuildNumber>` — and `ROLLBACK.md` states it is mutable. Jenkins already pushes an immutable 8-character SHA tag on every build. This is what blocks freezing a clinical study | [OBSERVED] `helm-charts` values files, `backend.q-acr/ROLLBACK.md`, `Jenkinsfile` |
| E-8 | **Repo naming: all 18 repositories created in 2026 use lowercase kebab `<product>-<role>`; zero use the dot form.** `qacr-spec` (2026-08-13) is the local precedent. There is **no written naming policy** in the org — `docs/`, the `.github` repo and `docs/engineering/engineering-uniformity.md` were searched. The convention is derived from creation dates | [OBSERVED] org repository listing; searches named |
| E-9 | **QACR does not use config-server at all** — zero references in `backend.q-acr`, no `configFiles/qacr*` in the `configurations` repo. A production QACR backend is the first QACR service that has to onboard | [OBSERVED] `backend.q-acr`, `configurations/configFiles/` |
| E-10 | **The commercial estate is already split** into an event-decoupled ring (fulfilment, adherence, BI, D2C — one publish or one callback each) and a fused core (`cc-api` ↔ behealthy Postgres, reached from the commercial backend by four hardcoded axios clients across 26 helm values files). **Billing does not exist anywhere in the org** — only a dead `Payment` model, an abandoned `paymentIntent` column and a test Stripe key in five CI workflows | [OBSERVED] `behealthy`, `cc-api`, `helm-charts` values, CI workflows |
| E-11 | **QACR's kit/colour-board tables are dead schema.** `ColorBoard`, `Lot`, `KitLot`, `Correction` exist in `common/prisma/schema/research/` as a structural copy of ACR's `color-board` service tables with **no writer** — no controller, no mutation, no import, an empty seed stub, and the only accessor (`kitLotRepository.getOneBy`) has no callers. What the flow uses is the string `exam.metadata.colorBoard` (`C1_1`, `Q1_2`, `Q1_3`), curated as `TagValue` rows by hand-written SQL migrations | [OBSERVED] `backend.q-acr/common/prisma/schema/research/`, `kitLotRepository` |
| E-12 | **The prod→research receiving half exists and is unused.** `Exam.prodId` is `String? @unique` with an index, and `MetadataSchema` accepts `prodSource`/`prodPatientId`/`prodExamId`/`prodExamOrderSession`/`prodPartnerName`. **Nothing writes any of them.** `prodId` appears only as a GraphQL filter and a CSV column | [OBSERVED] `backend.q-acr` Prisma schema, `MetadataSchema` |
| E-13 | **There is no EDC client in `backend.q-acr`.** `StudySetting.edcStudyId` is a reserved field; zero `castor` references in the repo. In ACR, EDC export is a clinician action in `research-portal` mapped to Castor field GUIDs, and starting a trial is manual database work | [OBSERVED] `backend.q-acr` schema and repo search; `research-portal` |
| E-14 | **ACR's partner delivery is nominally config, actually code.** Transport mechanics are declarative, but payload shape and clinical vocabulary are per-partner JS builders behind a `switch (partner)` in `behealthy/infra/beconfig/gatekeeper/index.js` — and an unknown partner returns `false` and **the message is silently dropped**. `partners-worker` also never nacks: a 590 s timer force-acks and every failure path acks and drops | [OBSERVED] `behealthy/infra/beconfig/gatekeeper/index.js`, `partners-worker` |

### L12.2 — Provenance of the `E` rows, and the map's known gaps

Four passes, and the provenance of each claim differs. (1) The ACR artifacts read directly — the
three-tier system map, the kit-lifecycle deep dive, the event contract, the FDA environment
precedent. (2) Three `mind`-based investigations run in parallel: deploy/CI/clusters/naming/
branching/configuration; `backend.q-acr` internals; the shared platform (user-management, ACR patient
auth, notifications, partner delivery, the ACR scan-to-result flow, the commercial surface). (3)
Requirement grounding — `product/FR-01/requirements.json` queried directly for the `SHR`, `LCM`,
`AUT` and `ACC` groups, and every `FR-*` id cited was checked to exist (51 ids, all valid). (4) A
constraint applied mid-session at the user's instruction: use `mind`, clone only if really required.
**No repository was cloned**; where the map was thin, targeted read-only `gh api` single-file reads
at HEAD were used. **Keep that constraint.**

**The caveat that qualifies every map-sourced claim.** `mind freshness` reported
`live_staleness.verified: false` — 0 of 179 extracts could be checked against live HEAD
(`gh: Not Found (HTTP 404)`). Map release 1.2.0, content generated 2026-08-14. Map-sourced claims may
lag HEAD; the `gh api` reads were current as of 2026-08-17. Where the two disagreed, the source read
won and the row says so.

Known map gaps, all re-extraction candidates, none blocking: `helm-charts` (the urine/qacr one) has
**no `deploys` extract** at all — only `helm-charts-wound` does, so everything about clusters,
namespaces and values files is a live read rather than a map fact; `backend.q-acr` recorded 6
endpoints against ~20 real routes; `behealthy auth-api` recorded 1 of its 4 routes; `send-results`
recorded **zero** endpoints.

### L12.3 — Corrections to the material the investigation started from (`C-1`–`C-7`)

Recorded so no later session chases them again.

| # | Correction | Tag |
| --- | --- | --- |
| C-1 | **`backend.q-acr/docs/app-exams-ingestion.md` does not exist** — not on HEAD, not on any of the 25 branches, and an org-wide filename search returns nothing. The ACR artifact cites it. The app-ingestion answer was reconstructed from the iOS client (`Progress.swift`, `ExamProvider+*.swift`) plus the server routes | [OBSERVED] searches named |
| C-2 | **`research-us` is a *cluster*, not a GCP project.** It lives inside `smiling-diode-638` (`gke_smiling-diode-638_us-central1-c_research-us`). The projects are `healthyio-prod`, `smiling-diode-638`, plus two AWS accounts | [OBSERVED] kube context |
| C-3 | **There is prior design work on an unmerged branch**: `backend.q-acr` branch `docs/qacr-existing-map-and-plan` carries `docs/qacr/{ARCHITECTURE_DIAGRAM,DB_ARCHITECTURE,EXISTING_URINE_MAP,FDA_ENV_VS_PRODUCTION,KIT_GAP_ANALYSIS,NEW_BACKEND_PLAN}.md`. The ACR artifacts are the published form of it. `NEW_BACKEND_PLAN.md` is referenced throughout them and was **never read** — it may answer or contradict parts of the absorbed answers. This is OQ-10 | [OBSERVED] branch listing |
| C-4 | **`helmfile.d/templates/env.yaml` is not the whole truth.** `qacr.yaml`, `behealthy.yaml` and `rehealthy.yaml` declare bare `environments:` and hardcode `kubeContext:` per release, so the template's environment→cluster table is overridden. `qacr` develop actually targets `dev-stg`, not `be-staging-uk` | [OBSERVED] `helm-charts/helmfile.d/` |
| C-5 | **Observed but unexplained:** `dev-stg_qacr-develop.yaml` deploys to the `dev-stg` cluster while its ingress hostnames still name `be-staging-uk`. Cause not determined | [UNKNOWN] |
| C-6 | **`USE_QUORUM_QUEUES` is read in code but set in neither values file**, while every queue is named `*_quorum`. Verify against the live broker before designing on it | [OBSERVED] `backend.q-acr`, `helm-charts` values |
| C-7 | **Treat "android-qacr → behealthy" in the `mind` map with suspicion.** `ENDPOINT_CLIENT_API` is a `qacr-*` host serving `backend.q-acr`'s `user-app`; the map resolved the edge to `behealthy` | [OBSERVED] `AndroidQacr` build config |
| C-8 | **The approved algorithm is not baked into the `algo-worker` image.** `architecture_plan.html` states it twice — "separate image (algo-base) · approved algorithm baked in" and "`algo-worker` runs the algorithm baked into its image". The worker instead fetches the algorithm as a **tarball from `ALGORITHMS_BUCKET` by blob key at runtime**, extracts it and caches it in an LRU, then spawns `./Classifier/run_classifier.py` inside `algo-base:5.0`. The image carries the runtime, not the algorithm. The spine's own boundary row is correct ("tarball in the production algorithms bucket plus an `algorithm_version` row"); the plan's rendering of it is not. Consequence carried into L14 | [OBSERVED] `backend.q-acr` `21b8cf9` `common/services/algo-worker/src/lib/{algorithmCache,algorithmExecution}.ts`; `architecture_plan.html` |

### L12.4 — Deliberately not established (`G-1`–`G-6`), and which row owns each now

Gaps in what was read, not in access. Each is cheap to close if it matters.

| # | Gap | Owned now by |
| --- | --- | --- |
| G-1 | **Algorithm wall-clock latency.** No figure exists in source; only the timeout policy (`ALGORITHM_TIMEOUT`, else `samples.length × 10 000 ms`) and per-step duration logging. Needs the metrics platform. Measure before tuning | OQ-9, and the Deferred autoscaling row |
| G-2 | **Client-side poll interval and the ACR waiting UI.** The mobile repos are readable; none were opened. No spinner or interval figure is known | AD-12 fixes the contract shape; the figure is build backlog |
| G-3 | **Exact RabbitMQ retry/requeue/DLQ counts.** They live inside `@ownhealthil/messenger@5.10.0` and `@ownhealthil/healthy-utils@0.10.0`, which were not read. `FR-RDY-012` and `FR-COM-006` both retry, so this is on the correctness path | AD-9's outbox contract; counts are build backlog |
| G-4 | **`send-results` outbound payload schemas** — HL7 segment layout, PCI/SES CSV columns, per-vendor SFTP path conventions. Flows, vendors and controllers were enumerated; the vendor services were not read | AD-10; the Deferred row on adopting the incumbent wire contract |
| G-5 | **What produces `exam.colorBoardError`** in the ACR exam-creation path — the board-register lookup itself was not traced end to end | OQ-7 (board-to-lot encoding) |
| G-6 | **`behealthy.patients.authId`** — column exists, no writer found, purpose unknown. Probably pre-UM legacy | Nothing. Recorded so it is not mistaken for a live mechanism |

### L12.5 — The best-practice review pass, 2026-08-17, and where each item lives now

The user asked whether the answers leaned too hard on what exists, given that greenfield is the
moment to adopt better practice. Verdict at the time: most answers land on best practice anyway
(modular monolith, single Postgres + RLS, polling, one-way prod→research) and were kept. The
strengthenings it added are recorded here with their present home, so it is visible that absorbing
the source dropped none of them.

| Strengthening added 2026-08-17 | Where it lives now |
| --- | --- |
| Transactional outbox for all event publishing | **AD-9** |
| "Immutable tag" upgraded to **image digest**, plus SBOM and image signing in the build pipeline | **AD-14**, **AD-24** |
| RLS implementation traps — `SET LOCAL` under pooling, no `BYPASSRLS`, CI policy tests | **AD-2** Rule, all three |
| OpenAPI-first contract, plus a `Retry-After` poll hint | **AD-12**; the `Retry-After` hint is `architecture_plan.html` §1.2, build detail rather than invariant |
| Mechanical module-boundary enforcement | **AD-1** Rule |
| user-management revocation, rotation and audit due diligence as a precondition | `architecture_plan.html` PQ-6 — still unowned |
| Dedicated tainted node pool for `algo-worker` | `architecture_plan.html` §2.1; Deferred (node-pool isolation) pending OQ-9 |
| NetworkPolicies as a stated requirement | `architecture_plan.html` §2.1 — deliberately not an AD; it prevents no divergence between units |
| Synthetic-only seed data for dynamic environments | **AD-18** |
| Workload Identity plus per-secret granularity over the `ENV_FILE` blob | Consistency Conventions → Configuration |
| Event payload `schema_version` on the prod→research contract | **AD-11**, Boundary With backend.q-acr, Conventions → Events |
| Q14.2 reopened — dedicated GCP project versus `healthyio-prod` | Closed: dedicated project and dedicated cluster [ADOPTED, user, 2026-08-23]. See L6.13, Structural Seed |

### L12.6 — The user's answers to the eight open items, verbatim (2026-08-19)

Quoted as written, typos included; this is the record. L1.1–L1.6 are the distilled form.

| Item | Question | Answer, verbatim |
| --- | --- | --- |
| 1 | Does Order survive into QACR? | "Order is currently out of scope for this phase, but will be added in the future , prefer to be decoupled as possible between the order and the kit and exam" |
| 2 | Backend retention of frames, traces and exam records | "backend retention should be same as we have in the ACR product, and according to regulations which we should follow up" |
| 3 | Which provider integration ships first at M3 | "defer for later answers" |
| 4 | The board → lot encoding for v1 | "rely on the same approach as ACR , try and simplify it if needed and possible" |
| 5 | Who owns EDC export | "defer to later , if needed rely on the status que" |
| 6 | `FR-ALG-003` and `FR-SHR-011` priorities | "defer" |
| 7 | `FR-KIT-005` kit valid-use period — withdrawn or deferred | Not answered. Carried as **OQ-6**, owner Product |
| 8 | Dedicated `qacr-prod` GCP project versus `healthyio-prod` | Not answered then. **Answered 2026-08-23**: a dedicated project *and* a dedicated cluster (L6.13), which voided Q14.1's "namespaces on the existing production clusters" |

Two of these ("same as ACR", "same approach as ACR") converted a decision into a read, and **neither
read was performed**. Both gate real design — retention sizes frame and trace storage, the encoding
gates the kit-register import. They are OQ-3 and OQ-7, and L3.3 and L3.4 are the same two facts.

### L12.7 — The seven OZ comments, verbatim

Written at the foot of the absorbed answers document, postdating both 2026-08-17 and 2026-08-19
reconciliation passes, and never folded into the answers. Quoted as written. L2 holds the collisions;
L8 holds the user's 2026-08-23 answers to OZ-2, OZ-5, OZ-1, OZ-6 and OZ-7.

| # | Comment, verbatim |
| --- | --- |
| OZ-1 | "Apply all the cyber security regulation on the architctual plan" |
| OZ-2 | "Save all PII in a dedicated table (n if already exisit" |
| OZ-3 | "What are we going to do with user managment and notfication worker services - we will copy them" |
| OZ-4 | "Keep solution as simple as possible , align with Solid principle" |
| OZ-5 | "keep current solution only to the point ,do not prepare infra for exentsion or implment what is not required" |
| OZ-6 | "make sure we have a monitoring guideline in every feature with which logs should be printed and with which information" |
| OZ-7 | "enable different managment backdoors - to maintain the product affectivly without extenral exposure" |

### L12.8 — Where the fourteen answers went

The absorbed document answered 14 questions with roughly sixty recommendations at mixed altitude.
This is the destination of each, so a reader who remembers a question can find its outcome. Anything
not listed was tuning value or build task — deliberately not architecture (L10).

| Q | Question | Destination |
| --- | --- | --- |
| Q1 | Repository names and the naming convention | Consistency Conventions → Repository and package naming; evidence E-8 |
| Q2 | Data model, three alternatives | AD-4; the alternatives and the inventory stay in `data_model.md` §3–6 |
| Q3 | The connection between research and production | AD-11, Boundary With backend.q-acr; evidence E-12 |
| Q4 | Clinical study — frozen version, tenancy, EDC | AD-14, AD-19, AD-13; Deferred (study deployment model, EDC export). Q4.1's borrowed "own logical database" was **not** an answer — see L11.1 |
| Q5 | Monolith or microservices | AD-1; Deferred (extraction of a role) |
| Q6 | Shared database or one per service | AD-2 |
| Q7 | Algorithm execution on a queue, and scaling | AD-1, AD-17, Runtime roles; every number → OQ-9 and the Deferred autoscaling row |
| Q8 | The partner interface | AD-10, AD-15; Deferred (which provider ships first) |
| Q9 | Scan to result; does ACR have progress | AD-12 (polling, no server-driven progress), AD-23; evidence E-4. The push-on-terminal-transition recommendation was **dropped** — L4.5, it builds an M5 capability at M3 |
| Q10 | Colour-board validation and kit onboarding | AD-5, AD-19; OQ-7; evidence E-11 |
| Q11 | Communication with the worker | AD-9, Stack (RabbitMQ), Conventions → Events; gaps G-3 |
| Q12 | No commercial implementation, extensible later | AD-16; Deferred (Order, commercial seams); evidence E-10 |
| Q13 | Login in one place | AD-6, Inherited Invariants; evidence E-5. Corrected 2026-08-23 — only the token half is inherited (L11.12c) |
| Q14 | Deploy — projects, clusters, CI, branching, configuration, environments | AD-14, AD-18, AD-22, AD-24, AD-25, Structural Seed, Conventions (Branching, Configuration); evidence E-1, E-6, E-7, E-9. Q14.1 is **void** — L6.13 |

### L12.9 — What the absorbed documents asserted that is no longer true

| # | Assertion | Status |
| --- | --- | --- |
| L12.9a | "Nothing in `architecture/` is committed — the whole directory is untracked on `master`" and the placement question behind it | Superseded. The directory is tracked on `master` (staged 2026-08-26) and stays in this repository — that answers L0.5's outstanding placement decision. The folder's contract is now the spine, this log, `architecture_plan.html` and `data_model.md`; the remaining inputs are being retired against that list. The repository-rule tension the question raised — `README.md:64` says this repository holds no reasoning, and this log is reasoning — stands as recorded in L10 |
| L12.9b | Q14.1 — new namespaces on the existing production clusters | Void. Dedicated project and dedicated cluster, L6.13 |
| L12.9c | Q13's `FR-COM-010` row — the whole requirement inherited from user-management | Corrected. Token half only; the patient-entitlement half is AD-23 (L11.12c) |
| L12.9d | Q9's "fire `notifications-worker.create-notification` with `type: pushNotification` on terminal transitions" | Dropped. Push is `FR-COM-013` at M5 (L4.5), and AD-7 bars a notification capability before then |
| L12.9e | The three named sources — the ACR artifacts, the `mind` map, `data_model.md` | Only `data_model.md` is part of this folder's contract. The ACR artifacts (`hadas_acr_artifacts/`) are evidence about the incumbent product, never a QACR decision per `SDLC.md`, and every claim this log took from them is restated as an `E` row with its own path citation — so the artifacts are no longer load-bearing for anything above. The `mind` map is a tool, qualified by L12.2 |

## L13 · Message broker choice for `qacr-backend` — one broker, not two

Raised as a direct question, not an `AQ` file: why does the incumbent estate run RabbitMQ and GCP
Pub/Sub side by side, and should `qacr-backend` do the same. Worked from the `mind` map plus source
reads of `behealthy` and `helm-charts`; landed as **AD-29**.

### L13.1 — What the incumbent split actually is, and why it exists

`behealthy` runs both brokers, but not by deliberate two-broker design:

- **Pub/Sub came first**, as one topic per worker type — algorithm, partners, ETL, health-check —
  with a single global subscription per type (`infra/bepubsub/src/pubsub.js`). Every partner's
  result-delivery message went through the one `partners` topic
- **RabbitMQ was added later, purpose-built for one integration.** Commit `75ebfc4b0`, "Change mesh
  to use new PW" (2021-06-30), introduced the `startResultDeliveryMethodType` per-partner flag and the
  RabbitMQ branch in `infra/bepubsub/src/partners/startResultDeliveryFlow.js`, then `8a4809bb5`
  (2021-08-01) extended it to other partners. The reason: `mesh-adapter` — the component that sends
  ACR results to NHS GP systems (EMIS/Vision/System1) as EDIFACT over NHS **MESH** — runs in a
  network-isolated AWS cluster wired to the NHS's private **HSCN** network
  (`helm-charts/values/aws-healthyio-prod/production_behealthy-production-hscn.yaml`: every other
  `behealthy` workload is `enabled: false` there; `ALLOW_SEND_TO_HSCN: true`; ingress locked to a
  hand-picked IP allowlist). GCP Pub/Sub is a Google-Cloud-bound API with no path into that boundary.
  A self-hosted RabbitMQ cluster does, because Healthy.io controls where it's network-placed
- **The split is per-partner and config-driven** (`partnerConfig.startResultDeliveryMethod`,
  `infra/bepubsub/src/partners/startResultDeliveryFlow.js:45`), not an architectural boundary anyone
  drew on purpose — it is a migration switch between an old delivery generation (Pub/Sub) and a new
  one (RabbitMQ) that never finished converging. **E-14** already recorded the cost: a
  `switch (partner)` gatekeeper where an unrecognised partner silently drops the message, and
  `partners-worker` never nacks — a 590 s timer force-acks and every failure path acks and drops

[OBSERVED] `behealthy/infra/bepubsub/{lib/messenger.js,src/pubsub.js,src/partners/startResultDeliveryFlow.js}`,
`behealthy` git history (`75ebfc4b0`, `8a4809bb5`), `helm-charts/values/aws-healthyio-prod/production_behealthy-production-hscn.yaml`,
`behealthy/projects/mesh-adapter/src/helpers/meshService.js`

### L13.2 — Why `qacr-backend` does not need the same split

`qacr-backend` has no NHS/HSCN-style network boundary today. **AD-22** fixes one region
(`us-central1`); the only place a message needs to leave the deployment's own broker is **AD-7**'s M5
`notifications-worker` push, and AD-7 already resolved that case with authenticated HTTP, not a
second broker — "a different project means a different broker, so the M5 push path cannot use AMQP."
RabbitMQ is already the ratified broker in **Stack** (L9). Nothing in `product/FR-01/requirements.json`
calls for Pub/Sub specifically, and introducing it now would buy a second client library, a second
retry/DLQ model and a second on-call surface with no requirement behind it — exactly the kind of
unrequired infrastructure OZ-5 asks to avoid ("do not prepare infra for extension or implement what is
not required").

### L13.3 — Decision

**AD-29**, landed in `spine.md`: one broker (RabbitMQ) for every internal async message. If a future
partner or integration needs to cross a boundary AMQP cannot reach — a different GCP project, a
different broker, or a compliance-isolated network like HSCN — the bridge is authenticated HTTP
behind the same per-partner adapter port **AD-10** already defines, generalising AD-7's M5 pattern
rather than adding a second broker technology. This is a call taken from the evidence above, not from
a `requirements.json` line; if a concrete future partner needs Pub/Sub specifically (for example, a
Google-native integration that only speaks Pub/Sub), that is a new case to raise against this AD, not
a reason to keep both brokers open by default now.

## L14 · The algorithm execution runtime — one artefact, two deployments

Raised while planning the production backend's algorithm path, once `user/services/user-app` in
`backend.q-acr` was confirmed as a stub to be replaced rather than extended, and separate databases
and separate deployments were settled. Worked from source reads of `backend.q-acr` and `helm-charts`.

**The plan placed the runner on the wrong premise, and the record inherited the omission.** It has
`algo-worker` as production's own image with the approved algorithm baked into it. The algorithm is
not baked in — it is fetched as a versioned tarball at runtime (**C-8**) — so the image is a generic
runner, and who builds it is a question the plan never had to ask and the spine therefore never
answers. AD-30 answers it.

**Proposed as AD-30 with OQ-19 and OQ-20; not adopted.** The evidence below is `[OBSERVED]`; the
decision is `[INFERRED]` from it and awaits the backend owner. `spine.md` is deliberately left
unamended — L14.6 carries the paste-ready text for when it is accepted, so nothing unadopted becomes
binding by being merged.

### L14.1 — What the estate already does

The worker is closer to a shared artefact than the spine assumes:

- **It is already built as its own image**, in a dedicated parallel Jenkins stage with
  `-f Dockerfile.algo-worker`, and pushed to
  `us.gcr.io/smiling-diode-638/backend.q-acr-algo-worker` alongside the main image
- **It holds no database client.** Its only `@prisma/client` use is two enum values —
  `ProductNames` and `MaterialType`, declared in `schema/shared/enums.shared.prisma` — consumed as
  runtime values in a zod schema and one comparison. No Prisma client, no repository, no query
- **Every piece of infrastructure is environment-supplied**, with no literals:
  `ALGORITHMS_BUCKET`, `RE_EXAM_SAMPLES_BUCKET`, `AW_QUEUE_NAME`, `AW_ROUTING_PATTERN`,
  `QACR_EXCHANGE_NAME`, `WORKER_API_URL`, `RABBIT_PREFETCH_COUNT`, `ALGORITHM_CACHE_SIZE`,
  `ALGORITHM_TIMEOUT`
- **The same image already runs twice**, as `algo-worker` on `qacr.aw.batchAlgorithm` and
  `algo-worker-short` on `qacr.aw.shortBatchAlgorithm` — separate Helm releases, separate quorum
  queues, separate KEDA scalers, one image tag
- **Nothing imports it.** It is a leaf service triggered by a published message, not a library;
  research fires it through `AlgoWorkerRoutingKeys.SHORT_BATCH_ALGORITHM`
- **The algorithm itself is already an artefact**, not code in any repository: fetched as a tarball
  by blob key from `ALGORITHMS_BUCKET`, LRU-cached and extracted, after which
  `./Classifier/run_classifier.py` is spawned inside the `algo-base:5.0` base image

So the worker's in-repo coupling is `@qacr/core` (170 lines) and `@qacr/rabbit` (145), both compiled
into the image at build time. Neither needs publishing for another deployment to run the image.

[OBSERVED] Read 2026-09-02 against `backend.q-acr` `origin/main` at **`21b8cf9`** and
`helm-charts` `origin/master` at **`1ed2669`**. Neither repository is in `evidence/pins.yaml`, which
scopes to the four application repositories `behaviour.tsv` cites; the commits are recorded here
instead, as L13 records `behealthy`'s.

`backend.q-acr/Jenkinsfile` (Build and Publish stages),
`backend.q-acr/Dockerfile.algo-worker:7,12,13,33`,
`backend.q-acr/common/services/algo-worker/{package.json,src/lib/{algorithmCache,algorithmExecution,utils}.ts,src/types/triggerAlgorithm.dto.ts}`,
`backend.q-acr/common/prisma/schema/shared/enums.shared.prisma`,
`backend.q-acr/research/services/research-app/src/services/triggerAlgo.service.ts:79`,
`helm-charts/values/smiling-diode-638/research-us_qacr-research.yaml:12,74,110`

All eight `backend.q-acr` files cited are byte-identical to `origin/main`, so nothing here rests on
the feature branch they were read from. The helm values file differs from `origin/master` only in
`global.image.tag` — `main-352` locally against `main-355` on master — which is the Jenkins
auto-bump described in L14.4 rather than a discrepancy in the rows cited.

### L14.2 — Why a second copy is not acceptable

`FR-LCM-009` requires each algorithm version, and each approved combination of mobile and backend
algorithm versions, to undergo verification and validation before release. `FR-ALG-004` requires the
exam to record the versions that produced its result. **AD-27** requires exactly one component to
apply the `FR-IMG-016` normalisation, with the artefacts crossing the algorithm port enumerated in a
contract and carrying a version.

Together those make duplication a validation problem rather than a maintenance one: if research
validates algorithm version X through one orchestration path and production runs the same version
through a copy of that path, the validation does not transfer, and the version recorded against a
production exam names a binary that was exercised somewhere else. Sharing the runtime is therefore
what makes one verification cover both executions — not a convenience.

### L14.3 — Why the result writer is not part of it

`worker-api` is the opposite shape. It imports `@qacr/prisma` five times plus `@qacr/repositories`
and `@qacr/algorithm`: it is the half that writes the database.

Production's must write insert-only `exam_result` (**AD-4**) under row-level security (**AD-2**), and
must accept a callback only against the single-use credential minted at job dispatch and bound to
that exam and that algorithm run (**AD-23**) — because first-writer-wins against one row per exam is
what makes an unauthenticated callback sufficient to become the clinical result. Research's has none
of that and needs none of it. So the compute is shared and the writer is per-deployment.

`common/algorithm` — `algoInputUtils`, `algoUtils`, `sampleAlgoErrorUtils` — sits with the trigger
side and the result side, both of which are per-deployment services, so it is copied rather than
shared. What must not drift is **what enters the algorithm and how its raw output is read**; what
each side does afterwards legitimately differs, production mapping onward to the `FR-ALG-012`
enumeration while research retains the raw output.

[OBSERVED] `backend.q-acr` at `21b8cf9` — `common/services/worker-api/src`,
`common/algorithm/src`, the latter imported by `worker-api/src/services/updateResults.service.ts`
and by four research services (`research-app/src/services/{triggerAlgo,sampleUploadCompletion}.service.ts`,
`research-backoffice/src/services/{publishExams.service,runAlgosOnExam.helpers}.ts`)

### L14.4 — What the plan assumed, and what follows from it being wrong

The runner was not overlooked. The plan places it, and treats it as production's own:

- `architecture_plan.html` lists `algo-worker/` in the production repository tree as a
  "separate image (algo-base) · **approved algorithm baked in**", and again later:
  "`algo-worker` runs the algorithm **baked into its image**"
- It states that "every box is the same repository and the same image except `algo-worker`", and
  gives it two Helm aliases — interactive and bulk — over that one image
- `spine.md` follows: **Runtime roles** lists `algo-worker` as a production role, "queue consumer ·
  algorithm execution, separate image"

**The premise is wrong** — see **C-8**. Nothing is baked in. The worker fetches the algorithm as a
tarball from `ALGORITHMS_BUCKET` by blob key at runtime, extracts and caches it, then spawns the
classifier inside `algo-base:5.0`. It holds no database client either. What the image contains is a
generic runner; what makes a run specific is the tarball and the message.

That is what the plan skipped rather than decided. If the algorithm is baked into the image, the
image is necessarily production's own — built from production's repository, pinned to the algorithm
version it carries — and there is no question to ask. Once the algorithm is a runtime-fetched
artefact, the runner is a generic component, and **who builds it becomes a live question the record
does not answer.** `spine.md`'s boundary row promotes the algorithm *tarball* research → production
and is correct as written; it says nothing about the *runner*, because under the plan's premise there
was nothing to say.

Both readings of that silence are consistent with the spine, and they produce different systems —
one of them the duplicated execution path L14.2 rules out.

One related defect is already recorded rather than new: **AD-22** names both QACR environments
pointing `ALGORITHMS_BUCKET` at `be-staging-algorithms` as a violation to correct before production.
Production needs its own algorithms bucket in its own region whichever way this decision goes.

### L14.5 — Proposed decision

[INFERRED] **AD-30 — The algorithm execution runtime is one promoted artefact; the result writer is
not shared.**

- **Binds:** algorithm execution, the research boundary, promotion
- **Prevents:** research validating an algorithm version through one orchestration path while
  production runs that version through a copy, which makes `FR-LCM-009`'s verification and
  `FR-ALG-004`'s recorded version non-transferable — and, in the other direction, production
  acquiring a standing credential into the research project in order to run it
- **Rule:** `algo-worker` is built **once**, in the repository that owns the algorithm, and
  production runs a **promoted, digest-pinned copy of that image** rather than building or
  maintaining its own. The image carries no database client and no research schema, so what
  production runs is the worker's own dependency closure and nothing else. It is configured entirely
  by environment against production's own broker, queues, buckets and `worker-api`. **`worker-api` is
  not shared** — each deployment implements its own, because it writes its own schema and
  production's carries AD-23's single-use credential and AD-4's insert-only result row under AD-2's
  row-level security. The **trigger message and output contract is versioned and additive-only**;
  drift in it is a defect, because that contract is what makes one verification cover both
  executions. Promotion of the image follows the same terms as promotion of an algorithm artefact: an
  explicit act with a recorded approval, into production's own registry, with **no shared registry
  credential across the boundary**

Two questions this raises that the rule does not answer, proposed as **OQ-19** and **OQ-20** in
L14.6.

### L14.6 — What `spine.md` must say if AD-30 is adopted

Paste-ready. Not applied here.

**One row added to Boundary With backend.q-acr**, after the algorithm-artefacts row:

> | Algorithm execution runtime, research → production | Research produces | Container image
> promoted by digest into the production registry and configured by environment against production's
> own broker, buckets and `worker-api`. No source dependency, no shared registry credential, and no
> database client in the image | Promotion is an explicit act with a recorded approval. The trigger
> and output contract is versioned and additive-only; a breaking change is a new version with both
> accepted during migration |

**AD-30**, after AD-29, with the Binds / Prevents / Rule text of L14.5 verbatim.

**Two rows added to Open Questions:**

> | OQ-19 | Who owns promoting the `algo-worker` image into production and where the approval is
> recorded. AD-30 requires promotion to be an explicit, approved act on the same terms as an
> algorithm artefact, and AD-14 requires the digest to be pinned; neither names a person or a place
> to write it down, and an approval with no recorded owner is not one | [UNKNOWN] | Backend owner +
> QMS | A named owner and a location for the record |

> | OQ-20 | Whether production needs the batch routing path or only the short one. Research runs both
> `qacr.aw.batchAlgorithm` and `qacr.aw.shortBatchAlgorithm` because it re-runs algorithms over many
> exams; production analyses one exam at a time, so the batch queue may have no production consumer.
> Inheriting both would build a queue, a scaler and a release nothing publishes to | [OBSERVED]
> `helm-charts/values/smiling-diode-638/research-us_qacr-research.yaml:74,110` | Backend owner | Confirming
> whether any production path publishes a batch trigger |

**One entry added to Deferred**, if the reviewer prefers to keep the option open rather than settle
where the runtime lives long-term:

> | Extracting the algorithm execution runtime into its own repository | AD-30 already gives one
> image, one build and a promoted digest, which is the property that matters. The remaining
> objection is only that a device component's source sits in the research repository, which is a
> submission-scope argument rather than a code one | The submission's component inventory is
> assembled under `FR-LCM-004`, or the research repository's release cadence starts to hold up an
> algorithm promotion |
