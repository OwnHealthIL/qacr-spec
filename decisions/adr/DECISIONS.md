# QACR decision log

**Every decision made while specifying QACR features, in one scannable, append-only log.** One
file for the whole product — iOS and Android answer from and write to the same log. There is no
per-feature file and no per-platform file; a decision recorded anywhere else is one this log does
not know about, and the question it answered gets asked again.

Written by a developer recording an answer, through the toolkit's `documentation` skill following
`.claude/skills/adr-conventions/SKILL.md`. Read by `qacr-context`, which folds live answers into feature
contracts so an answered question is never re-asked.

## The parse contract

A machine consumer may rely on exactly this, and nothing else:

- **Append-only.** Entries are never rewritten, reordered, or deleted. One exception: an entry's
  `record_status` field may be updated in place when the revision it awaits lands.
- **One entry = one `## <id> — <question>` heading, one fenced `yaml` block immediately after it,
  then prose.** Never an H1 per entry. Entries appear only below the marker comment at the end of
  this preamble; every heading above it is preamble, not an entry.
- **Field names are stable, and every field is present on every entry** — `n/a` when not
  applicable, never omitted.
- **Ids are stable.** Once written, an id never changes.
- **Superseding is appending.** A later entry names the old one in `supersedes:`. Nothing marks
  the old entry; currency is derived by scanning — an entry no later entry supersedes is current.

## Ids derive from the question

**Sequential numbering is forbidden.** An id is the requirement id plus a slug of the question —
`FR-PLT-002-min-os-mechanism`, never `ADR-007`. Two developers answering the same question must
derive the same id and conflict loudly in git; with a sequence number each would mint a fresh id
and the log would carry the same decision twice, silently.

## The fields

| field | holds |
|---|---|
| `id` | question-derived slug, e.g. `FR-PLT-002-min-os-mechanism` |
| `type` | `product` \| `implementation` \| `architectural` |
| `status` | `accepted` \| `deferred` — deferred is a legitimate answer (reason, owner, what reopens it) and counts as resolved for gating |
| `question` | one sentence, answerable |
| `answer` | what was decided — verbatim where it was given verbatim |
| `decided_by` | who answered — the person who took *this* decision, including the decision to defer |
| `owner` | who owns resolving a deferral; `n/a` on an accepted entry. Not the same as `decided_by`: one settled the deferral, the other has to end it |
| `reopens_when` | the condition that reopens a deferral; `n/a` on an accepted entry. A deferral with no stated reopen condition is a question quietly dropped |
| `decided_on` | the date of the answer |
| `how` | `face-to-face` \| `meeting` \| `chat` \| `review` \| ... |
| `recorded_by` | who wrote the entry |
| `product` | `QACR` |
| `spec` | id + revision, e.g. `QACR-APP-SPEC-01 Rev1.2` |
| `feature` | e.g. `F01.1` |
| `affects` | requirement ids, e.g. `[FR-PLT-002]` |
| `resolves` | spec-raised question ids, e.g. `[SD-1]` |
| `unblocks` | acceptance-criterion ids, e.g. `[AC-6]` |
| `decided_against` | the document revisions the question was read against, e.g. `{ FR-01: Rev1.20 }` |
| `record_status` | `pending-revision` \| `in-<revision>` \| `n/a` |
| `supersedes` | the id this entry replaces, or `n/a` |

What each `type` obliges:

| type | obligation |
|---|---|
| `product` | a requirements/brief revision is owed; `record_status` tracks it |
| `implementation` | nothing beyond the entry; `record_status: n/a` |
| `architectural` | also registered in `architecture/ios.md` or `architecture/android.md` per domain, citing the entry id |

## Entry template

````markdown
## FR-PLT-002-min-os-mechanism — <the question, one sentence>

```yaml
id: FR-PLT-002-min-os-mechanism
type: product                     # product | implementation | architectural
status: accepted                  # accepted | deferred
question: <one sentence, answerable>
answer: <what was decided — verbatim where it was given verbatim>
decided_by: <who answered>
owner: <who owns resolving it, n/a when accepted>
reopens_when: <what reopens it, n/a when accepted>
decided_on: 2026-08-27
how: face-to-face                 # face-to-face | meeting | chat | review | ...
recorded_by: <who wrote the entry>
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-002]             # requirement ids
resolves: [SD-1]                  # spec-raised question ids, or n/a
unblocks: [AC-6]                  # acceptance-criterion ids, or n/a
decided_against: { FR-01: Rev1.20 }
record_status: pending-revision   # pending-revision | in-<revision> | n/a
supersedes: n/a                   # id of the entry this one replaces, or n/a
```

**Context** — the evidence that made this a question, with citations.

**Decision** — what was decided, and the reason, terse.

**What the document must say** — `product` type only: exact paste-ready text for the document
owner to put in the next revision.

**Alternatives considered** — only when alternatives were genuinely weighed.
````

**Context** and **Decision** are mandatory on every entry. **What the document must say** appears
on `product` entries only. **Alternatives considered** appears only when something was genuinely
weighed — never as a ritual section.

---

<!-- The log begins here. Append the first entry directly below this comment, and every later
     entry below the one before it. -->

## FR-PLT-004-algo-sensor-dependency — Does the algorithm receive or depend on motion-sensor data?

```yaml
id: FR-PLT-004-algo-sensor-dependency
type: implementation
status: accepted
question: Does the algorithm receive or depend on motion-sensor data?
answer: No. No inertial or motion sensor data reaches the algorithm on either platform at any point. It receives camera frames plus camera metadata only — exposure, ISO, white-balance gains, tone mapping, flash, edge enhancement, noise reduction, focal length.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-08-27
how: review
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-004]
resolves: [SQ-B]
unblocks: [AC-8, AC-9]
decided_against: { SPEC-01: Rev1.2, FR-01: Rev1.20, EPIC-01: Rev1.14, iosDip: e0636af3, AndroidDip: a50d8b03, ios-camera: b59561e7, ios-foundations: 35dac5a5 }
record_status: n/a
supersedes: n/a
```

**Context** — The spec raised this as open question `SQ-B` because the algorithm ships as a compiled
framework, so `acr-behaviour-reference` recorded it `not_derivable: binary`, and both `AC-8` ("declare
exactly the hardware a test depends on") and `AC-9` ("no capability declared that the app does not
use") were unclosable without it. It also decides whether ACR's iOS `gyroscope` requirement should be
recreated. Settled by reading four layers rather than by a ruling:

- **The algorithm's input surface is three entry points per platform, and narrow.** iOS
  `Quant/Algorithm/Bridge/ObjectiveC/HLTAlgorithmAPI.h` — `prepareAlgorithm` (paths/ids),
  `runScan(CVImageBufferRef, HLTCameraConfig)`, `runAlgorithm(examId, dirs, images, imagesPoints,
  enableLearnedRaw)`; imports are only `UIKit` and `CoreVideo`. Android
  `android.shared-urine-algo/urine-algo/src/main/java/io/healthy/shared/urine_algo/Algorithm.kt:120-150`
  mirrors it.
- **Every payload field is imaging.** Android `camera/Frame.kt` is `data: ByteArray, width, height,
  points: FloatArray(8)`; `camera/CameraConfig.kt` carries exposure, white balance, tone mapping,
  flash, edge enhancement, noise reduction and focal length, all derived from `FrameInfo`. ACR iOS
  sends `PhotoData` + `ShotSettings` (`iosDip/Dip/Infra/Results/ResultData.swift:131`) — torch mode,
  torch level, exposure time. No motion field on either side.
- **Neither app reads a motion sensor.** No `CoreMotion`/`CMMotionManager` in `iosDip/Dip`,
  `iosDip/Algo`, `ios-camera` @ `b59561e7` (1.1.1) or `ios-foundations` @ `35dac5a5` (7.1.5), read at
  their `Package.resolved` pins. On Android `SensorManager` appears once in release sources
  (`AndroidDip/app/src/main/java/io/healthy/dip/utils/AppUtils.kt:69-70`) and **has no caller**; the
  only real sensor use is `ShakeDetector` under `app/src/debug/`, the debug environment switcher.
- **The binary cannot do it behind the app's back.**
  `iosDip/Algo/dip3/dip3.xcframework/ios-arm64/libdip3-phone.a` carries 2871 undefined symbols, 454
  of them mangled OpenCV C++, and **zero** `_OBJC_CLASS_$_` references and zero motion, gyroscope or
  accelerometer symbols. CoreMotion is Objective-C-only with no C API, so a pure C++ archive
  referencing no Objective-C class cannot reach it.

**Decision** — The algorithm depends on the camera and camera metadata only. Consequently ACR's iOS
`gyroscope` entry in `UIRequiredDeviceCapabilities`
(`iosDip/Dip/TargetFiles/Acr/MinutefulKidneyUS/ACR-Minuteful-US-Info.plist:59-65`) has **no
demonstrated dependency** and must not be recreated: QACR declares `camera-flash`, `video-camera` and
`auto-focus-camera`, and not `gyroscope`. This confirms the spec's `do_not_copy` entry with positive
evidence rather than absence of evidence, and gives `AC-9` its first concrete finding.

One residual, which does not change the answer: the symbol scan was run on ACR's `dip3` archive
because QACR's `qacr.xcframework` is not committed — it is fetched by `Quant/Scripts/download_algo.sh`.
Repeating the scan on QACR's own binary closes the loop. The QACR bridge above passes no sensor data
regardless, so the app cannot supply any even if the binary wanted it.

## FR-PLT-002-min-os-mechanism — What mechanism enforces the minimum supported OS?

```yaml
id: FR-PLT-002-min-os-mechanism
type: product
status: accepted
question: What mechanism enforces the minimum supported OS?
answer: The install-time build setting alone — the iOS deployment target and the Android minSdk. The backend-served iosMinOsVersion / androidMinOsVersion are a separate run-time gate belonging to F01.2, and are not the mechanism FR-PLT-002 and FR-PLT-003 speak to.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-08-27
how: review
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-002, FR-PLT-003]
resolves: [SD-1]
unblocks: [AC-5, AC-6, AC-7]
decided_against: { SPEC-01: Rev1.2, FR-01: Rev1.20, EPIC-01: Rev1.14, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — FR-PLT-002's `note` in FR-01 Rev1.20 reads "Minimum version TBD, to follow from the IVTS
device qualification. iosMinOsVersion currently 13.0.0". Three findings made that a question rather
than a detail:

- The shipping install-time minimum is **iOS 15.0**
  (`iosDip/Dip.io.xcodeproj/project.pbxproj:18438`, inside the `AcrMinutefulUS` configuration, whose
  `INFOPLIST_FILE` at `:18436` ties it to the in-scope target) and **Android 8.0** via `minSdk 26`
  (`AndroidDip/app/build.gradle.kts:37`). The note's 13.0.0 is two major versions below what ships.
- `iosMinOsVersion` is **not an install-time setting**. It appears nowhere in `iosDip`, `AndroidDip`
  or `iOS-ConfigurationFiles`, and resolves to the backend's init payload
  (`Server/behealthy/projects/client-api/src/handlers/tests/initAcr.test.js:88-94`) where it sits
  beside `iosMaxOsVersion` and `iosMinAppVersion`. **Neither app reads any of the three** — no
  reference to `minOsVersion`, `maxOsVersion` or `minAppVersion` exists in `iosDip/Dip` or
  `AndroidDip/app/src`.
- FR-PLT-003's note has the **same shape and the opposite outcome**: `androidMinOsVersion 8.0.0`
  coincides exactly with `minSdk 26` (Android 8.0), so that note is inert while its twin is live. The
  pair is why the disagreement was found at all — a scan for conflicts would have passed over both.

**Decision** — There are two mechanisms, not one, and F01.1 owns only the install gate. FR-PLT-002 and
FR-PLT-003 are satisfied by the build setting; the backend minimum is a run-time eligibility concern
and belongs to F01.2. The note is therefore describing the wrong mechanism for the requirement it sits
on, which is a note correction rather than a change of requirement. The *value* remains withheld by
U1/Q-03 — this entry settles the mechanism only, so `AC-6` and `AC-7` still state their threshold
rather than a number.

**What the document must say** — replace FR-PLT-002's note with: "Minimum version TBD, to follow from
the IVTS device qualification. Enforced by the iOS deployment target only; the current product ships
15.0. The backend-supplied `iosMinOsVersion` is a separate run-time gate (see F01.2) and is not this
requirement's mechanism." And FR-PLT-003's note with: "Minimum version TBD, to follow from the IVTS
device qualification. Enforced by the Android `minSdk` only; the current product ships API 26
(Android 8.0). The backend-supplied `androidMinOsVersion` is a separate run-time gate (see F01.2) and
is not this requirement's mechanism."

**Alternatives considered** — *Build setting only, note value simply stale*: rejected because it
discards a live mechanism; `iosMinOsVersion` is real, served per partner, and carries a companion
maximum, so striking it from the note would lose it rather than place it. *Backend config is the
mechanism*: rejected because it would move FR-PLT-002's subject from installability to run-time
eligibility, contradicting the requirement's own wording and duplicating F01.2.

## FR-PLT-004-supported-device-definition — What hardware must a device have for the app to be installable?

```yaml
id: FR-PLT-004-supported-device-definition
type: product
status: deferred
question: What hardware must a device have for the app to be installable?
answer: Deferred pending U1/Q-04, the minimum hardware specification owed by the IVTS device qualification. Reopened when Q-04 lands. Interim floor, already evidenced: camera, autofocus and flash, and no motion sensor.
decided_by: Omry Dabush
owner: Guy · IVTS device qualification
reopens_when: U1/Q-04 lands — the minimum hardware specification owed by the IVTS device qualification
decided_on: 2026-08-27
how: review
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-004]
resolves: [SD-2]
unblocks: n/a
decided_against: { SPEC-01: Rev1.2, FR-01: Rev1.20, EPIC-01: Rev1.14, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — FR-PLT-004 requires compatibility filters that prevent installation on unsupported
device models, but "not supported" currently means two different things, so there is no single as-is
behaviour to recreate:

- iOS requires `camera-flash`, `video-camera`, `auto-focus-camera` **and `gyroscope`**
  (`iosDip/Dip/TargetFiles/Acr/MinutefulKidneyUS/ACR-Minuteful-US-Info.plist:59-65`), and builds for
  iPhone only (`TARGETED_DEVICE_FAMILY = 1`, `iosDip/Dip.io.xcodeproj/project.pbxproj:18463`).
- Android requires camera, autofocus and flash, declares **no sensor at all**, and explicitly declares
  `telephony` as `required="false"` (`AndroidDip/app/src/main/AndroidManifest.xml:24-35`) so Play does
  not exclude non-telephony devices — a deliberate negative declaration against the `CALL_PHONE`
  permission at `:11`.
- QACR declares **nothing** today: `Quant/Info.plist` carries only `UIAppFonts`.

The gyroscope half of the disagreement is now settled — see `FR-PLT-004-algo-sensor-dependency`: the
algorithm takes camera data only, so the iOS gyroscope requirement has no demonstrated dependency.
What remains open is the positive definition, which is Product's to give and is exactly what U1/Q-04
withholds.

**Decision** — Deferred. Owner: **Guy · IVTS device qualification**, via U1/Q-04. Reopened when Q-04
lands, or earlier if Product fixes the supported-device set independently. This counts as resolved for
gating: `AC-8`, `AC-9` and `AC-10` verify against the answer whenever it arrives, and their evidenced
floor in the meantime is the camera trio with no sensor. Nothing is chosen here — recording a value
now would bury the question rather than answer it.

## FR-PLT-004-android-tablet-policy — Does the Android app exclude tablets, or serve them as the current product does?

```yaml
id: FR-PLT-004-android-tablet-policy
type: product
status: deferred
question: Does the Android app exclude tablets, or serve them as the current product does?
answer: Deferred pending U1/Q-04, the minimum hardware specification owed by the IVTS device qualification. Reopened when Q-04 lands.
decided_by: Omry Dabush
owner: Guy · IVTS device qualification
reopens_when: U1/Q-04 lands — the device family follows from the qualified hardware specification
decided_on: 2026-08-27
how: review
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-004]
resolves: [SD-4]
unblocks: n/a
decided_against: { SPEC-01: Rev1.2, FR-01: Rev1.20, EPIC-01: Rev1.14, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — The two platforms answer this differently today and no requirement states a device
family. ACR iOS is iPhone-only by build setting (`iosDip/Dip.io.xcodeproj/project.pbxproj:18463`);
nothing in `AndroidDip`'s build or manifests restricts the app to phones, so Play serves tablets. The
ACR Android flavour marks the app non-resizeable
(`AndroidDip/app/src/minutefulUs/AndroidManifest.xml`) but declares no device-class restriction.
QACR's iOS app inherits iPhone-only (`Quant.xcodeproj/project.pbxproj:2370` Debug, `:2410` Release)
from a setting nobody has revisited. Recorded as a question because an inconsistency inherited by
accident is the thing worth deciding, not the thing worth copying.

**Decision** — Deferred. Owner: **Guy · IVTS device qualification**, via U1/Q-04, since the device
family follows from the qualified hardware specification rather than standing on its own. Reopened
when Q-04 lands. Nothing is blocked in practice today: the QACR Android repository holds a single
README commit (`844860a`), so there is no Android build for a policy to apply to yet. `AC-10` verifies
against the answer whenever it arrives.

## FR-PLT-001-exclusivity-scope — Does "exclusively" in FR-PLT-001 cover internal pre-release distribution, or only the product build reaching users?

```yaml
id: FR-PLT-001-exclusivity-scope
type: product
status: deferred
question: Does "exclusively" in FR-PLT-001 cover internal pre-release distribution, or only the product build reaching users?
answer: Deferred pending a PM ruling on the scope of "exclusively". Owner: PM. Reopened when the PM rules. The interim reading the spec already applies is the narrow one — the stores' own tester channels (TestFlight, Play tester tracks) count as "through the store" — and no non-store channel is permitted for the product build under either reading.
decided_by: Omry Dabush
owner: PM
reopens_when: the PM rules on the scope of "exclusively"
decided_on: 2026-08-27
how: review
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-001]
resolves: [SD-3]
unblocks: n/a
decided_against: { SPEC-01: Rev1.2, FR-01: Rev1.20, EPIC-01: Rev1.14, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — FR-PLT-001 reads "The software shall be distributed exclusively through the Apple
App Store and Google Play Store." The brief dispositions it `as-is`, but the current product is
not unambiguously "exclusive" in the wide sense, which is what makes the scope a question rather
than a detail:

- ACR iOS carries an **enterprise-signed export**, under a different Apple team from the store
  export, shared by link and QR code from file storage
  (`iosDip/scripts/enterprise/exportOptions.plist:7-8`). Its build script takes the scheme as a
  command-line argument (`iosDip/scripts/enterprise/buildScript.py:114`), so the repository
  cannot say whether the ACR build is ever exported that way — the channel exists, its use is
  not readable from source.
- ACR Android carries a **test-distribution lane** publishing outside Play
  (`AndroidDip/fastlane/Fastfile:78-86`).
- QACR has neither today: nothing in the repository restricts or records who may install — no
  store metadata, no distribution pipeline, no CI configuration.

Under the **narrow** reading "exclusively" governs the product build reaching users, and
store-operated tester channels are inside it. Under the **wide** reading it covers every channel
including internal pre-release, and no non-store tester path may exist at all. Both are
defensible from the requirement's wording alone, which is why the spec declined to pick one:
spec `AC-13` is written to the narrow reading and *tightens* rather than changes shape under the
wide one, and `AC-12` forbids an out-of-store **product** build under either.

**Decision** — Deferred, not answered. Owner: **PM**, as the requirement's wording is what is
ambiguous and only its author can fix the scope. Reopened when the PM rules.

This counts as resolved for gating. Nothing in scope to build now waits on it: **FR-PLT-001 is
milestone M4**, so `AC-4`, `AC-12` and `AC-13` are outside the current build scope, and the spec
states its interim reading explicitly as Assumption 4 rather than silently assuming it. Nothing
is chosen here — recording a reading now would bury the question rather than answer it.

No **What the document must say** text accompanies this entry: there is no answer to paste yet.
It is owed when the ruling lands, at which point `record_status` moves off `pending-revision`.

## FR-PLT-002-max-os-and-min-app-version-ownership — Which feature owns the backend-served `iosMaxOsVersion` and `iosMinAppVersion` gates?

```yaml
id: FR-PLT-002-max-os-and-min-app-version-ownership
type: product
status: deferred
question: Which feature owns the backend-served iosMaxOsVersion and iosMinAppVersion gates?
answer: Deferred pending a Product ruling on feature ownership. Owner: Product. Reopened when Product rules, or when F01.2 is specified, whichever comes first. The evidenced reading, which this entry does not overturn, is that both are run-time gates of the same family as iosMinOsVersion and therefore belong to F01.2 rather than F01.1. No app reads either key today.
decided_by: Omry Dabush
owner: Product
reopens_when: Product rules on feature ownership, or F01.2 is specified, whichever comes first
decided_on: 2026-08-27
how: review
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-002]
resolves: [SQ-E]
unblocks: n/a
decided_against: { SPEC-01: Rev1.2, FR-01: Rev1.20, EPIC-01: Rev1.14, Server: unpinned, urine.com.ios-qacr-app: 6814fb64 }
record_status: pending-revision
supersedes: n/a
```

**Context** — The spec listed this as behaviour no requirement asked for: the backend init payload carries
two keys beside the `iosMinOsVersion` that `FR-PLT-002-min-os-mechanism` already placed in F01.2, and no
requirement in F01.1 contemplates either.

- **`iosMaxOsVersion` is an OS *ceiling*.** FR-PLT-002 speaks of installability "from the minimum
  version", a phrase with no upper bound in it, so the ceiling has no requirement to attach to. It is
  served per partner at a consistent `15.0.0`
  (`Server/behealthy/projects/client-api/src/handlers/tests/initAcr.test.js:92`, and the same value in
  `initDemoIntegrated`, `initDipUti`, `initFailures` and `initMaccabi`).
- **`iosMinAppVersion` is a force-upgrade gate**, not an install gate: it names an app version, not an OS
  version, and varies per partner (`5.0.7` for ACR at `initAcr.test.js:90`; `9.31.1` and `9.33.0` in
  `preLogin.test.js:20,36`). Its presence in the pre-login payload is itself evidence of a run-time
  concern rather than an install-time one.
- **QACR reads neither.** No reference to `maxOsVersion`, `minAppVersion` or `minOsVersion` exists
  anywhere under `Quant/`, matching the finding already recorded for ACR and Android in
  `FR-PLT-002-min-os-mechanism`.

**Decision** — Deferred, not answered. Owner: **Product**, since which feature owns a behaviour is a
scoping call and the spec routed this row to Product explicitly. Reopened when Product rules, or when
F01.2 is specified and either key is picked up there.

This counts as resolved for gating, and nothing in F01.1 waits on it: no acceptance criterion covers
either key, precisely because no requirement asked for them. What the deferral buys is that the two keys
are now owned rather than sitting between two features — the failure mode this row was raised to prevent.

No **What the document must say** text accompanies this entry: there is no answer to paste yet. It is
owed when Product rules, at which point `record_status` moves off `pending-revision`.

## FR-PLT-004-console-compatibility-baseline — What are the ACR US listing's published compatibility settings in the store consoles?

```yaml
id: FR-PLT-004-console-compatibility-baseline
type: implementation
status: deferred
question: What are the ACR US listing's published compatibility settings in the store consoles?
answer: Deferred pending observation by someone with console access. Owner: PM. Reopened when the availability and device-catalogue settings for the ACR US listing are read in App Store Connect and the Play Console. No value is recorded here — the settings are external state, and guessing one would create a baseline that reads as observed.
decided_by: Omry Dabush
owner: PM
reopens_when: the availability and device-catalogue settings for the ACR US listing are read in App Store Connect and the Play Console
decided_on: 2026-08-27
how: review
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.2
feature: F01.1
affects: [FR-PLT-004]
resolves: [SQ-G]
unblocks: n/a
decided_against: { SPEC-01: Rev1.2, FR-01: Rev1.20, EPIC-01: Rev1.14 }
record_status: n/a
supersedes: n/a
```

**Context** — `AC-11` asks that the compatibility filters published in the store consoles match the ones
the repository declares. Its "published" half is console state, which lives outside every repository and
cannot be read from source: the spec recorded it as a task rather than a question for that reason. Until
someone opens App Store Connect and the Play Console and reads the availability and device-catalogue
settings for the ACR US listing, `AC-11` has a declared side and no published side to compare it against.

Nothing in the repositories substitutes for the observation. QACR declares no compatibility filters at
all today (`Quant/Info.plist` carries only `UIAppFonts`), and ACR's declarations
(`iosDip/Dip/TargetFiles/Acr/MinutefulKidneyUS/ACR-Minuteful-US-Info.plist:59-65`,
`AndroidDip/app/src/main/AndroidManifest.xml:24-35`) are the *declared* side of the same comparison, not
the published one.

**Decision** — Deferred. Owner: **PM**, who can reach or route console access; the row had no owner
before, which is what made it liable to be re-raised each round rather than done. Reopened when the
settings are read.

Typed `implementation` rather than `product`: the answer is an observation that becomes `AC-11`'s test
baseline, and no requirements or brief revision is owed by it — hence `record_status: n/a`. Should the
observed settings contradict the declared filters, that contradiction is a new finding and gets its own
entry.

`AC-11` verifies against the baseline whenever it arrives; it remains a manual criterion either way,
since a store console's state is not assertable from inside the app.

## FR-RDY-005-connectivity-read-location — Where does a connectivity read that can actually fail live, given the shared package's is defective?

```yaml
id: FR-RDY-005-connectivity-read-location
type: architectural
status: accepted
question: Where does a connectivity read that can actually fail live, given the shared package's is defective?
answer: A new, correct connectivity API is added to ios-foundations alongside the existing one; internetReachable is left untouched and QACR consumes the new API. Additive, so no existing consumer's behaviour changes. Deprecating or removing internetReachable is deliberately not decided here.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-005]
resolves: [SD-1]
unblocks: [AC-RDY-07, AC-RDY-08]
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03, ios-foundations: cf743d568999 }
record_status: n/a
supersedes: n/a
```

**Context** — FR-RDY-005 is dispositioned `as-is`, meaning the current product is the specification.
But iOS's connectivity check cannot fail: `ios-foundations`' `NetworkManager.internetReachable`
initialises `true`, and its only assignment to `false` sits behind a guard that passes only when the
value is already `false`, so the `.noNetwork` branch is unreachable dead code. The QACR app pins a
revision carrying the byte-identical defect (`cf743d568999`, 7.1.6). There is therefore no working
prior art to recreate, and AC-RDY-08 exists precisely to prove a `true`→`false` transition is
observed.

The first framing of this decision was to repair `internetReachable` in place. That was rejected on
the contract's own consumer rule: *"In a repository serving more than one product: additive only.
Existing behaviour and existing consumers are untouched … If the requirement cannot be met
additively, that is a stop."* Repairing it in place is not additive — it wakes `.noNetwork` branches
that are currently dead in every other product on `ios-foundations`, whose behaviour under a genuinely
lost connection has never run.

**Decision** — Add a correct connectivity API to `ios-foundations` beside the broken one and have QACR
consume it. This meets the requirement without changing any existing consumer, so the additive-only
rule is satisfied and its stop does not apply. `internetReachable` stays as it is; whether it is
deprecated, fixed or removed is a separate decision for whoever owns the other consumers, and is not
taken here. Blast radius still to be checked with `/mind` before code lands, per the same rule.

**Alternatives considered** — *Repair `internetReachable` in place*: one fix, every consumer benefits,
and the defect stops propagating — but it is a behaviour change to products that have never exercised
the path, which the additive-only rule makes a stop rather than a trade-off. *Implement the read
privately inside QACR*: fully additive and the smallest blast radius, but it leaves the shared defect
in place with a second implementation beside it, and the next consuming app repeats the discovery.

## FR-RDY-006-backend-reachability-definition — What counts as "the backend server is reachable", and is a probe endpoint needed?

```yaml
id: FR-RDY-006-backend-reachability-definition
type: product
status: deferred
question: What counts as "the backend server is reachable", and is a probe endpoint needed?
answer: Deferred. No probe exists on either platform and the backend architecture defines no health or reachability endpoint, so the mechanism cannot be settled inside this repository. Reopened when a reachability mechanism is defined — either the backend exposes an endpoint, or Product rules that an existing authenticated call standing in is sufficient.
decided_by: Omry Dabush
owner: PM + backend
reopens_when: a reachability mechanism is defined — a backend endpoint is exposed, or Product rules that an existing authenticated request succeeding at initiation is the definition
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-006]
resolves: [SD-2]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — FR-RDY-006 is dispositioned `as-is`, but neither platform probes the backend. Both infer
reachability from whether the app-settings fetch completed, an indirect signal that may be minutes
stale by the time the user taps start, so there is no prior art to recreate. The backend architecture
that landed in `qacr-spec` at `fb13f8b` was checked against this question: `architecture/spine.md` and
`architecture/spine-decision-log.md` define no health, liveness or reachability endpoint. The nearest
statement is a line in `architecture/QACR-Software-Cybersecurity-Considerations.md` that notifications
and offline behaviour should not depend on the backend being reachable — which concerns the
notifications worker, not the pre-test gate.

**Decision** — Deferred to PM and backend jointly. The requirement's *intent* is not in doubt and the
spec specifies the mechanism-independent half of it; what cannot be defaulted is what the app should
call, and inventing that here would commit the backend to work nobody has agreed. AC-RDY-09 and
AC-RDY-10 stay written and unproven until this lands.

**What the document must say** — FR-RDY-006 needs a sentence naming the mechanism once chosen, e.g.:
"Backend reachability is established by <named mechanism> immediately before test initiation. A cached
result from an earlier application-settings fetch does not satisfy this requirement."

## FR-RDY-008-storage-threshold-ownership — Is the note's app-fixed storage threshold a departure the brief owes, or intent nobody recorded?

```yaml
id: FR-RDY-008-storage-threshold-ownership
type: product
status: deferred
question: Is the note's app-fixed storage threshold a departure the brief owes, or intent nobody recorded?
answer: Deferred. Only the PM can say whether their own note prescribed a change. Reopened when the PM rules either that the brief owes a departure row for an app-fixed threshold, or that the note describes intent that was never adopted and the threshold stays configuration-supplied.
decided_by: Omry Dabush
owner: PM
reopens_when: the PM rules whether FR-RDY-008's note is a departure the brief owes a D-row for, or intent nobody adopted
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-008]
resolves: [SD-3]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — FR-RDY-008's `note` in `product/FR-01/requirements.json` reads, verbatim: "Threshold TBD,
and fixed in the application rather than configuration-supplied. Unlinked from
staticData.lowDiskSpaceSize at review". That prescribes a change, and QACR-APP-SPEC-01 Rev 1.4 declares
no departure for this requirement while stating that everything outside its departures table is
recreated as-is. Prior art contradicts the note directly: the threshold is server-supplied on both
platforms, delivered by the init/flow-configuration response, with only a client-side fallback (iOS
`80`, Android `100L`). `/mind` traced the backend side to a per-partner Postgres value behind
`GET /flow-configuration` rather than a literal `staticData.lowDiskSpaceSize` key, so the note may name
a renamed or different backend concept than what ships. `architecture/data_model.md` and
`architecture/spine.md` at `fb13f8b` mention neither `flow-configuration` nor any client threshold.

This is the finding the exhaustive note pass exists for. Its sibling proves why: FR-RDY-007's note has
the same shape — "Threshold TBD; fixed in the application, not configurable" — and resolves the
opposite way, because ACR genuinely hardcodes the battery minimum. Neither note contradicts its
requirement's text, so a run scanning for conflicts rather than enumerating would have missed both, and
a run that spot-checked had even odds of picking the inert one.

**Decision** — Deferred to the PM. The requirement's text is agnostic about where the value comes from,
so the spec builds a single threshold seam and states the criterion as a threshold; the answer changes a
provider rather than call sites either way. What is not defaultable is whether a departure row is owed,
because that is a claim about the brief's own completeness.

**What the document must say** — one of two, depending on the ruling. If a departure was intended,
QACR-APP-SPEC-01 needs a new departures row: "| Dn | F01.4 | The available-storage minimum is fixed in
the application rather than supplied by configuration. | FR-RDY-008 |". If it was not, FR-RDY-008's
note should be corrected to drop "fixed in the application rather than configuration-supplied" and the
`staticData.lowDiskSpaceSize` reference, which names a key the backend does not serve.

## FR-RDY-007-threshold-boundary-inclusivity — Is "at or above the defined minimum threshold" inclusive as written, when prior art blocks at the threshold?

```yaml
id: FR-RDY-007-threshold-boundary-inclusivity
type: product
status: deferred
question: Is "at or above the defined minimum threshold" inclusive as written, when prior art blocks at the threshold?
answer: Deferred. Reading the boundary as written loosens a shipped safety gate by one increment, which needs RA as well as Product. Reopened when PM and RA rule on whether at-threshold permits.
decided_by: Omry Dabush
owner: PM + RA
reopens_when: PM and RA rule on whether a device exactly at the minimum may start a test
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-007, FR-RDY-008]
resolves: [SD-4]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — FR-RDY-007 and FR-RDY-008 both say "at or above the defined minimum threshold". Prior art
blocks *at* the threshold on both platforms and for both conditions, so the shipped behaviour is
strictly narrower than the requirements' words: a device sitting exactly on the minimum is blocked today
where the requirement says it should proceed. One boundary question, two requirements, four criteria.

The question is independent of U1/Q-01 and U1/Q-02: it decides the comparison, not the value, so it
stays answerable while the thresholds themselves are still owed by the IVTS qualification.

**Decision** — Deferred to PM and RA jointly. Following the requirement's words is the spec's default
and remains what AC-RDY-13 and AC-RDY-17 assert, but adopting it widens the set of devices permitted to
start a test, and a change to a shipped safety gate is RA's to confirm rather than a reading a spec can
settle on its own.

**What the document must say** — if the boundary is inclusive as written, no change is needed and this
entry records the confirmation. If blocking at the threshold is correct, both requirements need their
wording changed from "at or above the defined minimum threshold" to "above the defined minimum
threshold", in FR-RDY-007 and FR-RDY-008 alike.

## FR-RDY-009-camera-start-failure-feedback — Does "a camera that fails to start blocks" mean prevented from proceeding, or actively stopped with feedback?

```yaml
id: FR-RDY-009-camera-start-failure-feedback
type: product
status: accepted
question: Does "a camera that fails to start blocks" mean prevented from proceeding, or actively stopped with feedback?
answer: Actively stopped with feedback. The user must be told and given a route onward; being unable to proceed because a screen never advances does not satisfy it.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-009]
resolves: [SD-5]
unblocks: [AC-RDY-05]
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — QACR-APP-SPEC-01 Rev 1.4 records this as already settled, in its Confirmed-as-is table:
"Is a camera that fails to start recoverable? **No — it blocks.** The user cannot proceed with the
flow." The extraction found that answer holds on only one platform. On Android the flow genuinely stops
with feedback. On iOS the user cannot proceed only because the screen never advances: the camera's
completion closure is success-only, so the stage stays `.initial`, the preview stays at `alpha 0`, and
the `errorView` is unreachable — a blank screen that neither advances nor explains. The contract records
this confirmed-as-is answer as AMBIGUOUS rather than holding, which is why it reached the spec as a
decision despite the brief calling it closed.

FR-RDY-009's own text requires only that the software "shall not permit the user to proceed" — it does
not require a message. So demanding feedback goes beyond the requirement, which is what made this a
decision rather than a default.

**Decision** — "Blocks" means actively stopped with feedback. A user whose camera fails to start is told
and given a route onward. iOS's current blank-screen behaviour does not satisfy FR-RDY-009 as now read,
and is listed in the spec's Boundaries as a `do_not_copy` finding. The presentation is settled
separately in `FR-RDY-009-camera-start-failure-presentation`.

**What the document must say** — FR-RDY-009 needs its blocking clause extended, e.g. append: "Where the
user is not permitted to proceed, the software shall present an explanation of why and a route onward.
Preventing progress by leaving the user on a screen that neither advances nor explains does not satisfy
this requirement." The brief's Confirmed-as-is row should also be qualified, since as recorded it reads
as settled for both platforms when it describes only Android.

## FR-RDY-010-scope-of-all-readiness-checks — Does "all readiness checks" mean every condition in the gate, or only those F01.4 owns?

```yaml
id: FR-RDY-010-scope-of-all-readiness-checks
type: product
status: deferred
question: Does "all readiness checks" mean every condition in the gate, or only those F01.4 owns?
answer: Deferred. Reopened when the PM rules on the scope of "all" — whether it reaches conditions owned by F01.5 and F01.9, or is confined to the five this feature owns.
decided_by: Omry Dabush
owner: PM
reopens_when: the PM rules on the scope of "all readiness checks", or F01.5 and F01.9 are specified, whichever comes first
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-010]
resolves: [SD-6]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — FR-RDY-010 is one sentence: "The software shall re-evaluate all readiness checks
immediately before test initiation, and not only at application start-up." "All" is untrue on both
platforms today — order and block-flow eligibility is served from a value cached at the last lobby-load
and never re-validated at the tap. The scoping question is what "all" should reach. The readiness gate in
the current product also enforces conditions this feature does not own: kits exceeded, a recent previous
test, demonstration-mode warnings, order eligibility. A wide reading puts F01.4 in charge of
re-evaluating conditions belonging to F01.5 (blocked-state pattern) and F01.9 (run-time configuration),
neither of which is specified yet.

**Decision** — Deferred to the PM. The spec proceeds on its Assumption 8 — only the conditions this
feature owns — and AC-RDY-19 is written to that scope, because the wider reading would make F01.4 depend
on two unspecified features. The assumption is recorded and approved with the spec, so the build is not
blocked; what is deferred is whether the requirement means more than the spec assumes.

**What the document must say** — FR-RDY-010 should name its own scope rather than leaving "all" to the
reader, e.g.: "…shall re-evaluate all readiness checks it owns…" if narrow, or an explicit enumeration
of the conditions in scope if wide.

## FR-RDY-008-ios-storage-check-independence — Does iOS build the storage check as specified regardless of Android's non-firing implementation?

```yaml
id: FR-RDY-008-ios-storage-check-independence
type: implementation
status: accepted
question: Does iOS build the storage check as specified regardless of Android's non-firing implementation?
answer: Yes. iOS implements the check against the requirement's text. Android's defect is reported to that team, not inherited, and does not change what iOS builds.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-008]
resolves: [SD-7]
unblocks: [AC-RDY-16]
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: n/a
supersedes: n/a
```

**Context** — Android's storage check cannot fire at all. `IsDiskFullUseCase` computes `total − usable`,
which is space *used* rather than available, and compares it against a threshold of `100` in raw bytes
where iOS treats the same value as MB. On any real device the comparison is false, so the check never
triggers — and its three unit tests pass because they share the inversion, which is how it shipped. The
requirement is dispositioned `as-is`, so this decides whether iOS is recreating a working check, in which
case prior art is the specification, or writing a new one, in which case the requirement's text is the
only guide. The two produce different work.

This is the second, independent gap on FR-RDY-008; the first is
`FR-RDY-008-storage-threshold-ownership`, which concerns where the threshold value comes from and stays
deferred. This entry settles the comparison, not the value, and the two do not block each other.

**Decision** — iOS builds the check against the requirement's text: the quantity compared is space
available to the app, in one documented unit. Android's inversion is reported to that team and is not
inherited. The spec's Boundaries keep the two matching `do_not_copy` rules in force — never compute
available storage as `total − usable`, and never write tests that encode a check's misreading — so the
defect cannot be recreated by following prior art.

## FR-RDY-008-unreadable-condition-disposition — When a readiness condition cannot be read at all, does the gate fail closed or fail open?

```yaml
id: FR-RDY-008-unreadable-condition-disposition
type: product
status: deferred
question: When a readiness condition cannot be read at all, does the gate fail closed or fail open?
answer: Deferred for storage, connectivity and backend. Battery is already settled the other way by the brief — an unreadable battery level proceeds — so the answer must be given per condition rather than once. Reopened when PM and RA rule.
decided_by: Omry Dabush
owner: PM + RA
reopens_when: PM and RA rule on whether an unreadable storage, connectivity or backend condition blocks
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-005, FR-RDY-006, FR-RDY-008]
resolves: [SD-8]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — The requirements are silent on what should happen when a condition cannot be read at all: a
storage query that throws, a connectivity reader that errors, a backend probe that neither succeeds nor
cleanly fails. Silence is not a decision, and the directions are opposites — fail closed blocks a possibly
ready user, fail open admits a possibly unready one into a ten-minute test.

One half is already settled and points the other way. QACR-APP-SPEC-01 Rev 1.4 records, verbatim: "What
happens when the battery level cannot be read at all? **The test proceeds**, as today." The extraction
confirms that answer holds on both platforms. Prior art also fails closed for storage on both platforms,
but nobody recorded that as intended, so it is observed behaviour rather than a decision. The result is
that battery is settled fail-open while storage, connectivity and backend are unsettled with prior art
pointing fail-closed.

**Decision** — Deferred to PM and RA jointly, for the same reason as
`FR-RDY-007-threshold-boundary-inclusivity`: this decides when a safety gate admits someone. The spec's
default stands in the meantime — fail closed for storage, connectivity and backend, fail open for battery
per the recorded answer — and AC-RDY-18 asserts that a failed storage read does not silently permit the
test.

**What the document must say** — the requirements need an explicit statement, e.g. added once to section
5: "Where a readiness condition cannot be evaluated, the software shall prevent the test from starting,
except for battery level, where the test proceeds." Wording depends on the ruling; what matters is that
the silence is closed rather than left to each implementation.

## FR-RDY-007-minimum-battery-level — What is the minimum battery level a device must have to start a test?

```yaml
id: FR-RDY-007-minimum-battery-level
type: product
status: deferred
question: What is the minimum battery level a device must have to start a test?
answer: Deferred pending U1/Q-01, the minimum battery level owed by the IVTS device qualification. No value is chosen. Evidence for whoever sets it: prior art enforces 5% on both platforms while telling the user 10%.
decided_by: Omry Dabush
owner: Guy · IVTS device qualification
reopens_when: U1/Q-01 lands — the minimum battery level owed by the IVTS device qualification
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-007]
resolves: [U1/Q-01]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — U1 in QACR-APP-SPEC-01 Rev 1.4 withholds four values, owner "Guy · IVTS qualification", of
which Q-01 is the minimum battery level. The brief attaches its open items to no requirement ids, so the
join to FR-RDY-007 is a reading rather than a record. AC-RDY-11 and AC-RDY-13 state the condition as a
threshold naming Q-01 and choose no number, so the mechanism is fully specified and testable the moment a
value lands.

This entry exists because the log already carries two F01.1 entries deferred on U1/Q-04 — the same
register, the same owner — while this feature's dependency on Q-01 and Q-02 was recorded nowhere, so
`qacr-context` could see F01.1 waiting on IVTS but not F01.4.

**Decision** — Deferred to the IVTS device qualification, no value chosen here. Evidence for whoever sets
it: prior art enforces 5% on both platforms while the user-facing content says 10% — a discrepancy the
spec's Boundaries already forbid recreating.

**What the document must say** — U1/Q-01 resolves into FR-RDY-007 as a stated value, replacing "the
defined minimum threshold" with the qualified minimum, or leaving the requirement agnostic and recording
the value wherever thresholds are held.

## FR-RDY-008-minimum-available-storage — What is the minimum available storage a device must have to start a test?

```yaml
id: FR-RDY-008-minimum-available-storage
type: product
status: deferred
question: What is the minimum available storage a device must have to start a test?
answer: Deferred pending U1/Q-02, the available-storage minimum owed by the IVTS device qualification. No value is chosen. Evidence for whoever sets it: iOS falls back to 80 and Android to 100L, and the production value is a per-partner backend field.
decided_by: Omry Dabush
owner: Guy · IVTS device qualification
reopens_when: U1/Q-02 lands — the available-storage minimum owed by the IVTS device qualification
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-008]
resolves: [U1/Q-02]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — U1/Q-02 is the available-storage minimum, same open item and same owner as Q-01. AC-RDY-15
and AC-RDY-17 name it and choose no number. Recorded for the same reason as
`FR-RDY-007-minimum-battery-level`: to make this feature's dependency on the IVTS qualification visible to
the next `qacr-context` run rather than implicit in the brief's U1 row.

Note this is the value question only. Whether the threshold is app-fixed or configuration-supplied is a
separate deferred decision, `FR-RDY-008-storage-threshold-ownership`, and the two are independent — a
value can land while its delivery mechanism is still open, and the spec's threshold seam is built so
either answer changes a provider rather than call sites.

**Decision** — Deferred to the IVTS device qualification, no value chosen here. Evidence: iOS falls back
to `80` and Android to `100L` — in different units — and the production value is a per-partner Postgres
field behind `GET /flow-configuration`, which the app cannot read at rest.

**What the document must say** — U1/Q-02 resolves into FR-RDY-008 as a stated value with an explicit
unit, since the two platforms' fallbacks disagree about the unit today.

## FR-RDY-010-backend-freshness-window — Does the backend enforce a freshness window on the configuration and order state the readiness gate reads?

```yaml
id: FR-RDY-010-backend-freshness-window
type: product
status: deferred
question: Does the backend enforce a freshness window on the configuration and order state the readiness gate reads?
answer: Deferred. Not answerable from the application — the app cannot observe a server-side freshness rule. Reopened when the backend states whether such a window exists and what it is.
decided_by: Omry Dabush
owner: Backend + PM
reopens_when: the backend states whether a freshness window applies to the configuration and order state the gate reads, and what it is
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-010]
resolves: [SQ-A]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — Raised by the spec as an open question rather than a decision, classified
`not_derivable/backend`: `/mind` traced it and it survived the trace, meaning the answer is genuinely
invisible from inside the app. It bears on FR-RDY-010 because if the backend already enforces a freshness
window on the state the gate reads, the client's re-evaluation obligation may be narrower than the
requirement's "all" implies.

**Decision** — Deferred to backend and PM jointly. It is recorded rather than left in the spec alone
because it is a question someone can actually answer — unlike the observation tasks in this feature's
remaining open questions — and because it interacts with
`FR-RDY-010-scope-of-all-readiness-checks`, which is also open.

**What the document must say** — nothing yet. If a freshness window exists, FR-RDY-010's re-evaluation
obligation should say how it relates to it, so the client is not re-proving something the server
guarantees.

## FR-RDY-009-camera-start-failure-presentation — How is a camera that fails to start presented to the user?

```yaml
id: FR-RDY-009-camera-start-failure-presentation
type: implementation
status: accepted
question: How is a camera that fails to start presented to the user?
answer: A simple native alert. The PM will refine its content; wording itself is outside spec scope and lives in the content set.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-009]
resolves: [SQ-C]
unblocks: [AC-RDY-05]
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: n/a
supersedes: n/a
```

**Context** — SQ-C was raised as an observation task: what iOS actually displays while stuck on a failed
camera start, classified `not_derivable/needs-a-run`. Its purpose was to gather evidence for SD-5, which
is now settled by `FR-RDY-009-camera-start-failure-feedback` as stop-and-explain. That answer requires
*something* to be presented, so the presentation became a decision rather than an observation.

**Decision** — A simple native alert. This pairs with the stop-and-explain answer to close the
camera-start-failure path end to end: the user is stopped, and told, through the platform's own alert
rather than a bespoke surface. The PM will refine the alert's content. Per QACR-APP-SPEC-01 Rev 1.4
section 6 — "no spec states, constrains or enforces user-facing wording" — that refinement is not a spec
concern and belongs to the content set, which is why this entry is `implementation` and owes no document
revision.

The existing iOS permission alert is not a model to copy: the spec's Boundaries record that its button
"reads like an in-app retry but always leaves for system Settings", and that an action must never be
labelled for what it is not.

## FR-RDY-009-repeat-permission-request-ui — Does a repeat AVCaptureDevice.requestAccess show system UI?

```yaml
id: FR-RDY-009-repeat-permission-request-ui
type: implementation
status: accepted
question: Does a repeat AVCaptureDevice.requestAccess show system UI?
answer: Yes. Recorded as answered; NOT YET OBSERVED ON A DEVICE — see Context, which records that Apple's documented behaviour differs and that AC-RDY-04 carries a verify-before-build note.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-009]
resolves: [SQ-D]
unblocks: [AC-RDY-04]
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03, ios-camera: b59561e7 }
record_status: n/a
supersedes: n/a
```

**Context** — The spec raised this as `not_derivable/binary` with an explicit instruction: "A task:
observe on a device." It matters because AC-RDY-04 requires a refused camera permission to offer the user
a route to grant it, and whether that route can be an in-app re-prompt or must be a trip to system
Settings depends on this answer.

**This entry is recorded as answered but was not answered by observation, and the recorded answer runs
against Apple's documented behaviour.** `AVCaptureDevice.requestAccess(for:)` prompts only on the first
call for a given media type; once a decision is stored, later calls return it without presenting UI. The
current product's own behaviour is consistent with the documented reading rather than this entry's: iOS's
permission alert always leaves for system Settings, and the spec's Boundaries carry that as a
`do_not_copy` finding precisely because the button "reads like an in-app retry" while never being one.

Recorded as given, with the divergence stated, so that whoever builds AC-RDY-04's route-to-grant checks
it on a device first rather than inheriting an unverified premise. If observation contradicts it, this
entry is superseded by appending a new one — not edited.

**Decision** — Yes, as answered. Carried with the verification caveat above; AC-RDY-04 gains a
verify-on-device note in the spec rather than being built directly on this.

## FR-RDY-007-zero-percent-battery-disposition — At an exact 0% battery reading, does the test block or proceed?

```yaml
id: FR-RDY-007-zero-percent-battery-disposition
type: implementation
status: accepted
question: At an exact 0% battery reading, does the test block or proceed?
answer: Block. A 0% reading is a readable value below any minimum, and is not to be treated as an unreadable level.
decided_by: Omry Dabush
owner: n/a
reopens_when: n/a
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-007]
resolves: [SQ-E]
unblocks: [AC-RDY-22]
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: n/a
supersedes: n/a
```

**Context** — Raised as `not_derivable/needs-a-run` — whether an exact 0% reading is even reachable on a
real device — and it mattered because prior art diverges there: iOS blocks at 0% while Android proceeds,
because Android conflates a 0% reading with an unreadable one.

The answer interacts with a recorded confirmed-as-is answer pointing the other way. The brief settles
that an unreadable battery level proceeds, and the extraction confirms that holds on both platforms. So
blocking at 0% while proceeding on unreadable requires the implementation to **distinguish the two** —
which is exactly what Android fails to do.

**Decision** — Block at 0%. A 0% reading is a value, not the absence of one, and it is below any minimum
Q-01 could set. Consequently the build must treat "level unavailable" and "level is zero" as distinct
states, and the spec gains a criterion asserting it: AC-RDY-22, which this entry unblocks. Android's
conflation of the two is a `do_not_copy` finding rather than behaviour to recreate.

Whether 0% is reachable on real hardware remains unobserved and is no longer blocking: the disposition
holds whether or not the reading occurs, and a state that cannot arise simply never fires.

## FR-RDY-010-lobby-dwell-time — How long do users typically sit on the lobby before tapping start?

```yaml
id: FR-RDY-010-lobby-dwell-time
type: product
status: deferred
question: How long do users typically sit on the lobby before tapping start?
answer: Deferred. Reopened when Product supplies dwell-time data, or rules that the re-evaluation obligation does not depend on it.
decided_by: Omry Dabush
owner: PM
reopens_when: Product supplies lobby dwell-time data, or rules that FR-RDY-010's re-evaluation obligation does not depend on it
decided_on: 2026-09-01
how: chat
recorded_by: Claude Code (agent session), for Omry Dabush
product: QACR
spec: QACR-APP-SPEC-01 Rev1.4
feature: F01.4
affects: [FR-RDY-010]
resolves: [SQ-F]
unblocks: n/a
decided_against: { SPEC-01: Rev1.4, FR-01: Rev1.24, EPIC-01: Rev1.18, qacr-spec: fb13f8b, urine.com.ios-qacr-app: 6814fb64, iosDip: e0636af3, AndroidDip: a50d8b03 }
record_status: pending-revision
supersedes: n/a
```

**Context** — Raised as `not_derivable/needs-a-run`: how stale a cached readiness verdict actually gets
before the user taps start. It informs how much weight FR-RDY-010's re-evaluation obligation carries, and
therefore bears on `FR-RDY-010-scope-of-all-readiness-checks`, which is also deferred to the PM.

**Decision** — Deferred to the PM. It does not block the build: AC-RDY-19 and AC-RDY-20 require
re-evaluation at the tap regardless of how long the user waited, so a short dwell time would not license
caching. The data would inform how the requirement is argued, not what the spec asserts.

**What the document must say** — nothing. Recorded so the question is owned rather than re-raised; if
Product rules the obligation is independent of dwell time, this entry is superseded by that ruling.
