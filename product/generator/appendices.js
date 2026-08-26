// Rev 0.5 appendix data.

// [ID, requirement (abridged), disposition, Risk Analysis impact]
exports.withdrawn = [
  ["BL-38", "The software shall record analytics events for the post-test lobby, comprising lobby display with the completion state of each action, and action, done, undone, collapse and expand interactions, each identifying the action type.", "Not included", "Withdrawn at Guy's direction, 12 Aug 2026. Withdrawn at Guy's direction: the lobby analytics event set is feature-spec detail, not a functional requirement. FR-ANL-001 already requires analytics for progress through the test flow. Was a deferred backlog item and is not carried into milestone 5."],

  // ---- not included in this version ----
  ["FR-IMG-012", "The backend shall independently re-validate image quality and block a result where thresholds are not met",
   "Not included",
   "RESOLVED. The current RA draft has replaced the backend re-validation clause in RA 7.16 with “Software Algorithms safely invalidate scans…”, which FR-IMG-015 covers. No further RA edit is needed."],
  ["FR-CFG-005", "No configuration value shall be capable of disabling a requirement that implements a risk control",
   "Not included",
   "NO — an addition of this document. The intent is now largely met by other means: the timing values in section 12, the PIN parameters in section 18 and the readiness thresholds in section 5 are stated as fixed in the application rather than configurable, so they are not reachable by configuration. The residual exposure is the controls that remain configuration-driven, principally the IVTS thresholds and the demonstration flags, and FR-CFG-004 covers the latter server-side."],
  ["FR-CFG-007", "User-facing text supplied by configuration shall be drawn from the approved content set and meet section 10",
   "Not included",
   "NO — an addition of this document. Note the consequence: customBlockFlowAlertParams carries a free-text title and body set per partner, so blocking-message text can be authored outside the approved content set and outside the grade-6 reading level required by FR-TXT-001."],
  ["FR-LCM-001", "The device software shall be developed and maintained in accordance with the Class B classification under IEC 62304",
   "Not included",
   "NO — the classification is stated in RA section 6 and the obligation stands irrespective of this document. Development standards belong in the Software Development Plan; FR-LCM-017 covers release testing."],
  ["FR-LCM-013", "Usability testing shall evaluate whether the user understands each content requirement that is a risk control",
   "Not included",
   "PARTIAL — RA 7.3, 7.6 and 7.19 each cite usability testing of the instruction as a mitigation. FR-LCM-012 retains usability testing but only for platform coverage and interruptions, so evaluation of instructional comprehension is no longer required by this document. Confirm it is covered by the Usability Engineering Plan, otherwise those three RA clauses have no verification activity."],
  ["FR-LCM-014", "The reading level of all user-facing text shall be measured before each release",
   "Not included",
   "NO — no RA row cites it. Note that FR-TXT-001 remains at milestone 2, so the grade-6 ceiling is required but no longer has a stated verification activity in this document."],
  ["FR-LCM-015", "Component names shall be reconciled against the Product Glossary at each release",
   "Not included",
   "NO — no RA row cites it. As above, FR-TXT-002 remains at milestone 2 without a stated verification activity here."],
  ["FR-STA-011", "If the Urine Collection Cup was filled, disable cancellation, complete the test flow and upload the data",
   "Not included",
   "NO — SRS TSM.20 maps to it and should be marked withdrawn when the SRS is updated. FR-STA-008 still bars cancellation once the cup is filled, so the gate remains; what is no longer stated is the positive obligation to carry the test through to upload."],

  ["FR-TXT-018", "The instructional flow shall present the safety information applicable to buffer or reagent contact with skin or eyes, including the instruction to rinse with water",
   "Not included",
   "NO — RA 2.2, 2.5 and 7.36 each assign the safety warning and the rinse instruction to the User Manual alone. There is no in-app clause to delete, so the Risk Analysis is unaffected."],
  ["FR-CNS-004", "Record the type of consent given and the time it was given, and transmit both to the backend",
   "Not included",
   "NO — consent recording remains future development as FR-CNS-007 at milestone 5, which is where the obligation and the Q-11 decision sit. The identifier was issued for one draft revision on a mistaken reading of a review comment and is recorded here so that it is not reissued."],
  ["FR-SUR-005", "The application-store rating prompt shall not be presented during an active test, on a results screen, or after an invalid test",
   "Not included",
   "NO — an addition of this document. Note that the rating prompt itself is future development as FR-ANL-009, so nothing currently triggers the prompt. If FR-ANL-009 is implemented, the constraint should be reconsidered."],

  ["FR-PLT-007", "The software shall be published with automatic update enabled wherever the application store supports it",
   "Not included",
   "NO — RA 4.17 relies on the version check in FR-RDY-004, which blocks an unsupported application version outright, rather than on automatic update. The RA clause is satisfied without this requirement."],

  // ---- capability limit ----
  ["FR-ALG-008 (earlier wording)", "Detect out-of-sequence assay signatures and block a result where present",
   "Capability not achievable; FR-ALG-008 states the detectable conditions instead",
   "RESOLVED IN THE RISK ANALYSIS, EXCEPT RA 7.34. Nine rows cited “Software Algorithms detect out-of-sequence assay signatures and block invalid results”. Out-of-sequence detection is not achievable. What is achievable, and is required by FR-ALG-008, is detecting that the sample was not introduced into the buffer and that insufficient fluid reached the Detection Wells. The rows resolve as follows. RA 3.8, no fluid flow to the detection wells, is covered by the insufficient-fluid detection. RA 3.9 and RA 3.10, the release button operated before incubation is complete, no longer rely on software detection; RA 3.9 relies on the instruction and the timer, which are FR-TXT-015, FR-TIM-007 and FR-TIM-009. RA 7.9, 7.23, 7.29, 7.30 and 7.36 each retain at least one other requirement at milestone 1 to 3. RA 7.34, the test performed at extreme ambient temperature or humidity, is not yet resolved and is the one row whose only software control is a requirement at TBD priority."],

  // ---- consolidated into another requirement, no loss of substance ----
  ["FR-IMG-003", "Detect whether the Test Board is entirely within the camera frame",
   "Consolidated into FR-IMG-002", "NO — SRS TSM.10 now traces to FR-IMG-002."],
  ["FR-IMG-017", "Capture a set of images rather than a single image and transmit the complete set",
   "Consolidated into FR-CAM-001", "NO — SRS PER.2, PER.3 and the Glossary now trace to FR-CAM-001."],
  ["FR-KIT-006", "Prevent an additional test where the kit identifier has already been used",
   "Consolidated into FR-KIT-004", "NO — SRS TSM.40 now traces to FR-KIT-004."],
  ["FR-STA-001", "Persistently retain the current test state throughout the test flow",
   "Consolidated into FR-STA-003",
   "NO — the persistence obligation and all five RA traces (4.1, 4.2, 4.3, 4.4, 4.18) were carried into FR-STA-003 rather than dropped."],
  ["FR-STA-004", "On return to the application, resume at the active step and make instructions available for replay",
   "Consolidated into FR-STA-003", "NO."],
  ["FR-IMG-020", "Present the framing guidance in spoken form during scanning",
   "Restated as FR-IMG-024",
   "NO — RA 7.12, 7.14 and 7.16 trace to FR-IMG-024."],
  ["FR-TIM-010", "Prevent the Test Board being scanned before the colour-evolution period has elapsed",
   "Consolidated into FR-TIM-008", "NO — RA 4.4 now traces to FR-TIM-008 as well as FR-TIM-011."],
  ["FR-AUT-009", "Where the phone number and invite code do uniquely identify a single registered user, the software shall not request the Date of Birth at login",
   "Not included",
   "RESOLVED. The Date of Birth is not part of login in this version. Requesting it at login is only meaningful where more than one patient shares a phone number or an address, and both cases are future development as FR-AUT-007 and FR-AUT-011, so the condition was always true and the requirement was satisfied by writing no code. The Date of Birth confirmation at the start of every test, FR-AUT-012, is unaffected and is now milestone 3. The traceability is also reconciled: RA 6.4 traces to FR-AUT-010, FR-AUT-012, FR-AUT-013, FR-AUT-014 and FR-SHR-003, all in scope and all at milestone 3. That single list replaces the two inconsistent lists this appendix and the note now carried by FR-AUT-007 previously held."],

];

// [ref, requirement, source, note, priority]
// The backlog was emptied at Rev 1.18. Every item took an FR identifier in the section
// it belongs to, at milestone 5 (future development) except BL-34 at 1, BL-35 at 3 and
// BL-38 withdrawn. The disposition of each is in m5-map.js and each requirement's source
// field records 'formerly BL-nn'. Kept as an empty export so nothing needs a null check.
exports.backlog = [];

// [ref, topic, decision required, recommendation, decision taken]
exports.decisions = [
  ["F-1", "Inactivity timeout",
   "Whether a 15-minute inactivity timeout is a requirement as stated.",
   "Split it. A timeout must not run during an active test; recommend a session timeout applying only outside an active test, valued by the SPTA.",
   "APPROVED. FR-STA-003 states that no inactivity timeout applies while a test is active. The out-of-test session timeout is to be valued by the SPTA. SRS TSM.45 to be revised."],
  ["F-2", "Camera frame recipe",
   "Whether the frame count, torch states, white balance and exposure behaviour should be fixed in this document.",
   "Resolved by restructuring: FR-CAM-001 and FR-CAM-002 require the software to implement whatever the IVTS specification defines.",
   "CLOSED. The parameters are not to be reinstated in this document."],
  ["F-3", "Out-of-sequence assay detection",
   "Whether FR-ALG-008 is in scope for this version.",
   "It must be; nine risk rows cite it as their software mitigation.",
   "NOT ACHIEVABLE. Out-of-sequence detection is not possible. Detectable instead: that the sample was not introduced into the buffer, and that there is insufficient fluid. FR-ALG-008 has been rewritten accordingly and the consequence for the nine risk rows is recorded in Appendix D. This is the item requiring most attention in the Risk Analysis."],
  ["F-4", "Results letter PDF",
   "Whether PDF generation, download and email sharing are in scope for this version.",
   "Defer, consistent with deferring the user-initiated sharing features.",
   "DEFERRED to future development at priority 1. Recorded as BL-11."],
  ["F-5", "Third-party application launch",
   "Where the requirement originated and whether it is needed.",
   "Withdraw pending an answer; no RA basis and no stated use case.",
   "OPEN. To be confirmed what the capability is used for. Remains outside the body of the document; SRS TSM.44 not yet marked withdrawn."],
  ["F-6", "Verification requirements in this document",
   "Whether release-testing obligations belong in a functional requirements document.",
   "Keep a traceable reference, move the detail to the Software Development Plan.",
   "REFINED. Release testing and development standards are different things: release testing does not include unit testing. FR-LCM-017 now requires integration, system and regression testing at release, and points to the Software Development Plan for unit testing and development standards."],
  ["F-7", "Invalid-test reason category",
   "Whether the result payload carries a reason category for an invalid test.",
   "Reinstate in some form, or narrow FR-TXT-021. A minimal enumeration would be enough.",
   "APPROVED. FR-ALG-012 is reinstated at priority 0, requiring a reason category drawn from a defined enumeration. FR-TXT-021 depends on it."],
  ["F-8", "Privacy screen",
   "Whether the drag-gesture blur feature is in scope for this version.",
   "Defer, and let the SPTA drive it from a stated threat.",
   "RETAINED at priority 2, to be referenced in the SPTA. The Rev 0.4 wording was unclear; FR-SEC-007 now states the exposure to be prevented — content visible in the application switcher or in an operating-system screenshot — rather than the drag-gesture mechanism."],
];

// [component, candidates, comment, decision]
exports.nameSuggestions = [
  ["Transfer Valve",
   "1. Release Button   2. Blue Button (or the part's actual colour)   3. Step 2 Button",
   "“Release Button” names the action rather than the mechanism and survives translation. A colour-based name is simplest but constrains the industrial design. Avoid “valve”, which invites the user to look for something that turns.",
   "DECIDED — “coloured release button”. Adopted in FR-TXT-015, FR-TIM-007 and FR-TIM-009. Confirm the colour word once the part colour is fixed, and align the User Manual and any printed labelling."],
  ["Peel-Off Seal",
   "1. Pull Tab   2. Sticker   3. Cover",
   "“Pull Tab” states the required action and distinguishes the part from the Test Board pouch, which the user also opens. “Sticker” risks being read as a label that can be left in place, which is the failure mode RA 2.7 describes.",
   "TBD. FR-TXT-010 cannot be drafted as user-facing copy until a name is chosen."],
];
exports.renumber = [
 [
  "—",
  "FR-FLW-005",
  "New: step ordering, replacing the withdrawn per-step audit record"
 ],
 [
  "—",
  "FR-TXT-003",
  "New: instructional content must be consistent with the User Manual"
 ],
 [
  "—",
  "FR-TXT-004",
  "New: content held under configuration control as a versioned set"
 ],
 [
  "—",
  "FR-TXT-020",
  "New: consolidated content rule for blocking messages"
 ],
 [
  "—",
  "FR-TIM-014",
  "New: local notification when a timed window opens or is about to expire"
 ],
 [
  "—",
  "FR-COM-009",
  "New: local notifications independent of backend connectivity"
 ],
 [
  "—",
  "FR-RES-005",
  "New: invalid test presents no numeric value (was part of FR-RES-008)"
 ],
 [
  "FR-ALG-010",
  "FR-ALG-010",
  "Unchanged"
 ],
 [
  "FR-ALG-011",
  "FR-ALG-011",
  "Unchanged"
 ],
 [
  "FR-AUT-009",
  "FR-AUT-009",
  "Revised: DoB requested at login only when more than one user is registered"
 ],
 [
  "FR-AUT-012",
  "FR-AUT-012",
  "Revised: DoB confirmed at the start of every test"
 ],
 [
  "FR-AUT-015",
  "FR-AUT-015",
  "Revised: triggering condition for switch user now stated"
 ],
 [
  "FR-AUT-016",
  "—",
  "Withdrawn as a requirement; see open decision F-1"
 ],
 [
  "FR-AUT-017",
  "FR-AUT-016",
  ""
 ],
 [
  "FR-CAM-002 + FR-CAM-003",
  "FR-CAM-001",
  "Consolidated; frame set now defined by the IVTS specification"
 ],
 [
  "FR-CAM-004 + FR-CAM-005",
  "FR-CAM-002",
  "Consolidated; adjustments now defined by the IVTS specification"
 ],
 [
  "FR-CAM-007",
  "FR-CAM-003",
  ""
 ],
 [
  "FR-CAM-008",
  "FR-CAM-004",
  ""
 ],
 [
  "FR-CNS-001",
  "FR-CNS-001",
  "Revised: entry points stated"
 ],
 [
  "FR-CNS-004",
  "FR-CNS-003",
  ""
 ],
 [
  "FR-COM-007 + FR-COM-008",
  "FR-COM-007",
  "Consolidated into one requirement"
 ],
 [
  "FR-COM-009",
  "FR-COM-008",
  ""
 ],
 [
  "FR-FLW-006",
  "FR-TXT-001",
  ""
 ],
 [
  "FR-FLW-007",
  "FR-TXT-002",
  ""
 ],
 [
  "FR-FLW-010",
  "FR-TXT-005",
  ""
 ],
 [
  "FR-FLW-014",
  "FR-TXT-007",
  ""
 ],
 [
  "FR-FLW-015",
  "FR-TXT-006",
  ""
 ],
 [
  "FR-FLW-017",
  "FR-TXT-008",
  ""
 ],
 [
  "FR-FLW-018",
  "FR-TXT-009",
  ""
 ],
 [
  "FR-FLW-019",
  "FR-TXT-010",
  ""
 ],
 [
  "FR-FLW-020",
  "FR-TXT-011",
  ""
 ],
 [
  "FR-FLW-021",
  "FR-TXT-012",
  ""
 ],
 [
  "FR-FLW-022",
  "FR-TXT-013",
  ""
 ],
 [
  "FR-FLW-023",
  "FR-TXT-014",
  ""
 ],
 [
  "FR-FLW-024",
  "FR-TXT-015",
  ""
 ],
 [
  "FR-FLW-025",
  "FR-TXT-016",
  ""
 ],
 [
  "FR-FLW-026",
  "FR-TXT-017",
  ""
 ],
 [
  "FR-FLW-027",
  "FR-TXT-018",
  ""
 ],
 [
  "FR-IMG-004",
  "FR-IMG-003",
  ""
 ],
 [
  "FR-IMG-005",
  "FR-IMG-004",
  ""
 ],
 [
  "FR-IMG-006",
  "FR-IMG-005",
  ""
 ],
 [
  "FR-IMG-007",
  "FR-IMG-006",
  ""
 ],
 [
  "FR-IMG-008",
  "FR-IMG-007",
  ""
 ],
 [
  "FR-IMG-009",
  "FR-IMG-008",
  ""
 ],
 [
  "FR-IMG-010",
  "FR-IMG-009",
  ""
 ],
 [
  "FR-IMG-011",
  "FR-IMG-010",
  ""
 ],
 [
  "FR-IMG-012",
  "FR-IMG-011",
  ""
 ],
 [
  "FR-IMG-013",
  "FR-IMG-012",
  ""
 ],
 [
  "FR-IMG-014",
  "FR-IMG-013",
  ""
 ],
 [
  "FR-IMG-015",
  "FR-IMG-014",
  ""
 ],
 [
  "FR-IMG-016",
  "FR-IMG-015",
  ""
 ],
 [
  "FR-IMG-018",
  "FR-IMG-016",
  ""
 ],
 [
  "FR-IMG-019",
  "FR-IMG-017",
  ""
 ],
 [
  "FR-KIT-002",
  "FR-KIT-001",
  ""
 ],
 [
  "FR-KIT-003",
  "FR-KIT-002",
  ""
 ],
 [
  "FR-KIT-004",
  "FR-KIT-003",
  ""
 ],
 [
  "FR-KIT-005",
  "FR-KIT-004",
  ""
 ],
 [
  "FR-KIT-006",
  "FR-KIT-005",
  ""
 ],
 [
  "FR-KIT-008",
  "FR-KIT-006",
  ""
 ],
 [
  "FR-LCM-009",
  "FR-LCM-017",
  ""
 ],
 [
  "FR-LCM-010",
  "FR-LCM-009",
  ""
 ],
 [
  "FR-LCM-011",
  "FR-LCM-010",
  ""
 ],
 [
  "FR-LCM-012",
  "FR-LCM-011",
  ""
 ],
 [
  "FR-LCM-013",
  "FR-LCM-012",
  ""
 ],
 [
  "FR-LCM-014",
  "FR-LCM-013",
  ""
 ],
 [
  "FR-LCM-015",
  "FR-LCM-016",
  ""
 ],
 [
  "FR-LCM-016",
  "FR-LCM-014",
  ""
 ],
 [
  "FR-LCM-017",
  "FR-LCM-015",
  ""
 ],
 [
  "FR-RES-003",
  "FR-RES-003",
  "Retained; Source corrected to derived — RA 7.17 does not require units"
 ],
 [
  "FR-RES-004 + FR-RES-005 + FR-RES-006",
  "FR-TXT-019",
  "Consolidated as one content requirement"
 ],
 [
  "FR-RES-007",
  "FR-RES-004",
  ""
 ],
 [
  "FR-RES-008",
  "FR-TXT-021",
  ""
 ],
 [
  "FR-RES-012",
  "FR-TXT-001",
  "Absorbed into the general reading-level requirement"
 ],
 [
  "FR-SEC-003",
  "FR-SEC-002",
  ""
 ],
 [
  "FR-SEC-004",
  "FR-SEC-003",
  ""
 ],
 [
  "FR-SEC-005",
  "FR-SEC-004",
  ""
 ],
 [
  "FR-SEC-006",
  "FR-SEC-005",
  ""
 ],
 [
  "FR-SEC-007",
  "FR-SEC-006",
  ""
 ],
 [
  "FR-SHR-003",
  "FR-SHR-001",
  ""
 ],
 [
  "FR-SHR-004",
  "FR-SHR-002",
  ""
 ],
 [
  "FR-SHR-005",
  "FR-SHR-003",
  ""
 ],
 [
  "FR-SHR-006",
  "FR-SHR-004",
  ""
 ],
 [
  "FR-SHR-007",
  "FR-SHR-005",
  ""
 ],
 [
  "FR-SHR-008",
  "FR-SHR-006",
  ""
 ],
 [
  "FR-SHR-009",
  "FR-SHR-007",
  ""
 ],
 [
  "FR-SHR-010",
  "FR-SHR-008",
  ""
 ],
 [
  "FR-STA-003",
  "FR-STA-003",
  "Revised: no inactivity timeout during an active test"
 ],
 [
  "FR-STA-004",
  "FR-STA-004",
  "Revised: applies only where the application was not terminated"
 ],
 [
  "FR-TIM-006",
  "FR-TIM-006",
  "Revised: end event is Sample Pod connection; limit now 30 minutes"
 ],
 [
  "FR-TIM-014",
  "FR-TIM-012",
  ""
 ]
];

// [ref, open item, what it blocks, next step]
exports.openItems = [
  ["O-01", "User-facing name for the Peel-Off Seal", "FR-TXT-010 cannot be drafted as user-facing copy", "Product and regulatory to choose a name; candidates in the terminology appendix. The Transfer Valve is settled as “coloured release button”"],
  ["O-02", "Supported operating-system range, iOS and Android", "FR-PLT-002, FR-PLT-003, FR-RDY-003", "Two constraints apply and the higher governs: the IVTS device qualification for analytical performance, and SPTA 2.5, which requires that versions no longer receiving vendor security updates cannot be used to take a test. The security bound moves over time as vendors end support. Configuration currently admits iOS 13.0.0 and Android 8.0.0"],
  ["O-03", "Minimum battery level and minimum available storage", "FR-RDY-007, FR-RDY-008", "Values to be set and fixed in the application. staticData.lowDiskSpaceSize is currently 80, units to confirm"],
  ["O-04", "OTP attempt limit and expiry", "FR-AUT-005", "Value to be set"],
  ["O-05", "Maximum number of users per phone number", "BL-21", "Value to be set; realised by appUniqueIdentifier. The requirement is deferred to the backlog, so this is only open if that is adopted"],
  ["O-06", "Incubation residence time, release-button window, colour-evolution period and scanning window", "FR-TIM-001, FR-TIM-007, FR-TIM-008, FR-TIM-009, FR-TIM-011", "To be established by the timing-flex study, then fixed in the application. These are the values the two safety-critical timing controls enforce"],
  ["O-07", "Sample collection to Sample Pod connection limit", "FR-TIM-006", "Currently specified as 30 minutes; to be confirmed and fixed"],
  ["O-08", "PIN length, maximum incorrect attempts, and setup grace period", "FR-ACC-004, FR-ACC-005, FR-ACC-006", "Length and grace period to be set and fixed. The attempt limit is deferred to the backlog"],
  
  ["O-10", "Implementation priority for FR-CAM-002, FR-ALG-008 and FR-SHR-011", "Scheduling of camera adjustment, assay-failure detection and the provider engagement model. FR-ALG-008 also carries the only software control for RA 7.34", "Priorities to be assigned. FR-ALG-008 is the one to settle first, because RA 7.34 has no other software mitigation"],
  ["O-11", "Whether raw-equivalent image normalisation is performed on the device or in the backend", "FR-IMG-016 has no stated on-device counterpart", "Confirm with the algorithm team. The localLearnedRawEnabled flag was removed at review, which closed the flag but not the question"],
  ["O-12", "Whether the application needs to launch third-party applications", "SRS TSM.44 is neither implemented nor formally withdrawn", "Confirm the original use case. No Risk Analysis basis, and launching arbitrary applications from a Class B device warrants a security rationale"],
  ["O-13", "Whether doctor-to-patient engagement takes place within the application", "FR-SHR-011, and the scope of the deferred chat and consultation features", "Product decision per partner"],
];

// Appendix I. The conditions under which the software refuses a test or refuses to produce a
// result from one. Added at Rev 1.22 because FR-RDY-014's note claimed SPEC-01 recorded the
// set and SPEC-01 did not, so the note pointed at a list that existed nowhere. Guy asked for
// the list at the SPEC-03 review, specifically so the no-unused-kit block would be on it.
//
// It is a register for review and states no requirement. The requirements state the rule --
// FR-RDY-011, FR-RDY-014 and FR-CFG-006 deliberately do not enumerate their cases -- and this
// is where the cases are written down instead of inside them.
//
// The outcome column carries the three-way distinction, and it is the point of the table:
// a check configuration has switched off is not a check that passed.
// Row: [condition, where it is established, outcome, requirement]

exports.blockBackend = [
 ["The order for this kit cannot be found", "Backend, when the application asks whether a test may start", "Blocks", "FR-RDY-014"],
 ["The order has already been used", "Backend, same exchange", "Blocks", "FR-RDY-014"],
 ["The order has expired", "Backend, same exchange", "Blocks", "FR-RDY-014"],
 ["The user is not authorised to test", "Backend, same exchange", "Blocks", "FR-RDY-014"],
 ["The service has ended for this user", "Backend, same exchange", "Blocks", "FR-RDY-014"],
 ["No unused kit remains for this user", "Backend, from the kits sent against the tests already performed", "Blocks where the check is switched on for the partner", "FR-RDY-014, FR-KIT-004"],
 ["A previous test falls within a defined minimum interval", "Backend", "Blocks where switched on. Future development", "FR-KIT-010"],
 ["The configuration places the application in a blocked state", "Configuration. The reason may be an ended service, a scheduled period of unavailability, a partner-defined condition, or an expired kit", "Blocks", "FR-CFG-006"],
];

exports.blockDevice = [
 ["Device integrity is compromised", "On the device, at start-up", "Blocks", "FR-RDY-001"],
 ["Hardware is below the minimum specification", "On the device", "Blocks", "FR-RDY-002, FR-PLT-005"],
 ["The operating-system version is outside the supported range", "On the device", "Blocks", "FR-RDY-003, FR-PLT-005"],
 ["The application version is unsupported", "Against the backend", "Blocks or notifies. Configuration decides which", "FR-RDY-004"],
 ["There is no internet connection", "On the device", "Blocks", "FR-RDY-005"],
 ["The backend cannot be reached", "On the device", "Blocks", "FR-RDY-006"],
 ["The battery is below the minimum threshold", "On the device", "Blocks, whether or not the device is charging", "FR-RDY-007"],
 ["The battery level cannot be read at all", "On the device", "Neither. The test proceeds", "FR-RDY-007"],
 ["Available storage is below the minimum threshold", "On the device", "Blocks", "FR-RDY-008"],
 ["The camera is absent, or cannot be started", "On the device, and again where the flow requires it", "Blocks", "FR-RDY-009"],
 ["The session is no longer valid, or the backend holds no identity for the user", "On a request to the backend", "Blocks. The user verifies again", "FR-AUT-013, FR-AUT-022"],
 ["A test was performed within the preceding 24 hours", "On the device", "Notifies, once per window", "FR-KIT-007"],
 ["Demonstration behaviour is in force", "Configuration, enforced by the backend", "Notifies", "FR-CFG-004"],
];

exports.blockKit = [
 ["No kit identifier was read", "During the scan", "Refuses a result where the check is switched on for the partner", "FR-KIT-001"],
 ["The kit identifier does not match the defined template", "During the scan", "Refuses a result", "FR-KIT-003"],
 ["The kit identifier has already been used", "Backend, after the scan", "Refuses a result where the check is switched on for the partner", "FR-KIT-004"],
 ["The kit has expired", "After the scan", "Refuses a result where switched on. Future development", "FR-KIT-005"],
 ["The refusal cannot be attributed to a condition the software recognises", "After the scan", "Refuses a result, without stating a reason", "FR-KIT-008"],
 ["The user was asked to present the identifier and could not", "During the scan", "Refuses a result. Future development", "FR-KIT-009"],
];
