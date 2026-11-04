# Android 17 P2: PE external runtime dependencies, selected source graph

Reviewed 2026-11-05 against the historical PixelExperience `seventeen` branches and the `android-17.0.0_r1` AOSP manifest. These checks are a **source-ownership and compatibility gate**, not a ROM build.

The main PixelExperience-Reborn AOSP17 manifest remains on official Android17 ICU, libcxx, libnl, mksh. This is necessary to retain the working Android17 runtime, not a decision to abandon PE-specific features. Existing PE modifications are preserved in their original repositories until their consumers have been updated.

| Path | Old PE change | Modern owner and required action | Verified baseline |
| --- | --- | --- | --- |
| `external/icu` | `libandroidicu` broadly exposed to `//vendor:__subpackages__` | ICU 78 APEX (`com.android.i18n`) exposes a constrained Soong API and stubs. Require proof of a particular vendor client before broadening access. | Official [libandroidicu Android.bp](https://android.googlesource.com/platform/external/icu/+/refs/tags/android-17.0.0_r1/libandroidicu/Android.bp), commit `00c713278f65a4db343c388f0c4f8501f70387b9`; old PE patch `2abaffca7aff` |
| `external/json-c` | Vendor `libjson` built from an old Android.mk and linked `libcutils` + `libutils` | No entry in official AOSP17 reference manifest. Treat ABI as distinct from `libjsoncpp`; cannot revive unknown Qualcomm clients by creating an untested global library. | Old PE `external_json-c/Android.mk`, commit `75d63231d6dd530684cf96ca249b117410c5ca00` |
| `external/libcxx` | Changed `libc++fs` to a shared, vendor-visible library | Official Android17 Android.bp does not define a libc++fs module; retain modern toolchain and update actual old `libc++fs` consumers to standard C++17 filesystem when present. | Official [Android.bp](https://android.googlesource.com/platform/external/libcxx/+/refs/tags/android-17.0.0_r1/Android.bp), commit `88894a62bb97313ed9bf79a546f1486de4b2e723`; PE change `586bdf2bcd5b` |
| `external/libnl` | Replaced `in_addr_t` with `struct in_addr` for legacy Qualcomm WLAN header build | Source is AOSP17 libnl; keep the actual WLAN-facing type contract. Only amend modern source after verifying current `qcwcn/wifi_hal` consumer and compile diagnostics. | Official [libnl](https://android.googlesource.com/platform/external/libnl/+/refs/tags/android-17.0.0_r1), commit `2be7f4458cf7c7831df8fbac395e6a7222d0d13f`; PE `da4fac72fc5a` |
| `external/mksh` | Recovery `TMPDIR` isolation, `mkshrc` recovery packaging, terminal mode | **Still actionable:** official AOSP17 uses a distinct `sh.recovery` target but inherits `MKSH_DEFAULT_TMPDIR=/data/local`. Must explicitly verify that its recovery shell does not depend on a normally unavailable /data; do not mark complete until a tested modern fix. | Official [mksh Android.bp](https://android.googlesource.com/platform/external/mksh/+/refs/tags/android-17.0.0_r1/Android.bp), commit `71d564487c9b34f65961570073f037658e07eb06`; PE `b412d68c117f` |

## Implemented now

`tools/validate_aosp17_base_profiles.py` rejects accidental PE historical source substitution in **all 21** staged manifests: `external/icu`, `external/libcxx`, `external/libnl`, `external/mksh`, plus missing legacy `external/json-c`. It does not block a future reviewed new source pin when the appropriate tests exist.

## Remaining work before declaring these runtime paths complete

- Review each actual old PE native consumer, static and shared dependencies, and current Soong module names. The old `libjson`/modern `libjsoncpp` ABI mismatch must not be guessed.
- For mksh, fix recovery TMPDIR on the **official Android17 `sh.recovery` source**, not by overwriting with Android14 code. Verification requires a native build and recovery mount environment inspection.
- For WLAN, check the current legacy QCOM Wi-Fi HAL consumers against AOSP17 `libnl`.
- Full Soong/image/build/mondrian runtime checks remain deferred until the Android17 base can be assembled.

**No old forks, proprietary device blobs, kernel, AVB or signature policies were modified.**
