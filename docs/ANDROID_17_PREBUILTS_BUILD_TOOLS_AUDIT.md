# P0 — prebuilts/build-tools AOSP 17 provenance and migration decision

**Date:** 2026-11-03. **Target device:** POCO F5 Pro / Redmi K60 (`mondrian`) only.

**Decision:** retain the Google AOSP17 `platform/prebuilts/build-tools` project in the opt-in source manifest. No PE binary mirror or functional modification is justified until an actual Android17 build exposes a compatibility problem. Verification here is source provenance only, NOT successful execution of prebuilts.

## Verified release identity

- [Official AOSP17 tag](https://android.googlesource.com/platform/prebuilts/build-tools/+/refs/tags/android-17.0.0_r1): `android-17.0.0_r1`.
- Tagged Git object: `b7f999f25436fdd66116017ba9818c95cd12e30f`.
- Peeled official release commit: `9b6c8c6a2f582a9d7817fd8275c8014959c60cc4`.
- Official source tree: `ea52996a4beaea187e897b10ce36bcb913b92e02`.
- Selected `aosp17_reference.xml` checkout: `path="prebuilts/build-tools"`, `name="platform/prebuilts/build-tools"`, groups `pdk,sysui-studio`, clone-depth `1`. The WiFi/ADB staged source profiles inherit this project and **do not** replace it.
- [Provenance CI](../.github/workflows/aosp17-build-tools-provenance.yml) shallow-fetches the official Google tag with `blob:none` and checks the exact commit/tree. This avoids publishing a giant collection of prebuilt executables to GitHub. CI success is not claimed until it completes.

## Historical PE delta triage

- Old [`4ba330fa` "Use system date binary"](https://github.com/PixelExperience-Reborn/prebuilts_build-tools/commit/4ba330fa7bbbaa50fee6ff9597205bea279e96d0) removes a single `path/linux-x86/date` symlink that pointed to `../../linux-x86/bin/toybox`. **Do not blindly cherry-pick.** First determine which `date` the Android17 build environment resolves, why any old override was needed, and whether the host build tools rely on deterministic GNU/Toybox behavior. The full system's reproducibility must be preserved.
- The historical PE `seventeen` repo is a large, old build-tools tree (GitHub reports roughly 3.5 GB of repository size). Its branch is **not** an acceptable Android17 binary replacement without cross-platform executable/ABI validation.
- This row remains audited but **not completed**. A valid outcome for a historical repository can be retaining Google's unmodified project instead of adding unnecessary patches or mirroring huge binaries.

## Remaining gates

1. Official r1 source commit/tree provenance CI must pass.
2. Perform **complete** 1069-project source sync, including required prebuilt blobs, then Soong bootstrap.
3. Confirm `date`, `toybox`, `ninja`, Python/host tool binaries, executable permissions, ELF ABI and launcher paths on the actual build host. Reject host tools from Android14.
4. Run at least one genuine Android17 `m`/Soong target and compare reproducibility logs before considering any build-tools fork.
5. Separate full ROM build, recovery, AVB/OTA, CTS/VTS, and mondrian validation are still unverified.

**No claim:** the ADB and 16-project selected source checks do not download/build every AOSP17 build tool and do not demonstrate a bootable ROM.
