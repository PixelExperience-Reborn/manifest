# Android 17 PE-Reborn: Mondrian / sm8450 hardware source contracts

**2026-11-05 · source dependency inventory, not a successful product build.**

## Source-of-truth device configuration

Read-only existing device sources: [LF52406/mondrian_android_device_xiaomi_sm8450-common](https://github.com/LF52406/mondrian_android_device_xiaomi_sm8450-common/tree/lineage-24.0) and [mondrian](https://github.com/LF52406/mondrian_android_device_xiaomi_mondrian/tree/lineage-24.0). **Do not edit the user's MistOS/Lineage device trees as part of base platform work.**

### Confirmed required source paths

- `common.mk` line 12 inherits `hardware/qcom-caf/common/common.mk`. Old PE source lacked it.
- `Android.bp` imports `hardware/qcom-caf/common/libqti-perfd-client` and `vendor/qcom/opensource/commonsys-intf/display`.
- Device Audio package list includes `android.hardware.audio@7.0-impl`, `vendor.qti.hardware.AGMIPC@1.0-service`, `audio.primary.taro`, `libagm_compress_plugin`, `libagm_mixer_plugin`, `libagm_pcm_plugin` and `libfmpal`; current config copies audio configuration and Codec2 policy files from `hardware/qcom-caf/sm8450/audio/primary-hal/configs`.
- Display packages include QTI mapper, allocator and composer services with configuration from `hardware/qcom-caf/sm8450/display/config`.
- Other direct dependencies: `ipacm`, `android.hardware.boot-service.qti` / `.recovery`, QCOM `compatibility_matrix.xml`, `vendor_framework_compatibility_matrix.xml`, and vendor VINTF file declarations.
- `Android.bp` imports `hardware/google/pixel/pixelstats` and `hardware/google/pixel/power-libperfmgr` even though the device is Xiaomi. These are exact pending **source namespace** references; whether modules are actively used must be verified before removing or adding them.
- `BOARD_WLAN_DEVICE := qcwcn`, so historical Broadcom-specific SAE/libbt code is not a default mondrian requirement.

### Implemented source baseline

`hardware_qcom-caf_common` at [`50dc84295b97`](https://github.com/PixelExperience-Reborn/hardware_qcom-caf_common/commit/50dc84295b97415115dea24ccffaacb93c5b4936) merges old PE Git history and current Qualcomm common from LineageOS `lineage-24.0` upstream SHA `c7eda1ff7fd99f29999abbe19922ce59a41ee000`, current QSSI17 matrix. Seven conflicts were reviewed and resolved using the modern Soong, BoardConfig and VINTF contracts. A follow-up commit removes the optional LineageOS product policy import and only registers the legacy bootctrl namespace if its source exists.

**CI:** [#41935011870 PASS](https://github.com/PixelExperience-Reborn/hardware_qcom-caf_common/actions/runs/41935011870), [draft PR #1](https://github.com/PixelExperience-Reborn/hardware_qcom-caf_common/pull/1). Source-only checks, **not** a Soong build.

### Required integration sequence for a complete PE Android17 mondrian source tree

1. Confirm independent PE `vendor/aosp` product configuration is compatible with Android17 and modern Soong namespace visibility.
2. Pin a tested sm8450-common hardware common source together with real kernel header providers and VINTF schema, without importing `vendor/lineage` product base.
3. Align AGM, PAL, primary HAL and tinycompress module names, client ABI, mixer XML and vendor partitions as one set. The old QSSI14 archives are not proven source-compatible with QSSI17.
4. Align display composer/gralloc with current AOSP17 Graphics AIDL and QTI services; preserve panel features only through their supported vendor contracts.
5. Resolve modern QTI boot control AIDL implementation rather than activating old GPT-writing `bootctrl.sdm845`.
6. Review IPA, NFC, GNSS, WFD, vendor media and storage with exact device service dependencies; avoid blanket compatibility shims.
7. Only **after** platform source graph and base are ready: Soong image build, VINTF checks, SELinux, A/B OTA and tests on physical mondrian.

**Current status:** module dependencies identified and Qualcomm common source updated; hardware clients and complete ROM build are **not yet integrated/validated**.
