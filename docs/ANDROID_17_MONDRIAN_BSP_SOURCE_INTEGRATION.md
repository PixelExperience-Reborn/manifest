# 2026-11-08 — PE-Reborn AOSP 17 mondrian source integration preflight

**Status: source-only integration, not a kernel build and not a bootable ROM.**

Device: **POCO F5 Pro / Redmi K60 (mondrian, physical SM8475)**.
Project platform: independently maintained **AOSP 17** with audited
`vendor/aosp`; other ROM trees are read-only compatibility references.

## Why a separate manifest profile?

The historical `seventeen` branch is still rooted in an Android 14 PE
snapshot, while the AOSP17 staged source graph is kept in manifest Draft PR #2
(`port/a17-aosp17-manifest-20261102`). Our own vendor AOSP17 work remains
in vendor_aosp Draft PR #1. Therefore importing the new device files into
the historical default manifest would mix incompatible platform epochs.

`aosp17_pe_mondrian_source_audit.xml` is an **opt-in source profile**
layered on `aosp17_pe_p2_kernel_configs.xml`, inheriting AOSP17 r1 and
the reviewed PE vendor pin `38bf62440be54eb86b4f5c6ccc888e467b5a9a53`.

It adds **exactly five reviewed PE-Reborn repositories**, each pinned to a
full immutable Git commit, not a mutable branch name.

| Path | Branch / source status | Included |
| --- | --- | --- |
| `device/xiaomi/mondrian` | First independent product scaffold; Draft PR #1 | Yes, source only |
| `device/xiaomi/sm8450-common` | First SM8475-compatible common scaffold; Draft PR #1 | Yes, source only |
| `kernel/xiaomi/sm8450` | OEM/Goodix/Qualcomm source audit; Draft PR #1; NO selected kernel source | Yes, audits only |
| `kernel/xiaomi/sm8450-modules` | Qualcomm module/KMI contract; Draft PR #1; NO .ko source imported | Yes, audits only |
| `kernel/xiaomi/sm8450-devicetrees` | Board/display/camera DTBO contract; Draft PR #1; NO DT source imported | Yes, audits only |
| `vendor/xiaomi/mondrian` | Firmware and proprietary provenance not qualified | **No** |
| `vendor/xiaomi/sm8450-common` | Blob and VINTF dependencies not qualified | **No** |
| `hardware/xiaomi` | UDFPS/Power/other HAL interfaces still unqualified | **No** |

The last three GitHub repos **exist**, but empty starter repositories must
not be interpreted as an approved vendor/hardware implementation.

## Executable CI proof boundary

`tools/check_mondrian_source_audit_profile.py` validates the nested
manifest chain, Android17 platform revision, approved vendor pin and five
exact device/BSP commit IDs, with a guard against silent vendor and HAL
imports. Its `--checkout-root` mode additionally validates physical
`git rev-parse HEAD` at each selected checkout, `pe_mondrian` product
inheritance, our common board wiring, the official AOSP17 Make product
fragments and Launcher3QuickStep source product choice. It refuses premature
kernel/module/DTBO readiness flags.

`.github/workflows/aosp17-mondrian-source-audit.yml` uses the **official
Google repo tool** to parse the full AOSP17 project graph and `repo sync`
only these six PE sources (including vendor/aosp) plus Google build/make.
It also executes host-only contract tests from all five repositories.

This does **not** run `lunch`, native Soong, compile any C/C++, construct
`boot.img` or `vendor_boot.img`, package vendor blobs, boot the device
or pass VINTF/SELinux. CI source-sync success must never be described as
an Android 17 ROM compile or hardware support result.

## Hardware release blockers

1. Select a complete, redistributable, reproducible kernel/module/DT
   source BOM (currently just reference SHA evidence). OEM kernel 5.10.81
   is insufficient alone; later 5.10.269 is only a compatibility reference.
   Resolve GKI 5.10 Android17 QPR1+ support policy before shipping.
2. Reconcile Goodix manufacturer `goodix,brl-d` match table with mondrian
   `goodix,gt9916S`, matching actual IC, firmware, config, SPI/IRQ/ESD and
   suspend power behavior. Do not assume generic Goodix source can directly
   replace the active Xiaomi touch driver.
3. Qualify cape/cape-v2/capep, board PM8008, M11A display and mondrian
   camera DTBO against the selected kernel, built modules and bootloader.
4. Qualify vendor blobs, firmware and VINTF/FCM/SELinux partition ownership,
   FBE/KeyMint/AVB/recovery before enabling kernel/boot image Make variables.
5. Pass native Android17 product discovery, Soong parse and build, boot
   and full mondrian touchscreen/UDFPS/camera/NFC/radio/thermal tests.

FM radio, unaudited LineageOS product and permission dependencies, test
AVB keys and third-party firmware with unverified rights remain excluded.

## Merge boundaries

Do **not** merge this source-only profile into production default manifest,
or merge the underlying Draft PRs solely because source CI passes. A
successful source synchronization is necessary but not a substitute for a
reproducible matched device kernel and operational Android 17 target.
