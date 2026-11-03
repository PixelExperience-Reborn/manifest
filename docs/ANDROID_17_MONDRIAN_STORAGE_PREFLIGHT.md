# P1 — mondrian storage, recovery and KeyMint compatibility preflight

**Date:** 2026-11-04. **Status:** source-level compatibility review only. **Not a runtime test.** Device: POCO F5 Pro / Redmi K60 (`mondrian`).

This review relies on the existing owned device and proprietary vendor repositories at immutable `lineage-24.0` commits, not on a guessed Xiaomi encryption configuration.

## Pinned source evidence

- [sm8450-common root fstab](https://github.com/LF52406/mondrian_android_device_xiaomi_sm8450-common/blob/6e0022f5100e09ac97980095b6ed8528f4ff823f/rootdir/etc/fstab.qcom) and [recovery fstab](https://github.com/LF52406/mondrian_android_device_xiaomi_sm8450-common/blob/6e0022f5100e09ac97980095b6ed8528f4ff823f/rootdir/etc/recovery.fstab), device tree revision `6e0022f5100e09ac97980095b6ed8528f4ff823f`.
- [BoardConfigCommon.mk](https://github.com/LF52406/mondrian_android_device_xiaomi_sm8450-common/blob/6e0022f5100e09ac97980095b6ed8528f4ff823f/BoardConfigCommon.mk) sets `TARGET_RECOVERY_FSTAB := $(COMMON_PATH)/rootdir/etc/recovery.fstab`. Thus the distinct recovery table is a real configured build input, not merely an unused historical file.
- [Proprietary vendor package makefile](https://github.com/LF52406/proprietary_vendor_xiaomi_sm8450-common/blob/1d5437c0f615b45ad2315d78d9efa7eb78247d32/sm8450-common-vendor.mk), revision `1d5437c0f615b45ad2315d78d9efa7eb78247d32`, includes both `android.hardware.keymaster@4.1-service-qti` and `android.hardware.security.keymint-service-qti`, together with their init configuration; [KeyMint VINTF fragment](https://github.com/LF52406/proprietary_vendor_xiaomi_sm8450-common/blob/1d5437c0f615b45ad2315d78d9efa7eb78247d32/proprietary/vendor/etc/vintf/manifest/android.hardware.security.keymint-service-qti.xml) declares `IKeyMintDevice/default`, `ISharedSecret/default`, and `ISecureClock/default`.
- [AOSP17 vold source](https://android.googlesource.com/platform/system/vold/+/refs/tags/android-17.0.0_r1), commit `6d20a0078c2bcaa2499dc5d032f337bfe1182d9e`, exact tree `8a39be56cc76830d199878b5ea854022a71d3af2`; [own snapshot](https://github.com/PixelExperience-Reborn/system_vold/commit/76516faf8c3bd5e0eb330611a40793cd137f1f8a) matches it.

## Observed device configuration — important differences

| Area | Main `fstab.qcom` | `recovery.fstab` | Consequence |
| --- | --- | --- | --- |
| `/data` filesystem | `f2fs`, inlinecrypt, `checkpoint=fs`, `fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized+wrappedkey_v0` | `f2fs` with older `fileencryption=ice,wrappedkey`, also `checkpoint=fs` | **Must reconcile before testing AOSP17 recovery**. Different flags may select incompatible encryption-policy parsers; do not guess which will decrypt existing user data. |
| `/metadata` | ext4 first-stage mount; `/data` uses `keydirectory=/metadata/vold/metadata_encryption` and `metadata_encryption=aes-256-xts:wrappedkey_v0` | ext4 first-stage mount with additional `wrappedkey` flag | Do not migrate or rewrite existing keys before evaluating exact fs_mgr, KeyMint and kernel crypto compatibility. |
| `/system`, `/vendor`, `/product` and related logical partitions | Several system partitions specified as `erofs` | Recovery table still lists `ext4` for major logical partitions | **Potential recovery mount incompatibility** when partition images are actually EROFS. Verify real build image types and required recovery mount behavior. |
| Vendor security HAL | Both AIDL KeyMint and legacy Keymaster 4.1 services included by vendor makefile | Same vendor blob set; actual runtime selection not tested | Presence of both services is not proof which hardware implementation vold/keystore will use or whether a CAF-specific FBE tag is necessary. |

## Decisions and release gates

1. **Do not cherry-pick CAF/QSSI FBE_ICE code** into `vold` or `system/security` because the blobs contain Keymaster 4.1. Verify runtime HAL instance and exact fstab semantics first.
2. Before a recovery build, review `TARGET_RECOVERY_FSTAB` against current shipped filesystems and the Android17 fs_mgr parser. Any fix belongs to a **mondrian-only device policy/configuration change** with a separate PR/test, not a platform-wide global override.
3. Before first boot with old user data, have a full backup and verified restoration path. Prepare a clean non-production test device if possible. Do not use `fastboot erase userdata` or format as a debugging shortcut.
4. Verify `fileencryption` policy, wrapped keys, `metadata_encryption`, inline crypto, keydirectory, F2FS checkpoint and mounting with Android17 `vold`, fs_mgr, keystore2, SELinux and shipped Qualcomm vendor services.
5. Build and test the relevant modules, recovery image and AVB/OTA chain; then examine KeyMint service registration, `vold` logs, AVC denials, mounting results, encrypted direct boot, credential unlock and reboot. Passing a source-level Git tree check is not proof of data compatibility.

**Critical open risk:** the recovery table differs in both encryption and system filesystem options from the main fstab. This requires resolution or explicit validation before calling the ROM and recovery bootable on mondrian.

## Source CI result

- [Targeted vold source sync #41734986161](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41734986161), [19-profile manifest structure #41734986061](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41734986061), and [combined 20-source checkout #41734995050](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41734995050) **passed**. These CI checks validate selected source revision and structure only. They do **not** resolve the mismatches in this report or prove encryption/recovery correctness.
