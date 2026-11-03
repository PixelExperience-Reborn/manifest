# AOSP 17 P0 source migration decisions — ART, Bionic, system/core

**Status:** source/patch audit only. **No Android 17 port of these three repositories is complete and no target build or device test has passed.**
Work is staged in manifest PR #2. Keep the historical PixelExperience-Reborn `seventeen` branches intact until independently reviewed Android 17 branches are available.

## Verified official upstream baselines

| Path | Official upstream | Android 17.0.0 r1 commit |
| --- | --- | --- |
| art | https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1 | `b753cf97923c3695338d21466fa14c57b480a59a` |
| bionic | https://android.googlesource.com/platform/bionic/+/refs/tags/android-17.0.0_r1 | `06356e41c5ed7b12220b24c05ba4fdb873b126a7` |
| system/core | https://android.googlesource.com/platform/system/core/+/refs/tags/android-17.0.0_r1 | `545d2487e38192a2ce25040897ced877cf6b4f53` |

Historical Reborn forks still have Android 14-era changes; the default-branch name `seventeen` is **not** evidence of source compatibility. Prefer the official AOSP 17 source for each platform component until a real, tested PE port exists. Do not transplant entire Android 14 repositories into the AOSP 17 manifest.

## ART — specific PE deltas inspected

- [a9aea8adb753](https://github.com/PixelExperience-Reborn/art/commit/a9aea8adb753895e339ac21f79faa355f41e95bf) changes `ART_BUILD_TARGET_NDEBUG` and `ART_BUILD_HOST_NDEBUG` from true to false. This is not a safe default performance improvement; **do not port by default**.
- [7b31ee5857ac](https://github.com/PixelExperience-Reborn/art/commit/7b31ee5857ac4dc20a3f61005b5b200bfea1e98b) disables debug targets. Inspect Android 17's build variants first; **defer** unless an actual requirement is demonstrated.
- [3e9bf5812f2f](https://github.com/PixelExperience-Reborn/art/commit/3e9bf5812f2f17757da2a142a183079251ae101e) disables ART trace calls in release mode. This can remove observability needed for diagnosing runtime issues; **defer**.
- Acceptance: official ART 17 baseline, per-commit compatibility and observability review, a compiled ART/runtime, ART tests and real boot/runtime verification.

## Bionic — specific PE deltas inspected

- [d03609d85505](https://github.com/PixelExperience-Reborn/bionic/commit/d03609d85505afd70a04ce1e4d877f4bf451458d) adds cached /etc/hosts resolution. It changes libc DNS behavior and needs concurrency/invalidation tests; **defer**.
- [66f7f215e119](https://github.com/PixelExperience-Reborn/bionic/commit/66f7f215e119b38db41d5e9e87d94ec4256f1737) adds wildcard matching of hostnames; potential DNS/security behavior change; **do not automatically carry**.
- [178610a8f7a6](https://github.com/PixelExperience-Reborn/bionic/commit/178610a8f7a65c7c5471207034fbd1b3e02a757e) adds runtime linker SHIM libraries. It changes loading behavior, ABI and process isolation; **defer** without device-specific justification.
- [690a5921ac12](https://github.com/PixelExperience-Reborn/bionic/commit/690a5921ac12ac96917a9b90b90c4995f3b19a10) adds a scudo-free 32-bit libc variant. Do **not** weaken memory-hardening defaults for the entire platform.
- Acceptance: official Bionic 17 baseline and linker/libc API and host/unit test coverage before a PE delta is accepted.

## system/core — release and security review

- [caa0608aff7d](https://github.com/PixelExperience-Reborn/system_core/commit/caa0608aff7de9cbcf382cc27f8f83d8e4ab08fb) weakens protection of read-only properties in init; **reject for a secure AOSP 17 release**.
- [0cb776da5150](https://github.com/PixelExperience-Reborn/system_core/commit/0cb776da5150401f649c3ffd9636940330fa6a33) temporarily weakens property-override security to spoof SafetyNet; **reject for the secure platform baseline**.
- [7fbd71681316](https://github.com/PixelExperience-Reborn/system_core/commit/7fbd71681316ff97e76aac2fd2cfd2ac78471b1) skips a dm-verity setup path when an AVB flag is absent. Do **not** transplant without rigorous review against AOSP 17's verified boot design and actual fstab/AVB contract.
- This review is not a judgment that every old PE patch is unsafe. It isolates known high-risk behavior from necessary functional changes. All other system/core commits remain pending analysis.
- Acceptance: SELinux enforcing, unchanged read-only-property protections, correct vbmeta/rollback policy, first-stage mount, recovery, fastbootd and OTA tests for mondrian.

## P0 integration sequencing

1. **build/make**: the verified AOSP17 source is used **unchanged** in the three bootstrap profiles. The earlier local PE envsetup patch to core Make has been superseded: `vendor/aosp/vendorsetup.sh` now loads PE functions via AOSP17 `source_vendorsetup()`. Bash tests and the official `repo` manifest parser pass in GitHub Actions. Future PE Build/Make deltas require evidence of a concrete Android17 need; the old PE fourteen branch must not be synced as platform Make.
2. **build/soong**: [staged Android 17 branch](https://github.com/PixelExperience-Reborn/build_soong/tree/port/a17-soong-dumpvars-20261103) includes PE build banner metadata, removal of stale PE OTA sidecars on installclean, and a regression test. Complete Soong bootstrap/build validation before declaring ported.
3. **art / bionic / system/core**: begin from the pinned upstream commits in this document. Only add PE deltas after reviewing behavioral/security impact.
4. **frameworks and modules**: review platform APIs and namespace dependencies before enabling PE features.
5. **manifest**: current staged PR still routes 135 old PE projects, including unported P0 forks. It is **not** an Android 17 build-ready graph. The eventual bring-up graph must select official AOSP 17 sources or reviewed Android 17 port branches for each active override, and retain historic forks as reference until then.

## Test policy

Static source reviews and Go syntax checks are not substitutes for `repo sync`, Soong bootstrap, a Linux host build, target-files generation, Verified Boot verification or device/OTA tests. Never label an AOSP 17 component complete without those gates. Do not merge staged PRs into `seventeen` based only on filename matches or isolated tests.
