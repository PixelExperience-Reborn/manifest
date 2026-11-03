# Android 17 bring-up profiles — source selection and acceptance

**State: staged, unmerged, and not yet validated with Linux `repo sync`, Soong bootstrap, compilation or boot.**

The 135 PixelExperience-Reborn forks are kept as historical PE source references. Their default branches are named `seventeen`, but most contain Android 14 code. **Do not use the four PE override snippets as a ready-to-build AOSP 17 source graph.**

## Profiles in this manifest repository

| Profile | Purpose | Active project graph (static) | Android 14 PE code |
| --- | --- | --- | --- |
| [`aosp17_reference.xml`](../aosp17_reference.xml) | Clean AOSP 17 comparison baseline | 1087 official AOSP projects, 16 unrelated device trees removed = **1071 projects** | **None** |
| [`aosp17_pe_bootstrap.xml`](../aosp17_pe_bootstrap.xml) | Test source compatibility of the first PE Soong port against the otherwise unchanged AOSP17 project graph | 1070 official AOSP projects + 1 reviewed PE Soong work branch = **1071 projects** | **None intentionally enabled** |
| [`default.xml`](../default.xml) | Existing **experimental historical PE staging manifest**, NOT safe for a build | 1016 AOSP projects + 135 PE fork routes = **1151 projects** | **Many unported forks still active** |

### AOSP source

- AOSP release: `refs/tags/android-17.0.0_r1`. The reference profile retains the official AOSP project layout and build/make, ART, Bionic, system/core and other platform dependencies.
- Unrelated device trees removed: Amlogic Yukawa; Google ATV/contexthub/cuttlefish/sdv/trout/car; Linaro Dragonboard/HiKey and corresponding kernel projects (16 exact removals in these profiles).
- AOSP `device/common`, `device/generic/*` and `device/sample` remain because the generic platform tools/targets may depend on them. These are **not** third-party mondrian device trees and do not constitute a new port for other phones.
- Neither profile includes proprietary GMS, an unrelated device tree, or a mondrian-specific target. These are controlled later through licensed GMS and a **mondrian-only** device manifest.

### PE Soong port, immutable pin

- Repository: `PixelExperience-Reborn/build_soong`.
- Remote: `https://github.com/PixelExperience-Reborn/build_soong`.
- Source revision: **`6215d41c790a463b7795ce81ac77204c238cbf48`**, with `upstream=refs/heads/port/a17-soong-dumpvars-20261103` for repo fetch.
- Original AOSP `build/soong` `linkfile` entries for `root.bp` and `bootstrap.bash` have been retained.
- The PE profile deliberately omits the AOSP superproject acceleration metadata because a custom project revision replaces one upstream project.
- Changes staged in Soong: PE banner variable display, `installclean` removal of `*.zip.sha256sum`, and a regression test. No Linux Soong build/Go test result is claimed.

## Why this is a separate profile

We must be able to test the **official Android 17 platform unchanged** before introducing individual PE patches. A successful `repo sync` of the old `default.xml` would still place Android 14-era ART/Bionic/frameworks sources in the tree. This makes source-level failures impossible to attribute reliably.

The 135 project tracker stays complete; a fork moves into a PE bootstrap/bring-up profile only after its baseline and PE-specific delta are separately reviewed and the appropriate checks pass. The count of historical forks is **not** the count of active overrides in an initial AOSP17 bootstrap.

## Required validation gates (not run)

1. On an appropriately provisioned Linux host, use `repo init -u https://github.com/PixelExperience-Reborn/manifest -b port/a17-aosp17-manifest-20261102 -m aosp17_reference.xml` followed by `repo manifest -r` and `repo sync`. Record errors, exact revisions and object identity.
2. Repeat with `-m aosp17_pe_bootstrap.xml`. Confirm only the expected Soong source differs from the reference checkout and the pinned commit exists.
3. Run a matched AOSP17 Make/Soong bootstrap and the PE Soong Go test; investigate each failure rather than importing old Android14 fixes wholesale.
4. Validate build product discovery; later add ONLY mondrian's independent device/vendor/kernel trees, respecting their licensing and appropriate Qualcomm HALs.
5. Before release: product build, target-files, AVB and signing policy, SELinux enforcing, boot, telephony, Wi-Fi, camera, performance, CTS/VTS subsets and OTA upgrade/rollback.

The manifest profiles above have undergone **static source/name/path checks only**, not an actual `repo init` / `repo sync` or full build. Do not merge the existing staged manifest PR or advertise a functional Android 17 ROM until the gates pass.
