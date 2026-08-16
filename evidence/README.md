# evidence/

What the ACR and QACR code does **today**, as data — one cited claim per row.

This is the layer that stops "ACR already does this" from being a recollection. Every row carries a
`file:line` citation into a real repository at a known commit, so any claim can be re-checked
rather than believed.

Re-check them all at any time:

```bash
python3 tools/check_citations.py            # reads behaviour.tsv
```

## The files

| File | What it answers |
|---|---|
| `behaviour.tsv` | What does the code do today, per product, with a citation |
| `coverage.tsv` | Has anyone actually looked — and if so, did they find anything |
| `context.tsv` | What does a human know that no requirement states |
| `pins.yaml` | Which commit was all of this read against |

---

### `behaviour.tsv`

One row per cited claim. Tab-separated, one header line:

```
requirement  area  product  status  claim  citation  source
```

| Column | |
|---|---|
| `requirement` | `FR-XXX-NNN`, or empty where the claim is area-scoped rather than requirement-scoped |
| `area` | the atlas section name, or the FR area code |
| `product` | `acr-ios` · `acr-android` · `qacr-ios` · `qacr-android` |
| `status` | `present` · `partial` · `scaffold` · `absent`, or empty if the source states none |
| `claim` | one line, present tense, no markdown. What is true — not why it matters |
| `citation` | `path:line` or `path:start-end`, byte-for-byte as the source wrote it |
| `source` | `<vault file>:<line>` the row came from, so any row can be traced back and argued with |

Negative claims are kept: where a search found nothing, `status` is `absent`, the searched symbols
go in `claim`, and `citation` is empty. "This does not exist" is as valuable as "this exists" and
much easier to get wrong from memory.

**The table is built in slices, one spec at a time.** It currently covers
`QACR-APP-SPEC-01` only. Which is exactly why `coverage.tsv` exists.

### `coverage.tsv`

```
requirement  feature  epic  extraction_scope  evidence_rows  state
```

One row per requirement in the FR document — all 241, whether or not anyone has looked at it.
`state` is one of:

| | |
|---|---|
| `evidenced` | rows exist in `behaviour.tsv` |
| `no-evidence-found` | **someone looked and found nothing.** Nobody has read this area of the code |
| `not-extracted` | nobody has looked yet. Absence of rows means nothing here |

This file exists because in a partial table **absence is ambiguous**. Grep `behaviour.tsv` for
`FR-CFG-003`, get nothing, and you cannot tell "nobody has looked at this in the code" from "not
processed yet" — opposite conclusions that look identical. Always read `coverage.tsv` before
concluding anything from a missing row.

`no-evidence-found` is the most useful column in the repository. It is the list of things nobody
has checked in the code, and it is where a spec is most likely to be asserting something untrue.

### `context.tsv`

```
id  fact  what_no_requirement_states  attributed_to  date  affects
```

Eleven `CTX-nn` rows: facts a human supplied that no requirement states, each with the gap it
leaves, who said it and when.

This exists because a note can be accurate against the requirements, accurate about the code, and
still wrong about QACR — someone knows something that never got written down.

### `pins.yaml`

The commit each of the four repositories stood at. `Foo.swift:102` means nothing without it.

---

## Rules

- A row is added when someone reads the code, not when someone remembers it.
- Citations are preserved exactly as written; they are not tidied.
- **A citation that no longer resolves is a finding, not a row to delete.** It means either the
  code moved or the claim was always wrong, and both are worth knowing.
- Never read a missing row as "nobody has looked". Check `coverage.tsv`.
- `pins.yaml` is re-read whenever evidence is added.

## Remaining work

`PLAN.md` Phase 6 extends `behaviour.tsv` from the current spec-scoped slice to all 241
requirements. 2,859 candidates are already extracted with their citations resolved, on the
`wip/evidence-extraction` branch; `wip-evidence/NOTES.md` there records the resolution rule and the
defects found so far.
