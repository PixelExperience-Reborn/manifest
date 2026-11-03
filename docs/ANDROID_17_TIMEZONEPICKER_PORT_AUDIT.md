# P1 — frameworks/opt/timezonepicker Android 17 migration audit

**Date:** 2026-11-04. **Device:** POCO F5 Pro / Redmi K60 (`mondrian`) only.
**State:** official AOSP17 source imported as an exact Git tree; historical PE UI/API changes reviewed but not ported; Android build/UI tests pending.

## Official source identity and staged manifest

- Google [`android-17.0.0_r1`](https://android.googlesource.com/platform/frameworks/opt/timezonepicker/+/refs/tags/android-17.0.0_r1), tag object `8cdc80c09a9fc34455d196741763feec53877b08`, commit `32f38a793edf8659b21055e16cadd6e912fefcff`, exact tree `5561969c791e41a211ae706fa40f82fca83cc3c0`.
- [Import GitHub Actions #41742248811](https://github.com/PixelExperience-Reborn/frameworks_opt_timezonepicker/actions/runs/41742248811) **passed**; [exact-tree root snapshot `7a5698b6c651db16f243fe8d3d28008e4243e04c`](https://github.com/PixelExperience-Reborn/frameworks_opt_timezonepicker/commit/7a5698b6c651db16f243fe8d3d28008e4243e04c) independently matches the official tree. Root snapshot intentionally has no original Google commit ancestry.
- The AOSP17 reference manifest **does** contain `frameworks/opt/timezonepicker` as `platform/frameworks/opt/timezonepicker` in groups `pdk-cw-fs,pdk-fs`. New [`aosp17_pe_p1_timezonepicker.xml`](../aosp17_pe_p1_timezonepicker.xml) inherits P1 telephony and overrides only this path, pinned to the immutable snapshot. No default.xml edits.
- The Android17 library is still named `android-opt-timezonepicker`; its upstream `Android.bp` defines `sdk_version: "17"` with no AndroidX static library dependency. Its `TimeZonePickerDialog.java` imports `android.app.DialogFragment` and layout `time_zone_item.xml` uses `?android:attr/selectableItemBackground`.

## Original PixelExperience modifications and decisions

| Historical PE commit | What previous developers changed | Android17 decision |
| --- | --- | --- |
| [`d9ffdb80`](https://github.com/PixelExperience-Reborn/frameworks_opt_timezonepicker/commit/d9ffdb809f2bee5ac68c59ed4457ff9454d6e166) | Migrated from deprecated `android.app.DialogFragment` to `androidx.fragment.app.DialogFragment`; also changed `sdk_version` to `current` and added `androidx.fragment_fragment` dependency. | **Defer by default.** It changes the public Java type and consumer requirements. Confirm Settings callers, AndroidX version, Soong dependencies and API 17 compile before any migration. |
| [`30416fcd`](https://github.com/PixelExperience-Reborn/frameworks_opt_timezonepicker/commit/30416fcd479c0c4619eae4d6fec3839ab4e40d06) | Swapped selectable background to generic `itemBackground` for dark-theme rendering. | **Optional UI delta**, only if verified against current themes and accessibility focus. AOSP17 already has a selectable background. |
| [`14e90d68`](https://github.com/PixelExperience-Reborn/frameworks_opt_timezonepicker/commit/14e90d689715b5f555b5664a5afd6ba3f297c749) | Added `android:foreground="?android:attr/selectableItemBackground"` to restore ripple effect after the background change. | **Treat together** with the background patch: avoid one-sided drawable changes. Verify actual touch ripple, list focus, dark mode, light mode and performance. |

## Required integration gates

1. [Structural CI](../.github/workflows/aosp17-manifest-structure.yml) should resolve all **21** profiles, including unchanged 1069 selected checkouts for this opt-in source replacement.
2. [Targeted source CI](../.github/workflows/aosp17-p1-timezonepicker-source-sync.yml) validates immutable snapshot SHA/tree and checks Java API contract and XML resource syntax.
3. [Combined 22-project selected-source sync](../.github/workflows/aosp17-p0-source-sync.yml) checks the cumulative P0/P1 graph. The selected project set is **not** the full 1069-project sync.
4. Real Android17 `m android-opt-timezonepicker` / Soong build and consumer build are mandatory. Test rendering and selection on mondrian with light/dark themes, accessibility, screen reader, large fonts, localization, fragment lifecycle and time zone selection persistence. Confirm that any current Settings UI actually calls this library.
5. Only port an old PE UI/API delta to a separate reviewed A17 branch if it offers proven value and source/test compatibility. Never label a Git-tree or XML source check as a successful Soong Android build.

**Unverified:** entire Android17 checkout and compilation, Settings consumer linkage, on-device time zone picker display/behavior, CTS/VTS and mondrian boot. Manifest remains Draft.
