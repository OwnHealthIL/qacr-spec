#!/usr/bin/env python3
"""Render a spec to .docx so Guy can review it in Word.

    spec-to-docx.py <spec.md> [outdir]      outdir default: local/review/

The Markdown in `specs/` stays the artefact of record. This produces a **review copy**
and nothing else, which is why it goes to `local/` — untracked, on Guy's disk, and not
where anyone could mistake it for a deliverable. Section 1 of CLAUDE.md is the reason:
a second copy of a document where the first one lives is read as current by whoever
finds it first, and `layout-check.py` exists because that already happened once.

**Comments made in the .docx do not flow back.** The .md is edited and the .docx is
regenerated. Treat the Word file as read-and-mark-up, never as a source.
"""
import os, shutil, subprocess, sys

src = sys.argv[1]
outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join("local", "review")
if not os.path.isfile(src):
    sys.exit(f"no such spec: {src}")
if shutil.which("pandoc") is None:
    sys.exit("pandoc is not installed")

os.makedirs(outdir, exist_ok=True)
out = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + ".docx")

# No --toc. Pandoc writes a TOC *field*, which Word only fills in once someone updates
# it, so the review copy opens on a blank page headed "Table of Contents". The heading
# styles carry the navigation pane in Word regardless, which is what a reviewer uses.
cmd = ["pandoc", src, "-o", out,
       "--from", "markdown+pipe_tables+strikeout", "--standalone"]
# A4 with ~1.5cm side margins. Pandoc's own reference.docx carries no page setup at
# all, so the default is a narrow measure that squeezes the three-column open-items
# table into a ribbon. The reference doc exists only to widen that.
ref = os.path.join("generator", "spec-reference.docx")
if os.path.exists(ref):
    cmd += ["--reference-doc", ref]
subprocess.run(cmd, check=True)

print(f"wrote {out}  ({os.path.getsize(out):,} bytes)")
print("\nspecs/*.md is the artefact of record; this is a review copy. Mark it up freely,")
print("but the edits come back into the .md — nothing flows out of the .docx.")
