# QACR — Software Cybersecurity Considerations

**Purpose.** A plain-language list of what to take into account when building the QACR
Kidney Check mobile application, from a software engineering point of view.
Written to be readable by someone who does not work in the medical industry.

**Sources**

| | |
|---|---|
| Requirements | `product/FR-01/QACR-APP-FR-01 Rev1.19.docx` (Rev 1.19, draft) |
| Regulatory | `compliance/Premarket-Cybersecurity-Guidance-2026.pdf` — FDA, *Cybersecurity in Medical Devices: Quality Management System Considerations and Content of Premarket Submissions*, 3 February 2026 |
| Date compiled | 2026-08-20 |
| Status | Informal engineering note. Not a controlled document, not a requirement source. |

Requirement IDs in brackets (e.g. `FR-SEC-009`) refer to the functional requirements
document. Where a bullet has no ID, it comes from the FDA guidance and is not yet
covered by a requirement.

---

## First, the one framing fact

QACR is a **"cyber device"** under the FDA rules: it is software, it connects to the
internet, and it can be attacked. That means a chunk of the cybersecurity work is
**legally required**, not just recommended — and it is judged as part of whether the
product is *safe*, not as a separate IT concern. Two consequences for engineering:

- **Security has to be built in from the first sprint, not added before submission.**
  The FDA explicitly says security must be "built in, not bolted on," and expects to
  see it in design inputs and acceptance criteria.
- **Every security control needs a paper trail** linking: threat → requirement → code →
  test → evidence. If you cannot trace it, it does not count.

---

## Identity and access

- Phone + SMS code is the front door (`FR-AUT-001`–`019`), and a 4-digit PIN guards past
  results (`FR-ACC-*`). **All limits — attempt counts, lockouts, expiry — must be
  enforced on the server**, never in the app. Anything checked only in the app can be
  bypassed by editing the app.
- **Default to "no."** Reject anything not explicitly allowed: unknown requests, expired
  tokens, requests for someone else's record (`FR-COM-010`).
- **One user's account being stolen must not expose anyone else's data.** Partner
  organisations are logically isolated (`FR-SHR-001`) — that isolation is a safety
  control, not just a feature.
- Sessions must actually die on sign-out and on expiry (`FR-SEC-008`). A token left valid
  after logout is a finding.
- **Never hardcode secrets, default passwords, or API keys in the app.** The FDA calls
  this out by name, and static analysis will look for it.

## Data on the phone

- Encrypt everything sensitive at rest; keep only what the test needs (`FR-SEC-001`), and
  delete it the moment the server confirms upload (`FR-SEC-006`, `FR-COM-007`).
- Keys and tokens go in **iOS Keychain / Android Keystore only** — never files, never
  SharedPreferences (`FR-SEC-009`).
- **No patient data in logs, crash reports, analytics, or error messages**
  (`FR-SEC-004/005/010`, `FR-ANL-002/003`). Error text shown to users must be generic —
  no stack traces, no endpoint names, no versions.
- Block screenshots and blur the app-switcher preview on any screen showing results
  (`FR-SEC-007`).
- Ship release builds with debugging off and Android code obfuscated (`FR-SEC-002/003`).

## Talking to the server

- TLS 1.2+ with certificate pinning, and **refuse to connect** if either is not satisfied
  (`FR-COM-001/002`). No silent fallback to a weaker connection — downgrades are
  explicitly called out as an attack path.
- **Treat everything the app sends as hostile.** The server re-validates format, ranges,
  and authorisation on every request (`FR-COM-005`, `FR-SEC-011`).
- Every payload carries an integrity check so a truncated or tampered upload is
  detectable (`FR-COM-004`).
- Add **replay protection** on anything that matters (a nonce or equivalent) so a captured
  request cannot be re-sent later. The spec does not currently say this; the guidance
  asks for it.
- A checksum/CRC is **not** a security control — the guidance says so explicitly. It
  catches noise, not attackers.

## Third-party code — the biggest new obligation

- You must produce a **machine-readable SBOM** (a full inventory of every library,
  including the libraries your libraries pull in). For a cyber device this is required by
  statute, not optional.
- For each component you also need: **who maintains it, whether it is still maintained,
  and its end-of-support date.**
- Keep continuous dependency scanning (`FR-LCM-004`) and monitor advisories
  (`FR-LCM-005`). Anything in **CISA's Known Exploited Vulnerabilities catalogue must be
  designed out** — not risk-accepted.
- Have a plan for "what if this library is abandoned." Prefer modular boundaries so a
  component can be swapped. Keep a copy of source you depend on where licensing allows.
- Pick libraries from official sources and validate them inside the full system before
  release (`FR-LCM-002/003`).

## Crypto

- Use current NIST-recommended, industry-standard algorithms. **Nothing deprecated** (per
  NIST SP 800-131A), and pick things that will still be strong for the *whole service
  life* of the product, not just today.
- Do not derive keys from anything guessable — device IDs, serial numbers, phone numbers.
- Compromising one phone must not yield keys that unlock other users. No shared master
  key baked into the app.

## Updates and patching

- **You will need to ship security patches on a schedule the app stores do not control.**
  Design for it: server-side kill switches and forced-minimum-version checks so a
  vulnerable build can be blocked from running (`FR-PLT-005`, `FR-CFG-006` already give
  you the hooks).
- Security patches should be able to go out **independently of the normal feature release
  train.**
- **Block version rollback.** Let the app be updated, never downgraded to an older, weaker
  build.
- Keep the build environment, test suites and tooling for every released version alive, so
  you can patch an old release quickly rather than rebuilding the world.
- Assume a long tail of users on old versions. Every fielded version needs its own risk
  assessment.
- You will be asked to report **metrics**: % of vulnerabilities patched, time from
  discovery to patch, time from patch to actually reaching phones.

## Logging and detection

- Send security events to the server for audit: login attempts and outcomes, PIN failures,
  integrity-check failures, blocked tests (`FR-SEC-013`) — **carrying no patient data.**
- Logs must live **off the device** (a phone can be wiped or stolen), in a documented
  format something like a SIEM can consume.
- Document how long logs are kept and where. This is a submission item, not just ops
  hygiene.
- Tell the user when something is wrong — including possible security problems, not just
  functional errors.

## Resilience — do not lose a test

- A dropped connection must never destroy a test in progress: retain state, retry, resume
  (`FR-COM-006`, `FR-STA-003/005`).
- Analytics or survey services going down must never block a test (`FR-ANL-005`).
  Non-critical dependencies stay non-critical.
- Timers must survive backgrounding, calls, and screen lock (`FR-STA-002`, `FR-LCM-007`) —
  these are *clinical* timings, so a phone OS quirk becomes a patient-safety issue.
- Be robust to a hostile network: outages, denial of service, junk traffic, scanning.
- Notifications and offline behaviour should not depend on the backend being reachable
  (`FR-COM-009`).

## Testing — beyond normal QA

Standard unit and integration tests are not enough. The submission expects evidence of:

- **Fuzz testing** — malformed and unexpected inputs.
- **Abuse cases** — what a malicious user does, not just what a confused one does.
- **Static and dynamic analysis**, explicitly including a hunt for hardcoded/default
  credentials.
- **Software composition analysis** of the shipped binaries.
- **Penetration testing by people independent of the developers** — the report must state
  who tested, their expertise, scope, duration, methods, and findings. Budget for an
  external firm.
- **Attack-surface analysis** and vulnerability chaining (two small bugs combining into a
  big one).
- A rule that surprises people: **in security testing you cannot wave away a low-impact
  bug the way you can in functional testing.** If it is exploitable, it generally has to be
  fixed or formally justified.
- Repeat security testing after release, at regular intervals (annually is the example
  given).

## Documentation to produce alongside the code

- A **threat model**, kept current, covering supply chain, deployment, updates and
  decommissioning — not just runtime.
- **Architecture diagrams** in four specific flavours: whole system; what happens if many
  patients are hit at once; how updates reach a phone end-to-end; and per-feature security
  use cases.
- A **security risk assessment** scored on *exploitability* (how easy is it to attack)
  rather than *probability* — this differs from the normal safety risk process and is a
  separate document.
- A **vulnerability disclosure and postmarket monitoring plan** — how outsiders report bugs
  to you, who owns it, how fast you respond. Required for cyber devices.
- A list of **known unresolved bugs** with a security assessment of each.
- User-facing security information: how updates arrive, what data flows where,
  end-of-support dates.

---

## Open items already in the spec that are security decisions, not paperwork

Four things in the requirements document need resolving before they become expensive:

- **Q-63 — session token expiry.** Backend SRS says 24 hours; review flagged that as wrong
  for this app. Pick a value now; it shapes the auth implementation.
- **Q-03 — minimum OS versions.** The config currently allows iOS 13 / Android 8, which no
  longer get vendor security patches. The security analysis bars those. This will move, so
  do not hardcode against the low numbers.
- **Q-81 — screenshot blocking vs. saving the results PDF to the photo gallery.** These
  directly contradict each other: one says results must never be capturable, the other
  saves results to a folder every app on the phone can read. One of the two has to change.
- **`FR-SEC-014`** — any build without full TLS + pinning must never touch real patient
  data. That is a **CI/release-gate control**, not a code comment. Enforce it in the
  pipeline.

---

## The short version

Most of this the spec already tells you to do. What the FDA guidance adds on top is:

1. An **SBOM** with maintenance status and end-of-support date for every dependency.
2. **Independent penetration testing** with a formal report.
3. The ability to **push a security patch fast** and block old builds from running.
4. **Security logs stored off the device.**
5. **Traceability from threat to test** for every single control — far easier to build as
   you go than to reconstruct six months before submission.
