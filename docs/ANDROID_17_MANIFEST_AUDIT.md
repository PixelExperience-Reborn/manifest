# Android 17 AOSP manifest graph audit

**STAGED ONLY — NOT BUILD-READY.** This document records an independently reviewed manifest proposal, not a working ROM.

- Upstream: official AOSP immutable `android-17.0.0_r1`.
- Gitiles source: https://android.googlesource.com/platform/manifest/+/refs/tags/android-17.0.0_r1/default.xml
- Verified raw Git blob SHA-1: `f8c6b343b51c94693108dcefb6bc41f51ae24791`.
- Official AOSP projects retained after removals: **1016**.
- AOSP declarations removed (135 mirror overrides + non-mondrian device exclusion as applicable): **71**.
- Own PE projects: **135**, pinned to `PixelExperience-Reborn/seventeen`.
- Historical unmatched projects intentionally excluded: **50**.

## Design decisions

1. Preserve the upstream AOSP 17 project graph and tag; do not reuse the AOSP 14 project list.
2. Keep PE-specific overlay/manifest patterns via `snippets/remove.xml`, `pixel.xml`, `pixel-extras.xml`, and `pixel-caf.xml`.
3. Exclude platform device projects for other vendors, but retain `device/common`, `device/sample`, and generic AOSP device infrastructure.
4. Drop old PE per-SoC projects not owned by Reborn, while preserving Reborn common, sm8450 and general framework sources.
5. Remove legacy CAF linkfile destinations that target absent obsolete SoC projects.
6. Preserve the `fourteen` branches, as well as original PE commits on `seventeen`; no source reset or merge is performed here.

## Critical blockers for building / booting

- **All 135 Reborn sources remain Android 14-era until individually ported.** Correct manifest routing is not proof of Android 17 compatibility.
- The old `vendor_aosp/config/common.mk` unconditionally inherits `vendor/gms/products/gms.mk`; without a licensed GMS source build will fail. Resolve this dependency explicitly, rather than creating unauthorized proprietary public mirrors.
- `external_faceunlock` and `vendor_gms` were GitLab-only and are not available among the 135 Reborn GitHub mirrors.
- Qualcomm CAF/sm8450 repositories must be checked against corresponding vendor/Android 17 contracts. Do not treat all old HALs as valid just because they have the `seventeen` branch.
- Confirm Android 17 **Soong/build/release** integration, module namespace changes and SELinux before compiling.
- An actual Linux checkout, `repo manifest`, `repo sync`, Soong bootstrap and device test remain required.

## Next AOSP-first port sequence

1. Build core: `build`, `build_soong`, `art`, `bionic`, `system_core` and supported prebuilts.
2. Native and frameworks: `frameworks_native`, `frameworks_av`, `frameworks_base`, telephony.
3. PE custom layers: `vendor_aosp`, `vendor_pixel-framework`, Settings, face unlock and additional apps.
4. Modules: Wi-Fi, Bluetooth, Connectivity, Permission, security, SELinux, OTA and update engine.
5. Hardware only for mondrian/sm8450; verify Qualcomm HAL/API and proprietary component compatibility.
6. Build and test; retain history via isolated port branches and reviewed PRs.

## AOSP projects replaced by PE overrides

- `art` <- `platform/art`
- `bionic` <- `platform/bionic`
- `bootable/recovery` <- `platform/bootable/recovery`
- `build/make` <- `platform/build`
- `build/soong` <- `platform/build/soong`
- `development` <- `platform/development`
- `external/avb` <- `platform/external/avb`
- `external/cronet` <- `platform/external/cronet`
- `external/dtc` <- `platform/external/dtc`
- `external/e2fsprogs` <- `platform/external/e2fsprogs`
- `external/gptfdisk` <- `platform/external/gptfdisk`
- `external/icu` <- `platform/external/icu`
- `external/libcxx` <- `platform/external/libcxx`
- `external/libnl` <- `platform/external/libnl`
- `external/mksh` <- `platform/external/mksh`
- `external/tinycompress` <- `platform/external/tinycompress`
- `external/wpa_supplicant_8` <- `platform/external/wpa_supplicant_8`
- `frameworks/av` <- `platform/frameworks/av`
- `frameworks/base` <- `platform/frameworks/base`
- `frameworks/native` <- `platform/frameworks/native`
- `frameworks/opt/telephony` <- `platform/frameworks/opt/telephony`
- `frameworks/opt/timezonepicker` <- `platform/frameworks/opt/timezonepicker`
- `hardware/broadcom/libbt` <- `platform/hardware/broadcom/libbt`
- `hardware/interfaces` <- `platform/hardware/interfaces`
- `hardware/libhardware` <- `platform/hardware/libhardware`
- `hardware/qcom/wlan` <- `platform/hardware/qcom/wlan`
- `hardware/ril` <- `platform/hardware/ril`
- `kernel/configs` <- `kernel/configs`
- `packages/apps/Camera2` <- `platform/packages/apps/Camera2`
- `packages/apps/Settings` <- `platform/packages/apps/Settings`
- `packages/modules/Bluetooth` <- `platform/packages/modules/Bluetooth`
- `packages/modules/Connectivity` <- `platform/packages/modules/Connectivity`
- `packages/modules/Permission` <- `platform/packages/modules/Permission`
- `packages/modules/Wifi` <- `platform/packages/modules/Wifi`
- `packages/modules/adb` <- `platform/packages/modules/adb`
- `packages/providers/DownloadProvider` <- `platform/packages/providers/DownloadProvider`
- `packages/providers/MediaProvider` <- `platform/packages/providers/MediaProvider`
- `packages/services/Telecomm` <- `platform/packages/services/Telecomm`
- `packages/services/Telephony` <- `platform/packages/services/Telephony`
- `platform_testing` <- `platform/platform_testing`
- `prebuilts/build-tools` <- `platform/prebuilts/build-tools`
- `system/bpf` <- `platform/system/bpf`
- `system/core` <- `platform/system/core`
- `system/extras` <- `platform/system/extras`
- `system/libhidl` <- `platform/system/libhidl`
- `system/libhwbinder` <- `platform/system/libhwbinder`
- `system/libziparchive` <- `platform/system/libziparchive`
- `system/logging` <- `platform/system/logging`
- `system/media` <- `platform/system/media`
- `system/security` <- `platform/system/security`
- `system/sepolicy` <- `platform/system/sepolicy`
- `system/tools/mkbootimg` <- `platform/system/tools/mkbootimg`
- `system/update_engine` <- `platform/system/update_engine`
- `system/vold` <- `platform/system/vold`
- `tools/metalava` <- `platform/tools/metalava`

## AOSP device projects excluded

- `device/amlogic/yukawa`
- `device/amlogic/yukawa-kernel`
- `device/google/atv`
- `device/google/common/etm`
- `device/google/contexthub`
- `device/google/cuttlefish`
- `device/google/cuttlefish_prebuilts`
- `device/google/cuttlefish_vmm`
- `device/google/sdv`
- `device/google/sdv_display_safety`
- `device/google/trout`
- `device/google_car`
- `device/linaro/dragonboard`
- `device/linaro/dragonboard-kernel`
- `device/linaro/hikey`
- `device/linaro/hikey-kernel`

## Historical PE projects excluded (not mirrored)

- `device_qcom_sepolicy-legacy-um` (device/qcom/sepolicy-legacy-um; `pixel`)
- `device_qcom_sepolicy_vndr_legacy-um` (device/qcom/sepolicy_vndr/legacy-um; `pixel`)
- `device_qcom_sepolicy_vndr_sm8550` (device/qcom/sepolicy_vndr/sm8550; `pixel`)
- `hardware_qcom-caf_bengal_audio` (hardware/qcom-caf/bengal/audio; `pixel`)
- `hardware_qcom-caf_bengal_display` (hardware/qcom-caf/bengal/display; `pixel`)
- `hardware_qcom-caf_bengal_media` (hardware/qcom-caf/bengal/media; `pixel`)
- `hardware_qcom-caf_msm8953_audio` (hardware/qcom-caf/msm8953/audio; `pixel`)
- `hardware_qcom-caf_msm8953_display` (hardware/qcom-caf/msm8953/display; `pixel`)
- `hardware_qcom-caf_msm8953_media` (hardware/qcom-caf/msm8953/media; `pixel`)
- `hardware_qcom-caf_msm8996_audio` (hardware/qcom-caf/msm8996/audio; `pixel`)
- `hardware_qcom-caf_msm8996_display` (hardware/qcom-caf/msm8996/display; `pixel`)
- `hardware_qcom-caf_msm8996_media` (hardware/qcom-caf/msm8996/media; `pixel`)
- `hardware_qcom-caf_msm8998_audio` (hardware/qcom-caf/msm8998/audio; `pixel`)
- `hardware_qcom-caf_msm8998_display` (hardware/qcom-caf/msm8998/display; `pixel`)
- `hardware_qcom-caf_msm8998_media` (hardware/qcom-caf/msm8998/media; `pixel`)
- `hardware_qcom-caf_sdm660_audio` (hardware/qcom-caf/sdm660/audio; `pixel`)
- `hardware_qcom-caf_sdm660_display` (hardware/qcom-caf/sdm660/display; `pixel`)
- `hardware_qcom-caf_sdm660_media` (hardware/qcom-caf/sdm660/media; `pixel`)
- `hardware_qcom-caf_sdm845_audio` (hardware/qcom-caf/sdm845/audio; `pixel`)
- `hardware_qcom-caf_sdm845_display` (hardware/qcom-caf/sdm845/display; `pixel`)
- `hardware_qcom-caf_sdm845_media` (hardware/qcom-caf/sdm845/media; `pixel`)
- `hardware_qcom-caf_sm8150_audio` (hardware/qcom-caf/sm8150/audio; `pixel`)
- `hardware_qcom-caf_sm8150_display` (hardware/qcom-caf/sm8150/display; `pixel`)
- `hardware_qcom-caf_sm8150_media` (hardware/qcom-caf/sm8150/media; `pixel`)
- `hardware_qcom-caf_sm8250_audio` (hardware/qcom-caf/sm8250/audio; `pixel`)
- `hardware_qcom-caf_sm8250_display` (hardware/qcom-caf/sm8250/display; `pixel`)
- `hardware_qcom-caf_sm8250_media` (hardware/qcom-caf/sm8250/media; `pixel`)
- `hardware_qcom-caf_sm8350_audio` (hardware/qcom-caf/sm8350/audio; `pixel`)
- `hardware_qcom-caf_sm8350_display` (hardware/qcom-caf/sm8350/display; `pixel`)
- `hardware_qcom-caf_sm8350_media` (hardware/qcom-caf/sm8350/media; `pixel`)
- `hardware_qcom-caf_sm8550_audio_agm` (hardware/qcom-caf/sm8550/audio/agm; `pixel`)
- `hardware_qcom-caf_sm8550_audio_pal` (hardware/qcom-caf/sm8550/audio/pal; `pixel`)
- `hardware_qcom-caf_sm8550_audio_primary-hal` (hardware/qcom-caf/sm8550/audio/primary-hal; `pixel`)
- `hardware_qcom-caf_sm8550_data-ipa-cfg-mgr` (hardware/qcom-caf/sm8550/data-ipa-cfg-mgr; `pixel`)
- `hardware_qcom-caf_sm8550_dataipa` (hardware/qcom-caf/sm8550/dataipa; `pixel`)
- `hardware_qcom-caf_sm8550_display` (hardware/qcom-caf/sm8550/display; `pixel`)
- `hardware_qcom-caf_sm8550_media` (hardware/qcom-caf/sm8550/media; `pixel`)
- `vendor_qcom_opensource_data-ipa-cfg-mgr-legacy-um` (vendor/qcom/opensource/data-ipa-cfg-mgr-legacy-um; `pixel`)
- `external_faceunlock` (external/faceunlock; `pixel-gitlab`)
- `hardware_qcom_sdm845_data_ipacfg-mgr` (hardware/qcom/sdm845/data/ipacfg-mgr; `pixel`)
- `hardware_qcom_sdm845_display` (hardware/qcom/sdm845/display; `pixel`)
- `hardware_qcom_sdm845_media` (hardware/qcom/sdm845/media; `pixel`)
- `vendor_gms` (vendor/gms; `pixel-gitlab`)
- `device_google_contexthub` (device/google/contexthub; `pixel`)
- `device_google_cuttlefish` (device/google/cuttlefish; `pixel`)
- `hardware_qcom_sm7250_display` (hardware/qcom/sm7250/display; `pixel`)
- `hardware_qcom_sm7250_media` (hardware/qcom/sm7250/media; `pixel`)
- `hardware_qcom_sm8150_data_ipacfg-mgr` (hardware/qcom/sm8150/data/ipacfg-mgr; `pixel`)
- `hardware_qcom_sm8150_display` (hardware/qcom/sm8150/display; `pixel`)
- `hardware_qcom_sm8150_media` (hardware/qcom/sm8150/media; `pixel`)

## Legacy CAF linkfiles removed

- `hardware/qcom-caf/bengal/Android.bp`
- `hardware/qcom-caf/bengal/Android.mk`
- `hardware/qcom-caf/msm8953/Android.bp`
- `hardware/qcom-caf/msm8953/Android.mk`
- `hardware/qcom-caf/msm8996/Android.bp`
- `hardware/qcom-caf/msm8996/Android.mk`
- `hardware/qcom-caf/msm8998/Android.bp`
- `hardware/qcom-caf/msm8998/Android.mk`
- `hardware/qcom-caf/sdm660/Android.bp`
- `hardware/qcom-caf/sdm660/Android.mk`
- `hardware/qcom-caf/sdm845/Android.bp`
- `hardware/qcom-caf/sdm845/Android.mk`
- `hardware/qcom-caf/sm8150/Android.bp`
- `hardware/qcom-caf/sm8150/Android.mk`
- `hardware/qcom-caf/sm8250/Android.bp`
- `hardware/qcom-caf/sm8250/Android.mk`
- `hardware/qcom-caf/sm8350/Android.bp`
- `hardware/qcom-caf/sm8350/Android.mk`
- `hardware/qcom-caf/sm8550/Android.bp`
- `hardware/qcom-caf/sm8550/Android.mk`
- `hardware/qcom-caf/sm8550/audio/Android.mk`
- `hardware/qcom/sdm845/Android.mk`

## GitLab and licensing review

- `external_faceunlock`
- `vendor_gms`

## Non-mirrored GitHub repos intentionally excluded

- `device_google_contexthub`
- `device_google_cuttlefish`
- `device_qcom_sepolicy-legacy-um`
- `device_qcom_sepolicy_vndr_legacy-um`
- `device_qcom_sepolicy_vndr_sm8550`
- `hardware_qcom-caf_bengal_audio`
- `hardware_qcom-caf_bengal_display`
- `hardware_qcom-caf_bengal_media`
- `hardware_qcom-caf_msm8953_audio`
- `hardware_qcom-caf_msm8953_display`
- `hardware_qcom-caf_msm8953_media`
- `hardware_qcom-caf_msm8996_audio`
- `hardware_qcom-caf_msm8996_display`
- `hardware_qcom-caf_msm8996_media`
- `hardware_qcom-caf_msm8998_audio`
- `hardware_qcom-caf_msm8998_display`
- `hardware_qcom-caf_msm8998_media`
- `hardware_qcom-caf_sdm660_audio`
- `hardware_qcom-caf_sdm660_display`
- `hardware_qcom-caf_sdm660_media`
- `hardware_qcom-caf_sdm845_audio`
- `hardware_qcom-caf_sdm845_display`
- `hardware_qcom-caf_sdm845_media`
- `hardware_qcom-caf_sm8150_audio`
- `hardware_qcom-caf_sm8150_display`
- `hardware_qcom-caf_sm8150_media`
- `hardware_qcom-caf_sm8250_audio`
- `hardware_qcom-caf_sm8250_display`
- `hardware_qcom-caf_sm8250_media`
- `hardware_qcom-caf_sm8350_audio`
- `hardware_qcom-caf_sm8350_display`
- `hardware_qcom-caf_sm8350_media`
- `hardware_qcom-caf_sm8550_audio_agm`
- `hardware_qcom-caf_sm8550_audio_pal`
- `hardware_qcom-caf_sm8550_audio_primary-hal`
- `hardware_qcom-caf_sm8550_data-ipa-cfg-mgr`
- `hardware_qcom-caf_sm8550_dataipa`
- `hardware_qcom-caf_sm8550_display`
- `hardware_qcom-caf_sm8550_media`
- `hardware_qcom_sdm845_data_ipacfg-mgr`
- `hardware_qcom_sdm845_display`
- `hardware_qcom_sdm845_media`
- `hardware_qcom_sm7250_display`
- `hardware_qcom_sm7250_media`
- `hardware_qcom_sm8150_data_ipacfg-mgr`
- `hardware_qcom_sm8150_display`
- `hardware_qcom_sm8150_media`
- `vendor_qcom_opensource_data-ipa-cfg-mgr-legacy-um`

**Gate:** this draft PR is for source-graph review. Do not merge or call the port complete without resolving build dependencies and validating on a Linux host.
