# PixelExperience-Reborn Android 17 — independent mondrian device-tree architecture

Date: 2026-11-04. Status: **PLANNING AND SOURCE BOUNDARY ONLY; NO NEW MONDRIAN DEVICE TREE EXISTS IN THIS MANIFEST AND NO DEVICE BUILD HAS PASSED.**

Target: POCO F5 Pro / Redmi K60 (`mondrian`), Qualcomm SM8475, with selected shared sm8450 platform components. **No other phones are within the device-port scope.**

## 1. Source separation — mandatory

The pre-existing `LF52406/mondrian_android_device_xiaomi_mondrian` and `LF52406/mondrian_android_device_xiaomi_sm8450-common` source branches are **LineageOS-derived reference trees**. The device's original kernel and proprietary repos are also *reference/test inputs*, not approved PE product branches. Review these sources for documented hardware facts, vendor partition paths, firmware, kernel driver interfaces, VINTF HAL instances, encryption flags, init and SELinux labels. **Do not inherit their LineageOS build base or automatically copy their product packages and framework feature implementations.**

The project must create its **own** device repository and common device repository under PixelExperience-Reborn (names to be approved when provisioning). Existing PE-Reborn organization repository checks on 2026-11-04 did **not** find `device_xiaomi_mondrian`, `device_xiaomi_sm8450-common`, `vendor_xiaomi_sm8450-common` or `kernel_xiaomi_sm8450`; their absence is not an invitation to clone a LineageOS tree unchanged.

The build root is official AOSP17 r1 from the reviewed staged `manifest` profile, plus independently reviewed PE changes. The new ROM device products must not call `inherit-product` on `vendor/lineage/config/common_full_phone.mk`, or use `lineage_mondrian`, LineageOS namespace names, `org.lineageos.settings.resources`, `XiaomiParts` or proprietary `vendor.lineage.*` services by default. Such parts may serve as examples, but any actual implementation requires a new explicit design, build proof, device policy and source/license review.

## 2. Proposed native product layout (not yet created)

- `device/xiaomi/mondrian`: independent `AndroidProducts.mk`, PE-Reborn product makefile (`pe_mondrian.mk` or project-approved naming), `BoardConfig.mk`, `device.mk`, device-specific init/overlays, NFC SKU/display/touch and fingerprint configuration.
- `device/xiaomi/sm8450-common`: shared *SM8475-compatible* partition layout, init and fstab, VINTF matrices, HAL-specific configuration, SELinux vendor policy, thermal/power configuration and common product-package definitions; keep everything required only by mondrian while no second device is targeted.
- Vendor extraction/product repo: use legally distributable proprietary blob lists with verifiable sources/checksums, generated extraction/build metadata, correct `vendor`/`odm`/`system_ext` ownership. Do not copy unknown blobs or publish signed keys.
- Kernel + modules + device trees: pin a known-good kernel source revision, Defconfig, DTBO, vendor_dlkm modules, ABI assumptions and toolchain. Do not mistake a standalone AnyKernel zip build for a bootable ROM kernel integration.
- Platform/framework modifications: isolated PE-Reborn framework/Settings patches only when the selected app or HAL genuinely needs them, with precise scope and tests; no implicit LineageOS framework dependencies.
- ROM manifest: after each necessary repository exists with proven source, create a **new opt-in mondrian-only profile** layered on the reviewed AOSP17 source; do **not** inject it directly into baseline or silently activate it in all targets.

## 3. Hardware contract matrix required before Soong integration

| Area | Independent validation required |
| --- | --- |
| Boot/partitions | Device boot chain, dynamic partitions, `super`, AVB/vbmeta, init `fstab` vs recovery `fstab`, target copy-out partitions and OTA metadata |
| Security/FBE/recovery | AOSP17 `fs_mgr`, KeyMint/keymaster, wrapped keys, metadata encryption, rollback protection, recovery mount/decrypt, SELinux neverallow/VTS |
| RIL/IMS | Radio HAL/VINTF, carrier configuration, emergency calling, mobile data, SMS, Wi-Fi Calling / VoLTE only after *real* modem tests |
| Camera | Camera provider HAL, media codecs and recorder, permissions, CTS camera and reliable video capture |
| Display | DRM/HWC/SurfaceFlinger, logical resolution FHD+/WQHD+, ROI/partial update, density, UDFPS and orientation |
| Input/haptics | Touch driver, gestures, pocket detection, vibrator HAL/effects, rate limits, sensor/wakelock safety, no competing control path |
| Connectivity | Wi-Fi/Bluetooth/GNSS, Miracast/WFD, regulatory country-code rules, tethering, NXP NFC HAL/eSE and the selected NFC APEX/platform packaging |
| Audio/thermal/power | Primary audio HAL and offload, codecs, powerhint, thermal throttling, charging health, reverse charging only when tested |
| Storage/media | Official Android17 DownloadProvider/MediaProvider APEX, FUSE/URI grants, photo picker, real OTA data migration |
| UI/product | Native PE Settings integration, own device-specific settings resource owners, EN/RU/UK locale, theme, navigation/landscape, GMS vs no-GMS product independence |

## 4. Native device-settings/resource rule

The historical PE repository `packages_resources_devicesettings` produces `org.pixelexperience.settings.resources`. The *existing Lineage-derived reference* `XiaomiParts` requires `org.lineageos.settings.resources`. **These are not interchangeable**, and the proposed new PE product must not import either merely to satisfy old `XiaomiParts`.

The historical PE resources had 34 duplicate `string/button_swap_summary` declarations across locale qualifiers. The first audit intentionally failed. The isolated [resource collision fix](https://github.com/PixelExperience-Reborn/packages_resources_devicesettings/blob/fix/a17-pe-devicesettings-resource-collisions-20261104/docs/ANDROID_17_RESOURCE_COLLISION_FIX.md) removes only redundant definitions and the [140-locale source regression](https://github.com/PixelExperience-Reborn/packages_resources_devicesettings/actions/runs/41751112647) passed. **Neither this static test nor a renamed Android.bp establishes Android17 aapt2 or XiaomiParts compatibility.**

For the new device product, identify required native resources from the PE feature list, implement/reuse only those with verified symbols and Android17 UI APIs, and package them in a project-specific module with no duplicate resource ownership.

## 5. Build and merge order

1. Keep the staged manifest P0/P1 source graph immutable; verify repo init/sync and source provenance first.
2. Create new PE-Reborn device/common repositories **separately**, referencing but not extending LineageOS product inheritance.
3. Construct the smallest discoverable `lunch` product and ensure `soong_ui` can parse it; build minimal boot/recovery and target-files, without Google packages or optional device features initially.
4. Resolve all VINTF, vendor blobs and kernel/DTBO/modules; validate bootloader, FBE, AVB and recovery **before** adding optional Settings and gaming/UI changes.
5. Build a full AOSP17-derived bootable product and run device bring-up checks on mondrian; collect `logcat`, kernel log, SELinux denials, `lshal`/`vintf` and package manager evidence.
6. Only after the base boots reliably, port PE additions one feature at a time; each feature needs a clear source PR, test, rollback strategy and user-facing changelog grounded in actual fixes.
7. Run Android17 CTS/VTS relevant suites, OTA upgrade/downgrade and data retention tests, and validate GMS/no-GMS configurations before release.

## 6. Release gates and current truth

- [x] Device/base architecture rule documented: Lineage-derived LF52406 trees = **hardware references only**.
- [x] Old PE devicesettings resource dependency mismatch documented.
- [x] Duplicate resources fixed in **isolated** branch, with 140-qualifier source CI PASS.
- [ ] New PE-Reborn mondrian + sm8450-common device trees provisioned and independently authored.
- [ ] Compatible kernel/vendor source graph pinned with checksums, permissions and licenses.
- [ ] Native `lunch` and `m` with Android17 Soong builds.
- [ ] Verified mondrian boot, radio/Wi-Fi/camera/NFC, FBE/AVB/recovery.
- [ ] CTS/VTS/media/security, OTA updates and device regressions.

**Status: none of the last five bring-up gates has passed.** Do not claim the PixelExperience-Reborn Android17 device ROM is built or ready; per-repository source audits are necessary but not sufficient.
