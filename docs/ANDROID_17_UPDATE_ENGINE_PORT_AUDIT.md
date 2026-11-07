# P0 — system/update_engine Android17 migration and OTA security audit

**Date:** 2026-11-03. **Device target:** POCO F5 Pro / Redmi K60 (`mondrian`) only.

**Status:** exact official AOSP17 release source verified and published, zero PE security-bypass deltas. Android OTA build, signed payloads, AB/Virtual A/B, rollback and device tests have not run.

## Source provenance

- Official Google [`android-17.0.0_r1`](https://android.googlesource.com/platform/system/update_engine/+/refs/tags/android-17.0.0_r1), annotated tag `68b3634adfe39649ea804f12af0c72c733d397c5`, commit `4591637f51644f5429f9e2fe589ab22b92f61842`, tree `9eb8e796382bcd0b4366526766ccd08d15503ab2`.
- [GitHub source import #41727182476](https://github.com/PixelExperience-Reborn/system_update_engine/actions/runs/41727182476) **passed**.
- Independently checked GitHub snapshot commit [`c0309b604010b9b2e2c58d684e86b6090b74ad77`](https://github.com/PixelExperience-Reborn/system_update_engine/commit/c0309b604010b9b2e2c58d684e86b6090b74ad77) has the exact official Git tree, but not Google's full history. Historic Android14 PE `seventeen` is unchanged.
- [`aosp17_pe_p0_update_engine.xml`](../aosp17_pe_p0_update_engine.xml) inherits the staged sepolicy profile, replaces **only** `system/update_engine`, and pins this immutable revision.

## Rejected dangerous historical changes

| Old PE change | What it does and decision |
| --- | --- |
| [`8ad36a28` "Always disable signature and downgrade checks"](https://github.com/PixelExperience-Reborn/system_update_engine/commit/8ad36a2873a8055e90d95c86227727b803c4be53) | Makes `HardwareAndroid::AllowDowngrade()` return true regardless of properties, and makes `PayloadVerifier::VerifySignature()` return true without checking a signature. **Reject unconditionally for the project.** |
| [`c28ce0d5` "Don't verify payload signatures in recovery"](https://github.com/PixelExperience-Reborn/system_update_engine/commit/c28ce0d5b200663b04001c35f37a4a74324d6f93) | Bypasses `ValidateMetadataSignature` and `VerifySignature` for recovery builds via `__ANDROID_RECOVERY__`. **Reject.** Recovery is not a reason to accept unauthenticated payloads. |

## Android17 unchanged code verified

- `aosp/hardware_android.cc`: `AllowDowngrade()` requires both `ro.ota.allow_downgrade` and `ro.debuggable`.
- `payload_consumer/payload_verifier.cc`: `VerifySignature` requires nonempty `public_keys_` and processes payload signatures, without unconditional success.
- `payload_consumer/delta_performer.cc`: `ValidateMetadataSignature` checks payload metadata, and `payload_verifier->VerifySignature` checks the payload signature; no Android14-style `__ANDROID_RECOVERY__` skip exists around these calls.
- These are **source-level checks**, not proof of runtime secure update handling. The true OTA threat model also involves keys, payload signing, AVB rollback index, update metadata, slot management, recovery, init and bootloader.

## CI and next gates

1. [Targeted Linux source sync](../.github/workflows/aosp17-p0-update-engine-source-sync.yml) checks the immutable source commit/tree and original signature/downgrade conditions.
2. [Combined nineteen-project P0 source sync](../.github/workflows/aosp17-p0-source-sync.yml) extends the AOSP17 source graph and repeats the checks. Wait for CI, do not claim success early.
3. Build actual `update_engine`, `update_engine_sideload`, payload generator and relevant OTA components using the AOSP17 Soong environment. Run unit tests for payload signatures, downgrade blocking, recovery verification, dynamic partition/snapshot and AVB handling.
4. With mondrian-specific build and verified signing keys, safely test **signed** A/B OTA, incremental/full update, Virtual A/B snapshot/merge where supported, rollback rejection and recovery sideload. Never use production user data for destructive validation.
5. Only then decide any PE update UX/backend changes; never relax cryptographic verification or rollback protections to resolve an OTA failure.

**Still unverified:** full 1069-project repo sync, platform/Soong build, APK/APEX/product signing, device recovery/OTA, SELinux/VINTF and mondrian boot. Keep manifest PR in Draft.

## Confirmed source CI checkpoint

- [18-profile manifest structure #41727616461](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41727616461) **passed**.
- [update_engine targeted Linux repo sync #41727616362](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41727616362) **passed** exact snapshot SHA, Google Git tree, unchanged OTA signature-verification source, and debug-gated downgrade policy.
- The [joint 19-source P0 sync #41727616297](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41727616297) remained **in progress** at this checkpoint. Android payload tests and real signed OTA are still pending.
