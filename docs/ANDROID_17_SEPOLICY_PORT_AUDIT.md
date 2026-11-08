# P0 — system/sepolicy AOSP 17 migration audit

**Date:** 2026-11-03. **Device target:** POCO F5 Pro / Redmi K60 (`mondrian`) only.

**Status:** exact Google AOSP17 SELinux source tree imported, zero PE policy relaxations. Source CI and policy compilation are separate; source integrity is not a substitute for enforcing SELinux on a booted device.

## AOSP17 source identity

- [Official `android-17.0.0_r1` tag](https://android.googlesource.com/platform/system/sepolicy/+/refs/tags/android-17.0.0_r1) object `689b4b99b953ff2c29a2f1b520e9361a7cc7b633`.
- Original release commit `e066568e98d86db31a9346d30977f3632fa7073c`, exact tree `f0e857a84958d5472dee9187c54f7b4f191a415a`.
- [Import #41726344939](https://github.com/PixelExperience-Reborn/system_sepolicy/actions/runs/41726344939) **passed** and created independent [root snapshot `f12e84e0ba4fe3d1cc093af15c41ceb8dba8cc69`](https://github.com/PixelExperience-Reborn/system_sepolicy/commit/f12e84e0ba4fe3d1cc093af15c41ceb8dba8cc69) with identical tree; upstream commit ancestry intentionally condensed.
- `seventeen` (Android14) untouched. The active `default.xml` historical PE routing is not used for Android17 bootstrap.
- Staged [`aosp17_pe_p0_sepolicy.xml`](../aosp17_pe_p0_sepolicy.xml) includes the previous security P0 profile and replaces only `system/sepolicy`, pinned to immutable SHA `f12e84e0ba4fe3d1cc093af15c41ceb8dba8cc69`.

## Selected historical PixelExperience policy deltas

| Old patch | Review and Android17 decision |
| --- | --- |
| [`98e2523e` permit fsck_untrusted SYS_ADMIN](https://github.com/PixelExperience-Reborn/system_sepolicy/commit/98e2523e334b52a61485f83358ac684402ae5510) | Removed `sys_admin` from a strict Android14 `neverallow`; **reject** without a specific supported filesystem requirement and new policy proof. Broadly weakening `fsck_untrusted` is not an acceptable default. |
| [`7e1f8608` permit recovery rootfs mutation](https://github.com/PixelExperience-Reborn/system_sepolicy/commit/7e1f8608d3bb545aaf44f6db7f134275b0e67c11) and [`7efceff2` exempt recovery from mknod neverallow](https://github.com/PixelExperience-Reborn/system_sepolicy/commit/7efceff295c0fda5309c0609fe9228a6cfaba399) | Old global exceptions to writable rootfs / device node creation are security-sensitive and not appropriate as an unconditional Android17 port. Test current AOSP17 recovery first. |
| [`e8b15bc8` exempt data_between_core_and_vendor_violators from vold neverallow](https://github.com/PixelExperience-Reborn/system_sepolicy/commit/e8b15bc804c608b202b383e5179e23631a984987) | Historical workaround for obsolete trusted-zone fingerprint applets writing configuration in vendor data. No proof mondrian requires this workaround. **Reject blind port**, avoid destabilizing FBE and data separation. |
| [`04c19518` `wifi.interface.` label](https://github.com/PixelExperience-Reborn/system_sepolicy/commit/04c195189b5cb0f5d64889e6abe6f5fcf40dbaa4) | **Already present in official AOSP17** at `private/property_contexts` as `u:object_r:wifi_hal_prop:s0 prefix string`. No duplicate rule needed. |

**Important:** In AOSP17 the policy file organization differs from Android14 (for example `public/domain.te` may not exist as it did originally); old patch line numbers and API 34 prebuilts are not an authority for API 37 policy. This is an initial focused review of major PE deltas, not a complete audit of all historic merge commits.

## CI and acceptance

- [Targeted source sync](../.github/workflows/aosp17-p0-sepolicy-source-sync.yml) verifies immutable commit/tree, retains `vold.te` encryption-key ioctl checks and the upstream Wi-Fi HAL property label.
- [Joint 18-P0-project source sync](../.github/workflows/aosp17-p0-source-sync.yml) must confirm all pinned revisions together. Neither source-level check proves that SELinux compiles or enforces correctly.
- Required: full AOSP17 sepolicy CIL compilation, `sepolicy_tests`/`sepolicy-analyze neverallow`, mapping/public API compatibility, VINTF, recovery policy, vendor overlays and relevant CTS/VTS. Validate AVC logs on enforcing boots on mondrian only. Do not flip to permissive or bypass neverallow to hide errors.
- Use the current mondrian device/vendor SELinux policy only after compatibility review. Keep device-specific allow rules scoped to correct labels/domains and do not add global vendor exemptions.

**Unverified:** complete 1069-project sync, SELinux/Soong build, device boot, encryption/AVB, recovery/OTA and radio/vendor tests. Keep source integration in Draft.

## Confirmed source CI

- [system/sepolicy targeted source sync #41726747320](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41726747320) **passed**.
- [Joint 18 selected P0 projects #41726754727](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41726754727) **passed**. No CIL build, SELinux neverallow analysis, VTS or enforcing device boot has yet been demonstrated.
