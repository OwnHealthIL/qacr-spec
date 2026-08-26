// Spec status per feature, from the answered triage (QACR-APP-SPEC-00).
//
//   status : how much writing the spec needs — not whether the feature is in scope.
//            Milestone carries scope; this carries spec effort.
//   note   : what changes, so a developer can judge the work without the spec.
//   src    : "pm"      — the product manager's own words from the triage. Authoritative.
//            "derived" — read off the requirements by way of explanation. NEEDS CONFIRMING.
//            "std"     — the standard meaning of Unchanged, no per-feature claim made.
//   doc    : the spec document that will carry it, or null where none is coming.
//
// Readiness is derived, not stored: New and Changed wait for a spec, Unchanged can be
// built from the existing application, No spec has nothing coming at all.

const DOC = {
  E01: "SPEC-01", E02: "SPEC-02", E03: "SPEC-03", E04: "SPEC-04", E05: "SPEC-05",
  E06: "SPEC-06", E08: "SPEC-08", E09: "SPEC-09", E10: "SPEC-10", E11: "SPEC-11",
  E12: "SPEC-12", E13: "SPEC-13", E14: "SPEC-14",
};
// Where each spec document has got to. Rendered on the board, because a developer opening it
// needs to know whether a document can be built from or is still moving under them.
//   ready   — reviewed by Guy and settled; build from it
//   drafted — written, not yet reviewed
// A document not named here has not been written.
const STATE = { "SPEC-01": "ready", "SPEC-02": "ready", "SPEC-03": "ready", "SPEC-04": "drafted", "SPEC-05": "drafted" };
const STATE_LABEL = { ready: "ready", drafted: "drafted, not yet reviewed" };

// Features specified somewhere other than their own epic's document.
const DOC_OVERRIDE = { "F04.8": "SPEC-05", "F05.3": "SPEC-05" };

const UNCHANGED_DEFAULT =
  "Recreation of Minuteful Kidney behaviour. Implementation stays as it is; the spec " +
  "records it rather than redesigning it, so this can be built from the existing application.";

const S = {
  // ---------------------------------------------------------------- E01
  "F01.1": ["Unchanged", null, "pm"],
  "F01.2": ["Unchanged", null, "pm"],
  "F01.3": ["Unchanged", null, "pm"],
  "F01.4": ["Unchanged", null, "pm"],
  "F01.5": ["Unchanged", null, "pm"],
  "F01.6": ["Unchanged", null, "pm"],
  "F01.7": ["No spec", "Not a feature with behaviour of its own. A constraint every other spec inherits: iOS and Android present the same content, step sequence, confirmation behaviour and error handling.", "derived"],
  "F01.8": ["Unchanged", null, "pm"],
  // Was Changed on a derived note until Guy corrected it at the Rev 0.7 review of SPEC-01:
  // run-time configuration works exactly as it does in Minuteful Kidney US. Some values are
  // mandatory before a test may start and some are not; some have built-in defaults and some
  // do not. That is the existing behaviour, not a change, so the spec records it rather than
  // redesigning it — and SPEC-01 has no changed feature left, so it carries no behaviour
  // statements at all.
  "F01.9": ["Unchanged", null, "pm"],

  // ---------------------------------------------------------------- E02
  "F02.1": ["Unchanged", null, "pm"],
  "F02.2": ["Unchanged", null, "pm"],
  "F02.3": ["Unchanged", null, "pm"],
  "F02.4": ["Changed", "Just the flag behavior (adding a “not shown” status)", "pm"],
  // Was Changed pending the token inventory. Researched at the SPEC-02 Phase 0 review and
  // confirmed by Guy: the session holds three credentials, none of them persisted, and none of
  // them behaves differently for QACR. The inventory itself is implementation detail and does
  // not belong in a spec. Two behaviours it surfaced are uncovered by the requirements and are
  // proposed as such, but neither is a change to the product.
  "F02.5": ["Unchanged", null, "pm"],
  "F02.6": ["Unchanged", null, "pm"],
  "F02.7": ["Unchanged", null, "pm"],
  "F02.8": ["Unchanged", null, "pm"],

  // ---------------------------------------------------------------- E03
  "F03.1": ["Unchanged", "Adding this check to the scan practice as well", "pm"],
  "F03.2": ["Unchanged", "Adding this check to the scan practice as well", "pm"],

  // ---------------------------------------------------------------- E04
  "F04.1": ["Unchanged", "the chat engine supports what we want in the QACR flow, there are no new controls or mechanics except for the timers which will be in 5.4 and the scan practice in its own spec (4.7)", "pm"],
  "F04.2": ["Changed", "We made small changes to the video UX in QACR, this can go in this spec.", "pm"],
  "F04.3": ["Unchanged", null, "pm"],
  "F04.4": ["Unchanged", null, "pm"],
  // Was Changed on a derived reading that QACR's committed-sample point differs from
  // Minuteful's. Confirmed by Guy at the SPEC-04 draft, and re-sourced to him: his marks on
  // the E04 behaviour review say the deciding step is the one confirming the cup was used,
  // for the exit warning and for the absence reset alike. FR-STA-008 already places the
  // cut-off at cup fill, so the requirement does not move; which step that is in the QACR
  // flow does.
  "F04.5": ["Changed", "The cancellation cut-off is cup fill. The committed-sample point is the step confirming the Urine Collection Cup was used, not the dipping step, and the exit warning and the absence reset both move with it.", "pm"],
  "F04.6": ["Changed", "the mechanism exists in minuteful, we want to add a control to jump somewhere in the flow, and not specifically to the end of it.", "pm"],
  // Was New on a derived note. Confirmed by Guy at the SPEC-04 draft: New stands, and the
  // spec describes the practice framing only — the scanning interaction it reproduces is
  // E06's and is not restated.
  "F04.7": ["New", "New for QACR. No Minuteful equivalent. The spec describes the practice framing; the scanning interaction is E06's.", "pm"],
  "F04.8": ["New", "with 5.4", "pm"],

  // ---------------------------------------------------------------- E05
  "F05.1": ["New", "Same spec as 5.4.", "pm"],
  "F05.2": ["Changed", "Exists im minutefl. The timing and test steps are changed", "pm"],
  "F05.3": ["No spec", "This is just another chat-flow step. The timing mechanism is spec'ed in 5.4, as well as what happens in rainy day flow.", "pm"],
  "F05.4": ["New", "The spec will focus primarily on the UX within the chat during the reaction wait time. The timer constraints, the dynamic tips card, the happy and sad flow.", "pm"],
  "F05.5": ["New", "Same spec as 5.4. the countdown UX is not exactly like minuteful.", "pm"],
  "F05.6": ["Changed", "The invalidation mechanism in the chat flow exist in minuteful. The changes are the new additions", "pm"],

  // ---------------------------------------------------------------- E06
  "F06.1": ["Changed", "A frame set defined by the QACR IVTS specification rather than a single image, with the torch state per frame, the camera parameters recorded against each image, and recovery from a camera failure mid-capture. FR-CAM-002's priority is still undecided.", "derived"],
  "F06.2": ["Changed", "same mechanism. The marker reference is embedded within the Algo and we don't need a spec for that. There is an open question whether we capture RAW images along with PNG, this will change the spec", "pm"],
  "F06.3": ["Changed", "additional QCR boundary (specularity)", "pm"],
  "F06.4": ["Changed", "Adding the spoken text. This one is already 95% spec'ed and developed for the usability version", "pm"],
  "F06.5": ["No spec", "Algo domain, no product spec is needed", "pm"],
  "F06.6": ["Changed", "QACR IVTS boundary conditions, including the specular reflection condition added at review, plus a preparation-and-evaluation state after the frame set is captured so the user is not left on a viewfinder with nothing happening.", "derived"],

  // ---------------------------------------------------------------- E07
  "F07.1": ["No spec", "Content governance rather than application code. Copy is authored and version-controlled in the content set.", "derived"],
  "F07.2": ["No spec", "Instructional copy for the QACR flow. Authored in the content set, not specified here.", "derived"],
  "F07.3": ["No spec", "Result and invalid-test copy. Authored in the content set.", "derived"],
  "F07.4": ["No spec", "Blocking and error copy. Authored in the content set; the conditions that raise it are specified in the spec that owns them.", "derived"],

  // ---------------------------------------------------------------- E08
  "F08.1": ["No spec", "Spec'ed by algo", "pm"],
  "F08.2": ["Changed", "We need to verify the status, im not sure how is it handled in minuteful", "pm"],
  "F08.3": ["New", "the algo team handles the spec, I just want to have a place that aggregates all the requirements", "pm"],
  "F08.4": ["Changed", "The payload contract: a valid quantitative result distinguished unambiguously from an invalid test, an out-of-range condition conveyed for presentation, and a reason category per invalid test drawn from a defined enumeration.", "derived"],

  // ---------------------------------------------------------------- E09
  "F09.1": ["Changed", "this will also handle out of range results", "pm"],
  "F09.2": ["New", "We'll need a spec for all the different options for how the results will be displayed.", "pm"],
  "F09.4": ["Changed", "This does exist in minuteful. There are demo-partners configurations with the mock results in them, and the backend knows to override algo results and send the mock in these partners.", "pm"],

  // ---------------------------------------------------------------- E10
  "F10.1": ["Unchanged", null, "pm"],
  "F10.2": ["Unchanged", null, "pm"],
  "F10.3": ["Unchanged", "behavior unchanged, UI might change a bit.", "pm"],
  "F10.4": ["Unchanged", null, "pm"],
  "F10.5": ["Changed", "Currently minuteful supports in-app chat. We'll need to spec the email/telephone", "pm"],
  "F10.6": ["Unchanged", "Its differed to the backlog but we will still spec it", "pm"],

  // ---------------------------------------------------------------- E11
  "F11.1": ["Unchanged", null, "pm"],
  "F11.2": ["Unchanged", null, "pm"],
  "F11.3": ["Unchanged", null, "pm"],
  "F11.4": ["Unchanged", "Its differed to the backlog but we will still spec it", "pm"],
  "F11.5": ["Unchanged", "Its differed to the backlog but we will still spec it", "pm"],
  "F11.6": ["Unchanged", "Its differed to the backlog but we will still spec it", "pm"],
  "F11.7": ["Unchanged", "Its differed to the backlog but we will still spec it", "pm"],

  // ---------------------------------------------------------------- E12
  "F12.1": ["Unchanged", null, "pm"],
  "F12.2": ["Changed", "The application now explicitly requests the result and holds a waiting state until one arrives, and the waiting period is a system parameter with no value yet. The integrity check and the backend's rejection of malformed payloads are stated.", "derived"],
  "F12.3": ["Unchanged", null, "pm"],
  "F12.4": ["Unchanged", "Its differed to the backlog but we will still spec it", "pm"],

  // ---------------------------------------------------------------- E13
  "F13.1": ["No spec", "Security controls with no user-facing behaviour. The requirements are the specification, so this can be built from them directly.", "derived"],
  "F13.2": ["No spec", "Build hardening. As F13.1: no UX, the requirements are the specification.", "derived"],
  "F13.3": ["Unchanged", null, "pm"],
  "F13.4": ["No spec", "no spec but should be mentioned as a requirement somewhere", "pm"],
  "F13.5": ["Unchanged", null, "pm"],

  // ---------------------------------------------------------------- E14
  "F14.1": ["Changed", "Same Mixpanel instrumentation. The event set follows the QACR flow, so the steps and the scan outcomes differ.", "derived"],
  "F14.2": ["Unchanged", null, "pm"],
  "F14.3": ["Unchanged", null, "pm"],
  "F14.4": ["Unchanged", "Its differed to the backlog but we will still spec it", "pm"],

  // ---------------------------------------------------------------- E15
  "F15.1": ["No spec", "A process control applied to the product rather than behaviour built into it.", "derived"],
  "F15.2": ["No spec", "A verification activity, not application behaviour.", "derived"],
  "F15.3": ["No spec", "A verification activity covering the algorithm and the release.", "derived"],
  "F15.4": ["No spec", "Off-the-shelf component management. A process obligation.", "derived"],
  "F15.5": ["No spec", "Usability testing. A study, not code.", "derived"],
  "F15.6": ["No spec", "Provider integration testing. A verification activity.", "derived"],
};

const ORDER = ["New", "Changed", "Unchanged", "No spec"];

// A developer reading the board wants one of three answers.
//   wait  — a spec is coming and the work should not start before it
//   start — nothing is coming, or what is coming only records what already exists
//   other — not application code at all
function readinessFor(id, status, domains) {
  if (status === "New" || status === "Changed") return "wait";
  if (status === "Unchanged") return "start";
  if (id === "F05.3") return "wait";              // no document of its own, but SPEC-05 covers it
  const app = (domains || []).some(d => d === "iOS" || d === "Android" || d === "Backend");
  return app ? "start" : "other";
}

module.exports = function specStatusFor(featureId, epicCode, domains) {
  const row = S[featureId];
  if (!row) return null;                          // the caller reports this as a build failure
  const [status, note, src] = row;
  const doc = status === "No spec" && featureId !== "F05.3"
    ? null
    : (DOC_OVERRIDE[featureId] || DOC[epicCode] || null);
  return {
    status,
    note: note || (status === "Unchanged" ? UNCHANGED_DEFAULT : null),
    // "std" is the boilerplate meaning of Unchanged, not a claim about this feature,
    // so it is not flagged as needing confirmation.
    src: note ? src : (status === "Unchanged" ? "std" : src),
    doc,
    state: doc ? (STATE[doc] || "not written") : null,
    stateLabel: doc ? (STATE_LABEL[STATE[doc]] || "not written yet") : null,
    readiness: readinessFor(featureId, status, domains),
  };
};
module.exports.ORDER = ORDER;
module.exports.READINESS = {   // declaration order is the order shown to a reader
  start: "Can start now",
  wait:  "Waiting on a spec",
  other: "Not application code",
};
module.exports.COUNT = Object.keys(S).length;
