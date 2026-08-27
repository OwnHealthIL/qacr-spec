#!/usr/bin/env python3
"""Render the built documents to page images, so section 8.5 can actually be run.

    render-pages.py <product dir> [pages]      pages default: 1,2

Section 8.5 of CLAUDE.md asks for the pages to be **read as images**, because text
extraction cannot see a column too narrow for its content. It caught `+TBD` breaking
mid-word and `Q-36` wrapping to `Q-3 / 6`, and it is the one verification step that had
no tooling here: two revisions shipped with the step recorded as "could not be run in
this environment".

It can be run now. LibreOffice converts the .docx headlessly and poppler rasterises the
pages; both are ordinary Homebrew installs and neither touches the build.

    brew install --cask libreoffice
    brew install poppler

**This script does not check anything.** It produces PNGs and prints their paths. The
check is a person or an agent looking at them, which is the whole point — an automated
reader would be back to extracting text, which is exactly what does not work. Word was
tried first and rejected: driving it through AppleScript hangs on any dialog it decides
to show, and a verification step that can hang is not one you can rely on.

Output goes to a scratch directory, never into the repository: these are derived from a
derived artefact and nothing should read them as a deliverable.
"""
import glob, os, subprocess, sys

ROOT = sys.argv[1]
PAGES = sys.argv[2] if len(sys.argv) > 2 else "1,2"

SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
OUT = os.path.join(os.environ.get("TMPDIR", "/tmp"), "qacr-render")

if not os.path.exists(SOFFICE):
    sys.exit("LibreOffice is not installed: brew install --cask libreoffice")
if subprocess.run(["which", "pdftoppm"], capture_output=True).returncode != 0:
    sys.exit("poppler is not installed: brew install poppler")

os.makedirs(OUT, exist_ok=True)
docs = sorted(glob.glob(os.path.join(ROOT, "FR-01", "*.docx")) +
              glob.glob(os.path.join(ROOT, "EPIC-01", "*.docx")))
if not docs:
    sys.exit("no .docx found under FR-01/ or EPIC-01/")

wanted = [int(p) for p in PAGES.split(",")]
made = []
for d in docs:
    subprocess.run([SOFFICE, "--headless", "--norestore", "--convert-to", "pdf",
                    "--outdir", OUT, d], capture_output=True, check=True)
    pdf = os.path.join(OUT, os.path.splitext(os.path.basename(d))[0] + ".pdf")
    stem = os.path.join(OUT, os.path.splitext(os.path.basename(d))[0].replace(" ", "_"))
    for p in wanted:
        subprocess.run(["pdftoppm", "-png", "-r", "130", "-f", str(p), "-l", str(p),
                        pdf, f"{stem}-p{p}"], capture_output=True, check=True)
    made += sorted(glob.glob(f"{stem}-p*.png"))

print(f"Rendered {len(docs)} document(s), pages {PAGES}:\n")
for m in made:
    print(f"   {m}")
print("\nRead these as images. Section 8.5 is looking for a value broken across a line, "
      "a column too narrow for its content, and the cover's revision line — the one that "
      "froze at 1.15 and 1.9 through four shipped revisions because no guard reads a bare "
      "paragraph and no extraction sees a bad wrap.")
