# P0 — frameworks/av: PixelExperience delta review for AOSP17

**Scope:** media/codec2, camera, audio and display stack in the new PixelExperience-Reborn AOSP17 platform. Only POCO F5 Pro / Redmi K60 (`mondrian`) will be targeted for device validation. Source/manifest checks do not imply a usable media stack.

## Verified upstream and branch strategy

- Official upstream: `https://android.googlesource.com/platform/frameworks/av`, AOSP `refs/tags/android-17.0.0_r1`.
- Original upstream commit: **`475269ec44acec82792be6b01fb8e16357d4d2c8`**, tree **`6205f7fbf4fdd2c4b4197b02e960c5bac05b9cd1`**.
- Clean baseline with **full Git history**: [`port/a17-frameworks-av-aosp17-base-20261103`](https://github.com/PixelExperience-Reborn/frameworks_av/tree/port/a17-frameworks-av-aosp17-base-20261103). Official SHA and tree validated by [GitHub Actions](https://github.com/PixelExperience-Reborn/frameworks_av/actions/runs/41636963530).
- Isolated PE delta: [`port/a17-frameworks-av-pe-20261103`](https://github.com/PixelExperience-Reborn/frameworks_av/tree/port/a17-frameworks-av-pe-20261103); [draft PR #1](https://github.com/PixelExperience-Reborn/frameworks_av/pull/1) targets the clean baseline so the review contains only intentional PE changes.
- Historical `seventeen` (Android14-era) remains untouched. No direct merge of old framework files.

## Reviewed historical PixelExperience changes

| Historical PE change | Evidence and decision |
| --- | --- |
| [`977b3894` — CCodec buffer handling](https://github.com/PixelExperience-Reborn/frameworks_av/commit/977b3894d6c1) | **Adapted** to AOSP17. When the caller does not request a component buffer and no weak reference remains, release the client references without an unnecessary `asC2Buffer()`. Implemented in `FlexBuffersImpl::releaseSlot()` and `BuffersArrayImpl::returnBuffer()` by [`37aedd83`](https://github.com/PixelExperience-Reborn/frameworks_av/commit/37aedd8390fc32b615c335f8ef7c4e7759bd7a88). |
| [`5aa39625` — USB camera event argument check](https://github.com/PixelExperience-Reborn/frameworks_av/commit/5aa396256d67) | **Already in official AOSP17**: `CameraService::notifySystemEvent()` checks `args.size() != 1`. No duplicate patch. |
| [`22b279d7` — NuPlayer reset CHECK removal](https://github.com/PixelExperience-Reborn/frameworks_av/commit/22b279d71a2d) | **Deferred.** AOSP17 still has the decoder-state assertions. Removing them without verifying reset/flush states risks hiding actual corruption; needs NuPlayer lifecycle tests and crash evidence. |
| [`74c7329a` — configurable Miracast resolution](https://github.com/PixelExperience-Reborn/frameworks_av/commit/74c7329a2afa) | **Deferred / old path absent.** The historical `media/libstagefright/wifi-display/source/WifiDisplaySource.cpp` does not exist at that location in the checked AOSP17 tree. Find the actual A17 WFD provider or HAL implementation before porting. |
| [`f2510813` — expose auxiliary system cameras](https://github.com/PixelExperience-Reborn/frameworks_av/commit/f251081330bd) | **Rejected from generic platform bring-up.** Changes the classification of system-only cameras and could expose privileged camera devices to all third-party apps. |
| [`1227af86` — bypass system-camera permission](https://github.com/PixelExperience-Reborn/frameworks_av/commit/1227af864b04) | **Rejected.** Dropping `SYSTEM_CAMERA` permission checks is not a safe platform compatibility fix. |
| [`571d5689` — audio capture for WFD](https://github.com/PixelExperience-Reborn/frameworks_av/commit/571d568954dd) | **Deferred.** Changes audio-recording privilege logic. Requires an AOSP17 audio policy and media projection permissions audit; do not weaken capture permissions without narrowly scoped proof. |
| [`661b04ac`, `a6394cb4` — Codec2 pipeline/logging](https://github.com/PixelExperience-Reborn/frameworks_av/commit/661b04ac749f) | **Deferred.** Validate against AOSP17 hardware decoder pipeline, actual frame pacing and the Soong test build before choosing performance changes. |
| [`9a720b01` — media XML override](https://github.com/PixelExperience-Reborn/frameworks_av/commit/9a720b011784) | **Deferred.** Resolve current Android17 device-specific media profiles and proprietary HAL capabilities first. |

The table covers identified high-impact commits, **not every historical `frameworks/av` commit**. Unreviewed changes are not implicitly approved.

## Tests and status

- Actual production code change: [`37aedd83`](https://github.com/PixelExperience-Reborn/frameworks_av/commit/37aedd8390fc32b615c335f8ef7c4e7759bd7a88) affects two buffer-release paths only.
- Two Android gtest regression cases were added to the **existing `ccodec_unit_test`** in [`f9b6ba82`](https://github.com/PixelExperience-Reborn/frameworks_av/commit/f9b6ba824d38fa497ee0414fa7db1de1927f273e). They compare observable conversion/ref-clearing counts with a missing output pointer.
- [Source CI passed](https://github.com/PixelExperience-Reborn/frameworks_av/actions/runs/41638077335) for both code paths, registered tests and patch whitespace. This is **only a source validation**. The gtests themselves have not yet been compiled/run, and the full Android build is not available.
- Source graph: [`aosp17_pe_p0_av.xml`](../aosp17_pe_p0_av.xml) pins `5db9a6151f33cacb810a8fe7615be8c23d3fa858` and inherits the earlier AOSP17 P0 overrides without old Android14 platform code. Official `repo manifest` parser CI passed with **1069 default-selected projects**.

## Remaining acceptance gates — NOT done

1. Full `repo sync`, compatible Android17 Make/Soong bootstrap and target build; compile `libsfplugin_ccodec`, `ccodec_unit_test`, CameraService and AudioPolicy.
2. Actually run the new Codec2 gtests, media CTS/VTS subsets, decoder/encoder tests and stress tests, including null buffer and flush/release paths.
3. On mondrian: verify hardware codecs, playback, audio capture permissions, wired/Bluetooth routing, camera UVC/aux behavior and Miracast with real vendor/HAL stack.
4. Verify camera and audio permission checks still protect sensitive resources; resolve any legitimate device-specific needs in the appropriate vendor/HAL layer.
5. Only after successful tests, consider remaining PE enhancements, approve the draft PR, and prepare downstream integration and OTA policy.

**Status: AOSP17 source imported and two PE Codec2 guards ported, with Android gtests added and static CI passed. Not yet compiled, booted or device validated.**
