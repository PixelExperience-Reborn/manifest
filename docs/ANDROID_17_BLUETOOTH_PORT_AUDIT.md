# P0 — packages/modules/Bluetooth Android 17 migration audit

**Date:** 2026-11-03. **Device target:** mondrian (POCO F5 Pro / Redmi K60).

**Status:** exact AOSP17 source snapshot and single PE URI fix published; Java 17 host tests passed. Android Bluetooth stack/APEX build, HAL negotiation, controller and device tests still outstanding. Old `seventeen` remains untouched.

## Pinned Android17 source identity

- [Official Google `android-17.0.0_r1` Bluetooth module](https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/tags/android-17.0.0_r1) annotated tag `29b0cd5c7f25206eb0ad43078aebef38da67e3e8`, commit `c77db469de80f86660bc053bec4dee0c5d4b947c`, tree `385b36982cbe1daeb61471ab16ebad099aeb78b1`.
- New separate clean AOSP17 source [snapshot `8fbbdd62fc1ad3e0b252428d8b9134f9e3f3ad06`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/8fbbdd62fc1ad3e0b252428d8b9134f9e3f3ad06), with GitHub Git API tree SHA matching official Google tree. Snapshot is parentless; upstream full history is **not** imported.
- [GitHub Actions source import #41707458581](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/actions/runs/41707458581) **passed**. Existing Android14 PE `seventeen` was not altered.
- New working branch `port/a17-bluetooth-pe-20261103`, immutable SHA `e7c2f47e3c73c4f2b83f03145441e419f45124b3`; [draft PR #1](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/pull/1) against pristine snapshot.

## Historical PE delta decisions against exact AOSP17 code

| Historical patch | AOSP17 observation and decision |
| --- | --- |
| [`2d11abc`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/2d11abc3b5ae57b562791f1bee01d05e4a0888c2), [`67241b7`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/67241b759c13409f6c7c30b0cbdb87f4fc1db7b6) — GATT out-of-bounds writes | **Already present in AOSP17**. `attp_build_read_by_type_value_cmd` explicitly checks `payload_size < 5`; `btif_to_bta_response` clamps copied length to `GATT_MAX_ATTR_LEN`. No duplicate patches. |
| [`226a3de`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/226a3de27f384577c300e933eade06ab8ebad114) — OPP URI comparison | **Selected and adapted.** AOSP17 `BluetoothOppUtility.isBluetoothShareUri` still used `uri.getAuthority().equals(...)` in the first condition but used `Objects.equals` in the return. Replace only the unsafe first condition with `Objects.equals`, preserving security EventLog reporting and result. |
| [`90e2943`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/90e2943c5807baf5f6916758564cae741f657d12) — Bluetooth auto-enable/airplane-mode handling | **Do not cherry-pick.** Android17 `BluetoothManagerService` has modern `AirplaneModeController` state management. Test modern controller policies instead of editing obsolete boot logic. |
| [`2261959`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/226195980825e97dbf00d693451c92ff6c50a3a0) — alternative `sysbta` AIDL audio provider | **Defer**. Requires declared, accessible vendor binder service and explicit audio HAL mode matching; cannot assume it exists on mondrian. |
| [`5398670`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/53986709bc3bd259caf9d499c7efd3a1b4e12a4) — HCI supported-commands bitmap property | **Reject blind port**. Old code computes byte/bit offsets using /10 and %10 instead of /8 and %8, with no bounds check; a malformed property could cause memory corruption. Must independently redesign only for a verified controller need. |
| [`dd7d85f`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/dd7d85f8259bb721032d85f37bb5879c03231600) — HCI erroneous-data-reporting toggle | **Defer**. Vendor HCI capabilities and controller-specific behavior require tests. |
| [`156dd79`](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/commit/156dd79f97f9711592c873b38a2963739b025c0f) — disable APCF extended features | **Defer**. Not safe as a global property without evidence that the mondrian LE controller needs it. |

## Actual code and tests

- **Production source:** `android/app/src/com/android/bluetooth/opp/BluetoothOppUtility.java`; one Java expression adjusted to null-safe `Objects.equals`.
- **Host regression:** `tests/host/test_bluetooth_opp_uri.py` extracts and **compiles the actual Java method** using Java 17 with test doubles for `Uri`, `BluetoothShare` and `EventLog`. Tests valid URI, mismatched authority, null authority with matching prefix and unrelated URI while counting security event reports.
- [Source CI #41707947445](https://github.com/PixelExperience-Reborn/packages_modules_Bluetooth/actions/runs/41707947445) **passed**. This is a host contract test, not the complete Android Bluetooth app/module compilation.
- No released Bluetooth feature, runtime performance, codec offload or security certification is claimed.

## Source integration and pending gates

1. [`aosp17_pe_p0_bluetooth.xml`](../aosp17_pe_p0_bluetooth.xml) extends the existing ten-profile source graph and only overrides `packages/modules/Bluetooth` at exact PE SHA `e7c2f47e3c73c4f2b83f03145441e419f45124b3`.
2. Validate **eleven** repo manifest profiles with official `repo manifest` and no duplicate paths, expected 1069 default-selected projects in PE profiles.
3. Linux `repo sync` for Bluetooth alone, then twelve essential P0 projects in the same profile with all immutable HEAD values and host tests.
4. Compile Soong/APEX (Java, native C++, Rust), run relevant module tests, check VINTF/Bluetooth audio HAL and vendor dependencies.
5. Complete Bluetooth classic/LE, pairing, SBC/AAC/aptX/LDAC negotiation, suspend/resume, HCI, CTS/VTS and real mondrian device tests.

**Not done:** full compilation, signed APEX, controller hardware tests, vendor audio interaction, real PE device boot. Keep PR and staged manifest draft.
