// Disposition of the 42 backlog items. APPROVED by Guy, 12 Aug 2026, from
// "QACR-APP-FR-01 Milestone 5 proposal.xlsx". His comments are quoted verbatim.
//
// The backlog is emptied. Every item takes an FR identifier in the section it belongs
// to, and BL-nn ceases to exist as an identifier class.
//
// Row: [BL id, target FR id, why this group, milestone, text override or null]
//
//   milestone  "5"  future development, no date — 39 items
//              "1"  brought into scope for the demonstration — BL-34 only
//              "3"  brought into scope for the submission — BL-35 only
//              null withdrawn, not carried forward — BL-38 only
//
//   "restore" as the reason means the item was superseded into the backlog from that
//   exact identifier and it has been vacant ever since, so restoring it reoccupies its
//   own former number with unchanged text. Guy's decision, 11 Aug 2026.
//
// Existing gaps are NOT filled. FR-SHR-009, FR-PRT-006, FR-AUT-009 and the rest were
// left by withdrawn or superseded requirements and stay vacant, because an identifier is
// never reused for different content. FR-CFG-005 and FR-CFG-007 likewise stay vacant,
// the latter pending the SPEC-01 proposal to reinstate it.

const RESTORE = "restore";
const M5 = "5";

module.exports = [
  // ---- restored to their own former identifiers (14) ------------------------
  ["BL-19", "FR-SUP-001", RESTORE, M5, null],
  ["BL-20", "FR-AUT-007", RESTORE, M5, null],
  ["BL-21", "FR-AUT-011", RESTORE, M5, null],
  ["BL-22", "FR-AUT-015", RESTORE, M5, null],
  ["BL-23", "FR-KIT-005", RESTORE, M5, null],
  ["BL-24", "FR-TIM-004", RESTORE, M5, null],
  ["BL-25", "FR-ACC-003", RESTORE, M5, null],
  ["BL-26", "FR-ACC-007", RESTORE, M5, null],
  ["BL-27", "FR-ACC-008", RESTORE, M5, null],
  ["BL-28", "FR-ANL-004", RESTORE, M5, null],
  ["BL-33", "FR-CFG-003", RESTORE, M5, null],

  // Guy: "should be milestone 1". Brought into scope for the demonstration. Its own
  // deferral note is replaced, because that note described the consequence of deferring
  // it and there is no longer a deferral to have a consequence.
  ["BL-34", "FR-CFG-004", RESTORE, "1", null,
   "Brought into scope for the demonstration at Guy's direction, formerly BL-34. Server-side "
   + "enforcement matters because demonstration mode is a state the backend returns with the "
   + "configuration, so nothing held on the device can be relied on to keep a demonstration "
   + "result away from a patient. Settles the doubt recorded against Q-31."],

  // Guy: "milestone 3". Brought into scope for the submission. This is the configured
  // blocked state, which the product already returns as a typed block with screens for
  // it, and which SPEC-01 proposed promoting.
  ["BL-35", "FR-CFG-006", RESTORE, "3", null,
   "Brought into scope for the submission at Guy's direction, formerly BL-35. The configured "
   + "blocked state is a response the product already returns and has screens for; SPEC-01 "
   + "proposed promoting it. The blocking, notifying and configured-off distinction applies: "
   + "this one blocks."],

  ["BL-40", "FR-SUP-004", RESTORE, M5, null],

  // ---- consent and privacy (3) ---------------------------------------------
  // FR-CNS-004 is skipped. It is in Appendix D as a withdrawn requirement — an earlier
  // attempt at consent recording — and an identifier is never reissued for different
  // content. The identifier guard caught this: the first draft of this map put BL-01 on
  // FR-CNS-004 and the build failed with "reissued after withdrawal".
  ["BL-01", "FR-CNS-005", "Acknowledgement of policy documents before a doctor chat is a consent obligation.", M5, null],
  ["BL-02", "FR-CNS-006", "A second acknowledgement before sharing with a provider is consent, not routing.", M5, null],
  ["BL-03", "FR-CNS-007", "Recording which policy version was acknowledged, and when, belongs with consent. Distinct from the withdrawn FR-CNS-004, which attempted the same obligation and whose identifier is not reissued.", M5, null],

  // ---- identification (1) --------------------------------------------------
  // Guy: "stay in AUT"
  ["BL-04", "FR-AUT-020", "Blocking a second test on a shared phone number turns on identifying which user is testing. Guy confirmed FR-AUT over FR-KIT.", M5, null],

  // ---- transmission (1) ----------------------------------------------------
  ["BL-05", "FR-COM-013", "Receiving backend push is a transmission capability. FR-COM-009 already holds the local-notification counterpart.", M5, null],

  // ---- result routing and provider communication (7) -----------------------
  // Guy: "the requirement is to share results with PCP. Not sharing PCP details"
  ["BL-06", "FR-SHR-012", "Sharing results with a provider is the core of this section.", M5,
   "The software shall provide the user with an option to share test results with their primary care provider."],
  ["BL-08", "FR-SHR-013", "A chat with a doctor is provider communication.", M5, null],
  ["BL-09", "FR-SHR-014", "Calling a provider is provider communication.", M5, null],
  ["BL-11", "FR-SHR-015", "The results letter exists to reach a provider or be kept by the user; generation, saving and email sharing are one item.", M5, null],
  ["BL-41", "FR-SHR-016", "Handing off to an external application is how a sharing action completes.", M5, null],
  ["BL-43", "FR-SHR-017", "HISP is a provider delivery protocol.", M5, null],
  ["BL-44", "FR-SHR-018", "Detecting whether a configured sharing application is present governs which sharing options appear.", M5, null],

  // ---- configuration (1) ---------------------------------------------------
  ["BL-07", "FR-CFG-008", "The A/B testing interface is a configuration-driven capability.", M5, null],

  // ---- lifecycle (1) -------------------------------------------------------
  // Guy: "stay in LCM"
  ["BL-15", "FR-LCM-018", "Assessing a configuration change under change control is a lifecycle process obligation, not application behaviour. Guy confirmed FR-LCM over FR-CFG.", M5, null],

  // ---- results centre, main menu and the post-test lobby (8) ---------------
  // Guy: "stay in PRT"
  ["BL-10", "FR-PRT-008", "Opening a configured web page is an application-information capability; the results centre and menu both rely on it. Guy confirmed FR-PRT over FR-FLW.", M5, null],
  ["BL-16", "FR-PRT-009", "Viewing the results letter is a results-centre function.", M5, null],
  ["BL-17", "FR-PRT-010", "Sharing the results letter from the results centre.", M5, null],
  ["BL-18", "FR-PRT-011", "Further information about a result, reached from the results centre.", M5, null],
  ["BL-36", "FR-PRT-012", "The post-test lobby is a state of the home screen, alongside the results centre and menu.", M5, null],
  ["BL-37", "FR-PRT-013", "The lobby action set.", M5, null],
  ["BL-39", "FR-PRT-014", "Results-centre changes accompanying the lobby redesign.", M5, null],
  ["BL-42", "FR-PRT-015", "A results history screen is part of the results centre.", M5, null],

  // Guy: "this is too drilled down requirement… part of a feature spec, not a
  // functional requirement. Can be removed." Withdrawn rather than carried forward.
  ["BL-38", null, "Withdrawn at Guy's direction: the lobby analytics event set is feature-spec detail, not a functional requirement. FR-ANL-001 already requires analytics for progress through the test flow.", null, null],

  // ---- result presentation (1) ---------------------------------------------
  ["BL-12", "FR-RES-007", "Presenting albumin and creatinine alongside the ratio is result presentation.", M5, null],

  // ---- analytics and user feedback (4) -------------------------------------
  ["BL-29", "FR-ANL-006", "The post-test survey. FR-ANL is titled Analytics and User Feedback, so no FR-SUR section is reinstated. Guy's decision, 11 Aug 2026. Originally FR-SUR-001, superseded to BL-29 at review and now carried here; FR-SUR is not reinstated as a section.", M5, null],
  ["BL-30", "FR-ANL-007", "Declining or dismissing the survey. Originally FR-SUR-002, superseded to BL-30 at review and now carried here; FR-SUR is not reinstated as a section.", M5, null],
  ["BL-31", "FR-ANL-008", "When the survey may be presented. Originally FR-SUR-003, superseded to BL-31 at review and now carried here; FR-SUR is not reinstated as a section.", M5, null],

  // Guy: "ok. And the requirement can be generalized to not show exactly when, but
  // require that the rating prompt will be shown"
  ["BL-32", "FR-ANL-009", "The application-store rating prompt, kept with the survey it follows. Originally FR-SUR-004, superseded to BL-32 at review and now carried here; FR-SUR is not reinstated as a section.", M5,
   "The software shall present the operating system's application-store rating prompt."],
];
