# Android 17 manifest entrypoint and source ownership audit

**2026-11-06 | 135-repository matrix row 156: `manifest` | Reviewed source graph; device/build gates OPEN**

## What was actually repaired

The working port branch is `port/a17-aosp17-manifest-20261102`; historical PE `seventeen` is unchanged. This manifest is not an upstream Android framework module, so it must **not** receive an invented two-parent AOSP code merge. Its job is to select and pin independently verified source repositories.

Previously, the port branch's `default.xml` contained the AOSP17 r1 project declarations **plus four historic PE includes**:
- `snippets/remove.xml`
- `snippets/pixel.xml`
- `snippets/pixel-extras.xml`
- `snippets/pixel-caf.xml`

Those snippets were designed for historical PixelExperience projects and could reintroduce unported Android14 platform/service/Qualcomm projects. The previous branch `README.md` also incorrectly prescribed `PixelExperience/manifest -b fourteen`, `--force-sync`, `mka bacon`, and an unsupported product `lunch` command.

In the **isolated A17 port branch only**, `default.xml` now contains exactly one `include` of `aosp17_pe_p2_kernel_configs.xml`. All historical snippets remain in Git and their 135 matching PE forks remain in the matrix, but are **not** transitively imported by the AOSP17 default. The root `README.md` now gives the actual Reborn A17 branch, explicit manifest profile commands, and an honest source-only validation boundary.

## Exact active source selection

- The immutable AOSP `android-17.0.0_r1` project declarations live in `aosp17_reference.xml`; the reference profile removes 16 **other-device** projects while retaining generic and toolchain modules.
- `aosp17_reference.xml`: 1071 declared project paths / 1068 selected by default (three `notdefault` host prebuilts).
- `aosp17_pe_envsetup.xml` introduces `vendor/aosp`, increasing later profiles to 1072 declared / 1069 selected by default.
- The final `aosp17_pe_p2_kernel_configs.xml` uses exactly one owner at each platform path. In addition to P0/P1 exact-source PE forks, it selects the previously reviewed P2 pins:
  - `hardware/qcom/wlan`: `PixelExperience-Reborn/hardware_qcom_wlan` at `667daa664e107f0de451b9046a12da74b99a0e6b`.
  - `hardware/ril`: `PixelExperience-Reborn/hardware_ril` at `29ea93bac3efe871c54f86b05713f894575dc6b8`.
  - `kernel/configs`: `PixelExperience-Reborn/kernel_configs` at `d02620f1f46af9eef024fb41e6d911d935699492`.
- The final default does **not** activate `device/xiaomi/mondrian`, `device/xiaomi/sm8450-common`, old `hardware/qcom-caf/wlan`, `device/qcom/sepolicy`, `vendor/lineage`, old privileged Settings, FaceUnlock or unreviewed PE app repositories.
- Official platform-owned `external/avb`, `build/make`, `packages/apps/Settings`, `system/netd` and related security/service repos remain pinned to AOSP17 until a specifically tested port exists.

The manifest source validator now verifies **both** all 25 individual staged profiles and the `default.xml` entrypoint's exact source-owner, SHA and path equivalence to the last reviewed profile. CI's official `repo manifest` validation includes the default entrypoint in addition to the previous 25 profiles.

## Required gates before claiming this port 'ready'

1. Run `python3 tools/validate_aosp17_base_profiles.py` and `python3 tools/validate_135_repository_matrix.py` on the exact current HEAD. These are **offline structural checks**, not an Android build.
2. Run official Google `repo init -m default.xml` and `repo manifest -o resolved.xml` at the exact reviewed branch revision, validate that 1069 default-selected checkouts have no duplicate owner and the expected protected paths.
3. Run a complete or appropriately scoped pinned `repo sync`, then actual `soong_ui`/Make bootstrap and a generic AOSP17 product. A manifest parser check does **not** check headers, ABI, VINTF, SELinux, Mainline/APEX or product dependencies.
4. Author an independent PE-Reborn device/common product using the existing mondrian/SM8450 modern LineageOS trees **as reference material**; do not auto-import device sources into the platform-only graph.
5. Test the physical POCO F5 Pro / Redmi K60 (mondrian): boot/recovery/OTA, GKI 5.10 compatibility, vendor interfaces, radio, audio, camera, display, Wi-Fi, GNSS, enforcing SELinux, FCM, VTS and CTS as applicable. Licensed GMS is never supplied or enabled by this manifest audit.

**CI provenance caveat:** previously recorded manifest workflows reached SUCCESS at an **older** Nov 4 commit. They do not validate the newest branch HEAD unless a new run specifically reports that commit. A current pass of an upstream-source CI in another repo is also not a `repo manifest` or Soong build pass.

**Decision:** manifest source entrypoint migrated and repository graph safety gates improved; **platform build and device integration remain OPEN**. Do not merge Draft PR #2 into `seventeen` until the appropriate checks pass.

**Next matrix row (not part of this change):** 157, `platform_testing`.
