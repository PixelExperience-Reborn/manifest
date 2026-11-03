# P0 — system/security Android 17 migration audit

**Date:** 2026-11-03. **Target:** POCO F5 Pro / Redmi K60 (mondrian). **State:** exact official AOSP17 security source imported; no security code modifications, no full platform/device test.

## Verified provenance

- Official Google [`android-17.0.0_r1`](https://android.googlesource.com/platform/system/security/+/refs/tags/android-17.0.0_r1) tag object `5f9b5fa68fb3864e50bc95c14aee16791a0939a3`.
- Official AOSP17 commit `cbb2ef1617a94d6cdf2dc2ccb7a545575dbb20cb`, exact Git tree `dcea0071b9c34f1542c576b3f46fc14d1fb14823`.
- [GitHub import #41725595398](https://github.com/PixelExperience-Reborn/system_security/actions/runs/41725595398) **passed**; independently checked owned root [snapshot `a939bea3461e668355b1df87230f9308a8d50837`](https://github.com/PixelExperience-Reborn/system_security/commit/a939bea3461e668355b1df87230f9308a8d50837) has exactly Google's Git tree. Only history is condensed; it does not represent a full-history import.
- Legacy `system_security` branch `seventeen` (Android14) remains intact.
- Source is staged by [`aosp17_pe_p0_security.xml`](../aosp17_pe_p0_security.xml), inheriting the reviewed adb profile, overriding just `system/security`, and pinning immutable snapshot `a939bea3461e668355b1df87230f9308a8d50837`. No historical default manifest changes.

## Previous PixelExperience code compared with Android17

- Historical [commit `da216ccc`](https://github.com/PixelExperience-Reborn/system_security/commit/da216ccceb9b4117720051f9d735fbd7ce15940e), `keystore2/src/km_compat/km_compat.cpp`, explicitly adds `KM_TAG_FBE_ICE` and injects its boolean form into the **legacy Keymaster 4.0 generateKey parameter list**.
- The old patch's own test note says boot was verified with **QSSI 12.0 / Keymaster 4.0 and 4.1**. This is not evidence of need or compatibility with AOSP17 and mondrian.
- AOSP17 `keystore2/src/km_compat/km_compat.cpp` still implements `KeyMintDevice::generateKey`, the `convertKeyParametersToLegacy(extractGenerationParams(inKeyParams))` path and legacy `mDevice->generateKey`, but does **not** contain the old `KM_TAG_FBE_ICE` injection.
- **Decision: defer.** The nonstandard tag and its encoding may interact differently with current KeyMint interfaces, the device TEE, wrapped keys and FBE/metadata encryption. Never introduce a vendor-specific crypto tag without a proven need, explicit HAL contract and recovery plan. Confirm whether mondrian uses modern AIDL KeyMint, legacy Keymaster, or another vendor wrapper before any port.
- This is a review of the selected PE-specific Keymaster change, **not a full range-diff of every old upstream merge**. Other historical changes remain candidates for later targeted audit.

## Acceptance stages

1. [Targeted Linux source CI](../.github/workflows/aosp17-p0-security-source-sync.yml) must confirm committed source HEAD and exact upstream tree. Static source guards confirm no unexpected FBE_ICE port, not runtime correctness.
2. [Joint 17-project P0 source CI](../.github/workflows/aosp17-p0-source-sync.yml) must sync the whole selected graph with pinned SHA values.
3. Compile actual Android17 KeyMint adapters, keystore2 Rust/C++, fsverity, ondevice-signing and related security modules with appropriate Soong dependencies. Run relevant unit/CTS/VTS.
4. On mondrian, verify actual KeyMint/Keymaster instance, VINTF service version, Keymaster extension support, generated key persistence, credential unlock, FBE, metadata encryption, recovery decrypt (if available), AVB state and encrypted OTA boot behavior. Avoid destructive encryption tests without recoverable backups.
5. Only then create a separate tested PE delta branch/PR if a concrete missing function can be reproduced and fixed. No security fallbacks or policy relaxations to hide a failing HAL.

**Unverified:** full 1069-project sync, Android17 Soong compilation, signing, runtime, KeyMint/FBE/CTS/VTS, recovery, OTA and device boot. The manifest remains Draft.
