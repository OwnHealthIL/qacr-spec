// Application configuration register.
// Sources: "Apps Configurations.md" and the minuteful_kidney_us config folder
// (base.json, service.json, schema.ts, 31 partner overrides). Where the two
// disagree, the JSON folder governs.

// ---------------------------------------------------------------- BIND
// Config realises a requirement that already exists. The config name is the
// value the requirement refers to; no new requirement is needed.
// [config, where set, requirement, note]
exports.bind = [
  ["iosMinAppVersion, androidMinAppVersion", "service.json", "FR-RDY-004", "iOS 9.34.0 / Android 7.28.0 currently set"],
  ["iosMinOsVersion, androidMinOsVersion", "service.json", "FR-RDY-003, FR-PLT-002, FR-PLT-003", "iOS 13.0.0 / Android 8.0.0. FR-PLT-002, FR-PLT-003 and FR-RDY-003 defer the bounds to the IVTS device qualification; see open item O-02."],
  ["iosMaxOsVersion, androidMaxOsVersion", "service.json", "FR-RDY-003", "FR-RDY-003 now requires the version to be within the supported range, so both bounds are covered"],
  ["staticData.supportedHardwareConfig", "base.json, schema.ts", "FR-RDY-002", "Camera count, sensor resolution, aperture and sensor size bounds. Values are derived from the analytical studies. Note the schema comments this as Android-only; confirm iOS enforcement"],
  ["forceUpdateOnPreLogin", "base.json, schema.ts", "FR-RDY-004", "Governs whether the version check blocks before or after login"],
  ["allowCreation", "base.json", "FR-AUT-003", "false for this app — patient records are not created at phone verification"],
  ["allowRegistration", "base.json", "FR-AUT-006", "true — invite-code registration is enabled"],
  ["dobVerification", "base.json", "FR-AUT-012", "Set to force. skip and allowNull must not be used for this app. FR-AUT-012 requires confirmation at every test start. The login-identification case is deferred as FR-AUT-007"],
  ["staticData.privacyUrl, staticData.termsUrl, consentUrl", "base.json", "FR-CNS-001", "The documents FR-CNS-001 makes viewable"],
  ["enabledQrBlock", "base.json", "FR-KIT-002, FR-KIT-004", "true — enables QR validation to block kit reuse"],
  ["enabledNoQrBlock", "base.json", "FR-KIT-001", "true — validates that a colour-board identifier exists for the exam"],
  ["expiredKitDetection", "base.json, schema.ts", "FR-KIT-005", "true — the automatic expiry check. Not present in the MD. The requirement is future development at milestone 5"],
  ["blockSubsequentTests.moreTestsThanKits", "base.json", "FR-KIT-004", "true. Supersedes the MD entries blockSubsequentTest, validateMoreKitsThanExams and duplicateThresholdDays"],
  ["featureFlags.manualWhiteBalanceEnabled, featureFlags.manualExposureEnabled, featureFlags.customToneMappingEnabled", "service.json", "FR-CAM-002", "All true. FR-CAM-002 is at TBD priority, so these remain provisional; see open item O-10"],
  ["featureFlags.qrScanningOptimizationEnabled, featureFlags.qrDetectionUsingMLPackage", "service.json", "FR-KIT-001, FR-KIT-002", "Both true — implementation options for reading the QR code"],
  ["staticData.fieldOfVision", "base.json", "FR-IMG-002, FR-IMG-004, FR-IMG-005", "80.0 — bounds the framing distance checks"],
  ["staticData.supportNumber, staticData.supportEmail", "base.json, overrides", "FR-SUP-002, FR-SUP-003, FR-TXT-020", "844-688-5055 for this app"],
  ["appName", "MD only; not set for this app", "FR-TXT-002", "The application name shown to the user, subject to the approved user-facing naming rule"],
  ["mixpanelProxyEnabled", "base.json (true)", "FR-ANL-001, FR-ANL-004", "Analytics itself is in scope; routing events through the proxy rather than direct to the provider is deferred as FR-ANL-004"],
  ["staticData.surveyUrl", "15 partner overrides", "FR-ANL-006", "The post-test survey is future development at milestone 5"],
  ["staticData.blockFlow, appDownTime", "schema.ts", "FR-CFG-006", "Enum endOfLife / expiredKit / custom. The blocked-state behaviour is in scope at milestone 3 as FR-CFG-006, so these values now have a defined response. The enum here lists three; the product returns ten, which SPEC-01 raises"],
  ["staticData.withAppReview", "base.json (true)", "FR-ANL-009", "Governs the application-store rating prompt, future development at milestone 5 along with the chat flow it attaches to"],
];

// ---------------------------------------------------------------- BACKLOG
// Config controls a feature already deferred in Appendix E.
exports.backlogConfigs = [
  ["staticData.pcpConfig", "base.json (enabled: false)", "FR-SHR-012", "enabled, mandatory, showOnPositiveResultsOnly, isConsentRequired, withChatSkipButton. isConsentRequired maps to FR-CNS-006"],
  ["staticData.enabledPushNotifications", "base.json (true)", "FR-COM-013", "True in configuration although backend push is deferred. Notification behaviour is fixed rather than configurable; the local notifications in FR-TIM-014 and FR-COM-009 are in this version"],
  ["abTestingEnabled", "Not in scope", "FR-CFG-008", "Removed from scope. Reinstate with FR-CFG-008"],
  ["postResultConsultation", "base.json", "FR-SHR-013", "enableStartChat and enableResumeChat both false"],
  ["staticData.chatTransitionToResultsPortal", "base.json (true)", "FR-SHR-013", "Only meaningful once chat exists"],
  ["withDoctorNotes, doctorsNoteTemplateName", "base.json", "FR-SHR-015", "true — doctor notes returned with results."],
  ["resultsLetterFeedbackSurveyUrl", "schema.ts", "FR-SHR-015", "Survey on the results letter"],
  ["enableFollowupTests", "MD only", "No requirement", "Not set for this app; no requirement exists for a follow-up test flow"],
  ["staticData.faqUrl", "base.json", "FR-SUP-001", "The FAQ page and its menu route are future development at milestone 5"],
  ["staticData.additionalResultsCTA", "base.json, 9 overrides", "FR-SUP-004", "resultsChatCTAEnabled, resultsCenterCTAEnabled and type. Gates whether the book-an-appointment action in the post-test lobby offers a call control as well as mark-as-done"],
  ["staticData.resultsLobbyDuration", "base.json (90)", "FR-PRT-012", "90 days. The home screen presents the post-test lobby for this period after a result, then reverts to its regular state"],
  ["prescriptionFlowEnabled", "base.json (true)", "FR-SHR-001, FR-SHR-011", "FR-SHR-011 states whether doctor-to-patient engagement occurs in the application, which bounds this flow"],
];

// ---------------------------------------------------------------- OUT OF SCOPE
// No application requirement. Either backend-only, another product, or
// commercial/analytics function with no bearing on device safety or performance.
exports.outOfScope = [
  ["Backend messaging and ordering", "fromNumber, outgoingNumber, fromPhoneVerificationNumber, smsPartnerConsentOutgoingNumber, appLink, appHash / androidAppHash, leaflet, partners, partnerInitFlow, newService, allowOrderCreation, blockMultipleExamsOnOrder, doNotSendDuplicateResults, flagOrderManualInspection, checkPatientEndOfService", "Backend behaviour and outbound messaging. Belongs to the backend requirements specification, not the application. checkPatientEndOfService can block a patient holding a kit; if it does, the user-facing behaviour should use the blocked-state handling in FR-CFG-006 rather than a separate path."],
  ["Analytics", "useDeprecatedMixpanelToken, surveyViewProbability", "mixpanelProxyEnabled, surveyUrl and withAppReview each realise a requirement and appear in F.1. Analytics token selection has no bearing on device safety or performance, and surveyViewProbability is a sampling rate rather than a behaviour."],
  ["Other products", "getIpLocationInfo, shouldProcessColorBoardId, ignoreEmptyColorBoardId, storeLocatorUrl, pharmacyNotice, deliveryNotice, deliveryHours, withBloodPressure, checkPatientConsent, useUkMeasurements, isScaleNumerical, customBlockByFlow", "Velieve, Dip UTI, NHS or UK-market configurations. Not applicable to QACR US. "],
  ["Superseded by newer configuration", "blockSubsequentTest, validateMoreKitsThanExams, duplicateThresholdDays, complementaryCareConfig", "Replaced by blockSubsequentTests and additionalResultsCTA respectively. schema.ts marks complementaryCareConfig as retained only for backward compatibility."],
];

// ---------------------------------------------------------------- REVIEW
// [ref, config(s), the question, recommendation]
exports.review = [
  ["R-01", "staticData.shortFlowMinSuccessfulOrderNumber, staticData.shortFlowMinDaysSinceLastSuccessfulOrder",
   "These enable a shortened flow for users who have completed previous tests successfully. What is omitted in the short flow, and does it omit any instructional step that the Risk Analysis relies on?",
   "Treat as a risk question before a scope question. Sections 9 and 10 of this document exist because RA 4.1, 7.3, 7.6 to 7.10 and 7.26 to 7.29 place the control on step-by-step guidance with confirmation. If the short flow removes steps or confirmations, those rows no longer hold for repeat users and the RA needs a second scoring path. Recommend either excluding the short flow from this version, or specifying exactly which steps it omits so the affected rows can be re-assessed. Set in 8 partner overrides, so it is in active use."],

  ["R-02", "enabledDemoResults, demoResults, staticData.enabledResultsDemoFlow, staticData.enabledDemoSkip, staticData.demoFlow.mockResults",
   "How is it guaranteed that demo behaviour cannot occur for a real patient?",
   "This is the highest-risk group in the register. The MD states that enabledDemoResults “will override the algo results and return a demo result”, and enabledDemoSkip allows flows to be skipped. A configuration error would therefore produce a plausible but fabricated ACR result, which is RA 4.21 realised by configuration rather than by defect. FR-CFG-004 has been added requiring that demo behaviour is impossible for a non-demo partner and that the application marks any demo result unmistakably. Recommend confirming the enforcement is server-side and independent of the partner type flag, since the MD notes the two must agree."],

  ["R-03", "staticData.showAcrResultOnly",
   "Set to true. The device is described in the Risk Analysis and Glossary as quantifying albumin, creatinine and the ACR. Does the app show only ACR?",
   "FR-RES-002 currently implies all reported values are shown. If only ACR is displayed to the patient, say so explicitly in FR-RES-002 and confirm the albumin and creatinine values still reach the clinician through FR-SHR-002, since the intended use claims all three. Recommend clarifying rather than leaving the requirement broader than the product."],

  ["R-04", "featureFlags.localLearnedRawEnabled",
   "false in service.json, not in the MD. Is this the on-device raw-equivalent normalisation that the withdrawn FR-CAM-006 described?",
   "If yes, FR-CAM-006 should not have been withdrawn outright — Appendix D flags exactly this dependency, that FR-IMG-016 otherwise has no on-device counterpart. If normalisation is performed in the backend and this flag is an experiment, no requirement is needed. Recommend confirming with the algorithm team; it is the one withdrawal in Appendix D whose consequence is unresolved."],

  ["R-05", "staticData.supportedHardwareConfig",
   "The schema comments this as “Android camera configuration limits — US regulatory requirements”. Does it apply to iOS as well?",
   "FR-RDY-002 is written platform-neutrally. If the bounds are enforced on Android only, then iOS devices are admitted on the basis of the store compatibility filter in FR-PLT-004 alone, which is a weaker control than RA 4.5 assumes. Recommend either extending enforcement to iOS or stating in FR-RDY-002 that iOS relies on the curated model list, so the difference is visible."],

  ["R-06", "staticData.blockFlow, appDownTime, customBlockFlowAlertParams",
   "A general mechanism for blocking the application, with a configurable alert. No requirement covered it before this revision.",
   "FR-CFG-006 and FR-CFG-007 have been added. The point needing your decision is the alert content: customBlockFlowAlertParams carries a free-text title and body supplied by configuration, which bypasses the content controls in section 10, including the grade-6 reading level in FR-TXT-001. Recommend requiring that configured alert text is drawn from an approved content set rather than authored per partner."],

  ["R-07", "appSession, appSessionSignUpDaysLimit",
   "appSessionSignUpDaysLimit is 1 day. FR-ACC-006 states a 24-hour window to set a PIN before support intervention is required. Are these the same control?",
   "They appear to be, expressed in different units in different documents. Recommend confirming, and if so binding FR-ACC-006 to appSessionSignUpDaysLimit so there is one value rather than a requirement and a config that can drift apart."],

  ["R-08", "appUniqueIdentifier, skipValidationWhenFieldIsEmpty",
   "appUniqueIdentifier defines what makes a patient unique, with mobileNumber and dateOfBirth as the example. FR-AUT-011 assumes phone number plus DoB. Not set in this app's files.",
   "This config decides whether FR-AUT-011 holds. If it were set to mobileNumber alone, two family members sharing a phone could not be distinguished and RA 6.4, results attributed to the wrong patient, would lose its control. Recommend setting it explicitly for this app rather than relying on an inherited default, and binding FR-AUT-011 to it."],

  ["R-09", "blockSubsequentTests.timeLimit",
   "enabled false, hours 24. What does the time limit prevent, and should it be enabled?",
   "Distinct from the kit-reuse block in FR-KIT-006, which is already covered by moreTestsThanKits. A minimum interval between tests is a clinical rather than a safety control, and no RA row calls for it. Recommend leaving it disabled and out of this version unless there is a clinical rationale, in which case it needs its own requirement."],

  ["R-10", "portalResultsHistoryEnabled",
   "true. The results center retains a history of previous results. Section 18 covers access to the results center but no requirement describes what it contains.",
   "There is a real gap here: the requirements govern the result of the current test only. A history view raises questions the current set does not answer — whether invalidated tests appear, whether results from a different registered user on the same phone are visible, and how long history is retained. Recommend a short set of requirements for the results center contents, or deferring the history view. The second question touches RA 6.4 and unauthorised disclosure."],

  ["R-11", "prescriptionFlowEnabled",
   "true. FR-SHR-001 was expanded per your comment to mention prescription generation, but no requirement describes the prescription flow in the app.",
   "Either scope it now or defer it explicitly. It is enabled in configuration and in 11 partner overrides, which suggests it is live, so leaving it unspecified is the weakest of the three options. Recommend a decision on whether the prescription flow is part of this device's intended use or a separate service the app links to, because that determines whether it needs requirements here at all."],

  ["R-12", "staticData.positiveResultsVerifyUnderstandingEnabled",
   "true. Shows a different set of chat prompts after an abnormal result to verify the user understood it.",
   "This is directly relevant to RA 7.17, misinterpretation of the ACR result, whose current controls are the results-screen instruction and the automatic clinician share. A comprehension check is a stronger control than a static instruction. Recommend either bringing it into scope with a requirement in section 10 and citing it in RA 7.17, or noting that RA 7.17's residual score does not depend on it. It currently sits in configuration doing safety work that no requirement claims."],

  ["R-13", "staticData.enabledThumbnails, staticData.thumbnailsConfig",
   "true, with 30-frame save frequency, 0.85 JPEG compression and 0.2 resize. Thumbnails are uploaded to storage.",
   "Confirm whether thumbnails are part of the exam record or a diagnostic aid. If they inform any analysis or review decision, the compression settings affect that data and belong under configuration control per FR-CFG-003. If they are for engineering triage only, they are out of scope but FR-SEC-005 still applies to them."],

  ["R-14", "sendPngImages",
   "false by default per the MD, not set for this app. Controls whether PNG images are sent to the server.",
   "The withdrawn FR-CAM-006 concerned image format for classification, so the two are related. Recommend confirming the format the algorithm receives and whether it can vary by configuration; if it can, the algorithm version mapping in FR-ALG-002 should account for format as well as version."],

  ["R-15", "allowIpadForReview",
   "false by default. Allows a test to be performed on an iPad.",
   "FR-PLT-002 admits iOS but the platform list does not mention iPadOS, and the IVTS device qualification presumably does not cover iPad cameras. Recommend confirming this remains false for this app, and stating in FR-PLT-002 that iPadOS is not supported so the config and the requirement agree."],

  ["R-16", "minAge, maxAge",
   "Min and max patient age for the eligibility questions. Not set for this app.",
   "No eligibility flow appears anywhere in the requirements. If the app asks eligibility questions, that flow needs requirements; if eligibility is established before the kit is dispatched, these configs are out of scope. Recommend confirming which, since an in-app eligibility gate would be a new section."],

  ["R-17", "staticData.testPreviewEnabled, staticData.resultsLobbyDuration",
   "false and 90 respectively. Neither is documented in the MD and the schema comment for resultsLobbyDuration refers to “lobby 4”.",
   "Behaviour unclear from the configuration alone. Recommend a one-line description of each so they can be classified; resultsLobbyDuration in particular sounds as though it governs how long results remain accessible, which would interact with section 18."],

  ["R-18", "staticData.careManagementFlowEnabled, staticData.diagnosedCkdFlowEnabled, staticData.additionalResultsCTA, staticData.optumKidneySolutions",
   "A group controlling alternative post-result journeys for diagnosed users and partner-specific calls to action.",
   "These vary what the patient sees after a result, which is the subject of section 17 and FR-TXT-019. Recommend one requirement stating that post-result content and calls to action are drawn from an approved content set and do not alter the reported values or the instruction to consult a clinician. That bounds the variation without specifying each partner journey."],

  ["R-19", "resultsType, withDoctorNotes",
   "resultsWithInterpretation and true. Interpretation text and doctor notes accompany the result.",
   "Interpretation text shown to a lay patient is content under section 10 and subject to FR-TXT-001. Doctor notes generated from a per-partner template are not currently constrained by any requirement. Recommend confirming whether doctor notes are shown to the patient or only to the clinician; if to the patient, they need to fall under the approved content set."],

  ["R-20", "multiplePatientsSameAddressEnabled",
   "Set in three overrides, absent from the MD. Presumably permits several patients registered at one address.",
   "Likely relates to household use and therefore to FR-AUT-011 and RA 6.4. Recommend a one-line description so it can be classified alongside R-08."],

  ["R-21", "staticData.singleKit",
   "true. Informs the app that the user has a single kit.",
   "Interacts with FR-KIT-006 and FR-AUT-020. Recommend confirming whether it changes any user-facing behaviour, for instance whether the app offers a retest after an invalid result when only one kit was shipped. If it does, that behaviour needs stating, because RA rows that mitigate by “prompt the user to repeat the test with a new kit” assume a new kit is obtainable."],

  ["R-22", "staticData.enabledPushNotifications versus FR-COM-013",
   "Push notifications are enabled in configuration but the requirement is future development at milestone 5.",
   "The configuration and the requirement set disagree. FR-TIM-014 and FR-COM-009 require local notifications in this version, which may be what is actually in use. Recommend confirming which mechanism delivers the timing prompts, because if it is backend push then FR-TIM-014 depends on a deferred feature and connectivity."],

  ["R-23", "iosMinOsVersion 13.0.0, androidMinOsVersion 8.0.0",
   "The configuration admits older operating systems than the SRS states, and than FR-PLT-002 and FR-PLT-003 carry forward.",
   "One of the two is wrong. This matters because RA 4.6 relies on unsupported versions being blocked, and the IVTS device qualification defines which versions were actually tested. Recommend setting both from the IVTS qualification and correcting whichever document disagrees."],

  ["R-24", "checkPatientEndOfService",
   "true. The backend checks whether the patient's service period has ended during the init call.",
   "Classified as backend, but it can block a patient who is holding a kit. If it results in the application preventing a test, the user-facing behaviour needs a requirement and should use the blocking mechanism in FR-CFG-006 rather than a separate path. Recommend confirming what the app does when this check fails."],
];


// Configurations removed from scope at the Rev 0.4 review.
// [config, decision, consequence]
exports.removedConfigs = [
  ["staticData.lowDiskSpaceSize",
   "Unlinked at review",
   "FR-RDY-008 now states the storage threshold as fixed in the application. Decided together with the milestone-3 placement of configuration retrieval, so that a milestone-1 requirement does not depend on a mechanism that arrives later."],
  ["minValidFrames",
   "Unlinked at review",
   "The minimum number of valid frames is a property of the IVTS specification and is fixed in the application. FR-IMG-001 and FR-IMG-015 no longer refer to a configuration value."],
  ["featureFlags.selectBestCameraEnabled",
   "Unlinked at review",
   "The frame set FR-CAM-001 acquires is defined by the IVTS specification and fixed in the application. Note that featureFlags.manualWhiteBalanceEnabled, manualExposureEnabled and customToneMappingEnabled remain bound to FR-CAM-002, whose priority is still undecided."],
  ["resultsType, resultPortalMoreInfoUrl",
   "Unlinked at review",
   "The content FR-TXT-019 requires on the results screen is fixed and released under the versioned content set of FR-TXT-004, rather than varied per partner by configuration."],
  ["staticData.showAcrResultOnly",
   "Unlinked at review",
   "FR-RES-002 presents the ratio only, stated as fixed behaviour. Presentation of the albumin and creatinine values remains deferred as FR-RES-007."],
  ["staticData.shortFlowMinSuccessfulOrderNumber, staticData.shortFlowMinDaysSinceLastSuccessfulOrder",
   "Removed — the short flow is not supported ()",
   "The instructional controls in sections 9 and 10 now apply to every test without exception, so the RA rows that rely on step-by-step guidance need no second scoring path. Note the flags are currently set in eight partner overrides and must be cleared."],
  ["featureFlags.localLearnedRawEnabled",
   "Removed ()",
   "Closes the flag but not the underlying question recorded against FR-CAM-006 in Appendix D: if raw-equivalent normalisation is not performed in the backend, FR-IMG-016 has no on-device counterpart."],
  ["staticData.positiveResultsVerifyUnderstandingEnabled",
   "Removed ()",
   "RA 7.17 retains its existing controls only — the static results-screen instruction in FR-TXT-019 and the automatic clinician share — at a post-mitigation RPN of 6. The flag is currently true in base.json and must be cleared."],
  ["abTestingEnabled",
   "Removed",
   "Reinstate with FR-CFG-008 if A/B testing returns. Note base.json and service.json currently disagree on its value."],
  ["sendPngImages",
   "Removed ()",
   "Image format for analysis is fixed rather than configurable. Confirm the format the algorithm receives is stated in the IVTS specification."],
  ["allowIpadForReview",
   "Removed ()",
   "iPadOS is not a supported platform. FR-PLT-002 admits iOS only; the IVTS device qualification does not cover iPad cameras."],
  ["minAge, maxAge",
   "Removed ()",
   "No in-application eligibility flow. Eligibility is established before the kit is dispatched."],
  ["staticData.testPreviewEnabled",
   "Removed ()",
   "No consequence identified."],
];

// Decisions recorded against the Appendix I review items.
// [ref, decision]
exports.reviewDecisions = {
  "R-01": "REMOVE. The short flow is not to be supported. See Appendix J.",
  "R-02": "KEEP all three: the demonstration flag, the selector for real or mock results, and the mock results themselves. Enforcement is server-side per the revised FR-CFG-004.",
  "R-03": "BACKLOG. Presentation of the albumin and creatinine values is deferred to FR-RES-007.",
  "R-04": "REMOVE the configuration. See Appendix J and the FR-CAM-006 entry in Appendix D.",
  "R-05": "The minimum hardware specification is derived from the analytical studies. FR-RDY-002 revised accordingly.",
  "R-06": "Priority is carried by the requirements, not by the configuration. FR-CFG-006 is priority 2; the withdrawn FR-CFG-007 is recorded in Appendix D.",
  "R-07": "TBD, low priority.",
  "R-08": "TBD, low priority.",
  "R-09": "TBD, low priority.",
  "R-10": "TBD, low priority. Recorded as Q-23 so the results center-contents question is not lost.",
  "R-11": "A requirement is added: FR-SHR-011 states whether doctor-to-patient engagement is held within the application.",
  "R-12": "REMOVE. See Appendix J.",
  "R-13": "TBD, low priority.",
  "R-14": "REMOVE. See Appendix J.",
  "R-15": "REMOVE. See Appendix J.",
  "R-16": "REMOVE. See Appendix J.",
  "R-17": "REMOVE testPreviewEnabled. resultsLobbyDuration is TBD, low priority.",
  "R-18": "TBD, low priority.",
  "R-19": "TBD, low priority.",
  "R-20": "TBD, low priority.",
  "R-21": "TBD, low priority.",
  "R-22": "Notifications are to be fixed rather than configurable. Priority follows the requirement: FR-TIM-014 and FR-COM-009 are priority 1; backend push remains FR-COM-013.",
  "R-23": "TBD. FR-PLT-002, FR-PLT-003 and FR-RDY-003 now defer the version bounds to the IVTS device qualification.",
  "R-24": "TBD, low priority.",
};
