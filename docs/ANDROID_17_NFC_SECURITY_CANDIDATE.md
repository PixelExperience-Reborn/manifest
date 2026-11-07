# Android 17 NFC — independently pinned modern-source candidate

**Date:** 2026-11-07. **Scope:** NFC Mainline source selection for a future independent PE-Reborn device/product. **NOT** a release/ROM source upgrade.

## Why this candidate exists

The archived NXP `NQNfcNci` app (`vendor/nxp/opensource/commonsys/packages/apps/Nfc`) is Android13-era legacy source. It must not replace the actively staged official `platform/packages/modules/Nfc` or its native APEX. A current, maintained source should be reviewed instead.

- **Current safe default**: official AOSP17 `platform/packages/modules/Nfc`, tag `android-17.0.0_r1`, commit `940212c440f57032a19cf0f90c7faa8eca48d546`, tree `da01c841e3238648d0ae33c3392c05f1552e63d5`.
- **Isolated candidate**: official `android-security-17.0.0_r3`, commit `6f3a074cf6c87a2dcc3970c03462a6970b06f9cd`, tree `ee6a57f5ccc30d113588f6cc5bffff94932bffb5`, tag created 2026-11-02. Compared with r1, 20 paths differ, including `NfcService.java` and routing/native NFC files (verified by row 168 CI).
- **Staging file**: `aosp17_pe_p2_nfc_security_candidate.xml`, includes the existing reviewed P2 graph, replaces *only* its NFC source owner with the exact official commit, preserves checkout path, groups, remote and history, and leaves `default.xml` untouched. There is still exactly one NFC app source owner.

**CRITICAL security caveat:** `android-security-17.0.0_r3` being *tagged in November* does **not** mean it contains every November 2026 Android security fix. Google's AOSP build-numbers index lists build `16267537` with `2026-05-05` security patch level. The November 2026 bulletin includes `CVE-2026-58994` / `A-532588581`, an NFC Service permission-check issue affecting Android17, with published fix source `2a8b421b1d5c5cb82fc52438e352c0a726b7d008`. Do NOT claim the candidate has that patch until exact ancestry/diff/semantic verification and validation on the chosen Android17 branch. Do NOT increase `ro.build.version.security_patch` or ship anything as November-patched based on this profile.

References:
- https://android.googlesource.com/platform/packages/modules/Nfc/+/refs/tags/android-security-17.0.0_r3
- https://source.android.com/docs/setup/reference/build-numbers
- https://source.android.com/docs/security/bulletin/2026/2026-11-01
- https://osv.dev/vulnerability/ASB-A-532588581
- https://github.com/PixelExperience-Reborn/vendor_nxp_opensource_commonsys_packages_apps_Nfc/blob/audit/a17-nxp-nfc-app-mainline-20261107/docs/ANDROID_17_NXP_NFC_APP_MAINLINE_AUDIT.md

## Verification and promotion gates

1. The dedicated CI checks the official `repo manifest` resolved NFC owner and immutable commit, 1069 unique default-selected projects, exact NFC source/tree and preservation of AOSP17 NFC app/APEX/native module declarations. Source-only sync is **not** a Soong build.
2. Audit the November NFC permission fix **against the candidate's `NfcService.java`**, not only Git tag or version string. Independently verify any backport, permissions, tests, related SE and CardEmulation changes; no partial privilege patch without a full test set.
3. Confirm **whole-platform** compatible Android17 security sources (Settings/Framework/Base/SystemUI/Bionic/ART, module SDK interfaces, SE service, NFC HAL) before choosing a release. Avoid a mismatched single Mainline APEX update.
4. Verify Soong and NFC APEX build/linker/signing, stable AIDL VINTF, SELinux enforcing/neverallow, CTS/VTS, OTA/rollback, user/privileged service permissions and device NFC/SE/HCE on independent PE-Reborn mondrian hardware.
5. If any step fails, retain the safe reviewed AOSP17 source graph; do not enable old NXP components as a workaround.

**Decision:** modern NFC Mainline is preferred and the upstream r3 candidate is pinned for verification. A complete November 2026 security-patched ROM is **not** claimed.
