const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  HeadingLevel, AlignmentType, ShadingType, BorderStyle, PageBreak, TableOfContents,
  Header, Footer, PageNumber, VerticalAlign,
} = require("docx");
const fs = require("fs");

const OUT = process.argv[2];
const DIR = process.argv[3] || ".";
const V = require(DIR + "/version.js");

const sections = [...require(DIR + "/reqs-part1.js"), ...require(DIR + "/reqs-part2.js")];
const APX = require(DIR + "/appendices.js");
const EPICS = require(DIR + "/epics.js");
const domainsFor = require(DIR + "/domains.js");

// ---- derived indices ------------------------------------------------------
const PRI = new Map();   // FR id -> milestone
const REQTEXT = new Map();
const REQ = new Map();
sections.forEach(s => s.reqs.forEach(r => { PRI.set(r[0], r[4]); REQTEXT.set(r[0], r[1]); REQ.set(r[0], { text: r[1], note: r[3] }); }));
const BLPRI = new Map(); APX.backlog.forEach(r => BLPRI.set(r[0], r[4]));
const BLTEXT = new Map(); APX.backlog.forEach(r => BLTEXT.set(r[0], r[1]));

const OWNER = new Map();   // FR/BL id -> {epic, feature, name}
EPICS.forEach(e => e.features.forEach(f => {
  f[2].forEach(id => OWNER.set(id, { epic: e.code, feature: f[0], name: f[1] }));
  f[3].forEach(id => OWNER.set(id, { epic: e.code, feature: f[0], name: f[1] }));
}));

const MS = ["1", "2", "3", "4", "5"];
function roll(ids) {
  const v = ids.map(i => PRI.get(i));
  const n = v.filter(x => MS.includes(x)).map(Number);
  return {
    first: n.length ? Math.min(...n) : null,
    last: n.length ? Math.max(...n) : null,
    tbd: v.filter(x => x === "TBD").length,
  };
}

// A feature whose requirements sit at more than one milestone must say, in its
// description, which part lands when. Checked here so the obligation cannot be
// forgotten when a priority changes or a requirement is added.
{
  const bad = [];
  EPICS.forEach(e => e.features.forEach(f => {
    // Milestone 5 is excluded. The split exists so the scope of a *dated* milestone can
    // be read without cross-referencing; milestone 5 has no date, and "the rest is future
    // development" is the same sentence on every feature that has any. The requirements
    // column still groups the milestone-5 identifiers under their own heading.
    const labels = new Set(f[2].filter(i => PRI.get(i) !== "5")
                               .map(i => PRI.get(i)).map(m => m === "TBD" ? "TBD" : "M" + m));
    if (labels.size < 2) return;
    const given = new Set((f[6] || []).map(x => x[0]));
    const missing = [...labels].filter(l => !given.has(l));
    if (missing.length) bad.push(`${f[0]} spans ${[...labels].sort().join(", ")} but its description does not break out ${missing.join(", ")}`);
  }));
  if (bad.length) {
    console.error("features spanning several milestones without a per-milestone description:");
    bad.forEach(b => console.error("  " + b));
    process.exit(1);
  }
}
// Every feature must carry a development domain, so a new one cannot ship untagged.
{
  const untagged = [];
  EPICS.forEach(e => e.features.forEach(f => { if (!domainsFor(f[0])) untagged.push(f[0]); }));
  if (untagged.length) {
    console.error("features with no development domain in domains.js: " + untagged.join(", "));
    process.exit(1);
  }
}
function msLabel(f) {
  const r = roll(f[2]);
  if (!r.first) return r.tbd ? "TBD" : "—";
  let s = "M" + r.first;
  if (r.last !== r.first) s += "–M" + r.last;
  if (r.tbd) s += " +TBD";
  return s;
}
const MSNAME = {
  1: "Demo application",
  2: "Usability rehearsal",
  3: "Clinical study — submission must",
  4: "Clinical study — high priority",
  5: "Future development — no date",
};
const KINDNAME = {
  app: "Application",
  backend: "Backend and algorithm",
  content: "Content",
  process: "Process — not feature work",
};

// ---- geometry -------------------------------------------------------------
const MARGIN = 1080;
const USABLE = 12240 - 2 * MARGIN;              // 10080
const COMMENT_W = 1400;
const FCOLS = [640, 520, 3220, 2320, 1420, COMMENT_W];   // = 9520 + ... check
const HEAD_FILL = "1F3864";
const ALT_FILL = "F2F5FA";
const ACCENT = "1F3864";
const MSFILL = { 1: "C6553F", 2: "B07A1E", 3: "1F3864", 4: "4A6285", 5: "6E7480", TBD: "8A2F2F", "—": "777777" };
const DOMFILL = { iOS: "3C6E9F", Android: "2E7D5B", Backend: "6B4E9E", Algo: "9E5B2E", Content: "8A6D3B", Process: "6B7789" };

const thin = (c) => ({ style: BorderStyle.SINGLE, size: 4, color: c });
const cellBorders = { top: thin("BFC9DA"), bottom: thin("BFC9DA"), left: thin("BFC9DA"), right: thin("BFC9DA") };

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
function runs(list, opts = {}) {
  return new Paragraph({
    spacing: { before: opts.before ?? 0, after: opts.after ?? 0, line: 260 },
    children: list.map(x => new TextRun({
      text: x.t, bold: x.b, italics: x.i, size: x.s ?? 18, color: x.c, font: "Calibri",
    })),
  });
}
function cell(children, { width, fill, valign }) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined,
    borders: cellBorders,
    verticalAlign: valign ?? VerticalAlign.TOP,
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    children,
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, bold: true, size: 28, color: ACCENT, font: "Calibri" })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 23, color: ACCENT, font: "Calibri" })],
  });
}

// generic table with an appended comments column
function infoTable(header, rows, widths, opts = {}) {
  const withComments = opts.comments !== false;
  let hdr = header, w = widths;
  if (withComments) {
    const avail = USABLE - COMMENT_W;
    const total = widths.reduce((a, b) => a + b, 0);
    w = widths.map(x => Math.floor(x * avail / total));
    w[0] += avail - w.reduce((a, b) => a + b, 0);
    w = [...w, COMMENT_W];
    hdr = [...header, "Comments"];
  }
  const headRow = new TableRow({
    tableHeader: true,
    children: hdr.map((h, i) => cell([p(h, { bold: true, size: 18, color: "FFFFFF", after: 0 })],
      { width: w[i], fill: HEAD_FILL, valign: VerticalAlign.CENTER })),
  });
  const body = rows.map((r, idx) => {
    const cells = withComments ? [...r, ""] : r;
    return new TableRow({
      children: cells.map((c, i) => cell(
        [p(String(c), { size: 19, after: 0, bold: i === 0 && !(withComments && i === cells.length - 1) })],
        { width: w[i], fill: idx % 2 === 1 ? ALT_FILL : undefined })),
    });
  });
  return new Table({ columnWidths: w, width: { size: USABLE, type: WidthType.DXA }, rows: [headRow, ...body] });
}

// the epic feature table
function featureTable(features) {
  const W = [640, 560, 3200, 2320, 1400, COMMENT_W];
  const fix = USABLE - W.reduce((a, b) => a + b, 0); W[2] += fix;
  const hdr = ["Ref.", "M", "Feature and intent", "Design and UX", "Requirements", "Comments"];
  const headRow = new TableRow({
    tableHeader: true,
    children: hdr.map((h, i) => cell([p(h, { bold: true, size: 18, color: "FFFFFF", after: 0 })],
      { width: W[i], fill: HEAD_FILL, valign: VerticalAlign.CENTER })),
  });
  const rows = features.map((f, idx) => {
    const fill = idx % 2 === 1 ? ALT_FILL : undefined;
    const lab = msLabel(f);
    const key = lab.startsWith("M") ? lab[1] : (lab === "TBD" ? "TBD" : "—");
    // Requirements are grouped by the milestone they carry, so that a feature
    // spanning several milestones says plainly which part lands when.
    const frKids = [];
    const byMs = {};
    f[2].forEach(id => { const m = PRI.get(id); (byMs[m] = byMs[m] || []).push(id.replace(/^FR-/, "")); });
    const order = [...MS, "TBD"].filter(m => byMs[m]);
    order.forEach((m, i) => {
      frKids.push(runs([
        { t: (m === "TBD" ? "TBD" : "M" + m) + "  ", b: true, s: 16, c: MSFILL[m] || ACCENT },
        { t: byMs[m].join(", "), s: 16 },
      ], { after: (i < order.length - 1 || f[3].length) ? 50 : 0 }));
    });
    if (!frKids.length) frKids.push(p("—", { size: 16, after: 0 }));
    return new TableRow({
      children: [
        cell([p(f[0], { bold: true, size: 18, after: 0, color: ACCENT })], { width: W[0], fill }),
        cell([
          p(lab.replace(/ \+TBD$/, ""), { bold: true, size: 17, after: 0, align: AlignmentType.CENTER, color: MSFILL[key] || ACCENT }),
          ...(/ \+TBD$/.test(lab) ? [p("+TBD", { bold: true, size: 15, after: 0, align: AlignmentType.CENTER, color: MSFILL.TBD })] : []),
        ], { width: W[1], fill }),
        cell([
          runs(domainsFor(f[0]).flatMap((d, i, all) => [
            { t: d, b: true, s: 15, c: DOMFILL[d] || "666666" },
            ...(i < all.length - 1 ? [{ t: "  ·  ", s: 15, c: "C2CAD6" }] : []),
          ]), { after: 50 }),
          p(f[1], { bold: true, size: 19, after: 40 }),
          p(f[4], { size: 18, after: (f[6] && f[6].length) ? 70 : 0 }),
          ...((f[6] || []).map(([lab, txt], i) => runs([
            { t: lab + " — ", b: true, s: 17, c: MSFILL[lab.replace(/^M/, "")] || "8A6D3B" },
            { t: txt, s: 17, c: "3C4859" },
          ], { after: i < f[6].length - 1 ? 50 : 0 }))),
        ], { width: W[2], fill }),
        cell([p(f[5], { size: 17, after: 0, color: "444444" })], { width: W[3], fill }),
        cell(frKids, { width: W[4], fill }),
        cell([p("", { size: 17, after: 0 })], { width: W[5], fill }),
      ],
    });
  });
  return new Table({ columnWidths: W, width: { size: USABLE, type: WidthType.DXA }, rows: [headRow, ...rows] });
}

// ---- narrative content ----------------------------------------------------
const ROADMAP_NOTE = {
  "1": "The demonstration application: the physical procedure end to end. The guided flow and its confirmations, both timed windows, the scan and its validation, the instructional copy for every step, and a result screen. It does not include authentication, consent, kit validation, the results center or any security control. What it demonstrates is that the product works when nothing goes wrong, which is what a demonstration is for — but see section 4, because several of these features rest on machinery scheduled later.",
  "2": "What is needed to put the application in front of real users on both platforms. Behavioural parity between iOS and Android, the content standards the copy must meet, spoken scan guidance for a user whose eyes are on the board rather than the screen, and the algorithm and payload work that turns a scan into an outcome the user can be shown — including, for the first time, the invalid-test outcomes.",
  "3": "The bulk of the submission scope, and the milestone at which the application stops being a demonstration. Authentication and session control, kit validation and reuse detection, the timer framework the milestone-1 gates were standing in for, the blocked-state pattern every failure route uses, transport security, provider routing, analytics, cancellation, and the verification activities for timing, state and the algorithms.",
  "4": "Needed for the clinical study but not a precondition for starting it. The invite-code path and per-test date-of-birth confirmation, consent acknowledgement, run-time configuration governance, the PIN and the results center session controls, the security audit channel, and the parameter and provider-integration verification activities.",
};

// [status, needed at, depends on, situation, outcome]
const INVERSIONS = [
  ["Closed", "M1  F05.3, F05.4", "was M3  F05.1",
   "The incubation gate and the scanning window were needed for the demonstration while the timer framework they rest on — defined start events, persisted start times, elapsed time computed rather than counted — sat at milestone 3.",
   "FR-TIM-001, FR-TIM-002 and FR-TIM-003 moved to milestone 1. FR-TIM-012, the message shown when a test is invalidated on time, stays at 3 as not needed for the demonstration."],
  ["Closed", "M1  F09.1, F09.2", "was M2  F08.4",
   "The result screens were at milestone 1 while the payload contract that distinguishes a valid result from an invalid one, and carries the invalid reason category, was at milestone 2.",
   "Resolved by scope rather than by priority. FR-RES-006 was added: a demonstration build presents a fixed payload, does not present it as a clinical result, and makes the demonstration state evident. F09.4 is the new feature."],
  ["Closed", "M1  F12.2", "was M3  F12.1",
   "Test data was uploaded at milestone 1 while TLS enforcement and certificate pinning were at milestone 3, so a demonstration build transmitted over whatever the platform negotiated.",
   "Accepted, with the constraint written down. FR-SEC-014 bars any build in which FR-COM-001 and FR-COM-002 are unimplemented from carrying personal or health information."],
  ["Closed", "M3  F01.2", "was M4  F01.9",
   "The supported-operating-system list was backend-configurable and the version check read backend values, both at milestone 3, while configuration retrieval and its schema validation were at milestone 4.",
   "FR-CFG-001 and FR-CFG-002 moved to milestone 3, and five requirements that had been realised by configuration are now stated as fixed in the application: FR-RDY-008, FR-TXT-019, FR-RES-002, FR-IMG-001 and FR-CAM-001."],
  ["Mostly closed", "M1  six features", "M3  F01.5",
   "Six milestone-1 features block the user: the sample-freshness window, both timing gates, frame acceptance, boundary-condition detection and termination invalidation. The content standard governing every blocking message, and the blocked-state pattern, were both at milestone 3.",
   "FR-TXT-020 moved to milestone 1, so the content standard now precedes the messages. F01.5 still holds FR-RDY-011 and FR-SUP-003 at milestone 3, but those are specific screens rather than the shared pattern."],
  ["Accepted", "M3  F02.1", "M4  F02.7",
   "Phone-number entry is at milestone 3 and the consent checkbox that gates it is at milestone 4, so a milestone-3 application would collect a phone number without recording acceptance of the Privacy Policy and Terms.",
   "Accepted on the ground that users do not go through phone verification at milestone 3, so no personal information is collected before the gate exists. That answer raises its own question, recorded as Q-38: the authentication requirements are nevertheless at milestone 3."],
  ["Open", "M1  F06.2", "TBD  F06.1",
   "Frame acceptance is at milestone 1, but the camera adjustment behaviour it depends on when a boundary condition is raised — white balance, exposure, tone mapping — is FR-CAM-002, whose priority is still undecided.",
   "Still open. Withdrawal is now a live option rather than only a priority assignment. Frame acceptance rates measured in the demonstration will not represent the product until it is settled."],
  ["Open", "M3  F10.3", "M4  F10.1, F10.2",
   "The results history screen is at milestone 3; the PIN that protects it and the fifteen-minute results-center timeout are at milestone 4.",
   "Held open as Q-39, pending a view on whether the results center can be delivered for milestone 3 at all. Whatever is decided, the screen and its six access controls are to carry the same milestone."],
];

// [ref, feature, what design found, proposed requirement, status]
const UXQUEUE = [
  ["UX-01", "F01.6", "Nothing states what the home screen shows while a previous test's data is still waiting to be transmitted, or how the user learns that it finally went.",
   "The software shall indicate on the home screen that a previous test's data has not yet been transmitted, and shall inform the user when transmission completes.", "Raised"],
  ["UX-02", "F12.2", "There was no stated waiting experience between a successful upload and the arrival of the result, nor any stated behaviour if the result did not arrive. No requirement covered the application-side act of requesting a result at all.",
   "Adopted as FR-COM-011 at milestone 1: the software requests the result, holds a waiting state until a result or an invalid-test outcome arrives, and explains how the result will reach the user if none does. The period before it stops waiting is unvalued and is tracked as Q-37.", "Adopted"],
  ["UX-03", "F10.6", "The post-test lobby is future development, but the home screen still has to show something for the period following a completed test.",
   "The software shall define the state of the home screen following a completed test, in the absence of the post-test lobby.", "Raised"],
  ["UX-04", "F01.4", "Whether the readiness checks are a visible sequence the user watches or a silent check that surfaces only on failure was not stated, and it changes the first impression of the product.",
   "Answered at review: the checks run silently when the user taps start test and each surfaces as an alert only on failure. There is no visible checklist, and the whole blocked-state pattern is an alert pattern rather than a set of screens. No new requirement needed; recorded in the decision log at Q-69.", "Closed"],
  ["UX-05", "F04.1", "Every step requires explicit confirmation, but what confirmation was physically — a button, a swipe, a checkbox the user ticks — was unstated, and it is the most repeated interaction in the product.",
   "Answered at review: a button. FR-FLW-001 now requires the user to confirm by activating a control provided for that purpose.", "Adopted"],
  ["UX-06", "F04.2", "Instructional media is required for every step, but nothing states whether it is bundled or streamed. A test may well be taken on a poor connection, and the instructions are a risk control.",
   "Instructional media shall be available for every step without network access during a test.", "Raised"],
  ["UX-07", "F13.3", "Screenshots of result screens are prevented. The user's first instinct on seeing a result will be to photograph it and send it to someone, and they will meet a silent failure.",
   "Where the software prevents a screenshot, it shall tell the user why and offer the sanctioned route to obtain a copy of the result.", "Raised"],
  ["UX-08", "F03.1", "Nothing describes what the user sees between authentication and the first step of the test: what is in the box, what they need to hand, how long it will take, and that they cannot stop once the cup is filled.",
   "Not adopted. The equivalent screen in the predecessor application is obsolete and is not carried forward. Closed at review; see the decision log at Q-88.", "Closed"],
];

// =========================================================================
const children = [];

// --- title -----------------------------------------------------------------
children.push(new Paragraph({ spacing: { before: 1600, after: 0 }, children: [
  new TextRun({ text: "QACR – KIDNEY CHECK", bold: true, size: 24, color: "7F8FA6", font: "Calibri" })] }));
children.push(new Paragraph({ spacing: { before: 120, after: 0 }, children: [
  new TextRun({ text: "Mobile Application", bold: true, size: 52, color: ACCENT, font: "Calibri" })] }));
children.push(new Paragraph({
  spacing: { before: 40, after: 240 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
  children: [new TextRun({ text: "Epic and Feature Map", bold: true, size: 52, color: ACCENT, font: "Calibri" })],
}));
children.push(p("Document no. QACR-APP-EPIC-01   ·   Revision " + V.EPIC + " (Draft)", { size: 22, color: "444444", after: 60 }));
children.push(p("A delivery view of QACR-APP-FR-01 Functional Requirements Rev " + V.FR + ". Every requirement in that document appears here exactly once, grouped into the epic and feature a team would build, with the milestone derived from the requirement's own priority. This document adds no requirements and changes none.", { size: 20, italics: true, color: "666666", after: 500 }));

children.push(infoTable(["Field", "Value"], [
  ["Document title", "QACR Mobile Application – Epic and Feature Map"],
  ["Document number", "QACR-APP-EPIC-01"],
  ["Revision", V.EPIC + " — " + V.status],
  ["Derived from", "QACR-APP-FR-01 Functional Requirements Rev " + V.FR],
  ["Audience", "Product and development. Not a regulatory deliverable"],
  ["Status", "Working draft; not under change control"],
  ["Scope", `${EPICS.length} epics, ${EPICS.reduce((a, e) => a + e.features.length, 0)} features, ${PRI.size} requirements, ${APX.backlog.length} deferred items`],
  ["Requirements authority", "QACR-APP-FR-01. Where the two differ, that document governs"],
  ["Prepared by", "—"],
  ["Reviewed by", "—"],
], [2600, 7480], { comments: false }));

children.push(new Paragraph({ children: [new PageBreak()] }));

// --- contents --------------------------------------------------------------
children.push(h1("Contents"));
children.push(p("If the table below appears empty, right-click it in Word and choose “Update Field”.", { italics: true, size: 18, color: "888888", after: 160 }));
children.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));
children.push(new Paragraph({ children: [new PageBreak()] }));

// --- 1 purpose -------------------------------------------------------------
children.push(h1("1. Purpose and Relationship to the Requirements Document"));
children.push(p("QACR-APP-FR-01 states what the application must do, organised by the kind of obligation, which is the arrangement a risk analysis and a verification protocol need. It is not the arrangement a development team needs. A single screen in this product draws requirements from five or six of its sections at once, and a single section, such as user-facing content, is not a deliverable anyone can be assigned."));
children.push(p("This document rearranges the same material along what the user does and what the application must be, so that scope can be discussed per milestone, work can be assigned, and user-experience design can attach to something. It is deliberately not spec-level: a feature here states what it is and what design owes it, and points at the requirements for the detail."));

children.push(h2("1.1 What this document is for"));
children.push(p("Three uses. Understanding the shape and size of each milestone before committing to it. Giving design a unit of work to attach screens and flows to, one that is neither a single requirement nor the whole application. And surfacing the places where the requirements are silent about the user experience, so that the gaps become requirements rather than assumptions made during implementation."));

children.push(h2("1.2 The rule that keeps the two documents aligned"));
children.push(p("Both documents will keep changing, and QACR-APP-FR-01 remains the interface to regulatory and software quality. Four rules keep them from drifting apart."));
children.push(infoTable(["", "Rule"], [
  ["One", "Every requirement in QACR-APP-FR-01 belongs to exactly one feature here. That is checked mechanically each time either document is rebuilt, so a new requirement that has not been placed, or a feature naming a requirement that no longer exists, is caught rather than discovered later."],
  ["Two", "Milestones are stated once, in QACR-APP-FR-01, and derived here. The milestone shown against a feature is computed from the priorities of the requirements it contains; it is not typed in and cannot be edited here. To move a feature, change the priorities in the requirements document."],
  ["Three", "This document adds no requirements. Where user-experience work produces something the application must do, it is raised as a requirement in QACR-APP-FR-01 and given an identifier there. Section 5 holds the queue of candidates until that happens."],
  ["Four", "Open questions are recorded once, in the Review Register of QACR-APP-FR-01. Each epic here lists the register items that bear on it, by reference only, so that a scoping discussion can see them without a second list forming."],
], [700, 9380]));

// --- 2 how to read ---------------------------------------------------------
children.push(h1("2. How to Read This Document"));
children.push(h2("2.1 Identifiers"));
children.push(p("Epics are E01 to E" + String(EPICS.length).padStart(2, "0") + ". Features are numbered within their epic, so F04.3 is the third feature of epic E04. Requirements keep the identifiers they carry in QACR-APP-FR-01, abbreviated in the tables by dropping the FR prefix: RDY-002 is FR-RDY-002. Deferred items keep their BL numbers."));
children.push(p("Feature numbers are stable. A feature that is dropped is not reissued, and a new feature takes the next free number in its epic rather than being inserted."));

children.push(h2("2.2 The milestone column"));
children.push(p("The M column shows when the feature is needed, derived from the requirements it contains. A single value means every requirement in the feature sits at that milestone. A range such as M1–M3 means the feature is first needed at milestone 1 but is not complete until milestone 3, which is worth noticing: it is a feature that will be built more than once. “+TBD” means the feature also holds a requirement whose priority is undecided. “—” means every requirement in the feature is deferred."));
children.push(p("Where a feature spans more than one milestone, it says so twice, in two different registers. The Feature and intent column breaks the feature down in words, one line per milestone, so that the scope of a milestone can be read without cross-referencing anything. The Requirements column groups the identifiers the same way, under M1, M2, M3, M4 and TBD headings, so the words can always be checked against the requirements behind them. Deferred items are listed last, in italics, and carry no milestone.", { before: 100 }));
children.push(p("Both are generated from the same requirement priorities, and the build refuses to produce this document if a feature spanning several milestones has no per-milestone description — so the breakdown cannot fall behind a priority change.", { before: 80, italics: true, size: 18, color: "666666" }));
children.push(infoTable(["Milestone", "Meaning", "Requirements", "Features first needed"],
  MS.map(m => {
    const rc = [...PRI.values()].filter(x => x === m).length;
    const fc = EPICS.reduce((a, e) => a + e.features.filter(f => roll(f[2]).first === Number(m)).length, 0);
    return ["M" + m, MSNAME[m], String(rc), String(fc)];
  }).concat([
    ["TBD", "Priority undecided — see the Review Register", String([...PRI.values()].filter(x => x === "TBD").length), "—"],
  ]), [1000, 5000, 1600, 1900]));
children.push(p("Milestones accumulate: milestone 3 includes everything at milestones 1 and 2. The counts above are the requirements introduced at each milestone, not the running total.", { before: 100, italics: true, size: 18, color: "666666" }));

children.push(h2("2.3 Development domain"));
children.push(p("Each feature carries the disciplines that have to build it, above its name: iOS, Android, Backend, Algo, Content or Process. A feature tagged for three domains needs three people in the room when it is estimated, which is the point of showing it."));
children.push(p("The tags are a curated list rather than a derivation. They started as one, read from the requirement wording, but the wording turned out to be a poor guide to who has to build something — ten of the eighty-two were wrong — so each feature now carries an explicit set that this document is built from, and the build fails if a feature has none. The tag is per feature, so it is coarse by design: F13.2 reads iOS and Android although only the obfuscation half of it is Android alone.", { after: 120 }));

children.push(h2("2.4 The kind of work an epic is"));
children.push(p("Each epic states whether it is application work, backend and algorithm work, content, or process. Backend and content epics are included because the application is built against them and cannot be scheduled without them: the result screens depend on the payload contract, and the flow engine cannot be demonstrated without the instructional copy. The one process epic is not feature work at all, but each of its items is relied upon by the Risk Analysis and needs an owner."));

// --- 3 roadmap -------------------------------------------------------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("3. Milestone Roadmap"));
children.push(p("What each milestone contains, at epic level. A feature appears against the milestone at which it is first needed; a feature spanning several milestones appears at the earliest and is noted as continuing."));

MS.forEach(m => {
  const mn = Number(m);
  const rows = [];
  EPICS.forEach(e => {
    const fs = e.features.filter(f => roll(f[2]).first === mn);
    if (!fs.length) return;
    rows.push([
      e.code,
      e.title,
      fs.map(f => f[0] + (roll(f[2]).last !== mn ? "→" : "")).join(", "),
      String(fs.reduce((a, f) => a + f[2].filter(id => PRI.get(id) === m).length, 0)),
    ]);
  });
  children.push(h2(`3.${m} Milestone ${m} — ${MSNAME[m]}`));
  const total = rows.reduce((a, r) => a + Number(r[3]), 0);
  children.push(p(ROADMAP_NOTE[m], { after: 140 }));
  children.push(infoTable(["Epic", "Title", "Features first needed here", "New reqs."], rows, [800, 3900, 3100, 900]));
  children.push(p(`${rows.length} epics touched, ${total} requirements introduced. An arrow marks a feature that continues past this milestone.`, { before: 100, italics: true, size: 18, color: "666666" }));
});

children.push(h2("3.5 Future development"));
const m5Rows = [], m5Mixed = EPICS.reduce((a, e) => a + e.features.filter(f =>
  f[2].some(i => PRI.get(i) === "5") && f[2].some(i => PRI.get(i) !== "5")).length, 0);
EPICS.forEach(e => e.features.forEach(f => {
  const m5 = f[2].filter(i => PRI.get(i) === "5");
  if (m5.length && m5.length === f[2].length) m5Rows.push([f[0], e.code + " " + e.title, f[1], m5.join(", ")]);
}));
children.push(p(`${m5Rows.length} features are entirely future development, listed below, and a further ${m5Mixed} features carry some milestone-5 requirements alongside work in this version. Milestone 5 has no date. It is in the body of the requirements document with its section and its traceability, so a later revision starts from a requirement rather than reconstructing one.`, { after: 160 }));
children.push(infoTable(["Ref.", "Epic", "Feature", "Requirements"], m5Rows, [800, 3100, 2600, 2200]));
children.push(p("One further feature, F11.3, holds a single requirement whose priority is undecided and nothing else. It decides whether an entire branch of the product exists for a given partner, which is why it is not simply deferred.", { before: 100, italics: true, size: 18, color: "666666" }));

// --- 4 consistency findings ------------------------------------------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("4. Milestone Consistency"));
children.push(p("Priorities are assigned requirement by requirement, which is the right way to do it but does not guarantee that a requirement needed early does not depend on one scheduled late. Grouping requirements into features makes those cases visible. Eight were found here; a separate engineering review of Rev 1.5 found nineteen dependency and timeline issues, seven of which were these same ones reached by a different route."));
children.push(p("All of them were reviewed and dispositioned in QACR-APP-FR-01 Rev " + V.FR + ". The table below is now a record of what was decided rather than a list of findings, and it is kept because the reasoning matters more than the conclusion: two of these were closed by changing scope rather than by moving a priority, and one was accepted rather than fixed.", { after: 140 }));
children.push(infoTable(["Status", "Needed at", "Depends on", "The situation", "How it was resolved"], INVERSIONS, [1000, 1150, 1150, 3400, 2800]));
children.push(p("Two remain open and both are recorded in the Review Register of QACR-APP-FR-01: the camera-adjustment priority, and whether the results center can be delivered for milestone 3. Everything else is closed, and the decision log in that document records each answer against a stable reference.", { before: 140 }));
children.push(p("One observation worth keeping. Three of the four closures moved a requirement earlier, but two were resolved by narrowing what the earlier milestone claims to be — a demonstration build presents a fixed result payload, and a build without the transport controls may not carry patient data. That is usually the cheaper resolution, and it has the advantage of writing down what the milestone actually is rather than implying it is a smaller version of the product.", { before: 100 }));

// --- 5 UX feedback queue ---------------------------------------------------
children.push(h1("5. Requirements Arising from Design"));
children.push(p("Design work will produce obligations the requirements document does not yet state. The application has, for instance, no stated behaviour for what the home screen shows while a previous result is still uploading, and no stated waiting experience between upload and result. Those are requirements, not implementation details, and they belong in QACR-APP-FR-01 where verification and the Risk Analysis can see them."));
children.push(p("The queue below is the route in. A candidate is raised here with the feature it belongs to, and is either adopted into the requirements document with an identifier of its own, or closed with a reason. Nothing is implemented from this table; it is a holding area, and an empty one is the healthy state."));
children.push(infoTable(["Ref.", "Feature", "What design found", "Proposed requirement", "Status"], UXQUEUE, [900, 900, 3300, 3300, 1000]));
children.push(p("The eight entries above are the journey points I could see were unstated while building this map. They are deliberately phrased as questions, not answers, because several of them are product decisions rather than gaps.", { before: 100, italics: true, size: 18, color: "666666" }));

// --- 6 epic catalogue ------------------------------------------------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("6. Epic Catalogue"));
children.push(p("One entry per epic. The header line states the kind of work, where it sits in the user journey, the derived milestone span and the number of requirements it carries. The feature table follows, then the open items from the Review Register of QACR-APP-FR-01 that bear on the epic."));

EPICS.forEach(e => {
  const all = e.features.flatMap(f => f[2]);
  const r = roll(all);
  children.push(new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 400, after: 100 },
    children: [new TextRun({ text: `${e.code}. ${e.title}`, bold: true, size: 26, color: ACCENT, font: "Calibri" })],
  }));
  children.push(runs([
    { t: KINDNAME[e.kind], b: true, s: 18, c: MSFILL[3] },
    { t: "   ·   ", s: 18, c: "AAAAAA" },
    { t: e.journey, i: true, s: 18, c: "555555" },
    { t: "   ·   ", s: 18, c: "AAAAAA" },
    { t: r.first ? (r.first === r.last ? "M" + r.first : "M" + r.first + "–M" + r.last) : "deferred", b: true, s: 18, c: MSFILL[r.first] || "777777" },
    { t: "   ·   ", s: 18, c: "AAAAAA" },
    { t: `${all.length} requirements, ${all.filter(i => PRI.get(i) === "5").length} future development`, s: 18, c: "555555" },
    ...(r.tbd ? [{ t: "   ·   ", s: 18, c: "AAAAAA" }, { t: `${r.tbd} priority undecided`, b: true, s: 18, c: MSFILL.TBD }] : []),
  ], { after: 120 }));
  children.push(p(e.summary, { after: 160 }));
  children.push(featureTable(e.features));
  if (e.open.length) {
    children.push(p("Open items bearing on this epic", { bold: true, size: 19, before: 200, after: 60 }));
    e.open.forEach(o => children.push(p("·  " + o, { size: 18, after: 30, color: "444444" })));
    children.push(p("Recorded in the Review Register of QACR-APP-FR-01; resolve them there.", { size: 17, italics: true, color: "888888", before: 60, after: 200 }));
  } else {
    children.push(p("No open register items bear on this epic.", { size: 18, italics: true, color: "888888", before: 160, after: 200 }));
  }
});

// --- Appendix A: requirement to feature ------------------------------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix A – Requirement to Feature Index"));
children.push(p("Every requirement in QACR-APP-FR-01, in identifier order, with the feature that owns it. This is the reverse of the epic catalogue and is generated from the same data, so the two cannot disagree. Use it to answer the question that comes up most often in review: a requirement has changed, what does it affect?"));
const frRows = [...PRI.keys()].sort().map(id => {
  const o = OWNER.get(id);
  return [id, PRI.get(id), o.epic, o.feature, o.name];
});
children.push(infoTable(["Req. ID", "M", "Epic", "Feature", "Feature name"], frRows, [1400, 500, 700, 950, 5130]));

children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h1("Appendix B – Open Items by Epic"));
children.push(p("Every open item from the Review Register of QACR-APP-FR-01 that this map could attribute to an epic, so that a scoping discussion for one epic can see what is unresolved in it. The register remains the authority and the place to resolve them; this is an index into it."));
const openRows = [];
EPICS.forEach(e => e.open.forEach((o, i) => openRows.push([i === 0 ? e.code : "", i === 0 ? e.title : "", o])));
children.push(infoTable(["Epic", "Title", "Open item"], openRows, [700, 3100, 6280]));
children.push(p(`${openRows.length} attributions across ${EPICS.filter(e => e.open.length).length} epics. Several register items bear on more than one epic and appear more than once; a few bear on none and are absent.`, { before: 100, italics: true, size: 18, color: "666666" }));

// =========================================================================
const doc = new Document({
  creator: "Product",
  title: "QACR Mobile Application – Epic and Feature Map",
  styles: {
    default: { document: { run: { font: "Calibri", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: ACCENT, font: "Calibri" } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, color: ACCENT, font: "Calibri" } },
    ],
  },
  sections: [{
    properties: { page: { margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "QACR-APP-EPIC-01  ·  Epic and Feature Map  ·  Rev " + V.EPIC, size: 16, color: "9AA5B5", font: "Calibri" })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], size: 16, color: "9AA5B5", font: "Calibri" })],
      })] }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log("wrote " + OUT + "  " + b.length + " bytes"); });
