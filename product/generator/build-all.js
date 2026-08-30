// Builds all three deliverables with filenames derived from version.js, so a
// document's filename can never disagree with what the document says about itself.
//
// Run from the project root:  npm run build
const { execFileSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const DIR = __dirname;
const ROOT = path.resolve(DIR, "..");
const V = require(path.join(DIR, "version.js"));

// [script, destination directory relative to ROOT, filename].
//
// Each deliverable is written straight into the directory the shared repository reads
// it from, so there is exactly ONE copy of it on disk. A staging area at ROOT plus a
// copy step would put two, and a second copy of a deliverable is read as current by
// whoever finds it first.
const TARGETS = [
  ["build.js",       "FR-01",   `QACR-APP-FR-01 Functional Requirements Rev${V.FR}.docx`],
  ["build-epics.js", "EPIC-01", `QACR-APP-EPIC-01 Epic and Feature Map Rev${V.EPIC}.docx`],
  ["build-board.js", "EPIC-01", `QACR-APP-EPIC-01 Board.html`],
];

// Anything currently in the root that is a previous revision of what we are about to
// write gets moved aside rather than left to confuse the next reader.
const ARCHIVE = path.join(ROOT, "Previous revisions");
fs.mkdirSync(ARCHIVE, { recursive: true });

let archived = 0;
for (const [, dir, name] of TARGETS) {
  const m = name.match(/^(.*Rev)[\d.]+(\.docx)$/);
  if (!m) continue;
  const destDir = path.join(ROOT, dir);
  fs.mkdirSync(destDir, { recursive: true });
  // A superseded revision left beside its successor has no answer to "which revision is
  // this", so it is moved aside. The scan is per destination directory, not over ROOT:
  // the two documents live in different ones and neither should see the other's files.
  for (const f of fs.readdirSync(destDir)) {
    if (f !== name && f.startsWith(m[1]) && f.endsWith(m[2])) {
      fs.renameSync(path.join(destDir, f), path.join(ARCHIVE, f));
      console.log(`archived  ${dir}/${f}`);
      archived++;
    }
  }
}

for (const [script, dir, name] of TARGETS) {
  const out = path.join(ROOT, dir, name);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  execFileSync("node", [path.join(DIR, script), out, DIR], { stdio: "inherit" });
}

console.log(`\nbuilt FR Rev ${V.FR} and epic map Rev ${V.EPIC}` +
            (archived ? `, archived ${archived} previous revision(s)` : "") +
            `\nnow run:  npm run check`);
