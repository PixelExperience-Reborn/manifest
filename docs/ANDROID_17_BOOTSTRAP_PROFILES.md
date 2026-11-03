# Android 17 bring-up profiles — source selection and acceptance

**State: staged and unmerged. Selected P0-project `repo sync` and SHA pin checks have passed on Linux CI; complete 1069-project sync, Soong bootstrap, Android compilation and boot are not yet validated.**

The 135 PixelExperience-Reborn forks are kept as historical PE source references. Their default branches are named `seventeen`, but most contain Android 14 code. **Do not use the four PE override snippets as a ready-to-build AOSP 17 source graph.**

## Profiles in this manifest repository

| Profile | Purpose | Active project graph (static) | Android 14 PE code |
| --- | --- | --- | --- |
| [`aosp17_reference.xml`](../aosp17_reference.xml) | Clean AOSP 17 comparison baseline | 1087 AOSP declared, 16 removed = **1071 declared / 1068 repo-selected** | **None** |
| [`aosp17_pe_bootstrap.xml`](../aosp17_pe_bootstrap.xml) | Test source compatibility of the first PE Soong port against the otherwise unchanged AOSP17 project graph | 1070 AOSP + 1 PE Soong = **1071 declared / 1068 repo-selected** | **None intentionally enabled** |
| [`aosp17_pe_envsetup.xml`](../aosp17_pe_envsetup.xml) | Use AOSP17 Make/Soong plus PE vendor functions from the native vendorsetup hook | 1070 AOSP + 1 PE Soong + 1 PE vendor = **1072 declared / 1069 repo-selected** | **None intentionally enabled** |
| [`aosp17_pe_p0_native.xml`](../aosp17_pe_p0_native.xml) | PE ART and Bionic repositories at verified immutable official AOSP17 commits | **1072 declared / 1069 repo-selected** | No ART/Bionic PE patches imported |
| [`aosp17_pe_p0_core.xml`](../aosp17_pe_p0_core.xml) | Above + exact official AOSP17 system/core source tree from PE fork | **1072 declared / 1069 repo-selected** | No System Core PE patches imported |
| [`aosp17_pe_p0_frameworks.xml`](../aosp17_pe_p0_frameworks.xml) | Above + official AOSP17 frameworks/native mirrored with full history | **1072 declared / 1069 repo-selected** | Frameworks Native PE changes are not yet ported |
| [`aosp17_pe_p0_recovery.xml`](../aosp17_pe_p0_recovery.xml) | Above + reviewed AOSP17 PE Recovery changes | **1072 declared / 1069 repo-selected** | PE device title and optional-safe stage parsing only |
| [`aosp17_pe_p0_av.xml`](../aosp17_pe_p0_av.xml) | Above + official AOSP17 frameworks/av and selectively ported PE Codec2 release guards | **1072 declared / 1069 repo-selected** | Reviewed Codec2 delta only, Android gtests not executed |
| [`aosp17_pe_p0_base.xml`](../aosp17_pe_p0_base.xml) | Above + verified AOSP17 frameworks/base exact-tree snapshot and reviewed PE legacy-toast styling | **1072 declared / 1069 repo-selected; repo sync PASS** | One XML source change, standalone host tests; Android framework build and device runtime not tested |
| [`aosp17_pe_p0_hardware.xml`](../aosp17_pe_p0_hardware.xml) | Above + exact-tree AOSP17 hardware/interfaces snapshot and guarded HIDL audio `get_audio_port` callback | **1072 declared / 1069 repo-selected; targeted repo sync PASS** | C++17 host contract test PASS, Android HAL/VTS and device testing pending |
| [`aosp17_pe_p0_bluetooth.xml`](../aosp17_pe_p0_bluetooth.xml) | Above + AOSP17 packages/modules/Bluetooth snapshot and PE OPP URI null-authority fix | **1072 declared / 1069 repo-selected; joint 12-project sync PASS** | Java 17 host test PASS; module/APEX build and device testing pending |
| [`aosp17_pe_p0_connectivity.xml`](../aosp17_pe_p0_connectivity.xml) | Above + exact AOSP17 Connectivity tree without PE network-policy patches | **1072 declared / 1069 repo-selected; 13-source sync PASS** | Source checks only; NetworkStack/APEX build and device tests pending |
| [`aosp17_pe_p0_permission.xml`](../aosp17_pe_p0_permission.xml) | Above + exact AOSP17 Permission module tree, zero old PE permission patches | **1072 declared / 1069 repo-selected; parser/targeted sync PASS** | Versioned role guards reviewed, Android Permission/APEX/CTS tests pending |
| [`default.xml`](../default.xml) | Existing **experimental historical PE staging manifest**, NOT safe for a build | 1016 AOSP projects + 135 PE fork routes = **1151 projects** | **Many unported forks still active** |

**Project counts:** 1087 AOSP project declarations minus 16 unrelated device removals leaves 1071 declared checkouts. The official `repo manifest` default selection further excludes 3 upstream `notdefault` Darwin prebuilts (`prebuilts/clang/host/darwin-x86`, `prebuilts/go/darwin-x86` and `prebuilts/rust-toolchain/darwin`). Therefore 1068 AOSP/Soong projects and 1069 projects with the PE vendor are exported by `repo manifest`. These upstream entries are retained, not deleted.

### AOSP source

- AOSP release: `refs/tags/android-17.0.0_r1`. The reference profile retains the official AOSP project layout and build/make, ART, Bionic, system/core and other platform dependencies.
- Unrelated device trees removed: Amlogic Yukawa; Google ATV/contexthub/cuttlefish/sdv/trout/car; Linaro Dragonboard/HiKey and corresponding kernel projects (16 exact removals in these profiles).
- AOSP `device/common`, `device/generic/*` and `device/sample` remain because the generic platform tools/targets may depend on them. These are **not** third-party mondrian device trees and do not constitute a new port for other phones.
- None of these profiles includes proprietary GMS, an unrelated device tree, or a mondrian-specific target. These are controlled later through licensed GMS and a **mondrian-only** device manifest.

### PE Soong port, immutable pin

- Repository: `PixelExperience-Reborn/build_soong`.
- Remote: `https://github.com/PixelExperience-Reborn/build_soong`.
- Source revision: **`6215d41c790a463b7795ce81ac77204c238cbf48`**, with `upstream=refs/heads/port/a17-soong-dumpvars-20261103` for repo fetch.
- Original AOSP `build/soong` `linkfile` entries for `root.bp` and `bootstrap.bash` have been retained.
- The PE profile deliberately omits the AOSP superproject acceleration metadata because a custom project revision replaces one upstream project.
- Changes staged in Soong: PE banner variable display, `installclean` removal of `*.zip.sha256sum`, and a regression test. No Linux Soong build/Go test result is claimed.

## P0 source provenance

- `art`: upstream AOSP17 commit `b753cf97923c3695338d21466fa14c57b480a59a`, identical full-history import into [our ART branch](https://github.com/PixelExperience-Reborn/art/tree/port/a17-art-aosp17-base-20261103). Verified tree `539d87e9b7c4b00b7f1443cca44578c5b9f6e5b2`.
- `bionic`: upstream AOSP17 commit `06356e41c5ed7b12220b24c05ba4fdb873b126a7`, identical full-history import into [our Bionic branch](https://github.com/PixelExperience-Reborn/bionic/tree/port/a17-bionic-aosp17-base-20261103). Verified tree `31f89de9fffb766531426cc6ea69d20a5c1c8093`.
- `system/core`: upstream AOSP17 commit `545d2487e38192a2ce25040897ced877cf6b4f53`; [our System Core branch](https://github.com/PixelExperience-Reborn/system_core/tree/port/a17-system-core-aosp17-base-20261103) uses a parentless snapshot commit `8e0f22aaac0ee4114a83646e2c96d07578145bfa` with the **exact same upstream tree** `332cc42dfc29e8660d45b2c27ddc7c2ad4925868`. GitHub rejected the full official history due to an unrelated 219 MB historical blob. Only the history was condensed; source files were not altered.
- `frameworks/native`: complete official Android17 Git history imported at `ae266dcb706d083868578cfedce381ef44488a07` (tree `d0554d8875771ee2702dc51448d6b24a761bbe7a`), with no unreviewed PE patches.
- `bootable/recovery`: official AOSP17 base `080f671785c84ae1ac38797fe1fa7364d158fab4` (tree `08502f068321cd5d00b80a189b2362e6b2bbc5da`) and separate reviewed PE-ported branch pinned at `0ed8dc4f93020555afdfc19141263ca40629ef74`. [Audit and safety decisions](ANDROID_17_RECOVERY_PORT_AUDIT.md). C++17 stage parser host tests and source-level signature policy guards passed; full recovery compilation and device testing have not.
- Old PE commits remain on the `seventeen` branches. Neither the legacy ART performance switches, Bionic hosts/linker/memory-hardening changes nor System Core property/AVB bypasses have been blindly cherry-picked onto AOSP17.
- The `repo` project graph is parsed by CI for these profiles; this confirms correct paths and pins, **not** ABI compatibility, full sync, Go tests, a product build, Verified Boot or working ROM.

- `frameworks/av`: official full-history AOSP17 source commit `475269ec44acec82792be6b01fb8e16357d4d2c8` (tree `6205f7fbf4fdd2c4b4197b02e960c5bac05b9cd1`), then two PE Codec2 buffer release guards and new Android gtests in working branch `port/a17-frameworks-av-pe-20261103`. Pinned commit `5db9a6151f33cacb810a8fe7615be8c23d3fa858`. [Delta and security audit](ANDROID_17_FRAMEWORKS_AV_PORT_AUDIT.md). Source CI and manifest parser CI passed, but `ccodec_unit_test` compilation/execution still required.

## Why this is a separate profile

We must be able to test the **official Android 17 platform unchanged** before introducing individual PE patches. A successful `repo sync` of the old `default.xml` would still place Android 14-era ART/Bionic/frameworks sources in the tree. This makes source-level failures impossible to attribute reliably.

The 135 project tracker stays complete; a fork moves into a PE bootstrap/bring-up profile only after its baseline and PE-specific delta are separately reviewed and the appropriate checks pass. The count of historical forks is **not** the count of active overrides in an initial AOSP17 bootstrap.

## Native PE environment helpers

In the staged AOSP17 environment profile, core `build/make` stays official and unchanged. Upstream AOSP17 `source_vendorsetup()` automatically loads `vendor/aosp/vendorsetup.sh`, which now sources the existing PE `vendor/aosp/build/envsetup.sh` helper definitions. That preserves native AOSP17 `lunch`, product discovery and release configuration without importing an Android14 build/make fork or applying the old redundant Make hook.

The vendor PR uses GitHub Actions to test Bash syntax, PE breakfast/brunch argument translation, and the `vendorsetup` integration. These checks are not a Soong bootstrap, product build or boot test.

## Verified Linux source synchronization (not a product build)

[GitHub Actions run 41639702260](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41639702260) executed the official `repo sync` on Linux for nine exact AOSP17/PE P0 checkout paths and verified each resulting HEAD commit against its pinned SHA: `build/make` (official AOSP17 r1 `5ce6f787337d`), `build/soong`, `vendor/aosp`, `art`, `bionic`, `system/core`, `frameworks/native`, `bootable/recovery` and `frameworks/av`.

This proves the selected projects actually download and resolve to their chosen Git revisions. It does **not** prove that the other AOSP17 projects can all be synced, or that linker/Soong/Java/Kotlin dependencies compile.

## Required validation gates (not run)

1. On an appropriately provisioned Linux host, use `repo init -u https://github.com/PixelExperience-Reborn/manifest -b port/a17-aosp17-manifest-20261102 -m aosp17_reference.xml` followed by `repo manifest -r` and `repo sync`. Record errors, exact revisions and object identity.
2. Repeat with `-m aosp17_pe_bootstrap.xml`, then each successive `-m aosp17_pe_p0_native.xml`, `aosp17_pe_p0_core.xml`, `aosp17_pe_p0_frameworks.xml`, `aosp17_pe_p0_recovery.xml` and `aosp17_pe_p0_av.xml`. Verify immutable source pins, dependencies, host/Android ABI, compiled Recovery/Codec2 and OTA policy before merging.
3. Run a matched AOSP17 Make/Soong bootstrap and the PE Soong Go test; investigate each failure rather than importing old Android14 fixes wholesale.
4. Check `aosp17_pe_envsetup.xml` against the official `repo` manifest parser and confirm the only added checkout is `vendor/aosp`. Check the vendor shell integration in a full synced AOSP17 environment.
5. Validate build product discovery; later add ONLY mondrian's independent device/vendor/kernel trees, respecting their licensing and appropriate Qualcomm HALs.
6. Before release: product build, target-files, AVB and signing policy, SELinux enforcing, boot, telephony, Wi-Fi, camera, performance, CTS/VTS subsets and OTA upgrade/rollback.

The profiles have passed `repo init` / `repo manifest` parser checks. A real Linux `repo sync` of **nine selected P0 projects** also passed, but the full 1069-project checkout, Android17 Make/Soong bootstrap, product build and boot remain untested. Do not merge the existing staged manifest PR or advertise a functional Android 17 ROM until the gates pass.

- `frameworks/base`: official AOSP17 commit `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`; verified tree `908a2ce43657451526181a33ee94fc688add3117`; full-history push failed on GitHub HTTP 500, so the successful [snapshot commit](https://github.com/PixelExperience-Reborn/frameworks_base/commit/2a0f0690a4ec4fa914dd68ddb41289e1d3ff6bea) preserves the exact official tree while replacing ancestry. [Reviewed draft PR](https://github.com/PixelExperience-Reborn/frameworks_base/pull/1) pins `382d5c9c0b20bbdb67b70176bce02c7e64767b0c` with a one-line theme-aware PE legacy Toast adaptation and source-level tests. See [technical audit](ANDROID_17_FRAMEWORKS_BASE_PORT_AUDIT.md). Targeted [Linux repo sync](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41701334864) and pinned SHA/host XML resource tests passed. [Nine essential P0 paths](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41701334951) also synced successfully on the updated manifest; [nine manifest profile graphs](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41701334891) passed structural checks. This **does not establish** framework compilation, an Android image or successful mondrian boot. AOSP17 build and mondrian tests are pending.


## Hardware Interfaces P0: staging and decisions

- Official `hardware/interfaces` AOSP17 tag `android-17.0.0_r1` peels to **`0162af698935100a590b7359581ac8b1b80693e5`**, tree **`f5630c44a784efc32362ad4a8c51d9707f0e73a6`**. This is NOT the separate `frameworks/hardware/interfaces` checkout.
- A strictly isolated import workflow is staged at [`hardware_interfaces/port/a17-hardware-interfaces-import-20261103`](https://github.com/PixelExperience-Reborn/hardware_interfaces/tree/port/a17-hardware-interfaces-import-20261103). Its sole target is `port/a17-hardware-interfaces-aosp17-base-20261103`, which remains **unconfirmed until the CI publishes and independently verifies its SHA/tree**.
- The old PE `seventeen` branch is Android14-era code and remains unchanged. No hardware/interfaces override is included in `aosp17_pe_p0_base.xml` while the source import is pending.
- [Detailed hardware/interfaces patch review](ANDROID_17_HARDWARE_INTERFACES_PORT_AUDIT.md) classifies legacy AIDL Bluetooth audio, C++ HIDL Audio, Camera, fingerprint and keymaster patches without blind porting. Full source sync, VINTF/VTS and device tests are outstanding.

- `hardware/interfaces`: official AOSP17 commit `0162af698935100a590b7359581ac8b1b80693e5`, tree `f5630c44a784efc32362ad4a8c51d9707f0e73a6`. Its exact-tree snapshot is [`965e06d0293443f382676c1ec40b4cdfd2e262ac`](https://github.com/PixelExperience-Reborn/hardware_interfaces/commit/965e06d0293443f382676c1ec40b4cdfd2e262ac); historical A14 `seventeen` is untouched. [Draft PR #1](https://github.com/PixelExperience-Reborn/hardware_interfaces/pull/1) pins `735e364cbdd00b0d6e4dc33ea0866dbb6d971a11`, adds a null function-pointer guard, and compiles the actual C++ function with host mocks. [Audio CI #41706669761](https://github.com/PixelExperience-Reborn/hardware_interfaces/actions/runs/41706669761) passed. [Opt-in manifest profile](../aosp17_pe_p0_hardware.xml) isolates the replacement; real repo sync, Android HAL build/VINTF/VTS and mondrian hardware tests remain required.

- `packages/modules/Bluetooth`: official AOSP17 commit `c77db469de80f86660bc053bec4dee0c5d4b947c`, exact tree `385b36982cbe1daeb61471ab16ebad099aeb78b1`. Independent clean [source snapshot](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/8fbbdd62fc1ad3e0b252428d8b9134f9e3f3ad06) preserves this tree and leaves `seventeen` unchanged; the snapshot intentionally omits upstream Git ancestry. [Draft PR #1](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/pull/1) pins `e7c2f47e3c73c4f2b83f03145441e419f45124b3` and ports one null-safe OPP URI comparison; actual Java method host tests passed in [CI #41707947445](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/actions/runs/41707947445). [Opt-in manifest profile](../aosp17_pe_p0_bluetooth.xml) and targeted Linux source sync are the next gates. Full Java/APEX build, controller tests, CTS/VTS and mondrian device tests are still required.

- [Bluetooth targeted source-sync #41708380563](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41708380563) **passed**: immutable Bluetooth HEAD and source-extracted Java host tests. [Eleven profile structure checks #41708380008](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41708380008) **passed**; the new 12-P0-project combined `repo sync` was still running at the last check. This is still not a full AOSP/PE Android compilation.

- **Twelve selected P0 source projects** synchronised and checked successfully in [manifest CI #41708380062](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41708380062). This includes pinned commit SHA checks and source-extracted C++/Java/Python tests; it does **not** include Soong/Make compilation or a device image.

## Next P0 candidate — Connectivity

- Official AOSP17 tag `android-17.0.0_r1` in `platform/packages/modules/Connectivity` resolves to commit `347fbd34b368d19f0d87e908ea101eed3601a731`, tree `3a9df5486bd2b0d48cf22a4df8b8e097d36da07d`. Only `packages/modules/Connectivity` is in scope; other framework-t and network stacks are separate repositories as declared by the AOSP manifest.
- The historical PE `TrafficStats` change is already addressed by dynamic `Log.isLoggable(TAG, Log.DEBUG)` in AOSP17; the DUN bypass cannot be accepted without carrier-aware requirements and verification. **No PE code change is currently justified.**
- [Exact-source import workflow](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/tree/port/a17-connectivity-import-20261103) is running in [GitHub Actions #41713047058](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/actions/runs/41713047058). The final branch is **not** to be activated in any manifest until its published commit/tree are independently checked. Do not touch `seventeen`.
- [Technical comparison](ANDROID_17_CONNECTIVITY_PORT_AUDIT.md). Android17 Connectivity module compilation, tethering and carrier tests on mondrian remain pending.

- `packages/modules/Connectivity`: original AOSP17 commit `347fbd34b368d19f0d87e908ea101eed3601a731`, official tree `3a9df5486bd2b0d48cf22a4df8b8e097d36da07d`. Verified owned [snapshot `701882b51546230c6c32c9654a3f7b9814429e13`](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/commit/701882b51546230c6c32c9654a3f7b9814429e13) preserves the exact original file tree, but not original Git ancestry. Source-import [GitHub Actions #41713047058](https://github.com/PixelExperience-Reborn/packages_modules_Connectivity/actions/runs/41713047058) **passed**. No PE production-code changes are justified: AOSP17 already implements runtime TrafficStats logging, and carrier DUN policy must remain intact. Opt-in [`aosp17_pe_p0_connectivity.xml`](../aosp17_pe_p0_connectivity.xml) is staged for immutable SHA/tree and joint 13-project Linux source sync. No Android17 build or device testing has been performed.

- `packages/modules/Permission`: official AOSP17 tag `android-17.0.0_r1` source commit `1093eca7407576c72e51b1a88550ee0667a6e5dc`, tree `5f0dfec33529cfff7ad08c9e61f480e445a59d8b`. Exact source snapshot [`f6e6e14b5c4d6e094c205683940a1328384338d9`](https://github.com/PixelExperience-Reborn/packages_modules_Permission/commit/f6e6e14b5c4d6e094c205683940a1328384338d9) was independently verified via GitHub API, import [Actions #41714168389](https://github.com/PixelExperience-Reborn/packages_modules_Permission/actions/runs/41714168389) passed. Old managed-profile notification access fix is already present in API-versioned Android17 role classes. Broader usage history UI is deferred pending history storage and metrics review. This project has **zero PE code delta**; [opt-in manifest profile](../aosp17_pe_p0_permission.xml) and targeted source checks were staged, with Android APEX compilation and CTS/VTS still pending.

- [13 P0 project combined source sync #41713844843](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41713844843) **passed**. [13 manifest profiles #41714646564](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41714646564) and [targeted Permission source/tree & managed-role checks #41714659988](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41714659988) **passed**. Joint 14-source sync remains separately unverified. Full framework/APEX compilation, permission/role runtime tests, CTS/VTS and mondrian boot still pending.
