# PixelExperience-Reborn — Android 17 port

**State: preparation only. This is NOT an Android 17 build-ready source tree.**

## Verified baseline (2026-11-02)

- 135 organization repositories, all with `seventeen` as the default branch; initially they contain Android 14-era PE sources.
- The root `default.xml` still targets AOSP `android-14.0.0_r22`. Its project set and `snippets/remove.xml` are Android 14-era.
- The PE snippets list 185 projects. The 135 mirrored GitHub repositories are redirected by this stage to Reborn `refs/heads/seventeen`.
- The other 50 are left on their historical remotes until examined: 48 old/other-SoC/irrelevant repos and the GitLab-only `external_faceunlock` and `vendor_gms`.

## Android 17 reference

Use the official immutable AOSP release tag `android-17.0.0_r1` to establish the baseline:
https://android.googlesource.com/platform/manifest/+/refs/tags/android-17.0.0_r1/default.xml

Do **not** merely change the Android 14 tag string. The list of projects, renamed paths, module dependencies and removals must be rebuilt and validated against Android 17.

## Migration gates (in order)

1. Reconstruct root manifest from AOSP 17 and reapply PE overrides, with only relevant hardware repos; revisit every remove-project and linkfile; resolve old GitLab and GMS redistribution dependencies legally.
2. Port build chain (`build`, `build_soong`, `art`, `bionic`, core prebuilts, `system_core`) with isolated PRs; verify Soong bootstrap.
3. Port framework and UI patches (`frameworks_base`, `frameworks_native`, `frameworks_av`, Settings, PE overlays) after identifying current Android 17 APIs.
4. Port services, modules and security (telephony, Bluetooth, Wi-Fi, connectivity, permission, SELinux and vendor interfaces).
5. Add and test only Xiaomi mondrian / sm8450 device sources, HALs, vendor blobs and kernel.
6. Require real Linux checks: manifest parse, `repo manifest -r`, `repo sync`, Soong bootstrap, full build, boot, enforcing SELinux, key functional and stability tests. Do not merge until the gate passes.

## Upstream merge rules

- Work in per-repository `port/a17-...` branches; do not directly overwrite `seventeen`.
- Confirm repository provenance and Git ancestry. For genuine AOSP forks compare against the exact AOSP Android 17 tag, and preserve PE-specific patches by review/merge/cherry-pick as appropriate. Qualcomm/vendor projects need their own upstream analysis.
- No bulk force-push, no blind reset, and no claim of Android 17 compatibility after just a branch rename or a successful merge.
- Document each upstream tag/commit, conflict resolutions, API changes and test results in a separate PR.

## Important

This first change only repoints **existing** GitHub forks to Reborn; it does not upgrade their code, change the root AOSP 14 manifest, or perform a ROM build.
