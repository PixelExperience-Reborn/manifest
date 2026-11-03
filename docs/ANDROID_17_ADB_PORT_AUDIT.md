# P0 — packages/modules/adb Android17 migration and authorization review

**Date:** 2026-11-03. **Target:** POCO F5 Pro / Redmi K60 (mondrian) only.

**Status:** exact AOSP17 release source imported with **zero PE code delta**. Git tree and import workflow PASS. Linux repo sync, native build and device tests are separate gates.

## Source identity

- Official AOSP [tag `android-17.0.0_r1`](https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-17.0.0_r1), tag object `06e96b64ceed143faaa6386a43dc7e0efe53f32d`, commit `9084198a2d4b0f6a0f174260fb42da33485b684d`, exact tree `db70f52edb597631efbba79c00276bb68cb06831`.
- Owned isolated source [root snapshot `6daac89c0d6e395f9ff2a032206a21e04421dc5f`](https://github.com/PixelExperience-Reborn/packages_modules_adb/commit/6daac89c0d6e395f9ff2a032206a21e04421dc5f) has the **same tree** independently confirmed by GitHub Git API. The snapshot's commit SHA differs from Google's and does not preserve full upstream Git history.
- [Import Actions #41719562253](https://github.com/PixelExperience-Reborn/packages_modules_adb/actions/runs/41719562253) PASS. Original `seventeen` Android14 branch unchanged.
- AOSP17 default graph project is `platform/packages/modules/adb` at path `packages/modules/adb`. New [`aosp17_pe_p0_adb.xml`](../aosp17_pe_p0_adb.xml) includes the previously tested WiFi P0 profile and replaces **only** adb at immutable snapshot SHA `6daac89c0d6e395f9ff2a032206a21e04421dc5f`.

## Review of historical PixelExperience changes

| Legacy PE commit | Official AOSP17 state | Decision |
| --- | --- | --- |
| [`9479f069`](https://github.com/PixelExperience-Reborn/packages_modules_adb/commit/9479f06997587f7984c75e61db587ff37c117c50) — `ro.adb.secure.recovery` handling | Google AOSP17 `daemon/main.cpp` still has a deliberate `__ANDROID_RECOVERY__` branch allowing unauthenticated adbd when the boot state is orange or the build is debuggable; the comment documents fastbootd recovery/rescue of corrupted userdata. Non-recovery path uses `ro.adb.secure` as before. The PE patch changes this decision to a property-derived value, so both rescue availability and authorization semantics may change with product/boot props. | **Defer pending threat-model and device-specific compatibility tests.** Do not introduce a new security-affecting property without deciding a stable default and verifying rescue usability, locked vs unlocked bootloaders, user/userdebug variants and fastbootd. |

This is a targeted review of selected historical platform-specific PE changes, **not an exhaustive range-diff** of all old commit ancestry.

## Unmodified AOSP17 security baseline and test scope

- Upstream `daemon/main.cpp` source is immutable under our source snapshot. The new selected-source CI checks both commit SHA and tree SHA, as well as source-level invariants for `ro.boot.verifiedbootstate`, `ro.adb.secure` and `__ANDROID_RECOVERY__` handling.
- These static checks confirm that **upstream source logic has not changed**. They do **not** prove the runtime is secure, because property values, adbd service configuration, SELinux, ADB keys, fastbootd init setup and vendor/boot state are external factors.
- AOSP upstream recovery behavior is not a recommendation to bypass adbd authorization in production. Keep exact policy during platform bootstrap for reproducibility; review recovery policy in isolation after compiling adbd.
- No old `ro.adb.secure.recovery` property changes or authorization bypasses are introduced in the device tree or the manifest by this step.

## Validation gates

1. [Targeted Linux adb source sync](../.github/workflows/aosp17-p0-adb-source-sync.yml): HEAD `6daac89c0d6e395f9ff2a032206a21e04421dc5f`, tree `db70f52edb597631efbba79c00276bb68cb06831`, immutable source/policy checks.
2. [16-project selected-source CI](../.github/workflows/aosp17-p0-source-sync.yml): all earlier P0 checkouts plus adb, with independent SHA checks.
3. Compile actual AOSP17 host/device `adb`, `adbd`, transport, authorization and crypto components with current Soong/Make. Run upstream ADB host/device tests, CTS/VTS where applicable.
4. On mondrian, verify **locked user**, **unlocked user**, **userdebug**, recovery, rescue, fastbootd, adb over USB/TCP, pairing, authorization prompts, USB reconnect, encryption/access control, secure vs insecure boot states and absence of undesired unauthorized shell. Avoid destructive or bricking test sequences.
5. Only after test data and documented security policy: open a separate reviewed PR for any PE-specific recovery change. Do not merge old patch blindly.

**Release blockers:** full 1069 selected-project sync, Soong/Make build, target files, ADB/fastboot recovery integration, AVB, CTS/VTS and mondrian boot tests have not run. Keep the manifest PR in Draft.
