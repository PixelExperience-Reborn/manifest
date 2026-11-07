# Experimental Qualcomm Display / HWC3 AIDL for independent AOSP17

**Created 2026-11-07. STATUS: source-only, nondefault, incomplete dependencies.** Target `mondrian` SM8475 / `taro`. Never infer bootable display service or a calibrated Xiaomi panel from a Sony-hosted Qualcomm-derived code tree.

## Deliberate modern source direction

The original PE `vendor/qcom/opensource/display` repo from 2021 has only 18 files: HIDL Mapper4 `libgralloc.qti`, `libqdMetaData` and HIDL `vendor.display.config@2.0` shim, not a complete Composer HAL. The separate historical `hardware/qcom-caf/sm8450/display` tree from 2023 includes old SDM/DRM sources but uses **HIDL Composer2.1–2.4** and HIDL mapper4. Neither is a modern Android17 HWC3 solution, and the two source generations must **not** be blindly combined.

A newer Qualcomm-derived public source candidate is `sonyxperiadev/hardware-qcom-display` branch `aosp/DISPLAY.LA.5.0.r1`:
- Exact Git commit **`baf61f736e2109522e3f72754ee7cfacbfa2dc6c`**, tree **`f35e03e1904a346fad8257321233a32650b4ee77`**.
- `composer/Android.bp`: HWC3 **AIDL V2 or V3**, chosen by Soong config; `composer/vendor.qti.hardware.display.composer-service3_v3.xml` declares `android.hardware.graphics.composer3` V3 `IComposer/default` plus vendor display config V12, color, postproc, AIQE. The v2 VINTF file declares composer3 V2 and config V11.
- `gralloc/Android.bp`: **AIDL Allocator V2** service, Mapper **Native Stable-C V5** `mapper.qti` and backwards-compatible mapper HIDL4 source. These source alternatives **must not** automatically register competing active HALs.
- The actual PE AOSP17 `hardware_interfaces` fork (SHA `735e364cbdd00b0d6e4dc33ea0866dbb6d971a11`) already supplies **Composer3 AIDL V1–V5, Allocator AIDL V1–V3, Stable-C Mapper V5**. **A modern AIDL V3 vendor composer is not a V5 implementation**. Android17 VINTF/FCM/SurfaceFlinger compatibility and successful Composer3 + allocator/mapper VTS remain required.

**Critical incomplete-source blocker:** the Sony-hosted Git tree includes `composer/`, `gralloc/`, `libqservice/`, etc. but **no `sdm/libs/` or `sde-drm/` source**. Its build graph references `libsdmcore`, `libsdmclient`, `libsdmutils`, `libdrm` and QTI vendor display AIDL, which require matched sources or ABI-compatible libraries and headers. Do not assert it is a self-contained, buildable device HAL. The historical PE SM8450 SDM source is not necessarily ABI-compatible.

## Explicit 2026 SM8450 source comparison — not a drop-in SDM dependency

The Sony Open Devices `qcom-sm8450.xml` separately points to **`sonyxperiadev/vendor-qcom-opensource-display`**, branch `aosp/DISPLAY.LA.2.0.r1`. Its newer **2026-02-23** source commit `4744d4a2ee7c6c0a53fac76b54766b6eb23531d4`, tree `c97b019a8cfad9f90aa53690b4683d3b54d2ff4e`, has **376 files**, including `sdm/libs/core/Android.bp` and `sde-drm/Android.bp`. This is useful hardware-family **read-only evidence** for SM8450.

**But this source is still HIDL:** `composer/Android.bp` links `android.hardware.graphics.composer@2.1`–`@2.4` and `vendor.qti.hardware.display.composer@3.1`; VINTF declares **`android.hardware.graphics.composer@2.4/IComposer`**, and Gralloc uses HIDL Mapper4. Do **not** put it in the AOSP17 HWC3 candidate or simply combine its SDM with the new AIDL composer: compatible SDM headers, ELF symbols and vendor binaries have not been established. A later Git date is not automatically a newer HAL architecture.

[Source CI #42329757843](https://github.com/PixelExperience-Reborn/vendor_qcom_opensource_display/actions/runs/42329757843) verified both modern AIDL and SM8450 HIDL source identities. The historical Sony device tree, proprietary firmware and panel configuration are **not** PE-Reborn foundations.

## Nondefault source profile

`aosp17_pe_p2_qcom_display_aidl_candidate.xml`:
- Includes the unchanged `aosp17_pe_p2_kernel_configs.xml` baseline, introduces one source remote `sony-qcom-display-review` at `https://github.com/sonyxperiadev`;
- Adds **only** `hardware/qcom/display` → `hardware-qcom-display`, exact 40-hex commit `baf61f736e2109522e3f72754ee7cfacbfa2dc6c`, upstream `aosp/DISPLAY.LA.5.0.r1`, group `device`;
- Does **not** add historical `vendor/qcom/opensource/display` or `hardware/qcom-caf/sm8450/display`; does not replace `hardware/interfaces`, `frameworks/native`, `frameworks/av`, old product code, or the active **`default.xml`**;
- Is **not** a 26th active phase. The 25 reviewed source-only stages remain exactly as selected.

The Python validator rejects changes to the candidate's path, remote, owner, SHA, upstream, groups, other original project ownership and default profile. Negative regression tests reject historical HIDL activation and graphics owner takeover. A GitHub Actions workflow in the isolated archive tests immutable source trees, real `repo manifest`, and real **targeted `repo sync` of the new display checkout** (not a whole ROM sync or build).

## Completed source-reproduction verification

[GitHub Actions #42329757843](https://github.com/PixelExperience-Reborn/vendor_qcom_opensource_display/actions/runs/42329757843) **SUCCESS** pinned five source commit/tree pairs: archived HIDL vendor display helpers, 2023 SM8450 HIDL Composer/SDM, February 2026 SM8450 HIDL SDM read-only reference, modern Sony-hosted **HWC3 AIDL V2/V3 with Allocator V2 and Native Stable-C Mapper V5**, and the actual selected PE AOSP17 **Composer3 V5 / Allocator V3** interface tree.

**All 25** active source profiles and **55/55** regression tests passed. Official `repo manifest` resolved the HWC3 candidate to **1070 unique selected projects**, preserving `hardware_interfaces` and `frameworks_av` ownership. A targeted `repo sync` verified exact `hardware/qcom/display` commit `baf61f736e2109522e3f72754ee7cfacbfa2dc6c` and tree `f35e03e1904a346fad8257321233a32650b4ee77`. This is **source verification only**; matching SDM/DRM dependency closure, Soong, vendor ABI, SELinux, VINTF and actual panel remain unresolved.

## Hard hardware constraints for mondrian / SM8475

Do not inherit `hardware/qcom/display/config/display-product.mk`: this Sony-hosted template references **Visionox, Sony, Sharp, Novatek, etc.** generic/backlight/QDCM profiles and display properties (including HDR and rounded corners) that are **not** proof of the actual Xiaomi `mondrian` panel, OLED supplier, refresh modes, DSC/DSI configuration or safe brightness/power limits.

Before activating any product package, we must obtain exact matched Xiaomi firmware or authorized device evidence:
- DRM/SDM/KMS/Adreno/GBM/UBWC buffer format, protected buffers, gralloc/mapper handle ABI, `libsdm*` and vendor display service `DT_NEEDED` closure; correct kernel driver API and SELinux enforcing domains;
- panel ID/DSI/DSC modes, panel-specific QDCM/color and backlight, 60/120Hz/VRR/QSync, HDR/WCG, screen-off/doze/AOD, thermal/power budget and secure content/HDCP if supported;
- Android17 single Composer3 `IComposer/default`, Allocator `IAllocator/default`, native Mapper V5 provider and vendor QTI display config service with exact VINTF/FCM, verified default Soong composer version and no duplicate HIDL instance;
- AOSP17 Soong/Ninja build, `VtsHalGraphicsComposer3_TargetTest`, mapper Stable-C and allocator VTS, CTS/display/video/camera integration, suspend/resume, clean boot, ESD and recovery tests.

The complete independent PE-Reborn `mondrian` device/product source does not yet exist; the LF52406 LineageOS tree may only supply **exceptional read-only hardware facts**, not our ROM architecture or copied config.

**Decision:** Prefer the newer HWC3 AIDL architecture for investigation, and continue only after verifying the missing SDM/DRM/graphics vendor dependency graph. The older HIDL display components stay excluded from the active source graph. No flashable Android17 display HAL or working ROM is claimed.

Reference: [official AIDL HWC documentation](https://source.android.com/docs/core/graphics/aidl-hwc); [source audit PR](https://github.com/PixelExperience-Reborn/vendor_qcom_opensource_display/pull/1).
