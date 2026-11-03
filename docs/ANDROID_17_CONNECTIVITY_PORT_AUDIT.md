# P0 — packages/modules/Connectivity: AOSP 17 review

**Date:** 2026-11-03. **Device target:** POCO F5 Pro / Redmi K60 (`mondrian`) only.

**Current state:** official AOSP17 source tree imported and independently verified, with **zero PE functional modifications**. Historical PE Android14 `seventeen` remains unchanged. Manifest graph/source-sync acceptance is pending; Android module compilation and device tests have not run.

## Reproducible AOSP17 source

- Official Google source: https://android.googlesource.com/platform/packages/modules/Connectivity/+/refs/tags/android-17.0.0_r1
- Annotated tag: `8c2d0c1aca489c526227ed7a061308184d8c87eb`.
- Peeled source commit: `347fbd34b368d19f0d87e908ea101eed3601a731`.
- Exact Git tree: `3a9df5486bd2b0d48cf22a4df8b8e097d36da07d`.
- Target source branch: `port/a17-connectivity-aosp17-base-20261103`; do not assume this branch exists before checking GitHub Git API.
- [Import workflow](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/blob/port/a17-connectivity-import-20261103/.github/workflows/aosp17-connectivity-import.yml) verifies both SHAs before publishing a new root snapshot with the exact AOSP file tree. Such a snapshot has a different commit SHA and **does not carry full original Google commit ancestry**. It cannot overwrite an existing mismatched branch and never force-pushes.

## Historical PE behavior compared with exact AOSP17 files

| Old PE commit | AOSP17 source observation | Port decision |
| --- | --- | --- |
| [`dccdf9ac`](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/commit/dccdf9ac2c577131109770b7d762f23f787d3045) — turn off noisy `TrafficStats.SocketTagger.LOGD` | AOSP17 `framework-t/src/android/net/TrafficStats.java` already declares `private static final boolean LOGD = Log.isLoggable(TAG, Log.DEBUG);` with documented runtime log-level control. | **Reject duplicate.** Preserve debug observability; no unconditional `LOGD=false`. |
| [`407a3172`](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/commit/407a31721e252ec68bad12a609d8b6a4671edc3f) — disable DUN tethering requirement | AOSP17 `Tethering/src/com/android/networkstack/tethering/TetheringConfiguration.java` still reads the active `TelephonyManager.isTetheringApnRequired()` to select the proper upstream. | **Reject blanket bypass.** Cellular operator configuration and downstream behavior are relevant for mondrian; any exception requires explicit carrier/device proof. |
| Other historical changes (not yet exhaustively compared) | Historical `seventeen` is Android14-era with extensive translations and AOSP merges. | **No assumptions.** Review any subsequently discovered unique PE delta individually; never merge the old history. |

The comparison reads exact AOSP17 commit `347fbd34...` through a public Git mirror; commits refer to the original old PE fork. This is an initial functional review, **not** a full history range-diff.

## Acceptance gates

1. Confirm GitHub CI publication, remote branch existence and exact Git tree `3a9df548...` independently via Git API; do not confuse root snapshot SHA with Google's original source commit.
2. Prefer the unmodified AOSP17 source if no justified PE feature remains. A fork alone is not evidence a patch is needed.
3. If a reviewed source ref is selected, add an **opt-in** P0 manifest profile including the previous Bluetooth graph and pinning only the Connectivity project. Run manifest parser and Linux targeted `repo sync` with commit checks.
4. Full selected-project sync must prove all HEAD values match immutable revisions. Then validate AOSP17 `framework-connectivity`/NetworkStack/Tethering module compilation, related APEX and host tests. The exact build targets must be discovered from current Android.bp, not assumed from Android14.
5. Finally test mobile data, APN selection, DUN/tethering, network switching, VPN, Private DNS, IPv4/IPv6, Wi-Fi and cellular on real mondrian; run relevant CTS/VTS suites.

**No success claim:** full 1069-project sync, platform/Soong build, APEX, hardware test, OTA and device boot remain unverified.

## Exact snapshot and opt-in source integration (2026-11-03)

- [Connectivity source import #41713047058](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/actions/runs/41713047058) **passed**. GitHub Git API independently confirms snapshot commit `701882b51546230c6c32c9654a3f7b9814429e13` has exact official tree `3a9df5486bd2b0d48cf22a4df8b8e097d36da07d`, with zero parents. It is not the original Google commit, only the identical file tree.
- [`aosp17_pe_p0_connectivity.xml`](../aosp17_pe_p0_connectivity.xml) includes the previously reviewed Bluetooth profile and replaces only `packages/modules/Connectivity` at `701882b51546230c6c32c9654a3f7b9814429e13`. The historical default manifest remains unchanged.
- The [dedicated source CI](../.github/workflows/aosp17-p0-connectivity-source-sync.yml) will check exact pinned HEAD and tree after Linux `repo sync`, and enforce that AOSP17 dynamic socket debug logging and `TelephonyManager.isTetheringApnRequired()` are not overwritten by old PE code. The [joint selected-source CI](../.github/workflows/aosp17-p0-source-sync.yml) now covers thirteen P0 checkouts, pending real execution.
- No draft PR in this source fork because **there is no PE-specific source delta to propose**. Any later justified change should start from this exact source branch, use tests, and get a separate draft PR.

**Still required:** actual full Connectivity/NetworkStack/Tethering build and tests, other complete AOSP17 framework dependencies, tethering/APN cellular tests on mondrian, and complete product build.

- **Validation result:** [Connectivity selected source CI #41713844857](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41713844857) and [12-profile structure CI #41713844911](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41713844911) **passed**. The combined 13-project source sync is a separate acceptance gate and was still executing at the last check.

- [Joint 13-project source sync #41713844843](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41713844843) **passed**, including pinned source and checks that the AOSP17 dynamic TrafficStats debug flag and DUN carrier policy are retained. This is not a compiled NetworkStack or on-device tethering test.
