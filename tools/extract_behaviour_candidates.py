#!/usr/bin/env python3
"""Pull every cited claim about ACR/QACR code out of the Obsidian vault.

This is the mechanical half of building `evidence/behaviour.tsv`. It finds the
citations, the sentence around each one, where it came from, and which product
it is about. It does NOT write the `claim` column — compressing a paragraph of
prose into one line is a judgement, and a regex that tried would either truncate
meaning or invent it. It emits candidates for a model pass to compress.

    python3 tools/extract_behaviour_candidates.py OUT.jsonl

Reads (never writes) the vault at
  ~/Documents/Healthy.io/Healthy.io - MD/QACR - Implementation Plan

Scope, per source:

  05 Reference/acr-ios.md            whole file      -> acr-ios
  05 Reference/acr-android.md        whole file      -> acr-android
  05 Reference/qacr-current-state.md whole file      -> qacr-ios / qacr-android,
                                                        from the ### sub-heading
  03 Specs/*.md                      the `> [!quote]-` evidence block ONLY,
                                     split by the run-in labels
                                     **ACR today.** / **QACR iOS today.** /
                                     **QACR Android today.**

Everything else in a spec note is deliberately ignored — frontmatter, the
verified banner, the verbatim requirement quote, "In plain terms", the
intended-behaviour table, the code excerpts and the `> [!warning]- Analysis`
block. The requirement text in particular must not leave the vault: it is Rev
1.15 wording and `product/` holds the current wording.

Two things the vault's own citation checker cannot see, and this does:

  * `.pbxproj` and `.md` citations. The checker indexes both extensions but its
    regex never lists them, so every such citation was silently skipped.
  * Continuation citations. Android-side prose writes the filename once and then
    refers to further lines in the same file as a bare `:2422`. There are ~1,000
    of these across the vault. They are resolved here to the full path of the
    last full citation in the same paragraph, falling back to the last one in the
    same section (recorded as `inherited: section` so it can be audited).
"""
import os
import re
import sys
import json

VAULT = os.path.expanduser(
    "~/Documents/Healthy.io/Healthy.io - MD/QACR - Implementation Plan")
REFERENCE = os.path.join(VAULT, "05 Reference")
SPECS = os.path.join(VAULT, "03 Specs")

EXT = ("swift|kt|kts|java|xml|json|plist|gradle|yml|yaml|strings|xcstrings|"
       "arb|sh|h|m|pbxproj|md")
RANGES = r"\d+(?:-\d+)?(?:\s*,\s*\d+(?:-\d+)?)*"
CITE = re.compile(rf"`([^`\n]+?\.(?:{EXT})):({RANGES})`")
CONT = re.compile(rf"`:({RANGES})`")
# Build files that carry no extension. `AndroidDip/Jenkinsfile` followed by
# stage citations `:302` / `:351` is the whole of §23 on the Android side.
NOEXT = ("Jenkinsfile", "Dangerfile", "Fastfile", "Podfile", "Gemfile",
         "Makefile", "Appfile", "Matchfile", "Dockerfile")
BARE = re.compile(rf"`([^`\n*]+?(?:\.(?:{EXT})|(?<![\w.\-])(?:{'|'.join(NOEXT)})))`")
FENCE = re.compile(r"^\s*```")

# A citation's path usually settles the product on its own. Used when a passage
# carries no platform label of its own — inference from the repo the file is in,
# never a guess.
ACR_IOS_ROOTS = ("iosDip/", "ios-foundations/", "ios-views/", "ios-camera/",
                 "ios-chat-services/", "ios-questionnaire/", "ios-markup/",
                 "iOS-ConfigurationFiles/", "Dip/", "Dip.io.xcodeproj/", "Algo/")
ACR_ANDROID_ROOTS = ("AndroidDip/", "android.shared-")
QACR_IOS_ROOTS = ("urine.com.ios-qacr-app/", "Quant/", "Quant.xcodeproj/")
QACR_ANDROID_ROOTS = ("AndroidQacr/",)

IOS_EXT = re.compile(r"\.(swift|plist|pbxproj|m|h|strings|xcstrings|"
                     r"xcscheme|entitlements)$")
ANDROID_EXT = re.compile(r"\.(kt|kts|gradle|java|pro)$")


def path_signals(path):
    """(family, platform) inferred from a citation path. Never guesses beyond it.

    Family is decidable only when the path names a repository root. Platform is
    decidable much more often — an extension or a directory convention is enough
    — which is what lets an ACR passage with no platform sub-label be resolved.
    """
    family = ""
    if path.startswith(QACR_IOS_ROOTS):
        family, platform = "qacr", "ios"
    elif path.startswith(QACR_ANDROID_ROOTS):
        family, platform = "qacr", "android"
    elif path.startswith(ACR_IOS_ROOTS):
        family, platform = "acr", "ios"
    elif path.startswith(ACR_ANDROID_ROOTS):
        family, platform = "acr", "android"
    else:
        platform = ""
    if platform:
        return family, platform
    if IOS_EXT.search(path) or ".lproj/" in path:
        return family, "ios"
    if ANDROID_EXT.search(path) or "app/src/" in path or "/res/" in path \
            or path.endswith("AndroidManifest.xml") or "/java/" in path:
        return family, "android"
    return family, ""


REPO_ROOT = os.path.expanduser("~/Documents/Healthy.io")
_index = None
_lines = {}


def build_index():
    """basename -> {repo, ...} for every source file in the cloned repos."""
    global _index
    if _index is not None:
        return _index
    _index = {}
    skip = {".git", "build", ".build", "Pods", "node_modules", "DerivedData",
            ".gradle", ".idea", "Carthage", ".claude", ".swiftpm", "xcuserdata"}
    roots = set()
    for group in (QACR_IOS_ROOTS, QACR_ANDROID_ROOTS, ACR_IOS_ROOTS,
                  ACR_ANDROID_ROOTS):
        for r in group:
            r = r.rstrip("/")
            if os.path.isdir(os.path.join(REPO_ROOT, r)):
                roots.add(r)
            else:
                roots.update(d for d in os.listdir(REPO_ROOT)
                             if d.startswith(r)
                             and os.path.isdir(os.path.join(REPO_ROOT, d)))
    for name in sorted(roots):
        for dirpath, dirnames, filenames in os.walk(os.path.join(REPO_ROOT, name)):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for fn in filenames:
                rel = os.path.relpath(os.path.join(dirpath, fn), REPO_ROOT)
                _index.setdefault(fn, {})[rel] = None
    return _index


def file_lines(rel):
    if rel not in _lines:
        try:
            with open(os.path.join(REPO_ROOT, rel), encoding="utf-8",
                      errors="replace") as f:
                _lines[rel] = sum(1 for _ in f)
        except OSError:
            _lines[rel] = -1
    return _lines[rel]


def covers(path, last_line):
    """Does a file matching this citation path really have that many lines?

    Used only to REJECT an inheritance candidate, never to invent one. A path we
    cannot find at all is treated as unknown, not as a rejection.
    """
    idx = build_index()
    cands = idx.get(os.path.basename(path))
    if not cands:
        return None
    tail = path.lstrip("./")
    exact = [c for c in cands if c.endswith(tail)]
    for c in (exact or list(cands)):
        n = file_lines(c)
        if n >= last_line:
            return True
    return False


def repo_lookup(path):
    """Where a bare filename actually lives, read off disk.

    Last resort for a citation like `.natrium.yml:101` that carries no repo, no
    directory and no platform-bearing extension. Looking it up beats inventing a
    rule; if it resolves to exactly one repository, that repository decides.
    """
    owners = {rel.split(os.sep)[0] for rel in build_index().get(
        os.path.basename(path), {})}
    if len(owners) != 1:
        return "", ""
    owner = next(iter(owners))
    return path_signals(owner + "/x.txt")[0], \
        ("ios" if owner.lower().startswith(("ios", "urine.com.ios", "dip"))
         else "android")


def product_from_path(path, assume_family=""):
    family, platform = path_signals(path)
    if not (family and platform):
        f2, p2 = repo_lookup(path)
        family, platform = family or f2, platform or p2
    family = family or assume_family
    if family and platform:
        return f"{family}-{platform}"
    return ""


STATUS_WORDS = {
    "IMPLEMENTED": "present", "PARTIAL": "partial",
    "SCAFFOLD ONLY": "scaffold", "SCAFFOLD": "scaffold", "ABSENT": "absent",
}


def paragraphs(lines, first_lineno=1):
    """Maximal runs of consecutive non-blank lines, fenced code skipped.

    A paragraph is the inheritance scope for continuation citations: this is how
    the prose is actually written — the filename appears once at the top of a
    bullet list and the bullets carry bare line numbers.
    """
    buf, start, in_fence = [], None, False
    for i, raw in enumerate(lines):
        lineno = first_lineno + i
        if FENCE.match(raw):
            in_fence = not in_fence
            if buf:
                yield start, buf
                buf, start = [], None
            continue
        if in_fence:
            continue
        if raw.strip():
            if not buf:
                start = lineno
            buf.append((lineno, raw))
        elif buf:
            yield start, buf
            buf, start = [], None
    if buf:
        yield start, buf


SEG_SPLIT = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|\|)")


def segments(para):
    """Split a paragraph into claim-sized units: bullets, table rows, sentences.

    Each segment keeps the line number of its first line, so every row can name
    the vault line it came from.
    """
    chunks, cur = [], []
    for lineno, raw in para:
        if SEG_SPLIT.match(raw) and cur:
            chunks.append(cur)
            cur = []
        cur.append((lineno, raw))
    if cur:
        chunks.append(cur)

    out = []
    for chunk in chunks:
        lineno = chunk[0][0]
        text = " ".join(l.strip() for _, l in chunk)
        text = re.sub(r"\s+", " ", text).strip()
        out.append((lineno, text))
    return out


def sentence_around(text, pos):
    """The sentence containing offset `pos`, without splitting inside a citation."""
    starts = [0]
    for m in re.finditer(r"(?<![A-Z0-9])\.\s+(?=[A-Z`*\-])", text):
        starts.append(m.end())
    lo = max((s for s in starts if s <= pos), default=0)
    hi = min((s for s in starts if s > pos), default=len(text))
    return text[lo:hi].strip()


class Scope:
    """Heading and label state as the file is walked top to bottom."""

    def __init__(self, default_product, default_area=""):
        self.area = default_area
        self.product = default_product
        self.default_product = default_product
        self.section_product = default_product
        self.subsection = ""
        self.status = ""

    def heading(self, line):
        m = re.match(r"^##\s+(.*)", line)
        if m and not line.startswith("###"):
            self.area = m.group(1).strip()
            self.product = self.section_product = self.default_product
            self.subsection = self.status = ""
            return
        m = re.match(r"^###\s+(.*)", line)
        if m:
            sub = m.group(1).strip()
            if sub.lower() == "ios" and self.default_product == "qacr":
                self.product = self.section_product = "qacr-ios"
            elif sub.lower() == "android" and self.default_product == "qacr":
                self.product = self.section_product = "qacr-android"
            else:
                self.subsection = sub
            self.status = ""

    def bold_marker(self, text):
        m = re.match(r"^\*\*Status:\s*([A-Z ]+?)\*\*", text)
        if m:
            self.status = STATUS_WORDS.get(m.group(1).strip(), "")
            return
        m = re.match(r"^\*\*(Where|What exists|Visible gaps|Owner)\*\*", text)
        if m:
            self.subsection = m.group(1)


LABEL = re.compile(r"\*\*(ACR|QACR iOS|QACR Android) today\.\*\*")
PLATFORM = re.compile(r"\*\*(iOS|Android)\.\*\*")


def emit(records, *, requirement, area, product, status, sentence, citation,
         source, subsection, inherited, context="", note=""):
    records.append({
        "requirement": requirement,
        "area": area,
        "product": product,
        "status": status,
        "sentence": sentence,
        "context": context,
        "citation": citation,
        "source": source,
        "subsection": subsection,
        "inherited": inherited,
        "note": note,
    })


def scan(lines, scope, source_name, requirement="", label_mode=False,
         first_lineno=1):
    """Walk a body of prose and emit one candidate per citation, plus NOT FOUNDs."""
    records = []
    last_path_section = None
    document_files = {}
    section_files = FileScope(document_files)
    label, platform = None, None

    for start, para in paragraphs(lines, first_lineno):
        for lineno, raw in para:
            was = scope.area
            scope.heading(raw)
            if scope.area != was:
                section_files = FileScope(document_files)
                last_path_section = None
        head = re.sub(r"\s+", " ", para[0][1].strip())
        scope.bold_marker(head)

        if label_mode:
            m = LABEL.search(head)
            if m and m.group(1) != label:
                label, platform = m.group(1), None
                last_path_section = None
            if label == "ACR":
                pm = PLATFORM.search(head)
                if pm and pm.group(1) != platform:
                    platform = pm.group(1)
                    last_path_section = None

        last_path_para = None
        for lineno, text in segments(para):
            if label_mode:
                m = LABEL.search(text)
                if m and m.group(1) != label:
                    label, platform = m.group(1), None
                    last_path_para = last_path_section = None
                if label == "ACR":
                    pm = PLATFORM.search(text)
                    if pm and pm.group(1) != platform:
                        platform = pm.group(1)
                        last_path_para = last_path_section = None

            # Everything in this segment that names a file, in reading order.
            # A continuation citation (`:2422`) inherits from one of these; the
            # question is which, and getting it wrong attaches a true claim to
            # the wrong file, which is worse than losing the claim.
            mentions = []          # (pos, path) — cited with a line, or just named
            hits = []
            for m in BARE.finditer(text):
                mentions.append((m.start(), m.group(1)))
                hits.append((m.start(), m.group(1), None, "bare"))
            for m in CITE.finditer(text):
                mentions.append((m.start(), m.group(1)))
                hits.append((m.start(), m.group(1), f"{m.group(1)}:{m.group(2)}",
                             ""))
            for m in CONT.finditer(text):
                hits.append((m.start(), None, m.group(1), "continuation"))
            mentions.sort()
            hits.sort()

            for _, p in mentions:
                # one basename can name several real files — SyncManager.kt
                # exists in AndroidDip and in AndroidQacr — so keep them all and
                # let the product filter choose
                for store in (section_files, document_files):
                    seen = store.setdefault(os.path.basename(p), [])
                    if p not in seen:
                        seen.append(p)
            symbols = [(m.start(), m.group(1))
                       for m in SYMBOL.finditer(text)]

            resolved = []
            for pos, path, raw_cite, kind in hits:
                inherited = ""
                if kind == "bare":
                    # names a file without citing a line: not a claim of its own,
                    # but it is what a following `:14-71` may refer to
                    last_path_para = last_path_section = path
                    continue
                if kind == "continuation":
                    ctx = scope.product
                    if label_mode:
                        ctx = {"QACR iOS": "qacr-ios",
                               "QACR Android": "qacr-android"}.get(label or "", "")
                        if label == "ACR":
                            ctx = {"iOS": "acr-ios",
                                   "Android": "acr-android"}.get(platform or "", "")
                    base, how = resolve_base(
                        raw_cite, pos, mentions, symbols, section_files,
                        last_path_para, last_path_section,
                        ctx)
                    if not base:
                        # nothing in scope names the file. Keep the claim and let
                        # the citation fail the checker — a citation that cannot
                        # be resolved is a finding, not something to delete.
                        DROPPED.append((source_name, lineno, raw_cite))
                        resolved.append((pos, "", f":{raw_cite}", "unresolved"))
                        continue
                    inherited, citation, path = how, f"{base}:{raw_cite}", base
                else:
                    citation = raw_cite
                    last_path_para = path
                    last_path_section = path
                resolved.append((pos, path, citation, inherited))

            for pos, path, citation, inherited in resolved:
                product = scope.product
                if label_mode:
                    # inside a spec's evidence block the run-in label is the
                    # authority; the path settles what the label leaves open
                    if label == "QACR iOS":
                        product = "qacr-ios"
                    elif label == "QACR Android":
                        product = "qacr-android"
                    elif label == "ACR":
                        product = {"iOS": "acr-ios",
                                   "Android": "acr-android"}.get(platform or "", "")
                        product = product or product_from_path(path, "acr")
                    else:
                        product = product_from_path(path)
                    explicit = product_from_path(path)
                    if explicit and path_signals(path)[0]:
                        product = explicit
                elif product in ("", "qacr"):
                    product = product_from_path(
                        path, "qacr" if scope.default_product == "qacr" else "")
                emit(records, requirement=requirement, area=scope.area,
                     product=product, status=scope.status,
                     sentence=sentence_around(text, pos), context=text[:900],
                     citation=citation, source=f"{source_name}:{lineno}",
                     subsection=scope.subsection, inherited=inherited)

            # negative claims: a grep that returned nothing is evidence too
            if "NOT FOUND" in text and not resolved:
                product = scope.product
                if label_mode:
                    product = {"QACR iOS": "qacr-ios",
                               "QACR Android": "qacr-android"}.get(label or "", "")
                    if label == "ACR":
                        product = {"iOS": "acr-ios",
                                   "Android": "acr-android"}.get(platform or "", "")
                elif product == "qacr":
                    product = ""

                emit(records, requirement=requirement, area=scope.area,
                     product=product, status="absent",
                     sentence=text, context=text[:900], citation="",
                     source=f"{source_name}:{lineno}",
                     subsection=scope.subsection, inherited="",
                     note="NOT FOUND")
    return records


# A backticked token whose head is a capitalised identifier: `SyncManager.foo`,
# `AlgoRunner...handleThumbnailData`, `AlgorithmService.Input.serialize()`.
SYMBOL = re.compile(r"`([A-Z][A-Za-z0-9_]+)[^`\n]*`")


def last_line_of(ranges):
    return max(int(x) for x in re.findall(r"\d+", ranges))


def resolve_base(ranges, pos, mentions, symbols, section_files,
                 last_para, last_section, product=""):
    """Which file does a bare `:2422` belong to?

    Three signals, strongest first:

    1. A symbol named just before it. "called once per `DipApplication.reset()`
       (`:187`)" means line 187 of DipApplication — not of whatever file happened
       to be cited last. Only accepted when a file of that name is cited
       somewhere in the same section, so the name is never invented.
    2. The nearest file named earlier in the same sentence or bullet WHOSE REAL
       FILE IS LONG ENOUGH to have that line. Checking against the repository is
       what separates "Concrete Camera2 keys are set in `Camera2Extensions.kt`:
       `:492-493`" from a passing mention of a one-line Lottie asset.
    3. Failing both, the nearest file named earlier, then the last file named in
       the paragraph, then in the section.
    """
    want = last_line_of(ranges)
    before = [(p, x) for p, x in mentions if p < pos]

    # The symbol may sit either side of the citation: "polled by
    # `SyncManager.getOrderStatus` (`:463-524`)" puts it before, "`:191-240`
    # (`AlgorithmService.Input.serialize()`)" puts it after.
    # Backwards the symbol can be a clause away ("polled by `X.foo`, …, `:463`");
    # forwards it is only ever the immediate gloss ("`:191-240` (`X.serialize()`)"),
    # so a wide forward window just steals the base from the next sentence.
    near = sorted((abs(sp - pos), sp, sym) for sp, sym in symbols
                  if -160 <= sp - pos <= 16)
    wrong_product = []
    for _, _, sym in near[:4]:
        hit = section_files.get_symbol(sym, product, wrong_product)
        if hit and covers(hit, want) is not False:
            return hit, "symbol"
    if wrong_product:
        # The sentence names a file that exists — in the OTHER product. Whatever
        # this line belongs to, it is not the file that happens to sit nearest in
        # the prose. Leave it unresolved rather than attach it to the wrong file.
        return None, ""

    for _, cand in reversed(before):
        if covers(cand, want) is True:
            return cand, "verified"
    for cand, how in ((last_para, "paragraph"), (last_section, "section")):
        if cand and covers(cand, want) is True:
            return cand, how
    # Everything below is a positional guess. Emit one only if the file it names
    # could actually contain the cited line; otherwise leave the citation
    # unresolved and let the checker report it. A citation attached to the wrong
    # file reads as verified and is worse than a gap.
    if before and covers(before[-1][1], want) is not False:
        return before[-1][1], "nearest"
    for cand, how in ((last_para, "paragraph"), (last_section, "section")):
        if cand and covers(cand, want) is not False:
            return cand, how
    return None, ""


class FileScope(dict):
    """Files named in the current section, with the whole document behind it.

    A symbol like `Model.imagesSuffix` names a file the section may not have
    cited itself; the document almost always has. Section first, so a same-named
    file from another product cannot win.
    """

    def __init__(self, document):
        super().__init__()
        self.document = document

    def get_symbol(self, sym, product="", _wrong=None):
        """The file a symbol names — never one from the other platform.

        `CameraViewModel` exists as a Swift file and a Kotlin file, in ACR and
        in QACR — four files, one name. Resolving a QACR iOS sentence onto ACR's
        CameraViewModel.swift would attach a true claim to the wrong product, so
        when the passage's product is known and no file of that name matches it,
        this returns nothing and the position-based tiers decide instead.
        """
        for src in (self, self.document):
            hits = [p for k, v in src.items() if k.rsplit(".", 1)[0] == sym
                    for p in v]
            if not hits:
                continue
            if product:
                same = [h for h in hits if product_from_path(h) == product]
                if not same and _wrong is not None:
                    _wrong.append(sym)
                return same[0] if same else None
            return hits[0]
        return None


DROPPED = []

QUOTE_START = re.compile(r"^>\s*\[!quote\]")
CALLOUT_START = re.compile(r"^>\s*\[!")


def spec_quote_block(path):
    """The `> [!quote]-` evidence block of a spec note, and its line numbers."""
    lines = open(path, encoding="utf-8").read().split("\n")
    out, first, inside = [], None, False
    for i, raw in enumerate(lines, start=1):
        if QUOTE_START.match(raw):
            inside, first = True, i
            continue
        if inside:
            if raw.startswith(">"):
                if CALLOUT_START.match(raw):
                    break
                out.append(re.sub(r"^>\s?", "", raw))
            elif raw.strip() == "":
                out.append("")
            else:
                break
    return (first or 1) + 1, out


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        mm = re.match(r"^(\w+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip().strip('"')
    return fm


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "candidates.jsonl"
    records = []

    for fname, default in (("acr-ios.md", "acr-ios"),
                           ("acr-android.md", "acr-android"),
                           ("qacr-current-state.md", "qacr")):
        path = os.path.join(REFERENCE, fname)
        lines = open(path, encoding="utf-8").read().split("\n")
        scope = Scope(default)
        records += scan(lines, scope, f"05 Reference/{fname}")

    for fname in sorted(os.listdir(SPECS)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(SPECS, fname)
        fm = frontmatter(path)
        req = fm.get("requirement", "")
        first, body = spec_quote_block(path)
        if not body:
            continue
        area = req[3:6] if req.startswith("FR-") else ""
        scope = Scope("", area)
        records += scan(body, scope, f"03 Specs/{fname}", requirement=req,
                        label_mode=True, first_lineno=first)

    with open(out_path, "w", encoding="utf-8") as f:
        for i, r in enumerate(records):
            r["n"] = i
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    from collections import Counter
    print(f"{len(records)} candidates -> {out_path}")
    print("by product :", dict(Counter(r["product"] for r in records)))
    print("by source  :", dict(Counter(r["source"].split(":")[0].split("/")[0]
                                       for r in records)))
    print("continuation citations resolved:",
          dict(Counter(r["inherited"] for r in records if r["inherited"])))
    print("NOT FOUND rows:", sum(1 for r in records if r["note"] == "NOT FOUND"))
    print("with a requirement id:", sum(1 for r in records if r["requirement"]))
    unknown = [r for r in records if not r["product"]]
    print("continuation citations with no filename in scope (kept, "
          "citation left as written):", len(DROPPED))
    for d in DROPPED[:10]:
        print("   ", d)
    print("PRODUCT UNRESOLVED:", len(unknown))
    for r in unknown[:15]:
        print("   ", r["source"], r["citation"][:70])


if __name__ == "__main__":
    main()
