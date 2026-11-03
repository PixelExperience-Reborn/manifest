# Android 17 bring-up profiles — source selection and acceptance

**State: staged, unmerged, and not yet validated with Linux `repo sync`, Soong bootstrap, compilation or boot.**

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

## Why this is a separate profile

We must be able to test the **official Android 17 platform unchanged** before introducing individual PE patches. A successful `repo sync` of the old `default.xml` would still place Android 14-era ART/Bionic/frameworks sources in the tree. This makes source-level failures impossible to attribute reliably.

The 135 project tracker stays complete; a fork moves into a PE bootstrap/bring-up profile only after its baseline and PE-specific delta are separately reviewed and the appropriate checks pass. The count of historical forks is **not** the count of active overrides in an initial AOSP17 bootstrap.

## Native PE environment helpers

In the staged AOSP17 environment profile, core `build/make` stays official and unchanged. Upstream AOSP17 `source_vendorsetup()` automatically loads `vendor/aosp/vendorsetup.sh`, which now sources the existing PE `vendor/aosp/build/envsetup.sh` helper definitions. That preserves native AOSP17 `lunch`, product discovery and release configuration without importing an Android14 build/make fork or applying the old redundant Make hook.

The vendor PR uses GitHub Actions to test Bash syntax, PE breakfast/brunch argument translation, and the `vendorsetup` integration. These checks are not a Soong bootstrap, product build or boot test.

## Required validation gates (not run)

1. On an appropriately provisioned Linux host, use `repo init -u https://github.com/PixelExperience-Reborn/manifest -b port/a17-aosp17-manifest-20261102 -m aosp17_reference.xml` followed by `repo manifest -r` and `repo sync`. Record errors, exact revisions and object identity.
2. Repeat with `-m aosp17_pe_bootstrap.xml`, then each successive `-m aosp17_pe_p0_native.xml`, `aosp17_pe_p0_core.xml`, `aosp17_pe_p0_frameworks.xml` and `aosp17_pe_p0_recovery.xml`. Verify immutable source pins, dependencies, host/Android ABI, compiled Recovery and OTA policy before merging.
3. Run a matched AOSP17 Make/Soong bootstrap and the PE Soong Go test; investigate each failure rather than importing old Android14 fixes wholesale.
4. Check `aosp17_pe_envsetup.xml` against the official `repo` manifest parser and confirm the only added checkout is `vendor/aosp`. Check the vendor shell integration in a full synced AOSP17 environment.
5. Validate build product discovery; later add ONLY mondrian's independent device/vendor/kernel trees, respecting their licensing and appropriate Qualcomm HALs.
6. Before release: product build, target-files, AVB and signing policy, SELinux enforcing, boot, telephony, Wi-Fi, camera, performance, CTS/VTS subsets and OTA upgrade/rollback.

The profiles have undergone static source/name/path checks; a GitHub Actions `repo init` / `repo manifest` parser check has been added for validation. There is still no complete `repo sync` or Android17 build. Do not merge the existing staged manifest PR or advertise a functional Android 17 ROM until the gates pass.
