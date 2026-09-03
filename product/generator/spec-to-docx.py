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

    spec-to-docx.py <spec.md> [outdir] [--since <previous spec.md>]

With --since, every block that differs from the previous revision is coloured red in
the .docx. Most of a revision is usually unchanged and a reviewer should not have to
read it again to find out which part is not.
"""
import os, shutil, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

pos = [a for a in sys.argv[1:] if not a.startswith("--")]
if "--since" in sys.argv:
    pos = [a for a in pos if a != sys.argv[sys.argv.index("--since") + 1]]
src = pos[0]
outdir = pos[1] if len(pos) > 1 else os.path.join("local", "review")
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

# --since <previous spec.md>: colour every block that changed red, so a reviewer
# reads what moved rather than the whole document again. Guy asked for this after
# Rev 0.11, where most of the text was unchanged and none of it was marked.
prev = None
if "--since" in sys.argv:
    prev = sys.argv[sys.argv.index("--since") + 1]
if prev:
    if not os.path.isfile(prev):
        sys.exit(f"no such previous revision: {prev}")
    import redline
    units = redline.changed_units(open(prev, encoding="utf-8").read(),
                                  open(src, encoding="utf-8").read())
    rows, paras = redline.patch(out, units)
    print(f"wrote {out}  ({os.path.getsize(out):,} bytes)")
    print(f"marked red against {os.path.basename(prev)}: "
          f"{paras} paragraph(s), {rows} table row(s), from {len(units)} changed block(s)")
else:
    print(f"wrote {out}  ({os.path.getsize(out):,} bytes)")
print("\nspecs/*.md is the artefact of record; this is a review copy. Mark it up freely,")
print("but the edits come back into the .md — nothing flows out of the .docx.")
