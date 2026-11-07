# Android 17 — modern Qualcomm AudioReach / SoundTrigger3 AIDL source candidate

**Prepared 2026-11-07.** This is **not** the active `default.xml`, is **not** one of the 25 reviewed base profiles, does **not** include a PE-Reborn device/product tree, and does **not** claim a compiled audio HAL or working always-on hotword on `mondrian` (POCO F5 Pro / Redmi K60, SM8475, board family `taro`).

## Technical preference: newer compatible Qualcomm platform, not arbitrary newest date

The historical PE `vendor/qcom/opensource/audio-hal/st-hal` repository (`seventeen`, 2023) builds a legacy `sound_trigger.primary.$(TARGET_BOARD_PLATFORM)` vendor module using `Android.mk`, the old Sound Trigger C API, LSM and GCS backends and kernel-header coupling. Its makefile is **disabled when `TARGET_USES_QCOM_AUDIO_AR=true`**. Installing it alongside AudioReach-based `st-hal-ar` makes neither a valid modern Android17 Sound Trigger implementation.

The related historical PE `vendor/qcom/opensource/audio-hal/st-hal-ar` (2024) is PAL-backed but still exports `sound_trigger.primary.*` as a legacy HAL library. A *later commit date* is not the same as a newer HAL architecture: a September 2026 AOSPA branch `calcite-8650` retains a similar legacy `sound_trigger.primary.*` module. We must select the most modern **hardware-compatible** implementation, not mix multiple STHALs.

An inspectable Sony-hosted snapshot of Qualcomm-derived `AUDIO.LA.10.0.r1` introduces actual **`android.hardware.soundtrigger3` stable AIDL V1** service source:
- `libsoundtriggerhal.qti` exports `createISoundTriggerFactory()` and registers `ISoundTriggerHw/default` through NDK Binder, `AServiceManager_addService`;
- it uses `android.hardware.soundtrigger3-V1-ndk`, `android.media.audio.common.types-V2-ndk`, PAL `libar-pal`, and VINTF `android.hardware.soundtrigger3` **AIDL V1**; it is a **library factory**, not a standalone service executable with its own init.rc;
- corresponding primary Audio HAL `audiohalservice.qti` loads registration factories from configurable libraries using `dlopen()/dlsym()`; the **product must actually configure this `libsoundtriggerhal.qti` factory** and install exactly one matching VINTF declaration;
- newer Qualcomm primary Audio HAL source committed August 2026 sets **Audio Core AIDL V3** and **Effects AIDL V4** for Android17; this requires coordinated framework/SEPolicy/VINTF and vendor ABI validation, not a single module substitution.

Our **actual selected PE AOSP17 `hardware/interfaces` snapshot** (commit `735e364cbdd00b0d6e4dc33ea0866dbb6d971a11`) already has frozen **`android.hardware.soundtrigger3` AIDL V1, V2, V3, V4**, with `latest_android_hardware_soundtrigger3-V4`. An older frozen **HAL V1** service may be discoverable by the modern framework, but its methods, capability negotiation, hotword audio capture, permissions and complete VTS/CTS compatibility must be demonstrated on the selected `mondrian` product. Do **not** call it a V4 implementation merely because the framework defines V4. The AOSP SoundTrigger framework prefers an AIDL service and can fall back to HIDL for compatibility; it recommends a direct modern AIDL implementation. <https://source.android.com/docs/core/audio/sound-trigger>

## Exactly six pinned source checkouts — preview only

`aosp17_pe_p2_qcom_audio_aidl_candidate.xml` inherits `aosp17_pe_p2_kernel_configs.xml`, adds one Sony-hosted source remote `sony-qcom-audio-review` (`https://github.com/sonyxperiadev`), and pins the **entire identifiable public AudioReach source chain**:

| Path | GitHub repository | Exact commit | Exact source tree | Role |
| --- | --- | --- | --- | --- |
| `vendor/qcom/opensource/audio-hal/st-hal-ar` | `vendor-qcom-opensource-audio-hal-st-hal-ar` | `1dcb1275256b3f43b78d342d623870324a831720` | `d47390edeaf35ee6b50d15b88e9f5537f372174e` | SoundTrigger AIDL V1 PAL-backed library |
| `vendor/qcom/opensource/audio-hal/primary-hal-ar` | `vendor-qcom-opensource-audio-hal-primary-hal-ar` | `b071e74ead44a7aecee69969003b902632cd4ab3` | `c78551f4c27dab685e396cd8996c1458b724787d` | Android17 primary core/effects AIDL and service registration |
| `vendor/qcom/opensource/pal` | `vendor-qcom-opensource-arpal-lx` | `44e6ad74fd34c390b053bbe19811502c132f007e` | `a1ec1aec66c66d7672fde7f3349bdef852a5d962` | Public AudioReach PAL frontend |
| `vendor/qcom/opensource/agm` | `vendor-qcom-opensource-agm` | `7ad4167f2241beefd2a48b9e87453c3a80c5811b` | `6c4eaa800ab4d1f2d584b51ae4e020eb68408c90` | Audio graph manager |
| `vendor/qcom/opensource/audioreach-graphservices` | `vendor-qcom-opensource-audioreach-graphservices` | `d38796b5d74ff727a5fbd9f10ecbc7f5c0335ff5` | `40286aaa0fbdfad8538496de1096d6b68b6e60a2` | DSP graph services |
| `vendor/qcom/opensource/audioreach-conf` | `vendor-qcom-opensource-audioreach-conf` | `5e90f9e4d6bb790fca0a092d57fdee8572d5b990` | `76314d215f91c4125bc09ea48f6085eee02f3b1e` | Graph and AudioReach config sources |

This GitHub-hosted source is a **Sony Xperia Android BSP mirror of Qualcomm-derived code**. Its exact commits and trees are real and reviewable, but this audit is **not** a Qualcomm CodeLinaro attestation, guaranteed official current Qualcomm platform tag, OEM licensing determination, or a match to Xiaomi firmware.

## Necessary warning for SM8475 / taro

The newer primary HAL contains a `configs/taro/` directory, which is useful **platform-family evidence only**. Its `configs/taro/audio_policy_configuration.xml` declares the older **audio policy XML version 7.0**, while other platform families under the same tree have specific Audio AIDL modules and VINTF manifests. **Do not copy the generic `taro` audio XML to mondrian or infer that the current AIDL service is preconfigured for its actual vendor DSP/codec/AMP/ACDB**. We must first confirm the exact Xiaomi vendor image and ABI:
- stock soundtrigger/primary module names, `android.hardware.soundtrigger3.ISoundTriggerHw/default` vs HIDL declarations, and the installed Audio AIDL Core/Effects service versions;
- PAL/AGM/graph and firmware files, `libar-pal.so` and cross-module symbols, DSP SoC graph IDs, GPR, calibration/ACDB, ADSP firmware and any OEM extra libraries;
- audio routing for speaker, microphones, voice calls, VOIP, camcorder, hotword, Bluetooth LE/HFP/A2DP and the **Android17 SCO audio management** change;
- voice recognition model ABI, AAudio/AudioRecord LAB capture, callback ordering and resource contention, CHRE/LPMA if supported, SSR recovery, DSP suspend/wakeup, microphone privacy indicators, SELinux and battery cost.

Do not enable microphone/hotword capture, misrepresent missing DSP hardware, grant blanket audio permissions or install duplicate HIDL/AIDL HAL instances. A modern Qualcomm codebase is worth selecting **only as a coordinated compatible stack** after independent Soong/NDK build, real VINTF and vendor ABI verification, soundtrigger HAL VTS, audio CTS, voice/wakeup/RF/privacy/power and device tests.

## Verified source-reproduction result

[GitHub Actions #42327531250](https://github.com/PixelExperience-Reborn/vendor_qcom_opensource_audio-hal_st-hal/actions/runs/42327531250) **SUCCESS** confirmed nine pinned Git commit/tree pairs, source contracts, **48/48 manifest regressions**, official `repo manifest` resolution of **1075 selected project paths** (1069 original + 6 isolated modern Qualcomm-derived candidates), and **real targeted `repo sync` of the new AIDL STHAL and primary HAL source checkouts** with exact SHA and tree hashes. It checked SoundTrigger3 AIDL **V1**, Qualcomm primary Audio Core **V3** and Effects **V4**; the selected AOSP17 `hardware/interfaces` remains frozen through **SoundTrigger3 AIDL V4**.

**Important distinction:** this CI did **not** compile any Qualcomm audio modules. The remaining four modern companion repositories were Git-fetched and pinned but not `repo sync`-selected as an assembled product; the AIDL factory was not registered by a live service. Proven source identity must not be described as a working DSP/audio path or a compatible `mondrian` vendor ABI.

## Isolation and validation

The six source checkouts are deliberately added as a **nondefault, source-only preview**, not production dependencies. Active `default.xml`, all **25** reviewed source profiles, original `seventeen` branches, current AOSP17 SoundTrigger AIDL V4 interface, and independent PE-Reborn code stay untouched. A strict manifest validator checks the six immutable pins, single fetch remote and every original owner/revision/group; four negative tests fail if the old legacy `st-hal` is injected, a candidate SHA is changed, a source path is substituted, or `default.xml` is silently promoted.

The preview does not import Sony device trees nor LF52406 LineageOS implementation. LF52406 device sources remain only exceptional read-only hardware evidence, as required for independent PE-Reborn.

**Build/boot readiness: NOT TESTED.** This preview makes the *newer source option reproducible* so it can be evaluated accurately, not automatically chosen for incompatible vendor firmware.
