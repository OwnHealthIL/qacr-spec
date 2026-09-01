# iOS architecture rules

**What this file is.** The architectural rules QACR's iOS application is built to. Two kinds live
here, and the difference is load-bearing:

- **decided** — the rule follows from an entry in `decisions/adr/DECISIONS.md`, cited by id. It is
  binding.
- **proposed** — the rule was inferred while specifying a feature and has not been reviewed.
  Follow it for consistency, and treat it as unapproved. `qacr-context` reports it to the next
  feature's spec writer as `found`, so a rule recorded once stops being re-invented per feature —
  which is the whole reason this file exists.

**Created 2026-09-01**, while recording F01.4's decisions. It is the first mobile file under
`architecture/`; before it, `qacr-context` resolved both mobile domains to `absent`.

> **Open question — is this the right home?** `adr-conventions` names `architecture/ios.md` for the
> architectural side-write, and simultaneously records that "a mobile `architectural` decision has
> no settled home yet" and that the destination should be **raised, not chosen**. This file is
> created because the side-write rule names it and the write is otherwise undone, but the question
> stands and is raised rather than treated as answered here. It is deliberately **not** written into
> `architecture/spine-decision-log.md`, which `adr-conventions` scopes to the backend and explicitly
> forbids for mobile decisions.

---

## Connectivity reads come from a new API, added alongside the defective one

**decided** · `decisions/adr/DECISIONS.md` → `FR-RDY-005-connectivity-read-location` · 2026-09-01

`ios-foundations`' `NetworkManager.internetReachable` cannot report a lost connection: it
initialises `true`, and its only assignment to `false` sits behind a guard that passes only when the
value is already `false`. QACR pins a revision with the identical defect (`cf743d568999`, 7.1.6).

**The rule.** A correct connectivity API is added to `ios-foundations` *beside* `internetReachable`,
which is left untouched; QACR consumes the new one. This is additive, so no existing consumer's
behaviour changes — which is what the additive-only constraint on multi-product packages requires.
Whether `internetReachable` is later deprecated, repaired or removed is a separate decision owned by
whoever owns the other consumers, and is not settled by this rule.

**Never** build a connectivity verdict on a long-lived reachability flag. Read the condition at the
moment the verdict is needed.

---

The five rules below were **inferred while specifying F01.4** (`specs/pre-test-resource-and-permission-checks.md`,
in `urine.com.ios-qacr-app`) because no iOS guidelines existed to follow. They are recorded here per
the `qacr-context` consumer rule that an inferred rule is written back rather than re-invented —
eighty-two features each inventing an architecture being the failure that rule prevents.

## One readiness gate, one invocation point

**proposed** · inferred while specifying F01.4 · 2026-09-01 · unreviewed

All pre-test readiness checks sit behind a single call at the start-test action, not scattered
through the flow. `FR-RDY-010`'s re-evaluation obligation only means something against a single
evaluation point, and prior art on both platforms does exactly this with one function each.

## A check owns its own reading

**proposed** · inferred while specifying F01.4 · 2026-09-01 · unreviewed

Each condition is read at evaluation time by the component that owns it. No shared mutable
"current state" flag stands in for a reading.

*This is the exact shape of the `ios-foundations` connectivity defect — a long-lived flag standing in
for a live read — so the rule exists to stop it being recreated.*

## Verdicts are data; presentation is separate

**proposed** · inferred while specifying F01.4 · 2026-09-01 · unreviewed

The readiness gate returns a typed verdict. Mapping a verdict to an alert is the presentation
layer's job. This is what lets acceptance criteria be unit-tested without UI.

## Thresholds resolve through one seam

**proposed** · inferred while specifying F01.4 · 2026-09-01 · unreviewed

Whether a threshold is app-fixed or configuration-supplied is settled in one place per threshold, so
a change of answer changes a provider rather than every call site.

*Live reason: `FR-RDY-008-storage-threshold-ownership` is deferred to the PM, and the storage
threshold's source is exactly what it decides.*

## Additive-only in shared packages

**proposed** · inferred while specifying F01.4 · 2026-09-01 · unreviewed

In a package serving more than one product, changes are additive: existing behaviour and existing
consumers are untouched, and blast radius is checked with `/mind` before code lands. A requirement
that cannot be met additively is a stop, not a judgement call.

*This one is `proposed` here but originates as a binding consumer rule from `qacr-context`, not as an
inference — recorded so the next iOS feature reads it as a rule rather than rediscovering it. It is
what reshaped `FR-RDY-005-connectivity-read-location` from an in-place repair into an additive one.*
