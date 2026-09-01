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
