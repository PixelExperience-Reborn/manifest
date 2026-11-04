# Android 17 PixelExperience-Reborn — mondrian device port and selective LineageOS reuse

**Date:** 2026-11-04. **Scope:** POCO F5 Pro / Redmi K60 (`mondrian`), Snapdragon 8+ Gen 1 / SM8475 with SM8450 common platform. **Status:** architectural rules and migration plan; independent device trees and compiled ROM are **not yet delivered**.

## Clarification: LineageOS is another current Android base, not obsolete code

The existing LF52406 LineageOS 24.0 device/common trees are a **valuable, maintained hardware integration reference and source of potentially reusable solutions**. PixelExperience-Reborn will have its own AOSP17-derived platform, product identity, build integration and device tree ownership. Being originally written for LineageOS is **not a reason to reject a useful implementation**. Conversely, availability in a booting LineageOS device tree is **not proof** that the code builds or behaves correctly in PE-Reborn/AOSP17.

### Pinned references, not automatically inherited build inputs

- [mondrian device tree](https://github.com/LF52406/mondrian_android_device_xiaomi_mondrian/tree/lineage-24.0), `lineage-24.0`. Device product definition, partition/device overlays, display, haptics and device-specific integration.
- [sm8450-common device tree](https://github.com/LF52406/mondrian_android_device_xiaomi_sm8450-common/tree/lineage-24.0), checked source commit `6e0022f5100e09ac97980095b6ed8528f4ff823f`. Filesystem/fstab, BoardConfig, VINTF, init, hardware and power/audio/camera/NFC/Wi-Fi references.
- [proprietary vendor hardware inventory](https://github.com/LF52406/proprietary_vendor_xiaomi_sm8450-common/tree/lineage-24.0), prior audited commit `1d5437c0f615b45ad2315d78d9efa7eb78247d32`. **Do not assume redistributability** of proprietary binaries, licences or signing artefacts.
- Kernel/modules/devicetrees are separate hardware inputs; select only required mondrian variants and compatible vendor interfaces. The presence of an upstream fork does not by itself satisfy PE-Reborn source history or device compliance.

## Reuse classification for every candidate

| Category | What to do | Evidence required |
| --- | --- | --- |
| Hardware facts (partitions, panel, GPIO, touch, fstab, firmware names, VINTF instance) | Read from working LineageOS trees and validate on mondrian; preserve known-good hardware requirements in PE-Reborn native files | Exact source commit, actual vendor service/partition, AOSP17 parser/HAL requirements |
| Portable code or configuration (kernel patch, init, overlay, UI, HAL glue) | Port the **minimal useful change**, preserve copyright/licence/attribution, rebase to AOSP17-native interfaces | Relevant upstream provenance and licence; diff review; Soong/Make check; targeted tests |
| Build-system-specific LineageOS dependencies | Replace with AOSP17-native or own PE-Reborn equivalents; do not cargo-cult missing `lineage_*` modules, namespaces or makefiles | Dependency graph, active product variables, no stale references, reproducible checkout |
| Security-critical integrations (AVB, FBE, KeyMint, SELinux, recovery/OTA) | Inspect existing effective behaviour, then design independently validated equivalent policy; no blind bypass or global `permissive` | Security audit, VINTF/SELinux/AVB/rollback, actual device testing |
| Proprietary blobs and Google components | Keep only hardware/licensed components justified for mondrian; separate source, binary and distribution permissions | Provenance and applicable distribution rights; ABI/VINTF checks; product packaging tests |

## Architecture and sequencing

1. **Keep the verified AOSP17 source graph.** Historical `seventeen` branch of every PE archive remains unchanged. Active AOSP17 manifest profiles are opt-in; unported CAF or old Lineage-specific forks do not automatically replace official Android source.
2. **Create native PE-Reborn device ownership** for `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` when their dependency graph is ready. Do not pretend the existing LF52406 trees already are PE-Reborn device trees, and do not automatically import other device targets.
3. For each LineageOS candidate, record `source repository / branch / exact SHA / original path / licence / target owner / required changes / test gates`. Preserve authorship. Decide whether to **reuse unchanged, adapt, rewrite, replace with upstream AOSP17, or omit**; omission must have a reason, not a blanket policy.
4. Start from the hardware-critical sequence: partition layout, boot/recovery/AVB, vendor VINTF and KeyMint/FBE, init and SELinux, kernel/modules and graphics/radio/audio/camera/NFC, then device Settings/features. Cross-check vendor firmware and the Android17 API/ABI level at each step.
5. Keep separate **development** and **release** signing/verified-boot rules. Historical LineageOS reference `BoardConfigCommon.mk` uses public `testkey_rsa2048.pem` and `--flags 3`, which must not silently ship as a PE-Reborn release trust configuration.
6. Stage `repo init` and `repo manifest` checks, `repo sync` selected source verification, host/unit tests, then full Soong/Make build, resulting image/VINTF/security checks, recovery/OTA and finally monitored physical-device validation. CI static PASS is not a ROM build or a boot test.

## Known hardware integration blockers (as of this review)

- Main versus recovery fstab have different FBE wrapped-key and filesystem options; see [mondrian storage preflight](ANDROID_17_MONDRIAN_STORAGE_PREFLIGHT.md). **Do not format user data to shortcut debugging.**
- AVB historical archival `external/avb` signing extension and the Lineage-based **development configuration** need independent release review; official AOSP17 source remains chosen. See [AVB P2 audit](https://github.com/PixelExperience-Reborn/external_avb/blob/audit/a17-mondrian-avb-20261104/docs/ANDROID_17_MONDRIAN_AVB_SECURITY_AUDIT.md).
- FaceUnlock, alternate historical camera apps, ANT radio stack and CAF SELinux shortcuts are *not* proved necessary or compatible by their presence in historical repositories. Preserve functionality already provided by AOSP17 or the working hardware stack where applicable.
- An independent PE-Reborn device build is **not yet present**, and no Android17 mondrian boot, release signing or CTS/VTS claim is made.

## Release acceptance

The device port is not complete until an independently maintained and licence-reviewed source graph, product definition, full Android17 build, device-specific HAL/SELinux/FBE/AVB checks, and physical mondrian validation are recorded. A matrix status of `audited` or a green source-only GitHub Actions job is never `ready for release`.
