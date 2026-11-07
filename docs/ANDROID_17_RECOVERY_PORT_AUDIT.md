# P0 — bootable/recovery: PixelExperience delta review for Android 17

**Scope:** only PixelExperience-Reborn's Android 17 platform bring-up. The target device after platform validation is POCO F5 Pro / Redmi K60 (`mondrian`). Nothing here validates another device or builds recovery images.

## Verified source identity

- Original PE fork: [`PixelExperience-Reborn/bootable_recovery`](https://github.com/PixelExperience-Reborn/bootable_recovery/tree/seventeen). Default `seventeen` still contains AOSP Android 14-era source and PE history. Do not merge the fork wholesale into Android17.
- Official AOSP release: `platform/bootable/recovery` at `android-17.0.0_r1`.
- Official commit: `080f671785c84ae1ac38797fe1fa7364d158fab4`.
- Official tree SHA: `08502f068321cd5d00b80a189b2362e6b2bbc5da`.
- Imported unchanged full official history: [`port/a17-recovery-aosp17-base-20261103`](https://github.com/PixelExperience-Reborn/bootable_recovery/tree/port/a17-recovery-aosp17-base-20261103). GitHub Actions verified the tag commit, tree and Git objects.
- Independently reviewed working branch: [`port/a17-recovery-pe-20261103`](https://github.com/PixelExperience-Reborn/bootable_recovery/tree/port/a17-recovery-pe-20261103). Official branch remains the clean comparison baseline.

## Reviewed historical PE changes and decisions

| Old PE commit | Change | Android 17 decision |
| --- | --- | --- |
| [`009917da`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/009917da7198) | Show device codename in recovery title | **Adapted**: display nonempty `ro.product.device` after Android Recovery heading, without suppressing AOSP fingerprint lines. See [`50e7b26f`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/50e7b26f65ef5d1e35921d9e0cdebf3a8b9ffcfd) |
| [`1be56e58`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/1be56e5885d6) | Force recovery debug checks to always return true | **Rejected**. Keep AOSP17 `ro.debuggable` gating for recovery and recovery_main |
| [`4fdd614d`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/4fdd614d0385) | Disable OTA signature and downgrade checks | **Rejected**. Keep AOSP17 signature and downgrade verification |
| [`a4931d18`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/a4931d18b4e9) | Disable security-patch-level downgrade check | **Rejected**. Keep AOSP17 SPL downgrade policy |
| [`87cda688`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/87cda6881674) | Preserve spaces in `ui_print` | **Deferred** until the Android17 updater command protocol and newline handling can be verified with tests |
| [`265d8e4a`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/265d8e4adcd2) | Touch rotation | **Deferred** until AOSP17 minui and mondrian touch coordinate behavior can be exercised; do not introduce misaligned recovery touch input |
| [`2ac81ee2`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/2ac81ee20089) | Battery status UI/thread | **Deferred** pending AOSP17 Health HAL, thread lifetime and UI layout review |
| [`dbbe1bce`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/dbbe1bce2eb2) | Vendor QSSI13 DRM graphics changes | **Deferred**: needs AOSP17 DRM API and mondrian display/fence verification, and a license check for imported code |
| [`c087b2fe`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/c087b2febbe2) | fsck logs permissions | **Deferred** until filesystem checker log creation and SELinux/permission ownership are verified |
| [`422ca00e`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/422ca00eed44) | Comma-separated updater device assertions | **Deferred**; no need to loosen package device identity checks for mondrian without actual signed-OTA compatibility evidence |
| [`94c8e6f2`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/94c8e6f27cd5) | PE logo and UI theme assets | **Deferred** until resources, licenses, scaling and UI testing on AOSP17 are available |

This is a **targeted safety review**, not a line-by-line audit of every historical commit. Unreviewed PE patches have not been accepted.

## Additional AOSP17 bug fixed

- AOSP17's `start_recovery` was testing `!GetStage().has_value()` immediately before calling `GetStage().value()`. With absent stage metadata, dereferencing the optional is invalid.
- The working branch now uses a small `recovery::ParseRecoveryStage` helper shared by production code and a standalone C++17 host test. The parser retains the existing AOSP `current/max` format and simply returns no stage for absent or malformed input.
- Production patch: [`b00e922a`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/b00e922a7dbd7c7e4982e027f8d0701b8cf761fb). Host test: [`9becfeca`](https://github.com/PixelExperience-Reborn/bootable_recovery/commit/9becfeca77e535f24376d6adae3921482b229764).

## Verified checks

- AOSP17 baseline import workflow: [successful run](https://github.com/PixelExperience-Reborn/bootable_recovery/actions/runs/41635068389).
- PE Recovery working-branch workflow: [successful run](https://github.com/PixelExperience-Reborn/bootable_recovery/actions/runs/41636054862). `clang++` compiled and ran the **actual production stage parser** in host C++17 tests; shell/whitespace and source-level checks passed.
- Source checks assert that signature verification, SPL downgrade checks and `ro.debuggable` property checks were not removed. This is a guard against accidental text-level regressions, **not a signature-verification functional test**.
- The staged manifest [`aosp17_pe_p0_recovery.xml`](../aosp17_pe_p0_recovery.xml) pins the exact successful working-branch SHA `0ed8dc4f93020555afdfc19141263ca40629ef74`.

## Remaining acceptance gates — not passed

1. Full Linux `repo sync` and Android17 Soong/Make bootstrap, including all recovery linked libraries.
2. `recoveryimage`, `fastbootd`, and `recovery_unit_test` compiled with actual mondrian BoardConfig/fstab.
3. Test verified signed sideload, rejection of unsigned/downgrade OTA, SPL policy, and locked/unlocked AVB states.
4. Test A/B and Virtual A/B snapshots, recovery reason, bootloader message/BCB and partitions.
5. Test real USB ADB authorization, touch coordinates, rendering, battery UI and fsck logs on POCO F5 Pro / Redmi K60.
6. Only after these tests, consider remaining selected PE UI and hardware patches and merge into a release candidate.

**Status:** reviewed AOSP17 Recovery source and some PE functionality committed; host CI passed. **Not Android17 ROM-build-ready and not device-validated.** The legacy `seventeen` branch is unchanged.
