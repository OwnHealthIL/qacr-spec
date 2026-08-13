# evidence/

What the ACR and QACR code does **today**, as data — one cited claim per row.

This is the layer that stops "ACR already does this" from being a recollection. Every row carries a
`file:line` citation into a real repository at a known commit, so any claim can be re-checked
rather than believed.

## What is here now

| File | |
|---|---|
| `pins.yaml` | The commit each of the four code repositories stood at when evidence was read. All four were still HEAD on 2026-08-13. |

## What is coming

### `behaviour.tsv` — not built yet

One row per cited claim about what the code does. Tab-separated, one header line:

```
requirement  area  product  status  claim  citation  source
```

| Column | |
|---|---|
| `requirement` | `FR-XXX-NNN`, or empty where the claim is area-scoped rather than requirement-scoped |
| `area` | the atlas section name (its §0–25 spine), or the FR area code |
| `product` | `acr-ios` · `acr-android` · `qacr-ios` · `qacr-android` |
| `status` | `present` · `partial` · `scaffold` · `absent`, or empty if the source states none |
| `claim` | one line, present tense, no markdown. What is true — not why it matters |
| `citation` | `path:line` or `path:start-end`, byte-for-byte as the source wrote it |
| `source` | `<vault file>:<line>` the row came from, so any row can be traced back and argued with |

Negative claims are kept: where a search found nothing, `status` is `absent`, the searched symbols
go in `claim`, and `citation` is empty.

**Work in progress on the `wip/evidence-extraction` branch.** Mechanical extraction is complete —
2,859 candidate rows with resolved citations — and the compression pass that writes the `claim`
column is 3 batches of 20 done. `wip-evidence/NOTES.md` on that branch records where it got to,
the citation-resolution rule it settled on, every class of defect found so far, and what to do
differently on the next attempt. Read it before resuming.

### `context.tsv` — not built yet

The facts a human supplied that no requirement states. Derived from the vault's Context register.

```
id  fact  what_no_requirement_states  attributed_to  date  affects
```

Roughly eleven `CTX-nn` entries. These exist because a note can be accurate against the
requirements, accurate about the code, and still wrong about QACR.

## Rules

- A row is added when someone reads the code, not when someone remembers it.
- Citations are preserved exactly as written; they are not tidied.
- A citation that no longer resolves is a **finding**, not a row to delete. It means either the
  code moved or the claim was always wrong, and both are worth knowing.
- `pins.yaml` is re-read whenever evidence is added. A row read at a commit that is no longer HEAD
  is the short list worth re-verifying.
