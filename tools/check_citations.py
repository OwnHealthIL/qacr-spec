#!/usr/bin/env python3
"""Check every citation in the evidence tables against the real repositories.

Read-only. Prints a resolve rate and every failure, so the validity figure is
something you re-run rather than something you were told once.

    python3 tools/check_citations.py                       # evidence/behaviour.tsv
    python3 tools/check_citations.py path/to/other.tsv      # any claims TSV
    python3 tools/check_citations.py wip-evidence/candidates.jsonl

Exit code is 0 when every citation resolves, 1 otherwise.

It needs the cloned repositories under ~/Documents/Healthy.io. A repository that
is missing is reported and skipped rather than counted as a failure.

WHAT IT PROVES, AND WHAT IT DOES NOT
------------------------------------
It proves a citation points at a real file that really has that line. It does
**not** prove the cited lines say what the claim says they say. For that, read
the code beside the row — which is the reason `citation` is in the table at all.

It cannot check citations to documents that are not in the repositories — the
Risk Analysis, SRS, SPTA, Glossary and User Manual. Those come from the
requirements document and are recorded in `product/FR-01/requirements.json` as
`source_refs`, never verified against a source nobody has.

A FAILING CITATION IS A FINDING
-------------------------------
It means the code moved, or the claim was always wrong. Both are worth knowing
and neither is fixed by deleting the row. `evidence/pins.yaml` records the commit
each claim was read at; a citation that stops resolving is the short list worth
re-verifying, rather than a reason to re-read everything.

PORTED FROM THE VAULT, WITH ITS TWO KNOWN GAPS FIXED
-----------------------------------------------------
The vault's `05 Reference/Citation checker.py` reads the vault's markdown. This
reads the evidence tables instead, and fixes two gaps that made its resolve rate
flattering:

1. **`.pbxproj` and `.md` were silently skipped.** Its extension index listed
   both, but its citation regex never did, so every citation into an Xcode
   project file or a markdown file was invisible to it — not failed, not
   counted, just absent from the denominator.

2. **Continuation citations were invisible.** The vault writes a filename once
   and then refers to further lines in the same file as a bare `:2422`. There are
   ~851 of those. The checker had no way to see them, so the largest single class
   of citation in the vault was never validated by anything. Here, a citation that
   still carries no filename is reported as `unresolved continuation` — it is a
   real defect in the source prose, not something to pass over.

One thing the vault's version got right and this keeps: resolution is
product-aware. ACR and QACR share many filenames, so resolving by basename alone
lets a citation validate against a same-named file from the wrong product and
pass. The `product` column decides which repository is looked at first.
"""
import os
import re
import sys
import json
from collections import Counter

ROOT = os.path.expanduser("~/Documents/Healthy.io")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(REPO, "evidence", "behaviour.tsv")

# Every repository a citation can legitimately point into.
REPOS = [
    "iosDip", "AndroidDip", "urine.com.ios-qacr-app", "AndroidQacr",
    "ios-foundations", "ios-views", "ios-camera", "ios-chat-services",
    "ios-questionnaire", "ios-markup", "iOS-ConfigurationFiles",
    "android.shared-infra", "android.shared-camera", "android.shared-chat",
    "android.shared-questionnaire", "android.shared-urine-algo",
]

# Which repositories each product's citations should resolve against, in
# preference order: its own app first, then the shared packages it consumes.
IOS_SHARED = ["ios-foundations", "ios-views", "ios-camera", "ios-chat-services",
              "ios-questionnaire", "ios-markup", "iOS-ConfigurationFiles"]
ANDROID_SHARED = ["android.shared-infra", "android.shared-camera",
                  "android.shared-chat", "android.shared-questionnaire",
                  "android.shared-urine-algo"]
PRODUCT_REPOS = {
    "acr-ios": ["iosDip"] + IOS_SHARED,
    "acr-android": ["AndroidDip"] + ANDROID_SHARED,
    "qacr-ios": ["urine.com.ios-qacr-app"] + IOS_SHARED,
    "qacr-android": ["AndroidQacr"] + ANDROID_SHARED,
}

EXTS = {".swift", ".kt", ".kts", ".java", ".xml", ".json", ".plist", ".gradle",
        ".yml", ".yaml", ".strings", ".xcstrings", ".arb", ".h", ".m", ".sh",
        ".pbxproj", ".md", ".pro", ".xcscheme", ".entitlements", ".cfg", ".txt"}
SKIP = {".git", "build", ".build", "Pods", "node_modules", "DerivedData",
        ".gradle", ".idea", "Carthage", ".claude", ".swiftpm", "xcuserdata"}
# Extensionless build files the prose cites by name.
NOEXT = {"Jenkinsfile", "Dangerfile", "Fastfile", "Podfile", "Gemfile",
         "Makefile", "Appfile", "Matchfile", "Dockerfile"}

# path:ranges — ranges may be a list, e.g. `build.gradle.kts:87-89, 267-283`
CITATION = re.compile(r"^(?P<path>.*?):(?P<ranges>\d+(?:-\d+)?(?:\s*,\s*\d+(?:-\d+)?)*)$")


def index_repos():
    """basename -> [repo-relative path, ...] for every source file."""
    files, missing = {}, []
    for repo in REPOS:
        base = os.path.join(ROOT, repo)
        if not os.path.isdir(base):
            missing.append(repo)
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP]
            for fn in filenames:
                if os.path.splitext(fn)[1] in EXTS or fn in NOEXT:
                    files.setdefault(fn, []).append(
                        os.path.relpath(os.path.join(dirpath, fn), ROOT))
    return files, missing


def line_count(rel, cache):
    if rel not in cache:
        try:
            with open(os.path.join(ROOT, rel), encoding="utf-8",
                      errors="replace") as f:
                cache[rel] = sum(1 for _ in f)
        except OSError:
            cache[rel] = -1
    return cache[rel]


def candidates_for(path, product, index):
    """Real files a cited path could mean, best first.

    An explicit path the author wrote outranks the product context — a row may
    legitimately cite the other product when comparing the two — so the suffix
    match is applied first and the product preference only orders what is left.
    """
    base = os.path.basename(path)
    cands = index.get(base, [])
    if not cands and base.startswith(("\u2026", "...")):
        # the elision ate part of the filename too: `\u2026ServiceConfigurator.swift`
        stem = base.lstrip("\u2026.")
        cands = [c for name, paths in index.items() if name.endswith(stem)
                 for c in paths]
    if not cands:
        return []
    if "/" in path:
        # the prose elides long paths as `.../Minuteful UK/X.swift` or with a
        # single `…`; either way what follows is a real suffix of a real path
        tail = path.lstrip("\u2026.").lstrip("/")
        exact = [c for c in cands if c.endswith(tail)]
        if exact:
            cands = exact
    prefer = PRODUCT_REPOS.get(product, [])
    if prefer:
        rank = {r: i for i, r in enumerate(prefer)}
        cands = sorted(cands, key=lambda c: rank.get(c.split(os.sep)[0], 99))
    return cands


def rows_from(path):
    """(citation, product, source, where) for every row of a TSV or JSONL file."""
    out = []
    if path.endswith(".jsonl"):
        for i, line in enumerate(open(path, encoding="utf-8"), start=1):
            r = json.loads(line)
            out.append((r.get("citation", ""), r.get("product", ""),
                        r.get("source", ""), f"line {i}"))
        return out
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            ci, pi = header.index("citation"), header.index("product")
        except ValueError:
            sys.exit(f"{path}: header must contain 'citation' and 'product' "
                     f"columns, found {header}")
        si = header.index("source") if "source" in header else None
        for i, line in enumerate(f, start=2):
            cells = line.rstrip("\n").split("\t")
            if len(cells) <= ci:
                continue
            out.append((cells[ci], cells[pi] if len(cells) > pi else "",
                        cells[si] if si is not None and len(cells) > si else "",
                        f"line {i}"))
    return out


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.exists(target):
        sys.exit(f"no such file: {target}\n"
                 f"(evidence/behaviour.tsv is not built yet — see PLAN.md)")

    print(f"claims : {target}")
    print(f"repos  : {ROOT}")
    print("indexing repositories ...")
    index, missing = index_repos()
    for m in missing:
        print(f"  ! repository not found, skipping: {m}")
    print(f"  {sum(len(v) for v in index.values())} source files indexed\n")

    cache, stats, failures = {}, Counter(), []
    for citation, product, source, where in rows_from(target):
        citation = citation.strip()
        if not citation:
            stats["no citation (negative claim)"] += 1
            continue
        stats["checked"] += 1

        m = CITATION.match(citation)
        if not m:
            stats["unparseable"] += 1
            failures.append((where, citation, source, "not a path:line citation"))
            continue
        path = m.group("path").strip()
        if not path:
            # a bare `:2422` that no rule could attach to a filename
            stats["unresolved continuation"] += 1
            failures.append((where, citation, source,
                             "continuation citation — the source prose never "
                             "names the file these lines are in"))
            continue
        last = max(int(x) for x in re.findall(r"\d+", m.group("ranges")))

        cands = candidates_for(path, product, index)
        if not cands:
            stats["no such file"] += 1
            failures.append((where, citation, source,
                             "no file of that name in any repository"))
            continue

        best = None
        for c in cands:
            n = line_count(c, cache)
            if best is None or n > best[1]:
                best = (c, n)
            if n >= last:
                stats["resolved"] += 1
                break
        else:
            stats["line out of range"] += 1
            failures.append((where, citation, source,
                             f"{best[0]} has {best[1]} lines, citation needs {last}"))

    checked = stats["checked"] or 1
    print("=" * 78)
    print(f"{stats['checked']} citations checked")
    print(f"{stats['resolved']} resolve to a real file with that line "
          f"({100 * stats['resolved'] / checked:.1f}%)")
    for k in ("no such file", "line out of range", "unresolved continuation",
              "unparseable"):
        if stats[k]:
            print(f"{stats[k]} {k}")
    if stats["no citation (negative claim)"]:
        print(f"{stats['no citation (negative claim)']} rows carry no citation "
              f"(negative claims — correct, not counted above)")
    print("=" * 78)

    if failures:
        print("\nCitations that do not resolve — each is a finding:\n")
        for where, citation, source, why in failures:
            print(f"  {where}  {citation}")
            print(f"      {why}")
            if source:
                print(f"      from {source}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
