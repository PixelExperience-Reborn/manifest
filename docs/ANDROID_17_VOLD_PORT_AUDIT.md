# P1 — system/vold AOSP17 storage and encryption migration audit

**Date:** 2026-11-04. **Device:** POCO F5 Pro / Redmi K60 (`mondrian`) only.
**Status:** exact AOSP17 source import and official Git tree PASS; no PE vold functional delta; new P1 manifest and selected sync CI pending; full build, FBE and on-device tests not run.

## Official source provenance

- Original Google repository: [`platform/system/vold` at `android-17.0.0_r1`](https://android.googlesource.com/platform/system/vold/+/refs/tags/android-17.0.0_r1).
- Annotated tag `9287cdc9c63597ec00f856dac55546825ec539f5`, peeled commit `6d20a0078c2bcaa2499dc5d032f337bfe1182d9e`, exact tree `8a39be56cc76830d199878b5ea854022a71d3af2`.
- [Import CI #41734536933](https://github.com/PixelExperience-Reborn/system_vold/actions/runs/41734536933) **PASS**. GitHub Git API independently confirmed isolated parentless [snapshot `76516faf8c3bd5e0eb330611a40793cd137f1f8a`](https://github.com/PixelExperience-Reborn/system_vold/commit/76516faf8c3bd5e0eb330611a40793cd137f1f8a) with identical tree. Google history was not mirrored.
- Historical PE `system_vold` branch `seventeen` is not changed. New [`aosp17_pe_p1_vold.xml`](../aosp17_pe_p1_vold.xml) extends P0 update_engine and pins just `system/vold` to `76516faf8c3bd5e0eb330611a40793cd137f1f8a`. It is opt-in; `default.xml` stays unchanged.

## Targeted historical PE-vs-AOSP17 review

| Old PE change | Finding | Port decision |
| --- | --- | --- |
| [`3dfe30c8` additional wrapped-key/FBE_ICE key generation](https://github.com/PixelExperience-Reborn/system_vold/commit/3dfe30c8af7df4a14b969bb9ccd4041ceef070e5) | Adds nonstandard `KM_TAG_FBE_ICE` to KeyMint/legacy keymaster parameters, modifies v1 fscrypt key reference handling and wrapped-key opt-in. Official AOSP17 `KeyStorage.cpp` and `FsCrypt.cpp` do not contain this tag. | **Defer** pending fstab, hardware KeyMint service, TEE and existing FBE key compatibility confirmation. Modifying persisted key formats without evidence risks data inaccessibility. |
| [`5fbf0115` and `58368e0d` metadata wrapped-key](https://github.com/PixelExperience-Reborn/system_vold/commit/5fbf0115c688c99393c82e63fb45b23f3955e25d) | Uses `/metadata` fstab's `wrapped_key` flag and extra legacy metadata encryption behavior. Official AOSP17 `MetadataCrypt.cpp` does not include old helper. | **Defer**. Review actual `/metadata`, `/data` and inline-crypt fstab parameters plus kernel/fscrypt versions on mondrian. |
| [`61fb0582` F2FS/ext4 mount DIRSYNC for adopted storage](https://github.com/PixelExperience-Reborn/system_vold/commit/61fb0582155ff080e0c1cc69fe00358d1e5d7086) | Changed mount flags on adopted volumes; Android17 storage mounting architecture differs. | **Do not cherry-pick** without adopted volume support requirement and filesystem test matrix. |
| [`02f035f4` public volume fsck security domains](https://github.com/PixelExperience-Reborn/system_vold/commit/02f035f417d8de15cfa89c052769435bcf577305) | Old ext4/F2FS external filesystem checks distinguished trusted and untrusted fsck contexts, linked to PE public-volume extensions. | **Defer** until reviewing contemporary vold fsck approach, SELinux `fsck_untrusted`, `PublicVolume` and actual device storage exposure. |
| [`6a0b26c9` public volume custom mount options](https://github.com/PixelExperience-Reborn/system_vold/commit/6a0b26c911a5cb5abc221f4e5a4991da38c3cb9b) | Old changes passed additional external volume fstype/mountopts through DiskSource and `ext4::Mount`/`f2fs::Mount`. | **Defer**. This is not evidence of a platform-wide internal F2FS requirement for mondrian. |

This is a **targeted first-pass review**, not an exhaustive range-diff of every old PE commit or translation.

## AOSP17 invariants

- Exact Git tree is the strongest source identity check. Targeted source CI separately guards that `FsCrypt.cpp` still contains normal volume fscrypt option handling, `MetadataCrypt.cpp` contains metadata encryption mount logic, `KeyStorage.cpp` contains no unreviewed `KM_TAG_FBE_ICE`, and `IdleMaint.cpp` retains `RunIdleMaint`/TRIM pathways.
- Existing local **Storage Refresh** in the mondrian product must be reviewed against Android17 `vold` APIs as an independent integration. Source presence alone does not mean the Settings button or F2FS maintenance still works.
- Never rewrite, wipe, reformat or experimentally migrate **existing** user encryption metadata without a tested recovery path and backups.

## Acceptance gates

1. [Manifest P1 source profile](../aosp17_pe_p1_vold.xml), [targeted source sync](../.github/workflows/aosp17-p1-vold-source-sync.yml), and [20 selected P0/P1 source checkouts](../.github/workflows/aosp17-p0-source-sync.yml) must each complete successfully.
2. On an actual Linux builder, **fully sync** the Android17 project graph, compile `vold`, `vdc`, `fs_mgr`, F2FS/ext4 helpers and related `keystore2`, SELinux, KeyMint integrations with Soong, then run module/host/CTS/VTS tests.
3. Review **actual mondrian** fstab in device and vendor trees, `fileencryption`, `metadata_encryption`, `wrappedkey`, inline-crypt, kernel fscrypt/UFS capabilities, KeyMint HAL interface and vendor services. Static source review cannot establish which are in use.
4. Validate cold boot, direct-boot CE/DE unlock, lockscreen credential change, recovery access where supported, storage key rotation, internal F2FS integrity/trim/GC, volume maintenance and OTA data preservation on disposable test data or with backups.
5. Avoid global SELinux `neverallow` relaxations, unverified Keymaster vendor tags or masking encryption failures with destructive formats.

**Unverified:** complete 1069 default-selected source projects, platform compilation and packaged ROM, FBE/metadata runtime, signed OTA and mondrian boot. Keep the manifest Draft.

## Device-tree evidence: encryption and recovery mismatch

- The dedicated [mondrian storage compatibility preflight](ANDROID_17_MONDRIAN_STORAGE_PREFLIGHT.md) identifies the **actual** main fstab's `wrappedkey_v0` FBE/metadata encryption, recovery fstab's older `ice,wrappedkey` parameters, and EROFS-versus-ext4 partition type differences. `BoardConfigCommon.mk` explicitly selects this recovery fstab. This is a concrete outstanding recovery integration risk, not just a general future test item.
- The vendor makefile also contains both KeyMint AIDL and Keymaster 4.1 services. Their presence does **not** justify blindly adding old `KM_TAG_FBE_ICE` code; verify runtime HAL behavior and compatible ciphertext/key formats first.
- [P1 targeted vold source check #41734986161](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41734986161) and [19-profile structure check #41734986061](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41734986061) **passed**. Joint 20 selected-project CI was still running at this checkpoint.

## Combined CI milestone

- [Combined 20-source P0/P1 run #41734995050](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41734995050) **passed** on manifest commit `3132a920f55d4681c77d5c4b73cd905cf2fd0803`. All selected source SHAs and predefined host/source checks passed; no actual `vold` module compilation or device FBE test was performed.
- The next [mondrian fstab and vendor KeyMint audit](ANDROID_17_MONDRIAN_STORAGE_PREFLIGHT.md) is a separate required gate before boot/recovery claims. The two fstab files differ substantially.
