# P0 — packages/modules/Permission, AOSP17 source review

**Date:** 2026-11-03. **Device target:** mondrian only. **Status:** exact AOSP17 tree imported and verified; no legacy PE patch accepted, full Android module build and CTS/VTS not run.

## Official source identity

- Google tag: https://android.googlesource.com/platform/packages/modules/Permission/+/refs/tags/android-17.0.0_r1
- Annotated release tag: `a80cd71366023b782a5180c0418ca4624605a932`
- Official release commit: `1093eca7407576c72e51b1a88550ee0667a6e5dc`
- Git tree: `5f0dfec33529cfff7ad08c9e61f480e445a59d8b`.
- Verified GitHub [source snapshot `f6e6e14b5c4d6e094c205683940a1328384338d9`](https://github.com/PixelExperience-Reborn/packages_modules_Permission/commit/f6e6e14b5c4d6e094c205683940a1328384338d9) has an identical tree, confirmed independently via Git API. The snapshot has **no original Google commit ancestry** (it is a root commit). Historical PE Android14 `seventeen` remains untouched.
- [Import GitHub Actions #41714168389](https://github.com/PixelExperience-Reborn/packages_modules_Permission/actions/runs/41714168389) **passed**.

## Old PixelExperience changes reviewed against exact AOSP17

| Old change | Observed AOSP17 behavior | Decision |
| --- | --- | --- |
| [`cecdb11b`](https://github.com/PixelExperience-Reborn/packages_modules_Permission/commit/cecdb11b278c53ef9276f0206c6a3bc95a30f9c8) — prevent notification-access grants to work profile companion apps | AOSP17 has moved companion role behaviors into versioned `behavior/v31`, `v33` and `v34` packages. All four reviewed watch/computer/app-streaming/glasses classes use `UserUtils.isManagedProfile(user, context)` to guard `grantNotificationAccessForPackageAsUser` and revoke. | **Already in AOSP17.** Do not reapply Android14 patch. |
| [`6377f6fa`](https://github.com/PixelExperience-Reborn/packages_modules_Permission/commit/6377f6fa01226a28d3aa8d2e2884fec24e4b2972) — timeline for additional permission groups | AOSP17 `PermissionUsageControlPreferenceUtils.kt` currently limits `SENSOR_DATA_PERMISSIONS` in this UI to Location, Camera and Microphone; old PE enabled many others. Metrics, discrete history collection and permission group presentation may have changed. | **Defer** until the Android17 storage, app-op events, stats and UI/CTS contract are reviewed. Do not enable timelines with missing data. |

This is a review of selected meaningful historical commits, **not a comprehensive range-diff** of every old PE merge/translation.

## Manifest integration

- [`aosp17_pe_p0_permission.xml`](../aosp17_pe_p0_permission.xml) extends the Connectivity P0 profile, replaces only `packages/modules/Permission`, and pins snapshot SHA `f6e6e14b5c4d6e094c205683940a1328384338d9`. No product source change and no direct permission code delta.
- [CI source-sync](../.github/workflows/aosp17-p0-permission-source-sync.yml) will verify pinned HEAD and Git tree after real Linux checkout and assert the four AOSP17 managed-profile role guards are still present.
- Joint selected-source CI now targets 14 pinned P0 projects; its result must be checked, not presumed.
- Do not ship debug/test APEX keys from the AOSP tree as release signing credentials. Release key management, signing and module compatibility remain separate requirements.

**Outstanding:** Android17 complete Soong build, permission APEX/application compile, SELinux and role behavior, CTS/VTS/AppOps, integration with system services and actual on-device permission behavior on mondrian.
