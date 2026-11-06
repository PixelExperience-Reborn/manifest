#!/usr/bin/env python3
"""Offline source-graph ownership gate for PE-Reborn's staged AOSP17 manifests.

This is NOT a replacement for the official `repo manifest`, `repo sync` or a
Soong/Make build. It checks only the deliberately simple project/include/remove
subset used by these checked-in bootstrap profiles, without network access.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

# Stage order is intentional: each file changes one reviewed source boundary.
# All SHAs below identify approved AOSP17-source fork commits, not old
# PixelExperience Android14 'seventeen' refs.
STAGES = [
    ("aosp17_reference.xml", {}),
    ("aosp17_pe_bootstrap.xml", {
        "build/soong": ("build_soong", "6215d41c790a463b7795ce81ac77204c238cbf48"),
    }),
    ("aosp17_pe_envsetup.xml", {
        "vendor/aosp": ("vendor_aosp", "07a2c6976375f971d05fa5f210bcd8e45d7723e0"),
    }),
    ("aosp17_pe_p0_native.xml", {
        "art": ("art", "b753cf97923c3695338d21466fa14c57b480a59a"),
        "bionic": ("bionic", "06356e41c5ed7b12220b24c05ba4fdb873b126a7"),
    }),
    ("aosp17_pe_p0_core.xml", {
        "system/core": ("system_core", "8e0f22aaac0ee4114a83646e2c96d07578145bfa"),
    }),
    ("aosp17_pe_p0_frameworks.xml", {
        "frameworks/native": ("frameworks_native", "ae266dcb706d083868578cfedce381ef44488a07"),
    }),
    ("aosp17_pe_p0_recovery.xml", {
        "bootable/recovery": ("bootable_recovery", "0ed8dc4f93020555afdfc19141263ca40629ef74"),
    }),
    ("aosp17_pe_p0_av.xml", {
        "frameworks/av": ("frameworks_av", "5db9a6151f33cacb810a8fe7615be8c23d3fa858"),
    }),
    ("aosp17_pe_p0_base.xml", {
        "frameworks/base": ("frameworks_base", "382d5c9c0b20bbdb67b70176bce02c7e64767b0c"),
    }),
    ("aosp17_pe_p0_hardware.xml", {
        "hardware/interfaces": ("hardware_interfaces", "735e364cbdd00b0d6e4dc33ea0866dbb6d971a11"),
    }),
    ("aosp17_pe_p0_bluetooth.xml", {
        "packages/modules/Bluetooth": ("packages_modules_Bluetooth", "e7c2f47e3c73c4f2b83f03145441e419f45124b3"),
    }),
    ("aosp17_pe_p0_connectivity.xml", {
        "packages/modules/Connectivity": ("packages_modules_Connectivity", "701882b51546230c6c32c9654a3f7b9814429e13"),
    }),
    ("aosp17_pe_p0_permission.xml", {
        "packages/modules/Permission": ("packages_modules_Permission", "f6e6e14b5c4d6e094c205683940a1328384338d9"),
    }),
    ("aosp17_pe_p0_wifi.xml", {
        "packages/modules/Wifi": ("packages_modules_Wifi", "f228be88b2f0b8ed7a39ca1c4db94bc5aaaecbce"),
    }),
    ("aosp17_pe_p0_adb.xml", {
        "packages/modules/adb": ("packages_modules_adb", "6daac89c0d6e395f9ff2a032206a21e04421dc5f"),
    }),
    ("aosp17_pe_p0_security.xml", {
        "system/security": ("system_security", "a939bea3461e668355b1df87230f9308a8d50837"),
    }),
    ("aosp17_pe_p0_sepolicy.xml", {
        "system/sepolicy": ("system_sepolicy", "f12e84e0ba4fe3d1cc093af15c41ceb8dba8cc69"),
    }),
    ("aosp17_pe_p0_update_engine.xml", {
        "system/update_engine": ("system_update_engine", "c0309b604010b9b2e2c58d684e86b6090b74ad77"),
    }),
    ("aosp17_pe_p1_vold.xml", {
        "system/vold": ("system_vold", "76516faf8c3bd5e0eb330611a40793cd137f1f8a"),
    }),
    ("aosp17_pe_p1_telephony.xml", {
        "frameworks/opt/telephony": ("frameworks_opt_telephony", "548270c2e6ab41b036c670339fa0d4b04ca1ed59"),
    }),
    ("aosp17_pe_p1_timezonepicker.xml", {
        "frameworks/opt/timezonepicker": ("frameworks_opt_timezonepicker", "7a5698b6c651db16f243fe8d3d28008e4243e04c"),
    }),
    ("aosp17_pe_p2_tinycompress.xml", {
        "external/tinycompress": ("external_tinycompress", "25951427f9de414c3d5e01cd92b98f21ad490372"),
    }),
    ("aosp17_pe_p2_qcom_wlan.xml", {
        "hardware/qcom/wlan": ("hardware_qcom_wlan", "667daa664e107f0de451b9046a12da74b99a0e6b"),
    }),
    ("aosp17_pe_p2_ril.xml", {
        "hardware/ril": ("hardware_ril", "29ea93bac3efe871c54f86b05713f894575dc6b8"),
    }),
    ("aosp17_pe_p2_kernel_configs.xml", {
        "kernel/configs": ("kernel_configs", "d02620f1f46af9eef024fb41e6d911d935699492"),
    }),
]

# P2 source graph owner integrity: SHA-only checks are not sufficient.
# A changed fetch remote, upstream or group can resolve the correct hash in
# the wrong trust domain or change what the official repo client selects.
P2_PROJECT_ATTRIBUTES = {
    "external/tinycompress": {
        "remote": "reborn-tinycompress",
        "upstream": "refs/heads/integrate/a17-tinycompress-20261105",
        "groups": "pdk",
    },
    "hardware/qcom/wlan": {
        "remote": "reborn-wlan",
        "upstream": "refs/heads/integrate/a17-aosp17-qcom-wlan-20261105",
        "groups": "qcom_wlan,pdk-qcom",
    },
    "hardware/ril": {
        "remote": "reborn-ril",
        "upstream": "refs/heads/integrate/a17-aosp17-ril-20261105",
        "groups": "pdk",
    },
    "kernel/configs": {
        "remote": "reborn-kconfigs",
        "upstream": "refs/heads/audit/a17-kernel-configs-source-20261105",
        "groups": "vts,pdk",
    },
}

P2_STAGE_REMOTES = {
    "aosp17_pe_p2_tinycompress.xml": "reborn-tinycompress",
    "aosp17_pe_p2_qcom_wlan.xml": "reborn-wlan",
    "aosp17_pe_p2_ril.xml": "reborn-ril",
    "aosp17_pe_p2_kernel_configs.xml": "reborn-kconfigs",
}


# Explicit platform-only ownership remains until a reviewed new port exists.
OFFICIAL_PATHS = {
    "build/make": "platform/build",
    "external/avb": "platform/external/avb",
    "external/cronet": "platform/external/cronet",
    "external/dtc": "platform/external/dtc",
    "external/e2fsprogs": "platform/external/e2fsprogs",
    "external/gptfdisk": "platform/external/gptfdisk",
    "external/icu": "platform/external/icu",
    "external/libcxx": "platform/external/libcxx",
    "external/libnl": "platform/external/libnl",
    "external/mksh": "platform/external/mksh",
    "external/tinyxml2": "platform/external/tinyxml2",
    "external/wpa_supplicant_8": "platform/external/wpa_supplicant_8",
    "hardware/broadcom/libbt": "platform/hardware/broadcom/libbt",
    "hardware/libhardware": "platform/hardware/libhardware",
    "hardware/nxp/nfc": "platform/hardware/nxp/nfc",
    "platform_testing": "platform/platform_testing",
    "prebuilts/build-tools": "platform/prebuilts/build-tools",
    "prebuilts/clang/host/linux-x86": "platform/prebuilts/clang/host/linux-x86",
    "prebuilts/tools": "platform/prebuilts/tools",
    "packages/apps/Settings": "platform/packages/apps/Settings",
    "packages/apps/Camera2": "platform/packages/apps/Camera2",
    "packages/modules/Nfc": "platform/packages/modules/Nfc",
    "packages/providers/MediaProvider": "platform/packages/providers/MediaProvider",
    "packages/providers/DownloadProvider": "platform/packages/providers/DownloadProvider",
    "system/bpf": "platform/system/bpf",
    "system/bpfprogs": "platform/system/bpfprogs",
    "system/netd": "platform/system/netd",
    "system/libufdt": "platform/system/libufdt",
    "system/tools/mkbootimg": "platform/system/tools/mkbootimg",
    "tools/metalava": "platform/tools/metalava",
}
FORBIDDEN_PATH_PREFIXES = (
    "external/json-c/",
    "external/ntfs-3g/",
    "external/ant-wireless/",
    "device/xiaomi/",
    "hardware/custom/",
    "vendor/lineage/",
    "device/qcom/sepolicy",
)
FORBIDDEN_NAMES = {
    "packages_apps_Settings", "packages_apps_FaceUnlockService",
    "vendor_pixel-framework", "device_custom_sepolicy",
    "device_qcom_sepolicy", "device_qcom_sepolicy_vndr_sm8450",
    "external_avb",
    "external_cronet", "external_dtc", "external_e2fsprogs",
    "external_gptfdisk", "external_connectivity",
    "external_icu", "external_json-c", "external_libcxx", "external_libnl", "external_mksh",
    "external_tinyxml", "external_wpa_supplicant_8",
    "platform_testing",
    "prebuilts_extract-tools", "prebuilts_kernel-build-tools",
    "prebuilts_tools-custom",
    "tools_extract-utils", "tools_metalava",
    "vendor_codeaurora_telephony",
    "vendor_custom-preference", "vendor_nxp_nfc",
    "hardware_broadcom_libbt", "hardware_custom_compat",
    "hardware_google_pixel", "hardware_libhardware",
}


def resolve(filename: str, stack=()):
    """Resolve checked-in project/remove/include commands in XML order.

    The official `repo` client is still the sole authority for full manifest
    semantics such as groups, copyfiles, remotes, superprojects and checkout.
    """
    if filename in stack:
        raise ValueError(f"include cycle: {stack} -> {filename}")
    file = ROOT / filename
    if file.parent != ROOT or not file.is_file():
        raise ValueError(f"missing or outside-root manifest: {filename}")
    root = ET.parse(file).getroot()
    if root.tag != "manifest":
        raise ValueError(f"{filename}: root is not <manifest>")
    projects = {}
    for elem in root:
        if elem.tag == "include":
            target = elem.get("name")
            if not target:
                raise ValueError(f"{filename}: unnamed include")
            for path, project in resolve(target, stack + (filename,)).items():
                if path in projects:
                    raise ValueError(f"{filename}: duplicate include checkout {path}")
                projects[path] = project
        elif elem.tag == "project":
            name = elem.get("name")
            path = elem.get("path") or name
            if not path or not name or path in projects:
                raise ValueError(f"{filename}: duplicate/unnamed project {path}")
            projects[path] = elem
        elif elem.tag == "remove-project":
            name = elem.get("name")
            targets = [k for k, v in projects.items() if v.get("name") == name]
            if len(targets) != 1:
                raise ValueError(f"{filename}: cannot uniquely remove {name}: {targets}")
            del projects[targets[0]]
    return projects


def validate():
    expected_files = {name for name, _ in STAGES}
    actual_files = {p.name for p in ROOT.glob("aosp17_*.xml")}
    if actual_files != expected_files:
        raise ValueError(f"stage list drift: missing={expected_files - actual_files}, extra={actual_files - expected_files}")

    baseline = resolve("aosp17_reference.xml")
    if len(baseline) != 1071:
        raise ValueError(f"unexpected base path count {len(baseline)}, expected 1071")
    if "vendor/aosp" in baseline:
        raise ValueError("reference must not contain PE vendor")
    if baseline["build/soong"].get("name") != "platform/build/soong":
        raise ValueError("reference is not official Soong")
    for k, v in OFFICIAL_PATHS.items():
        if baseline[k].get("name") != v:
            raise ValueError(f"reference changed official owner: {k}")

    expected_pins = {}
    for index, (file, new_pins) in enumerate(STAGES):
        for path, pinned in new_pins.items():
            if path in expected_pins:
                raise ValueError(f"duplicate ownership stage for {path}")
            expected_pins[path] = pinned
        # An immutable revision still requires the intended organization
        # remote. Reject any P2 stage that repoints its remote elsewhere.
        if file in P2_STAGE_REMOTES:
            stage = ET.parse(ROOT / file).getroot()
            remotes = stage.findall("remote")
            if (len(remotes) != 1 or
                    remotes[0].get("name") != P2_STAGE_REMOTES[file] or
                    remotes[0].get("fetch") !=
                    "https://github.com/PixelExperience-Reborn"):
                raise ValueError(f"{file}: unreviewed P2 fetch remote")
        projects = resolve(file)
        # Report a forbidden legacy binary import before the generic count
        # check, so this failure remains actionable and regression-testable.
        if "prebuilts/extract-tools" in projects:
            raise ValueError(f"{file}: unreviewed host-only extract-tools activated")
        # Kernel build tools come from a separate, kernel-version-specific
        # graph. Android17 platform does not own this 2022 binary bundle.
        if "prebuilts/kernel-build-tools" in projects:
            raise ValueError(f"{file}: legacy kernel host prebuilts activated")
        # Older host-only cpio/lz4c/Perl/dtc binaries are not a reviewed
        # platform module or standalone AOSP17 source dependency.
        if "prebuilts/tools-custom" in projects:
            raise ValueError(f"{file}: legacy custom host tools activated")
        # Python extractor is host source and requires vetted external tools.
        # Never import the legacy PE Bash fork or a partially ported Python
        # helper into the ROM until its device/kernel/vendor graph is reviewed.
        if "tools/extract-utils" in projects:
            raise ValueError(f"{file}: unreviewed vendor extractor host source activated")
        # Preserve the reviewed Qualcomm source in an isolated PE branch
        # until vendor IMS/ExtPhone ABI, radio Java libraries and Soong build
        # have been validated against a real new mondrian product graph.
        if "vendor/codeaurora/telephony" in projects:
            raise ValueError(f"{file}: unverified Qualcomm telephony source activated")
        # Old custom-preference has LineageHardwareManager and a privileged
        # cross-process remote broadcast protocol. Android17 Settings has no
        # such source dependency; gate a future independent PE redesign.
        if "vendor/custom-preference" in projects:
            raise ValueError(f"{file}: unreviewed legacy preference library activated")
        # The archived PN81T HIDL 1.2 service is not the NXP AIDL service
        # selected by the mondrian hardware reference and official AOSP17.
        # Block both legacy checkout path and its archived repo name.
        if "vendor/nxp/nfc" in projects:
            raise ValueError(f"{file}: unreviewed legacy PN8x NXP NFC HAL activated")
        expected_count = 1071 + int(index >= 2)
        if len(projects) != expected_count:
            raise ValueError(f"{file}: {len(projects)} paths, expected {expected_count}")
        notdefault = sum("notdefault" in p.get("groups", "").split(",")
                         for p in projects.values())
        expected_selected = 1068 + int(index >= 2)
        if len(projects) - notdefault != expected_selected:
            raise ValueError(f"{file}: default-selected count changed")
        for legacy_path in ("external/json-c", "external/ntfs-3g", "external/tinyxml",
                            "hardware/custom/compat", "hardware/google/pixel"):
            if legacy_path in projects:
                raise ValueError(f"{file}: unreviewed historical PE external dependency {legacy_path}")
        if projects.get("external/avb") is None:
            raise ValueError(f"{file}: official AVB missing")
        for p, official in OFFICIAL_PATHS.items():
            if projects[p].get("name") != official:
                raise ValueError(f"{file}: replaced critical AOSP17 owner {p}")
        for path in projects:
            if path.startswith(FORBIDDEN_PATH_PREFIXES):
                raise ValueError(f"{file}: device/unported dependency {path}")
        if any(p.get("name") in FORBIDDEN_NAMES for p in projects.values()):
            raise ValueError(f"{file}: unexpected historical repo")
        expected_paths = set(baseline)
        if index >= 2:
            expected_paths.add("vendor/aosp")
        if set(projects) != expected_paths:
            raise ValueError(f"{file}: unexpected paths added or removed")
        for path, project in projects.items():
            if path in expected_pins:
                owner, sha = expected_pins[path]
                if project.get("name") != owner or project.get("revision") != sha:
                    raise ValueError(f"{file}: bad revision/owner for {path}")
                for key, value in P2_PROJECT_ATTRIBUTES.get(path, {}).items():
                    if project.get(key) != value:
                        raise ValueError(
                            f"{file}: changed P2 {key} for {path}")
            elif path in baseline:
                if project.get("name") != baseline[path].get("name"):
                    raise ValueError(f"{file}: unexpected override of {path}")
            else:
                raise ValueError(f"{file}: unexpected project {path}")
        print(f"PASS: {file}: {len(projects)} declared, {expected_selected} selected, "
              f"{len(expected_pins)} reviewed pins")
    # The default source graph must be the final reviewed stage, never
    # historical PE Android14 snippets or a second, untracked owner.
    # Validate both the single-entrypoint contract and every resolved
    # project attribute: path, remote, name, immutable SHA and groups.
    entry = ET.parse(ROOT / "default.xml").getroot()
    direct = list(entry)
    if (entry.tag != "manifest" or len(direct) != 1 or
            direct[0].tag != "include" or
            direct[0].get("name") != STAGES[-1][0] or
            len(direct[0].attrib) != 1):
        raise ValueError("default.xml must include only the latest reviewed AOSP17 stage")
    active = resolve("default.xml")
    final = resolve(STAGES[-1][0])
    if set(active) != set(final):
        raise ValueError("default.xml checkout paths differ from last reviewed stage")
    for path, project in final.items():
        if active[path].attrib != project.attrib:
            raise ValueError(f"default.xml unexpected owner/revision/groups: {path}")
    print(f"PASS: safe default.xml resolves to {len(active)} reviewed project paths")

    print("PASS: all 25 AOSP17 staged profiles retain official AVB/Settings and no device trees")
    print("SOURCE/STRUCTURE ONLY: full repo sync, Soong/Make build and device boot NOT tested")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ET.ParseError, ValueError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
