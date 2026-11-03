# P0 — Wi-Fi Android 17 migration review

**Date:** 2026-11-03. **Target device:** POCO F5 Pro / Redmi K60 (`mondrian`) only.

**Status:** official AOSP17 source commit/tree identified and source import workflow launched; no verified clean Wi-Fi snapshot ref at the time of writing. No PE Wi-Fi patch has been applied, no Wi-Fi Android17 build or device tests have run.

## Exact source identity

- Google repository: [platform/packages/modules/Wifi](https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/tags/android-17.0.0_r1)
- Release tag: `android-17.0.0_r1`; annotated tag object `95d3a4a22d0ec1cc41209e96046cfbed99d3a922`.
- Peeled commit: **`67beff9acf0e91046d2a9a36a68cb06ef263d1f1`**.
- Official tree: **`9d1062a94a9d7c7c4f4ef86a834154e2001f8114`**.
- Historical [PixelExperience `seventeen`](https://github.com/PixelExperience-Reborn/packages_modules_Wifi/tree/seventeen): Android14-based; preserve without changes.
- [Isolated import branch](https://github.com/PixelExperience-Reborn/packages_modules_Wifi/tree/port/a17-wifi-import-20261103) contains an Actions job that verifies the exact Google commit and tree before attempting a non-forced root snapshot upload. It does **not** retain full AOSP ancestry. Target `port/a17-wifi-aosp17-base-20261103` may be used only after the Actions job **succeeds** and the GitHub Git API independently confirms the tree SHA. [Import run #41717006140](https://github.com/PixelExperience-Reborn/packages_modules_Wifi/actions/runs/41717006140).

## Legacy PixelExperience change review against exact AOSP17

| Historical PE change | Official AOSP17 finding | Decision |
| --- | --- | --- |
| [`772a5084` Ignore Miracast internal connectivity scans](https://github.com/PixelExperience-Reborn/packages_modules_Wifi/commit/772a5084ae5adbf35856be6a19c5de3308d09314) | Old PE A14 modifies `ClientModeImpl`, `WifiConnectivityManager.startForcedSingleScan` and `WifiP2pServiceImpl.setMiracastMode`; adds stateful suppression whenever P2P group and source/sink mode are active. Exact AOSP17 sources still have `startForcedSingleScan` and P2P Miracast mode handling, but no matching suppression hooks or state fields. `ClientModeImpl` uses a reworked common P2P state handler. | **Defer.** Could suppress reconnect/watchdog/roaming scans and cause stale state or Wi-Fi-to-Wi-Fi switching failures. Needs explicit work-source, P2P session lifecycle, Wifi toggle, multi-STA and WFD performance tests on mondrian before a minimal redesigned change. No blind cherry-pick. |
| [`39349c5b` Notify country-code listener when country code unchanged](https://github.com/PixelExperience-Reborn/packages_modules_Wifi/commit/39349c5b29bba3cf1243444e66fc296536e549c7) | Exact AOSP17 `WifiCountryCode.java` calls `handleCountryCodeChanged(country)` on driver change and updates timestamp, country, P2P metrics and listeners without the obsolete old equality early return. | **Already in AOSP17.** Do not duplicate. |
| Remaining historical merges and translations | Initial inspection covered selected meaningful changes, not a full historical range-diff. | Individually review only if evidence shows a necessary unique PE behavior; no wholesale merge. |

## Required integration gates

1. Import exact official Wi-Fi tree and independently verify published SHA/tree against Google's tag. Refuse overwrites and preserve `seventeen`.
2. With no reviewed PE functional delta yet, prefer **pure AOSP17 source**; if a future WFD fix is needed, create a distinct working branch and draft PR with unit tests.
3. Add opt-in `aosp17_pe_p0_wifi.xml` manifest profile including the previous Permission graph, replacing **only** `packages/modules/Wifi` at a verified immutable commit SHA. Validate all profiles by `repo manifest` parser and targeted Linux `repo sync`, compare exact commit and tree SHA.
4. Extend joint P0 selected-source CI from 14 to 15 pinned source projects and verify source semantics against the old patch regressions.
5. Compile actual Android17 Wi-Fi module/APEX build targets and run WifiService, connectivity manager, CountryCode and P2P tests. Validate Wi-Fi AIDL/HIDL services, Qualcomm vendor and regulatory integration.
6. On **mondrian** test 2.4/5/6 GHz only as hardware/region support permits, WPA2/WPA3, scan/roam/sleep/resume, hotspot, tethering, STA+P2P, Miracast start/stop/remote display, multi-STA if supported, MAC privacy, airplane mode and recovery from disconnect.

**No bootable-ROM claim:** source sync is not equivalent to building Wi-Fi APEX or validating vendor blobs, SELinux/VINTF, recovery/OTA, device boot or RF performance.
