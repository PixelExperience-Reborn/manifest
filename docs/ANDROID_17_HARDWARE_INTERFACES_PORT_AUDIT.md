# P0 — hardware/interfaces Android 17 bring-up audit

**Date:** 2026-11-03

**Target:** PixelExperience-Reborn Android 17 for POCO F5 Pro / Redmi K60 (`mondrian`) only.

**Status:** exact AOSP17 source snapshot independently verified and imported; one reviewed PE Audio HIDL null-guard change staged in [Draft PR #1](https://github.com/PixelExperience-Reborn/hardware_interfaces/pull/1). Host C++ tests passed; actual Android HAL/VINTF/VTS and mondrian device tests have not run. Old PixelExperience A14 `seventeen` remains unchanged.

## Source and safety

- Official AOSP project: [platform/hardware/interfaces](https://android.googlesource.com/platform/hardware/interfaces/+/refs/tags/android-17.0.0_r1); **not** `platform/frameworks/hardware/interfaces`, `platform/system/hardware/interfaces` or vendor-specific Qualcomm trees.
- Release tag: `android-17.0.0_r1` (annotated tag `32a116715a696303475cf72c01b77f298da084db`).
- Peeled commit: `0162af698935100a590b7359581ac8b1b80693e5`.
- Official tree: `f5630c44a784efc32362ad4a8c51d9707f0e73a6`.
- Existing [PE `seventeen`](https://github.com/PixelExperience-Reborn/hardware_interfaces/tree/seventeen): historical Android14 source; not interchangeable with Android17 AIDL/VINTF.
- [Isolated import branch](https://github.com/PixelExperience-Reborn/hardware_interfaces/tree/port/a17-hardware-interfaces-import-20261103) contains a CI workflow that fetches a shallow/filtered **official** Android17 commit, checks both exact SHAs, then publishes an **independent root snapshot commit** with the official file tree to `port/a17-hardware-interfaces-aosp17-base-20261103`. It explicitly avoids force-pushing, cannot overwrite a differing target, and preserves `seventeen`. It does **not** retain full AOSP ancestry and never claims it does.
- Source-import [GitHub Actions #41705878021](https://github.com/PixelExperience-Reborn/hardware_interfaces/actions/runs/41705878021) was **in progress** when this audit started. No commit/branch existence beyond the staging branch was established yet.
- The separate `aosp17_pe_p0_base.xml` manifest profile deliberately retains Google's AOSP17 `hardware/interfaces` until the reviewed PE snapshot and tests are available.

## Legacy PE patch triage against official Android17 files

The original commits below were inspected, together with the AOSP17 files at exact commit `0162af698935...` from the GitHub mirror of the same Git object. This is a **sample of historically important commits**, not a complete A14 delta audit.

| Legacy PE commit | Android17 observation and decision |
| --- | --- |
| [`f363670a`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/f363670a12bcfccdf67b68e8c356886f6b912fa1) — Audio HIDL `getAudioPortImpl` null guard | In Android17, `audio/core/all-versions/default/Device.cpp` still invokes `halGetter(mDevice, &halPort)` without checking `halGetter` for null. **A small defensive P0 candidate**, provided callback receives `Result::NOT_SUPPORTED` and `Void()` exactly once on null. Must be compiled and tested with the selected legacy HAL path. |
| [`05eced625`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/05eced6257155d867b4b312e28fbb3efdabd595d) — LDAC quality modes | Exact AOSP17 `bluetooth/audio/utils/aidl_session/BluetoothAudioCodecs.cpp` still advertises LDAC `HIGH` only. **Defer** additional `MID/LOW/ABR` until Qualcomm Bluetooth offload provider, headset capability negotiation, VTS and actual session testing confirm support. |
| [`8668ccffd`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/8668ccffd3dca1f24854bee9d2e7f1614d5d5771) — aptX HD 16-bit | Exact AOSP17 aptX HD capabilities still specify 24-bit only. **Defer**, do not advertise an unverified 16-bit capability or conflate aptX and aptX HD. |
| [`a78acfac`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/a78acfac620de24a610f9c8ae341038c7fe311ae) — fingerprint service CPU profile | AOSP17 still uses `ServiceCapacityLow` in a generic HIDL 2.1 fingerprint service. **Defer** changing CPU capacity: this may not be mondrian's running fingerprint service; compare vendor init manifests and power/performance metrics first. |
| [`4133de9d`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/4133de9d5c63c120656a3ce23f2434e884adbb6f), [`2b994cc3`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/2b994cc3a7516e8289d5d091da3d429aea62d55d) — Camera legacy `camera3_stream::reserved` repurposing | **Do not cherry-pick.** Reserved pointers and format override semantics affect ABI/ownership and camera buffer safety. A mondrian vendor HAL contract and exact current AOSP17 path must be inspected before any guarded adaptation. |
| [`a3a6ff5f`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/a3a6ff5fafb07a772828a01461a22931d0b2fd8e) — forced SoundDose implementation | AOSP17 still uses dynamic SoundDose factory loading. **Defer**: its VINTF and implementation ownership differ by vendor. Replacing it risks audio startup, duplicated HAL services or incorrect dose tracking. |
| [`658a8e92`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/658a8e92b370a2cb637c72a2ed2d4faf0ef9c91f) — vendor-specific Keymaster 4.0 tags for FBE | **Reject by default.** Changing old Keymaster tag values without matching KeyMint/vold and vendor TEE support risks encryption/key management failures. |
| [`f814e08f`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/f814e08f0c32ebbda3f85a543ba555010e9e1161) — old FCM V4 compatibility override | **Defer.** Android17 framework compatibility matrix must be authoritative; do not lower VINTF requirements without exact device manifest and vendor evidence. |

## Acceptance sequence

1. Confirm actual published `port/a17-hardware-interfaces-aosp17-base-20261103` commit's Git **tree** equals `f5630c44a784efc32362ad4a8c51d9707f0e73a6` using GitHub's Git API.
2. Create a **distinct working branch from that exact snapshot**. Review every selected diff against AOSP17 before modifying files; never cherry-pick the whole old branch.
3. Begin with a minimal, guarded `getAudioPortImpl` fix only if the compiled Android17 code path and result enums are still valid. Add regression/source checks; no pretended on-device tests.
4. Open a **draft PR** against the pristine verified snapshot and preserve old `seventeen`.
5. Only after an immutable reviewed PE SHA exists: add optional `aosp17_pe_p0_hardware.xml` including `aosp17_pe_p0_base.xml`, `remove-project name="platform/hardware/interfaces"`, and one pinned checkout. Run official `repo manifest` structural checks and targeted Linux `repo sync` to verify the exact SHA.
6. Full AOSP17 platform build, HAL VINTF/VTS, fingerprints, Bluetooth codecs/audio, camera, encryption, power/perf and device boots for mondrian remain hard blockers for declaring completion.

**Current declaration:** source import in progress, historical-delta triage performed. No Android17 HAL patch, build, VINTF result or actual device validation is claimed here.

## Verified bring-up checkpoint (2026-11-03)

- [Source import #41705878021](https://github.com/PixelExperience-Reborn/hardware_interfaces/actions/runs/41705878021) **passed**. GitHub Git API independently confirmed published pristine snapshot commit `965e06d0293443f382676c1ec40b4cdfd2e262ac` with tree **`f5630c44a784efc32362ad4a8c51d9707f0e73a6`** (same as official upstream).
- PE working branch `port/a17-hardware-interfaces-pe-20261103` starts from this verified snapshot. [Production patch `57978c8`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/57978c8eee5e25a47746d6ed9bf0a622353a857c) adds one early `halGetter == nullptr` guard and uses existing `Result::NOT_SUPPORTED` without changing other HAL dispatch behavior.
- Actual production `Device::getAudioPortImpl` function is extracted and compiled as C++17 with minimal fake HAL types by [`test_audio_port_guard.py`](https://github.com/PixelExperience-Reborn/hardware_interfaces/blob/port/a17-hardware-interfaces-pe-20261103/tests/host/test_audio_port_guard.py). The tests exercise absent getter, working getter and conversions that fail before/after dispatch. [CI #41706669761](https://github.com/PixelExperience-Reborn/hardware_interfaces/actions/runs/41706669761) **passed**.
- Draft [hardware_interfaces PR #1](https://github.com/PixelExperience-Reborn/hardware_interfaces/pull/1) isolates precisely `735e364cbdd00b0d6e4dc33ea0866dbb6d971a11`, with production, host test and CI changes only.
- New [`aosp17_pe_p0_hardware.xml`](../aosp17_pe_p0_hardware.xml) includes the previously reviewed base/AV/Recovery/native/core/ART/Bionic source graph, replaces only `hardware/interfaces`, and pins the immutable PR SHA. It does not modify the historical default manifest. New manifest parser and targeted source-sync jobs are required before marking manifest integration verified.
- **Still unverified:** complete Android17 platform build, native HAL compilation, audio VTS, codec offload, fingerprint, camera, KeyMint/FBE, device boots and end-to-end hardware tests on mondrian. Do not merge into production.

- **Manifest verification update:** [P0 hardware source-sync #41706963447](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41706963447) **passed**, confirming actual `repo sync` and pinned SHA with C++ host tests. A subsequent [11-P0-project source-sync #41707153912](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41707153912) **passed** with both `frameworks/base` and `hardware/interfaces`; no full Android compilation was part of it.
