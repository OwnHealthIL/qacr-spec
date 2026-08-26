const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  HeadingLevel, AlignmentType, ShadingType, BorderStyle, PageBreak, TableOfContents,
  Header, Footer, PageNumber, VerticalAlign, convertInchesToTwip
} = require("docx");
const fs = require("fs");

const OUT = process.argv[2];
const DIR = process.argv[3] || ".";
const V = require(DIR + "/version.js");

const sections = [
  ...require(DIR + "/reqs-part1.js"),
  ...require(DIR + "/reqs-part2.js"),
];
const APX = require(DIR + "/appendices.js");
const CFG = require(DIR + "/configs.js");
const SPT = require(DIR + "/spta.js");
const REV = require(DIR + "/review.js");
const EPICS = require(DIR + "/epics.js");
require(DIR + "/id-guard.js")(DIR, sections, APX, { verbose: true });

// Feature ownership, read from the epic map so the two documents cannot drift.
// Rebuilding either document fails loudly if a requirement has no owner.
const FEATURE = new Map();
EPICS.forEach(e => e.features.forEach(f => {
  f[2].forEach(id => FEATURE.set(id, f[0]));
  f[3].forEach(id => FEATURE.set(id, f[0]));
}));
{
  const ids = new Set();
  sections.forEach(s => s.reqs.forEach(r => ids.add(r[0])));
  const orphan = [...ids].filter(i => !FEATURE.has(i));
  const ghost = [...FEATURE.keys()].filter(i => !ids.has(i));
  if (orphan.length || ghost.length) {
    console.error("epic map out of step with the requirements:");
    if (orphan.length) console.error("  no feature owns: " + orphan.join(", "));
    if (ghost.length) console.error("  feature names a requirement that does not exist: " + ghost.join(", "));
    process.exit(1);
  }
}

// ---- geometry -------------------------------------------------------------
const MARGIN = 1080;                      // 0.75"
const USABLE = 12240 - 2 * MARGIN;        // 10080 dxa
const COMMENT_W = 1560;                   // reviewer comment column, all tables
const PRI_W  = 520;
const FEAT_W = 700;                       // feature reference, from the epic map
const COLS   = [1150, PRI_W, FEAT_W, 3320, 1360, 1470, COMMENT_W];  // = 10080
const COMMENT_HDR = "Comments";
const HEAD_FILL = "1F3864";
const ALT_FILL  = "F2F5FA";
const ACCENT    = "1F3864";

const noBorders = {
  top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
  left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
};
const thin = (c) => ({ style: BorderStyle.SINGLE, size: 4, color: c });
const cellBorders = {
  top: thin("BFC9DA"), bottom: thin("BFC9DA"),
  left: thin("BFC9DA"), right: thin("BFC9DA"),
};

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: opts.before ?? 0, after: opts.after ?? 100, line: 260 },
    alignment: opts.align,
    children: [new TextRun({
      text, bold: opts.bold, italics: opts.italics,
      size: opts.size ?? 20, color: opts.color, font: "Calibri",
    })],
  });
}

function cell(children, { width, fill, header, valign }) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined,
    borders: cellBorders,
    verticalAlign: valign ?? VerticalAlign.TOP,
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    children,
  });
}

function reqTable(reqs) {
  const headers = ["Req. ID", "Pri.", "Feat.", "Requirement", "Source", "Notes", COMMENT_HDR];
  const headRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => cell(
      [p(h, { bold: true, size: 18, color: "FFFFFF", after: 0 })],
      { width: COLS[i], fill: HEAD_FILL, valign: VerticalAlign.CENTER }
    )),
  });
  const rows = reqs.map((r, idx) => {
    const fill = idx % 2 === 1 ? ALT_FILL : undefined;
    return new TableRow({
      cantSplit: false,
      children: [
        cell([p(r[0], { bold: true, size: 18, after: 0, color: ACCENT })], { width: COLS[0], fill }),
        cell([p(r[4] || "—", { bold: true, size: 19, after: 0, align: AlignmentType.CENTER, color: r[4] === "0" ? "9C1F1F" : ACCENT })], { width: COLS[1], fill }),
        cell([p(FEATURE.get(r[0]) || "—", { size: 17, after: 0, align: AlignmentType.CENTER, color: "5A6B85" })], { width: COLS[2], fill }),
        cell([p(r[1], { size: 19, after: 0 })], { width: COLS[3], fill }),
        cell([p(r[2], { size: 17, after: 0, color: "444444" })], { width: COLS[4], fill }),
        cell([p(r[3] || "—", { size: 17, after: 0, italics: !!r[3], color: "444444" })], { width: COLS[5], fill }),
        cell([p("", { size: 17, after: 0 })], { width: COLS[6], fill }),
      ],
    });
  });
  return new Table({
    columnWidths: COLS,
    width: { size: USABLE, type: WidthType.DXA },
    rows: [headRow, ...rows],
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, bold: true, size: 28, color: ACCENT, font: "Calibri" })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 23, color: ACCENT, font: "Calibri" })],
  });
}

// ---- simple two/three column info tables ---------------------------------
// Appends an empty reviewer comment column and rescales the supplied widths so
// the table still spans the text block. Pass {comments:false} to opt out.
function infoTable(header, rows, widths, opts = {}) {
  const withComments = opts.comments !== false;
  let hdr = header, w = widths;
  if (withComments) {
    const avail = USABLE - COMMENT_W;
    const total = widths.reduce((a, b) => a + b, 0);
    w = widths.map(x => Math.floor(x * avail / total));
    w[0] += avail - w.reduce((a, b) => a + b, 0);   // absorb rounding
    w = [...w, COMMENT_W];
    hdr = [...header, COMMENT_HDR];
  }
  const headRow = new TableRow({
    tableHeader: true,
    children: hdr.map((h, i) => cell(
      [p(h, { bold: true, size: 18, color: "FFFFFF", after: 0 })],
      { width: w[i], fill: HEAD_FILL, valign: VerticalAlign.CENTER }
    )),
  });
  const body = rows.map((r, idx) => {
    const cells = withComments ? [...r, ""] : r;
    return new TableRow({
      children: cells.map((c, i) => cell(
        [p(c, { size: 19, after: 0, bold: i === 0 && !(withComments && i === cells.length - 1) })],
        { width: w[i], fill: idx % 2 === 1 ? ALT_FILL : undefined }
      )),
    });
  });
  return new Table({ columnWidths: w, width: { size: USABLE, type: WidthType.DXA }, rows: [headRow, ...body] });
}

// =========================================================================
const children = [];

// --- Title block
children.push(new Paragraph({ spacing: { before: 1600, after: 0 }, children: [
  new TextRun({ text: "QACR – KIDNEY CHECK", bold: true, size: 24, color: "7F8FA6", font: "Calibri" })
]}));
children.push(new Paragraph({ spacing: { before: 120, after: 0 }, children: [
  new TextRun({ text: "Mobile Application", bold: true, size: 52, color: ACCENT, font: "Calibri" })
]}));
children.push(new Paragraph({
  spacing: { before: 40, after: 240 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
  children: [new TextRun({ text: "Functional Requirements", bold: true, size: 52, color: ACCENT, font: "Calibri" })],
}));
children.push(p(`Document no. QACR-APP-FR-01   ·   Revision ${V.FR} (Draft)`, { size: 22, color: "444444", after: 60 }));
children.push(p("Derived from QACR-RA-01 Risk Analysis Rev 1 (draft), SRS Application – QACR Rev 1.0 and SRS Backend – QACR Rev 1.0; terminology aligned to the QACR System Component Glossary, July 2026; configuration reconciled against the minuteful_kidney_us configuration set; implementation priorities tied to development milestones; security requirements derived from the Security and Privacy Threat Analysis; each requirement mapped to its feature in QACR-APP-EPIC-01 Epic and Feature Map", { size: 20, italics: true, color: "666666", after: 500 }));

children.push(infoTable(
  ["Field", "Value"],
  [
    ["Document title", "QACR Mobile Application – Functional Requirements"],
    ["Document number", "QACR-APP-FR-01"],
    ["Revision", `${V.FR} — ${V.status}`],
    ["Status", "Working draft; not yet under change control"],
    ["Audience", "Development, test and regulatory"],
    ["Open items", "See the Review Register, immediately after the Contents"],
    ["Delivery view", "QACR-APP-EPIC-01 Epic and Feature Map, derived from this document. See section 2.4"],
    ["Prepared by", "—"],
    ["Reviewed by", "—"],
    ["Approved by", "—"],
    ["Software safety class", "Class B per IEC 62304:2006+A1:2015"],
  ],
  [2600, 7480],
  { comments: false }
));

children.push(new Paragraph({ children: [new PageBreak()] }));

// --- TOC
children.push(h1("Contents"));
children.push(p("If the table below appears empty, right-click it in Word and choose “Update Field”.", { italics: true, size: 18, color: "888888", after: 160 }));
children.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));
children.push(new Paragraph({ children: [new PageBreak()] }));


// --- Review register (front matter, unnumbered)
children.push(h1("Review Register"));
children.push(p("Everything still outstanding, gathered here so that a review pass can be made without reading the whole document to find it. The register carries open items only; once an item is decided it moves to the Decision Log appendix. Nothing here is a requirement; each row points at the requirement, appendix or source document where the item lives. References of the form Q-nn are stable, so a closed item keeps its number in the log and is not reissued."));
children.push(p("Six groups follow. Undecided priorities, taken straight from the requirement tables. Parameter values not yet set. Conflicts between this document and one of its sources. Scope questions. Edits the Risk Analysis needs as a consequence of decisions taken here. And consequences of deferral, which are not questions but are things worth knowing before the document is signed off."));

children.push(infoTable(
  ["Group", "Open items"],
  (() => {
    const tbd = sections.reduce((a, s) => a + s.reqs.filter(r => r[4] === "TBD").length, 0);
    const g = [["R.1 Priorities not assigned", tbd], ["R.2 Parameter values not set", REV.parameters.length],
               ["R.3 Conflicts between documents", REV.conflicts.length], ["R.4 Scope questions", REV.scope.length],
               ["R.5 Risk Analysis edits", REV.raEdits.length], ["R.6 Consequences of deferral", REV.consequences.length]];
    const rows = g.map(([n, c]) => [n, String(c)]);
    rows.push(["All groups", String(g.reduce((a, x) => a + x[1], 0))]);
    return rows;
  })(),
  [6600, 1300]
));
children.push(p("", { after: 120 }));

children.push(h2("R.1 Priorities Not Yet Assigned"));
children.push(p("Requirements marked TBD in the body. Every other requirement carries a milestone."));
children.push(infoTable(
  ["Req. ID", "Requirement", "Section", "Note"],
  (() => {
    const rows = [];
    sections.forEach(sec => sec.reqs.forEach(r => {
      if (r[4] === "TBD") rows.push([r[0], r[1].length > 190 ? r[1].slice(0, 190) + "…" : r[1], `${sec.code}. ${sec.title}`, r[3] || "—"]);
    }));
    return rows;
  })(),
  [1100, 4000, 2200, 2780]
));
children.push(p("FR-ALG-008 is the one to settle first, since it carries the only software control for RA 3.8 and RA 7.36, recorded as Q-27.", { before: 120 }));

children.push(h2("R.2 Parameter Values Not Yet Set"));
children.push(p("Each of these is a number a requirement depends upon. The requirement states the behaviour; the value does not yet exist, so the requirement cannot be verified. Appendix B carries the full parameter list, including those now settled."));
children.push(infoTable(["Ref", "Parameter", "Where", "What is needed"], REV.parameters, [780, 2420, 2060, 4820]));

children.push(h2("R.3 Conflicts Between Documents"));
children.push(p("Places where this document and one of its sources say different things. Each needs a decision about which is right, not simply an edit here."));
children.push(infoTable(["Ref", "Conflict", "Where", "What is needed"], REV.conflicts, [780, 2740, 2340, 4220]));

children.push(h2("R.4 Scope Questions"));
children.push(p("Questions whose answer changes what is in the document rather than how something is worded."));
children.push(infoTable(["Ref", "Question", "Where", "What is needed"], REV.scope, [780, 2540, 1860, 4900]));

children.push(h2("R.5 Edits the Risk Analysis Needs"));
children.push(p("Consequences in the Risk Analysis of decisions recorded in this document. Appendix D gives the full assessment for each requirement not included; these are the items where an RA edit is still outstanding."));
children.push(infoTable(["Ref", "Item", "Risk Analysis rows", "What is needed"], REV.raEdits, [780, 2640, 2140, 4520]));

children.push(h2("R.6 Consequences of Deferral"));
children.push(p("Not questions, and not defects. Each is a capability that a source document assumes exists but which is future development at milestone 5, so the assumption does not hold in this version. They are listed because they are easy to lose sight of once an item carries no date."));
children.push(infoTable(["Ref", "Consequence", "Deferred item", "What is affected"], REV.consequences, [780, 2640, 1860, 4800]));

children.push(new Paragraph({ children: [new PageBreak()] }));

// --- 1 Purpose
children.push(h1("1. Purpose and Scope"));
children.push(p("This document establishes the functional requirements for the QACR – Kidney Check mobile application. It is the foundation document from which the Software Requirements Specification, the software architecture and design specifications, and the verification protocols are derived."));
children.push(p("The requirements have been derived from four sources. The first is the QACR Risk Analysis (QACR-RA-01, Rev 1 draft): every risk-control measure in that document that is realised in software, or that depends on the application to convey information for safety, has been translated into one or more requirements here. The second is the pair of Software Requirements Specifications, for the application and for the backend (SRS Application – QACR and SRS Backend – QACR, both Rev 1.0), whose requirements have been carried forward and restated. Where the two describe the same control from opposite sides, one requirement states it and cites both. The third is the Security and Privacy Threat Analysis, from which every threat control realised in the application has been translated into a requirement; Appendix G records that mapping."));
children.push(p("A note on the threat analysis used. The document reviewed is the Minuteful – Kidney Test Security and Privacy Threat Analysis, MNT-KT-US-SPTA-01 Rev 6.0 of 14 November 2024. Its device description refers to a reagent strip and a Color-Board, so it describes the predecessor product rather than QACR, while the SRS cites a separate Q-ACR-US-SPTA-01 Rev 1.0. The two products share their application and backend architecture, and every threat in Rev 6.0 concerns that shared architecture rather than the kit, so it has been treated as the applicable threat model. When the QACR threat analysis is issued, the mapping in Appendix G should be re-run against it and any threat unique to QACR added."));
children.push(p("Component terminology follows the QACR System Component Glossary (July 2026), which is the authority and is not reproduced here. Two rules from it are stated as requirements because they bind the software: the grade-6 reading level for all user-facing text, and the restriction of displayed component names to the approved user-facing set. Both are in section 10. Where the earlier documents use a different name for the same component, Appendix A maps them."));

children.push(h1("2. How to Read This Document"));
children.push(p("Requirements are grouped into functional areas and ordered to follow the user's path through a test: what must be true of the device before a test can begin, who the user is, what kit they are holding, how they are guided through the procedure, how time and image quality are controlled, how data is transmitted and analysed, and how the result is presented and shared. Cross-cutting concerns — security, and the lifecycle controls that risk analysis places on the development process — are placed at the end."));
children.push(p("Each requirement is stated as a single testable obligation using “shall”. Where a requirement is conditional, the condition precedes the obligation."));

children.push(h2("2.1 Requirement Identifiers"));
children.push(p("Identifiers take the form FR-XXX-nnn, where XXX denotes the functional area. Identifiers are permanent: a requirement that is withdrawn is marked as such and its identifier is not reissued."));
children.push(p("From this revision that rule is enforced rather than merely stated. Every identifier ever issued is recorded in a manifest, and each build checks the manifest against the four places an identifier may live — the requirement tables, Appendix D, Appendix E, or a “formerly” note in Appendix E. An identifier that disappears from all four, or that returns to the body after being withdrawn, fails the build. The same rule and the same check apply to the BL references in Appendix E, which were renumbered between earlier revisions and are stable from here. Five identifiers were already unaccounted for when the check was introduced; they are listed in Appendix D.4 rather than quietly absorbed."));
children.push(infoTable(
  ["Prefix", "Functional area"],
  [
    ["FR-PLT", "Platform, distribution and compatibility"],
    ["FR-RDY", "Pre-test readiness verification"],
    ["FR-AUT", "User identification and authentication"],
    ["FR-CNS", "Consent and privacy acknowledgement"],
    ["FR-KIT", "Kit identification and validation"],
    ["FR-FLW", "Guided test flow — structure and behaviour"],
    ["FR-TXT", "User-facing content — what the application says"],
    ["FR-STA", "Test state retention, interruption and cancellation"],
    ["FR-TIM", "Timing control"],
    ["FR-IMG", "Image capture and validation (IVTS)"],
    ["FR-CAM", "Camera control and image acquisition"],
    ["FR-COM", "Data transmission and backend communication"],
    ["FR-ALG", "Analysis, quality control and algorithm version management"],
    ["FR-RES", "Result presentation"],
    ["FR-ACC", "Results access protection"],
    ["FR-PRT", "Results center and application information"],
    ["FR-SHR", "Result routing and provider communication"],
    ["FR-SUP", "Support and help"],
    ["FR-ANL", "Analytics and instrumentation"],
    ["FR-SEC", "Security and data protection"],
    ["FR-CFG", "Application configuration"],
    ["FR-LCM", "Software lifecycle and verification"],
  ],
  [1800, 8280]
));

children.push(h2("2.2 Implementation Priority"));
children.push(p("Each requirement carries the milestone at which it is first needed. The number in the Pri. column is the milestone number. The scale is cumulative: a requirement marked 1 is not less important than one marked 3, it simply has to exist earlier. Everything marked 1, 2 or 3 is required for the clinical study and the submission."));
children.push(infoTable(
  ["Priority", "Milestone", "Date", "Meaning"],
  [
    ["1", "Demonstration app", "mid-October 2026", "Needed to demonstrate the product. The shortest path through a working test"],
    ["2", "Usability rehearsal", "early December 2026", "Needed before an intended user attempts the test unaided. A checkpoint rather than a delivery gate"],
    ["3", "Clinical study and submission — must", "early January 2027", "Mandatory for the study and the submission"],
    ["4", "Clinical study — high priority", "early January 2027", "Wanted for the study but not gating"],
    ["5", "Future development", "none", "Agreed in principle and not in scope for this version. Held in the body, with its section and its traceability, so that a later revision has somewhere to start rather than a list to reconstruct. No date, and no verification obligation for this submission."],
    ["TBD", "Not yet decided", "none", "No milestone and therefore no owner. Listed in the Review Register at R.1"],
  ],
  [800, 2500, 1500, 3780]
));
children.push(p("Milestones 3 and 4 share a date; the difference between them is commitment rather than timing. Two consequences follow and are applied throughout this document. A requirement at milestone 3 may not depend on one at milestone 4, because if milestone 4 is not delivered the milestone-3 obligation cannot be met. And there is no milestone between the clinical study and the submission: everything required for the submission is required for the study. Where behaviour is required for the submission but should not be shown to study participants, it is held behind a feature flag at milestone 3 rather than deferred, which is why FR-AUT-010 and FR-AUT-012 sit at 3.", { before: 120 }));
children.push(p("Every requirement in the body carries a milestone or is marked TBD. Milestone 5 is future development: agreed, held in its own section with its traceability, and carrying no date and no verification obligation for this submission. Requirements identified as not to be implemented are in Appendix D and carry no milestone at all. The Priority Summary appendix gives the distribution by section, and the Review Register lists the requirements whose milestone is undecided.", { after: 200 }));
children.push(p("The Source column records where the requirement came from, so that the traceability matrices in the Risk Analysis and the SRS can be completed without re-deriving the linkage. “RA n.n” refers to a risk row in QACR-RA-01. “SPTA n.n” refers to a threat in the Security and Privacy Threat Analysis, numbered by its STRIDE group. “SRS XXX.n” refers to an individual requirement in the application SRS, and “SRS-BE XXX.n” to one in the backend SRS, using the identifier prefixes below. Where a requirement is stated in neither document but is necessary for a stated risk control to be effective, the source is marked “derived” and the risk it supports is named."));
children.push(p("The SRS numbers its requirements by feature, restarting at 1 in each. The prefixes are:", { after: 100 }));
children.push(infoTable(
  ["Prefix", "SRS feature", "Range", "SRS clause"],
  [
    ["EX.n", "External interfaces requirements", "EX.1 – EX.2", "3.1"],
    ["AUT.n", "Authentication mode", "AUT.1 – AUT.12", "3.2.1"],
    ["STM.n", "Startup mode", "STM.1 – STM.10", "3.2.2"],
    ["TSM.n", "Test mode", "TSM.1 – TSM.46", "3.2.3"],
    ["CON.n", "User consent", "CON.1 – CON.5", "3.2.4"],
    ["LOC.n", "Installation requirements", "LOC.1 – LOC.2", "3.3"],
    ["ATT.n", "Software system attributes", "ATT.1 – ATT.6", "3.4"],
    ["PER.n", "Camera performance requirements", "PER.1 – PER.6", "3.5"],
    ["OTH.n", "Other requirements", "OTH.1", "3.6"],
  ],
  [1300, 4600, 2180, 2000]
));
children.push(p("The backend SRS uses its own prefixes, cited as SRS-BE: EX for external interfaces, SEC for cybersecurity, AUT for authentication, COM for communication mode, AD for administrator mode, LOG for logical database, CON for user consent, PIN for the PIN code and TSM for test mode. Where a requirement here names both an SRS and an SRS-BE identifier, the obligation is shared between the application and the backend.", { before: 120 }));
children.push(p("Two points to confirm when the SRS is updated. First, the SRS carries a note that “ST.7 – ST.11 are associated to the strip and not relevant for the Q-ACR”, which suggests an earlier numbering in the originating document; the identifiers cited here are those the current SRS Rev 1.0 actually renders. Second, several SRS requirements are not included or are deferred, and should be marked as such in the SRS rather than left in force: TSM.16 and PER.1 per Appendix D, and CON.3, CON.5, TSM.36 to TSM.39, TSM.41 to TSM.43, TSM.46, EX.2 and OTH.1 per Appendix E. TSM.44 is unresolved and appears as open item O-12.", { before: 120 }));

children.push(h2("2.4 The Feature Column"));
children.push(p("Each requirement carries the feature that owns it in QACR-APP-EPIC-01, the Epic and Feature Map. That document rearranges these same requirements along what the user does and what the application must be, so that scope can be discussed per milestone and design work has something to attach to. It adds no requirements and changes none; this document remains the authority."));
children.push(p("A reference such as F04.3 is the third feature of epic E04. Every requirement in this document belongs to exactly one feature, and every deferred item in Appendix E carries one too. The mapping is generated rather than typed, and both documents fail to build if a requirement has no feature or a feature names a requirement that no longer exists, so the two cannot quietly drift apart."));
children.push(p("The practical use is answering a question that arises constantly in review: this requirement has changed, what else does that touch? Look up the feature, then read that feature's other requirements in the epic map.", { after: 120 }));

children.push(h2("2.5 System Parameters"));
children.push(p("Appendix B lists every system parameter this document depends upon, states whether it is fixed in the application or supplied by configuration, and records those still to be valued. The Review Register at the front lists the same open values as actionable items."));

children.push(h1("3. Application Overview"));
children.push(p("The QACR – Kidney Check is a prescription-only in vitro diagnostic system for home use, providing quantitative determination of albumin, creatinine and the albumin-to-creatinine ratio in human urine. The application is one component of that system, alongside the physical kit, the backend services and the analysis algorithms."));
children.push(p("The application performs four roles that bear on safety. It is the sole means of guiding a lay user through a multi-stage physical procedure. It is the sole means of enforcing the two time windows on which assay validity depends. It is the means by which image quality sufficient for colorimetric analysis is obtained across a heterogeneous population of smartphone cameras. And it is the means by which a result is associated with the correct patient record and routed to the correct provider."));

children.push(p("Two design principles follow from the Risk Analysis and are applied throughout the requirements below. First, where a precondition for a valid test is not satisfied, the application blocks the action rather than warning the user; the user is not placed in a position of judging whether to proceed. Second, where validity cannot be established, no result is produced; the application never presents a result of reduced or unknown reliability."));

children.push(h2("3.1 The Test Sequence the Application Guides"));
children.push(p("The requirements in sections 9 to 12 follow the physical sequence below, which is derived from the component descriptions in the Product Glossary. Understanding the sequence is necessary to understand why particular steps are timed, blocked or confirmed."));
children.push(p("1.  The user collects a midstream urine sample in the Urine Collection Cup, to or above its fill line. The Sample Pod is pre-attached to the cup's Self-Sealing Valve, and its Capillary Tube draws the precise volume required.", { size: 19, after: 60 }));
children.push(p("2.  The user detaches the Sample Pod and inserts it into the Sample Tank port of the Mixing Cartridge. The Piercer punctures the Sample Tank foil, and the sample mixes with the buffer held there. A second chamber, the Buffer Tank, holds unmixed buffer.", { size: 19, after: 60 }));
children.push(p("3.  The user removes the Peel-Off Seal from the cartridge, places the Test Board on a flat surface, and connects the cartridge to it. This engages the Plunger and Spring assembly, whose vacuum draws diluted sample and unmixed buffer through the Test Board Connector into the Microfluidic Chip.", { size: 19, after: 60 }));
children.push(p("4.  Fluid reaches the Incubation Wells, where the albumin first-stage reaction proceeds. The Transfer Valve holds it there. This is the first timed window.", { size: 19, after: 60 }));
children.push(p("5.  When the incubation time has elapsed, the user opens the Transfer Valve, releasing fluid into the Detection Wells, where the Lyophilized Spheres rehydrate and colour develops for both analytes. This is the second timed window.", { size: 19, after: 60 }));
children.push(p("6.  The user scans the Test Board. The application captures a set of images through the transparent Top-Plate, using the Color Print as the colour reference, and transmits them for analysis.", { size: 19, after: 160 }));

children.push(new Paragraph({ children: [new PageBreak()] }));

// --- requirement sections
let total = 0;
sections.forEach((s) => {
  children.push(h1(`${s.code}. ${s.title}`));
  if (s.intro) children.push(p(s.intro, { after: 180 }));
  children.push(reqTable(s.reqs));
  children.push(p("", { after: 200 }));
  total += s.reqs.length;
});

// --- Appendix A
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix A – Terminology Mapping"));
children.push(h2("A.1 Superseded Component Names"));
children.push(p("The Product Glossary is authoritative and its terms are used throughout this document. The Risk Analysis and the SRS predate it and in places use different names for the same component. This table is provided so that a requirement here can be matched to the clause it came from when reading either source document."));
children.push(infoTable(
  ["SRS Rev 1.0", "Risk Analysis Rev 1", "Used in this document"],
  [
    ["Color-Board", "Test Board", "Test Board — the whole scanned component"],
    ["Color-Board", "Color Print", "Color Print — the printed reference layer on the Top-Plate"],
    ["Capillara", "Sample Pod", "Sample Pod — pre-attached to the Urine Collection Cup"],
    ["Calibration markers", "Color Print reference anchors", "Color Print reference markers"],
    ["—", "Test Board internal valve", "Transfer Valve, shown to the user as the coloured release button"],
    ["—", "Peel foil on the buffer tank", "Peel-Off Seal — user-facing name still open, see A.2"],
    ["—", "self-sealing valve", "Self-Sealing Valve, on the Urine Collection Cup"],
    ["—", "suction-generating mechanism", "Plunger and Spring"],
    ["—", "first-stage wells / detection wells", "Incubation Wells / Detection Wells"],
    ["ACR strip", "—", "Not applicable. SRS clauses ST.7 to ST.11 relate to the strip and were excluded"],
    ["results portal", "results portal", "Results center — renamed at review. The SRS and the Risk Analysis both say portal; the two configuration keys portalResultsHistoryEnabled and resultPortalMoreInfoUrl keep their names, and the FR-PRT identifier prefix is unchanged since identifiers are permanent"],
  ],
  [2100, 2600, 5380]
));
children.push(h2("A.2 Names for User-Operated Parts"));
children.push(p("The glossary classifies the Transfer Valve and the Peel-Off Seal as internal engineering sub-components, yet the user operates both during the test, so each needs a name that may be shown on screen. FR-TXT-002 prohibits presenting internal names to the user."));
children.push(infoTable(
  ["Component", "User-facing name", "Affected requirements"],
  [
    ["Transfer Valve", "Coloured release button — decided. Confirm the colour word once the part colour is fixed, and align the User Manual and any printed labelling.", "FR-TXT-015, FR-TIM-007, FR-TIM-009"],
    ["Peel-Off Seal", "Open — see item O-01. Candidates considered were Pull Tab, Sticker and Cover; Pull Tab states the action and distinguishes the part from the Test Board pouch, which the user also opens.", "FR-TXT-010"],
  ],
  [1700, 5000, 3380]
));
children.push(p("One point to confirm. The Risk Analysis states that the kit identifier QR code sits within the frame area of four black-and-white hexagons that the camera must locate in order to capture a frame. The Product Glossary does not describe a QR code or those hexagons as part of the Color Print. Section 8 and FR-IMG-002 assume the Risk Analysis description holds; if the design has changed, they need review.", { before: 140 }));

children.push(h1("Appendix B – System Parameters"));
children.push(p("Each parameter below is referenced by one or more requirements and requires a value, a permitted range and a documented rationale before design verification can be planned. Most are fixed in the application rather than supplied by configuration; where that is so it is stated, and FR-LCM-006 places them under configuration control either way. The Review Register at the front lists the same open values as actionable items."));
children.push(infoTable(
  ["Parameter", "Referenced by", "Status"],
  [
    ["Minimum battery level", "FR-RDY-007", "TBD"],
    ["Minimum available storage", "FR-RDY-008", "TBD. staticData.lowDiskSpaceSize currently 80, units to confirm"],
    ["Minimum hardware specification", "FR-RDY-002, FR-PLT-005", "Derived from the analytical studies. Realised by staticData.supportedHardwareConfig"],
    ["Supported operating-system range", "FR-RDY-003, FR-PLT-002, FR-PLT-003", "TBD, to follow from the IVTS device qualification. Open item O-02"],
    ["OTP attempt limit and expiry", "FR-AUT-005", "5 minutes to expiry; 5 consecutive failures lock verification for 15 minutes, per SRS-BE AUT.5 and AUT.6"],
    ["Maximum users per phone number", "FR-AUT-011", "TBD. Realised by appUniqueIdentifier"],
    ["Results-center inactivity timeout", "FR-ACC-009", "15 minutes per SPTA 1.7, fixed not configurable. No timeout applies during an active test, per FR-STA-003"],
    ["Post-test lobby duration", "FR-PRT-012", "90 days per staticData.resultsLobbyDuration. The home screen shows the post-test lobby for this period after a result, then returns to its regular state"],
    ["Sample collection to Sample Pod connection limit", "FR-TIM-006", "TBD, fixed not configurable. Currently specified as 30 minutes"],
    ["Incubation Well residence time and release-button window", "FR-TIM-001, FR-TIM-007, FR-TIM-009", "TBD, fixed not configurable. To be established by timing-flex study"],
    ["Colour-evolution period and scanning window", "FR-TIM-001, FR-TIM-008, FR-TIM-011", "TBD, fixed not configurable. To be established by timing-flex study"],
    ["IVTS acceptance thresholds and minimum valid frames", "FR-IMG-001, FR-IMG-015", "Defined in the IVTS document and referenced rather than restated. Realised by minValidFrames and staticData.fieldOfVision (80.0)"],
    ["PIN length and composition", "FR-ACC-004", "Four digits, numeric only. Settled at review"],
    ["Maximum incorrect PIN attempts", "FR-ACC-005", "5 consecutive failed attempts per SRS-BE PIN.5, enforced server-side"],
    ["New-kit alert window", "FR-KIT-007", "24 hours, configurable. Settled at review"],
    ["PIN setup grace period", "FR-ACC-006", "24 hours, confirmed by SPTA 1.7 and SRS-BE PIN.6. After this the PIN is locked and only support can reset it"],
    ["Session token lifetime", "FR-AUT-013", "24 hours per SRS-BE AUT.8"],
    ["Reading-level ceiling", "FR-TXT-001, FR-RES-012", "Flesch-Kincaid grade 6 per the Product Glossary. Fixed, not configurable"],
  ],
  [3000, 3000, 4080]
));
children.push(p("A maximum total test duration and a tone-mapping parameter appear in neither list: the requirements that referenced them are not included, and are recorded in Appendix D.", { before: 120 }));

// --- Appendix C
children.push(h1("Appendix C – Traceability"));
children.push(p("The Source column of each requirements table provides the forward trace from this document to the Risk Analysis and the SRS. Two matrices are to be produced from it and maintained alongside it:"));
children.push(p("•  Risk Analysis to requirements — for every risk in QACR-RA-01 whose risk-control measure is implemented in software, the requirement or requirements that implement it. This matrix populates the traceability appendix of the Risk Analysis and demonstrates that no software risk control is left unimplemented.", { size: 19 }));
children.push(p("•  Requirements to verification — for every requirement in this document, the verification activity that demonstrates it. Requirements in section 25 are verified by review of process records rather than by software test.", { size: 19 }));
children.push(p("•  Glossary to requirements — for every main component and user-operated sub-component in the Product Glossary, the instructional-flow requirement that covers the user action involving it. This matrix is the means of detecting a procedural step that the application does not guide, which is how the Peel-Off Seal step in FR-FLW-019 was identified.", { size: 19 }));
children.push(p(`This revision contains ${total} requirements across ${sections.length} functional areas.`, { before: 160, italics: true, color: "666666" }));

// --- Appendix D : withdrawn
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix D – Requirements Considered and Not Included"));
children.push(p("Requirements that were considered and are not part of this version. They are recorded rather than deleted, because a requirement absent from this document does not by itself remove the obligation from the Risk Analysis. The final column states whether the Risk Analysis relies on the application to deliver the control, and therefore whether the RA needs editing."));
children.push(p("The appendix is divided into four parts. The first three hold the three different kinds of row this appendix has always carried, separated because only the first is an exclusion and reading them as one list has caused confusion before. The fourth records identifiers that are unaccounted for.", { after: 180 }));

const APXD_COLS = [1150, 2900, 2100, 3930];
const APXD_HDR = ["Requirement", "Description", "Disposition", "Risk Analysis impact"];
{
  const isConsolidated = r => /^Consolidated into/.test(r[2]);
  const isSuperseded = r => / \(earlier wording\)$/.test(r[0]) || /^Rewritten/.test(r[2]) || /^Capability not achievable/.test(r[2]);
  const consolidated = APX.withdrawn.filter(isConsolidated);
  const superseded = APX.withdrawn.filter(r => !isConsolidated(r) && isSuperseded(r));
  const excluded = APX.withdrawn.filter(r => !isConsolidated(r) && !isSuperseded(r));

  const n = (c, s, pl) => `${c} ${c === 1 ? s : (pl || s + "s")}`;

  children.push(h2(`D.1 Not Included in This Version — ${n(excluded.length, "requirement")}`));
  children.push(p("Genuine exclusions. Each was considered and is not part of this version. These are the only rows in this appendix that represent a scope decision."));
  children.push(infoTable(APXD_HDR, excluded, APXD_COLS));

  children.push(h2(`D.2 Superseded Wording and Capability Limits — ${n(superseded.length, "row")}`));
  children.push(p("Not an exclusion. A requirement of the same number remains in force in the body of this document, with different wording, so the identifier appears here and in the body at the same time. That is intended: the row records the earlier wording and why it changed, so that a reader coming from the Risk Analysis or the SRS can find the clause they are looking for. Read this one first — it is a capability limit rather than a scope decision, and nine risk rows relied on what is no longer detectable."));
  children.push(infoTable(APXD_HDR, superseded, APXD_COLS));

  children.push(h2(`D.3 Consolidated into Another Requirement — ${n(consolidated.length, "requirement")}`));
  children.push(p("Not exclusions either. The substance of each was carried into another requirement, which is named in the disposition and which also names it in its own Notes column. Nothing was lost; the identifier is retired and is not reissued."));
  children.push(infoTable(APXD_HDR, consolidated, APXD_COLS));

  children.push(h2("D.4 Identifiers Not Accounted For"));
  children.push(p("Five identifiers appear in none of the four places an identifier may legitimately live — the requirement tables, this appendix, Appendix E, or a “formerly” note in Appendix E. Every other number in every prefix is accounted for. They are recorded here so that the gap is deliberate rather than silent."));
  children.push(infoTable(
    ["Identifier", "Status"],
    [["FR-IMG-018", "Not accounted for. Never traced in any revision of this document"],
     ["FR-IMG-019", "Not accounted for"],
     ["FR-SHR-009", "Not accounted for"],
     ["FR-SHR-010", "Not accounted for"],
     ["FR-TIM-013", "Not accounted for"]],
    [1600, 8480]
  ));
  children.push(p("Whether these ever carried text is to be confirmed before this document is finalised; if any did, it needs a withdrawal row of its own in D.1. The review register carries this as an open item. From this revision onward the build checks every identifier ever issued against a manifest, so a number cannot disappear or be reissued without the build failing — see section 2.1.", { before: 120 }));
}

// --- Appendix H : configuration register
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix E – Application Configuration Register"));
children.push(p("The application's behaviour is governed at run time by a configuration set resolved per application and per partner. This register records every configuration flag and states its disposition: whether it realises a requirement that already exists, whether it controls a feature held at milestone 5 as future development, or whether it falls outside the scope of the application requirements. Section 22 states the requirements that apply to configuration itself."));
children.push(p("The configuration set examined was that of the existing minuteful_kidney_us application, used as a reference. A new configuration set will be created for this test and will not carry the flags that are out of scope, so the values quoted below indicate current behaviour rather than a specification. What matters for development is the left-hand column: which requirement each configuration realises, and therefore which values must exist for the requirement to be verifiable.", { after: 180 }));

children.push(h2("E.1 Configurations That Realise an Existing Requirement"));
children.push(p("Each of these is the value a requirement refers to. The requirement states the behaviour; the configuration supplies the number or the switch."));
children.push(infoTable(
  ["Configuration", "Set in", "Requirement", "Note"],
  CFG.bind,
  [2500, 1500, 1700, 4380]
));

children.push(h2("E.2 Configurations Controlling Deferred Features"));
children.push(p("These control features that are future development at milestone 5. No requirement is needed for them in this version."));
children.push(infoTable(
  ["Configuration", "Current value", "Requirement", "Note"],
  CFG.backlogConfigs,
  [2500, 2100, 1200, 4280]
));

children.push(h2("E.3 Configurations Outside the Scope of This Document"));
children.push(p("Grouped by reason. No application requirement follows from any of these."));
children.push(infoTable(
  ["Reason", "Configurations", "Basis"],
  CFG.outOfScope,
  [2000, 4100, 3980]
));


// --- Appendix H : threat analysis coverage
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix F – Threat Analysis Coverage"));
children.push(p("The Security and Privacy Threat Analysis records 40 threats across 8 STRIDE groups. This appendix separates those whose control is realised in, or constrains, the mobile application from those whose control lives in the cloud, the backend or a process, and names the requirement for each of the former. It is the security counterpart of the traceability described in Appendix C."));
children.push(p("Six requirements have no source other than this analysis: FR-SEC-008 to FR-SEC-013, together with FR-COM-010 and FR-ACC-009. Neither the Risk Analysis nor the SRS asked for secure key storage, non-persistence of credentials, generic technical error messages, general input validation, encrypted release artefacts or an audit event channel.", { after: 180 }));

children.push(h2("F.1 Threats With an Application Control"));
children.push(infoTable(
  ["Threat", "Mode or cause", "E·S=R → residual", "Control stated in the threat analysis", "Requirement"],
  SPT.appThreats,
  [700, 2100, 1000, 3400, 1300]
));

children.push(h2("F.2 Threats Controlled Outside the Application"));
children.push(p("No application requirement follows from these. They are listed so that the analysis can be seen to have been read in full, and so that a reviewer can confirm nothing app-facing was missed."));
children.push(infoTable(
  ["Group", "Threats", "Where the control lives"],
  SPT.outsideApp,
  [2200, 1700, 6180]
));

children.push(h2("F.3 Observations"));
children.push(p("Three points arose from the mapping that are not simply requirements."));
children.push(p("•  The minimum operating-system version is constrained twice, and for different reasons. The IVTS device qualification sets a lower bound for analytical performance; SPTA 2.5 sets one for security, requiring that versions no longer receiving vendor security updates cannot be used to take a test. The binding constraint is whichever is higher, and it will move over time as vendors end support. FR-RDY-003 and open item O-02 both note this.", { size: 19, after: 60 }));
children.push(p("•  SPTA 4.11 states that code obfuscation is implemented on Android. FR-SEC-002 has been narrowed to Android to match, so the two documents now agree. Recorded as review register Q-14, now closed.", { size: 19, after: 60 }));
children.push(p("•  SPTA 1.7 supplies the 15-minute inactivity value that was left open at the previous revision, and states it as a security control on the results center rather than a general session timeout. That is consistent with FR-STA-003, which bars any inactivity timeout during an active test, and it closes the open item that was carried for it.", { size: 19, after: 60 }));


// --- Appendix I : decision log
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix G – Decision Log"));
children.push(p("Items that were open in the review register and have since been decided. They are recorded rather than deleted so that the reasoning behind a settled question survives into later revisions, and so that a decision can be revisited knowing why it was taken. References are not reissued: a number that appears here will not reappear in the register."));
children.push(infoTable(
  ["Ref", "Question", "Decision", "Where it landed", "Closed at"],
  REV.closed,
  [780, 2140, 3820, 2060, 880]
));


// --- Appendix J : priority summary
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix H – Priority Summary"));
children.push(p("Distribution of implementation priorities by functional area. Read across a row to see where a section's weight lies; read down the milestone 1 column to see the shortest path to a working demonstration."));
children.push(infoTable(
  ["Area", "1", "2", "3", "4", "5", "TBD", "Total"],
  (() => {
    const order = ["1","2","3","4","5","TBD"];
    const rows = []; const tot = {};
    sections.forEach(sec => {
      const c = {}; order.forEach(k => c[k] = 0);
      sec.reqs.forEach(r => { const k = order.includes(r[4]) ? r[4] : "TBD"; c[k]++; tot[k] = (tot[k]||0)+1; });
      rows.push([`${sec.code}. ${sec.title}`, ...order.map(k => c[k] ? String(c[k]) : "—"), String(sec.reqs.length)]);
    });
    const grand = order.reduce((a,k) => a + (tot[k]||0), 0);
    rows.push(["All areas", ...order.map(k => String(tot[k]||0)), String(grand)]);
    return rows;
  })(),
  [4100, 640, 640, 640, 640, 640, 720, 720]
));
children.push(p("Every requirement in the body is counted, including those at milestone 5. Milestone 5 is future development: agreed, traceable, and carrying no verification obligation for this submission.", { after: 200 }));

// --- Appendix I : the conditions that refuse a test, or refuse it a result
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix I – Conditions That Refuse a Test"));
children.push(p("This register records the conditions under which the software refuses to start a test, or refuses to produce a result from one that has been run. It states no requirement and adds none. It exists because the requirements state the rule and not the cases: FR-RDY-011 requires each condition to be declared as blocking or informing without saying which conditions there are, FR-RDY-014 requires a message specific to each reason the backend refuses without enumerating the reasons, and FR-CFG-006 requires a reason to be given without saying what the reasons are. That is deliberate, because per-partner configuration changes which apply. The cases are written down here instead of inside the requirements."));
children.push(p("Read the outcome column carefully. A condition may block the user, may inform them and let them continue, or may not be assessed at all because configuration has switched the check off for that partner. Those are three different things, and a check that configuration has switched off is not a check that passed. Which values a partner is given is guarded by the product manager rather than by the software.", { after: 180 }));
children.push(p("Not repeated here: the outcomes of the image checks and of the algorithm. An image failing the IVTS thresholds is FR-IMG-015, and the reason categories for an invalid test are FR-ALG-012, which carries its own enumeration obligation.", { after: 180 }));

children.push(h2("I.1 Refused by the Backend When a Test Is Requested"));
children.push(p("The backend answers with at most one reason. Each needs its own message rather than a generic failure, which is what FR-RDY-014 requires."));
children.push(infoTable(
  ["Condition", "Where it is established", "Outcome", "Requirement"],
  APX.blockBackend,
  [2900, 2200, 2600, 2380]
));

children.push(h2("I.2 Established on the Device Before a Test Starts"));
children.push(p("Every one of these is re-evaluated immediately before a test starts and not only at application start-up, which is what FR-RDY-010 requires."));
children.push(infoTable(
  ["Condition", "Where it is established", "Outcome", "Requirement"],
  APX.blockDevice,
  [2900, 2200, 2600, 2380]
));

children.push(h2("I.3 Established at or After the Scan"));
children.push(p("The kit identifier is printed on the Test Board and is therefore read during the scan, at the end of the physical procedure. So none of these can refuse a test before it is run; each refuses it a result."));
children.push(infoTable(
  ["Condition", "Where it is established", "Outcome", "Requirement"],
  APX.blockKit,
  [2900, 2200, 2600, 2380]
));


// =========================================================================
const doc = new Document({
  creator: "QACR Product",
  title: "QACR Mobile Application – Functional Requirements",
  description: "Functional requirements derived from QACR-RA-01 and SRS Application QACR Rev 1.0",
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 21 }, paragraph: { spacing: { line: 264 } } },
      heading1: { run: { font: "Calibri", size: 28, bold: true, color: ACCENT } },
      heading2: { run: { font: "Calibri", size: 23, bold: true, color: ACCENT } },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 560, footer: 560 },
      },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "BFC9DA", space: 4 } },
        children: [new TextRun({ text: `QACR-APP-FR-01 Rev ${V.FR}  ·  QACR Mobile Application – Functional Requirements`, size: 16, color: "7F8FA6", font: "Calibri" })],
      })]}),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], size: 16, color: "7F8FA6", font: "Calibri" })],
      })]}),
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("wrote", OUT, buf.length, "bytes;", total, "requirements in", sections.length, "sections");
});
