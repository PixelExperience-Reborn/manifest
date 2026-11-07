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
    "hardware/nxp/secure_element": "platform/hardware/nxp/secure_element",
    "platform_testing": "platform/platform_testing",
    "prebuilts/build-tools": "platform/prebuilts/build-tools",
    "prebuilts/clang/host/linux-x86": "platform/prebuilts/clang/host/linux-x86",
    "prebuilts/tools": "platform/prebuilts/tools",
    "packages/apps/Settings": "platform/packages/apps/Settings",
    "packages/apps/Camera2": "platform/packages/apps/Camera2",
    "packages/modules/Nfc": "platform/packages/modules/Nfc",
    "system/secure_element": "platform/system/secure_element",
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
    "vendor_nxp_opensource_commonsys_external_libnfc-nci",
    "vendor_nxp_opensource_commonsys_frameworks",
    "vendor_nxp_opensource_commonsys_packages_apps_Nfc",
    "vendor_nxp_opensource_interfaces_nfc",
    "vendor_nxp_opensource_pn5xx_halimpl",
    "vendor_nxp_opensource_pn5xx_hidlimpl",
    "vendor_nxp_opensource_sn100x_halimpl",
    "vendor_nxp_opensource_sn100x_hidlimpl",
    "vendor_nxp_secure_element",
    "vendor_nxp_secure_element_extns",
    "vendor_qcom_opensource_audio-hal_st-hal",
    "vendor_qcom_opensource_audio-hal_st-hal-ar",
    "vendor_qcom_opensource_display",
    "hardware_broadcom_libbt", "hardware_custom_compat",
    "hardware_google_pixel", "hardware_libhardware",
}


# FM broadcasting is intentionally not part of the PE-Reborn mondrian product.
# Protect source ownership by exact path and by legacy repository aliases.
# This does not replace later PRODUCT_PACKAGES / installed-file checks.
FM_SOURCE_PATHS = {
    "vendor/qcom/opensource/fm-commonsys",
    "vendor/qcom/opensource/libfmjni",
    "vendor/qcom/opensource/commonsys/fm",
}
FM_SOURCE_NAMES = {
    "vendor_qcom_opensource_fm-commonsys",
    "vendor_qcom_opensource_libfmjni",
    "vendor-qcom-opensource-fm-commonsys",
    "vendor-qcom-opensource-libfmjni",
    "android_vendor_qcom_opensource_fm-commonsys",
    "android_vendor_qcom_opensource_libfmjni",
}


def reject_mondrian_fm_source(profile, projects):
    for path, project in projects.items():
        if path in FM_SOURCE_PATHS or project.get("name") in FM_SOURCE_NAMES:
            raise ValueError(
                f"{profile}: optional FM broadcast source excluded for mondrian: {path}")


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
    # An isolated source-only experiment is not an active STAGES entry.
    expected_files = {name for name, _ in STAGES}
    expected_files.add("aosp17_pe_p2_nfc_security_candidate.xml")
    expected_files.add("aosp17_pe_p2_se_security_candidate.xml")
    expected_files.add("aosp17_pe_p2_qcom_audio_aidl_candidate.xml")
    expected_files.add("aosp17_pe_p2_qcom_display_aidl_candidate.xml")
    actual_files = {p.name for p in ROOT.glob("aosp17_*.xml")}
    if actual_files != expected_files:
        raise ValueError(f"stage list drift: missing={expected_files - actual_files}, extra={actual_files - expected_files}")

    baseline = resolve("aosp17_reference.xml")
    reject_mondrian_fm_source("aosp17_reference.xml", baseline)
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
        reject_mondrian_fm_source(file, projects)
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
        # Archived 2022 NXP SN100x libnfc-nci binds legacy HIDL/commonsys.
        # Android17 Mainline already owns the NFC stack, JNI/APEX and utils.
        # Do not add a second unreviewed controller-to-framework stack.
        if "vendor/nxp/opensource/commonsys/external/libnfc-nci" in projects:
            raise ValueError(f"{file}: legacy NXP libnfc-nci stack activated")
        # The old NXP framework exposes hidden Java Binder NFC extensions,
        # proprietary SEMS APIs and WLC calls; none is a validated AOSP17
        # Mainline/OMAPI consumer or independently reviewed PE interface.
        if "vendor/nxp/opensource/commonsys/frameworks" in projects:
            raise ValueError(f"{file}: unreviewed NXP NFC Java framework activated")
        # Archived 2022 NQNfcNci is a separate privileged com.android.nfc
        # app/JNI + QSSI/HIDL stack; Android17 uses a Mainline NFC owner.
        if "vendor/nxp/opensource/commonsys/packages/apps/Nfc" in projects:
            raise ValueError(f"{file}: legacy NXP NFC application activated")
        # Archived 2020 NXP HIDL interface packages do not automatically
        # provide modern NFC AIDL V2 or vendor.nxp.nxpnfc_aidl V1.
        if "vendor/nxp/opensource/interfaces/nfc" in projects:
            raise ValueError(f"{file}: archived NXP NFC HIDL interfaces activated")
        # Archived PN5xx 2021 HAL ships HIDL NFC 1.2, vendor extension
        # services and unverified example PN81T/eSE configuration.
        # Official AOSP17 already owns the compatible NXP AIDL HAL.
        if "vendor/nxp/opensource/pn5xx/halimpl" in projects:
            raise ValueError(f"{file}: archived PN5xx NXP HIDL HAL activated")
        # 2020 PN5xx HIDL service wrappers register system INfc 1.2 and
        # vendor HIDL, require archived nfc_nci.nqx.default.hw (row 170).
        # Never allow them to replace Android17 NFC AIDL HAL ownership.
        if "vendor/nxp/opensource/pn5xx/hidlimpl" in projects:
            raise ValueError(f"{file}: archived PN5xx NFC HIDL service activated")
        # Old SN100x HIDL + eSE/JCOP initialization libraries must not
        # shadow the official Android17 NXP AIDL HAL and secure element.
        if "vendor/nxp/opensource/sn100x/halimpl" in projects:
            raise ValueError(f"{file}: archived SN100x NXP NFC HAL activated")
        # 2020 SN100x HAL wrappers link the archived HIDL NFC1.2/NXP
        # service and eSE extension stack, not stable Android17 NFC AIDL.
        if "vendor/nxp/opensource/sn100x/hidlimpl" in projects:
            raise ValueError(f"{file}: archived SN100x NFC HIDL services activated")
        # 2023 archived P73 SE-HIDL1.2/JCOP updater must not shadow
        # official AOSP17 SE AIDL V1 and system OMAPI source owners.
        if "vendor/nxp/secure_element" in projects:
            raise ValueError(f"{file}: archived NXP P73 Secure Element HAL activated")
        # Obsolete eSE JCOP/DWP update checker and APDU downloader are
        # neither an AOSP17 SE AIDL HAL nor the system OMAPI implementation.
        if "vendor/nxp/secure_element_extns" in projects:
            raise ValueError(f"{file}: archived NXP JCOP eSE client activated")
        # Legacy Qualcomm 2023 C/LSM/GCS STHAL is excluded from modern
        # AOSP17 SoundTrigger3 AIDL and AudioReach/PAL device integration.
        if "vendor/qcom/opensource/audio-hal/st-hal" in projects:
            raise ValueError(f"{file}: archived Qualcomm legacy Sound Trigger HAL activated")
        # Old PAL-backed 2024 sound_trigger.primary.* frontend is still
        # legacy, unlike separately pinned modern Qualcomm AIDL factory.
        # This path is ONLY permitted in nondefault exact six-project preview.
        if "vendor/qcom/opensource/audio-hal/st-hal-ar" in projects:
            raise ValueError(f"{file}: archived Qualcomm PAL legacy Sound Trigger HAL activated")
        # Old 2021 HIDL mapper 4 / vendor.display.config 2 metadata shim
        # cannot silently become a modern Android17 Composer3/Gralloc5 HAL.
        if "vendor/qcom/opensource/display" in projects:
            raise ValueError(f"{file}: archived Qualcomm HIDL display helpers activated")
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
    reject_mondrian_fm_source("default.xml", active)
    if set(active) != set(final):
        raise ValueError("default.xml checkout paths differ from last reviewed stage")
    for path, project in final.items():
        if active[path].attrib != project.attrib:
            raise ValueError(f"default.xml unexpected owner/revision/groups: {path}")
    # Strict review of the experimental candidate; default must stay on r1.
    candidate_name = "aosp17_pe_p2_nfc_security_candidate.xml"
    candidate_root = ET.parse(ROOT / candidate_name).getroot()
    candidate_nodes = list(candidate_root)
    expected_nfc = {
        "path": "packages/modules/Nfc",
        "name": "platform/packages/modules/Nfc",
        "remote": "aosp",
        "revision": "6f3a074cf6c87a2dcc3970c03462a6970b06f9cd",
        "upstream": "refs/tags/android-security-17.0.0_r3",
        "groups": "pdk-cw-fs,pdk-fs",
    }
    if (candidate_root.tag != "manifest" or len(candidate_nodes) != 3 or
            [n.tag for n in candidate_nodes] !=
            ["include", "remove-project", "project"] or
            candidate_nodes[0].attrib != {"name": STAGES[-1][0]} or
            candidate_nodes[1].attrib !=
            {"name": "platform/packages/modules/Nfc"} or
            candidate_nodes[2].attrib != expected_nfc):
        raise ValueError("unreviewed NFC security candidate manifest shape or pin")
    candidate = resolve(candidate_name)
    if set(candidate) != set(final):
        raise ValueError("NFC security candidate changed source checkout paths")
    for candidate_path, source in final.items():
        expected = expected_nfc if candidate_path == "packages/modules/Nfc" else source.attrib
        if candidate[candidate_path].attrib != expected:
            raise ValueError(f"NFC candidate changed unexpected source: {candidate_path}")
    # Newer official NXP Secure Element AIDL channel-index fix source
    # experiment. Exactly one repo checkout changes; never the default.
    se_candidate_name = "aosp17_pe_p2_se_security_candidate.xml"
    se_root = ET.parse(ROOT / se_candidate_name).getroot()
    se_nodes = list(se_root)
    expected_se = {
        "path": "hardware/nxp/secure_element",
        "name": "platform/hardware/nxp/secure_element",
        "remote": "aosp",
        "revision": "8aec22fde8121bf3f74006730ce42e9ac0366b62",
        "upstream": "refs/tags/android-security-17.0.0_r3",
        "groups": "pdk",
    }
    if (se_root.tag != "manifest" or len(se_nodes) != 3 or
            [n.tag for n in se_nodes] !=
            ["include", "remove-project", "project"] or
            se_nodes[0].attrib != {"name": STAGES[-1][0]} or
            se_nodes[1].attrib !=
            {"name": "platform/hardware/nxp/secure_element"} or
            se_nodes[2].attrib != expected_se):
        raise ValueError("unreviewed NXP SE security candidate manifest shape or pin")
    se_candidate = resolve(se_candidate_name)
    if set(se_candidate) != set(final):
        raise ValueError("NXP SE security candidate changed source checkout paths")
    for candidate_path, source in final.items():
        expected = (expected_se if candidate_path == "hardware/nxp/secure_element"
                    else source.attrib)
        if se_candidate[candidate_path].attrib != expected:
            raise ValueError(
                f"NXP SE candidate changed unexpected source: {candidate_path}")
    # Modern Sony-hosted Qualcomm-derived AudioReach AIDL sources form
    # one isolated six-repository candidate; never silently activate a
    # single STHAL .so with a mismatched PAL, AGM or primary audio HAL.
    qcom_name = "aosp17_pe_p2_qcom_audio_aidl_candidate.xml"
    qcom_root = ET.parse(ROOT / qcom_name).getroot()
    qcom_nodes = list(qcom_root)
    qcom_expected = {
        "vendor/qcom/opensource/audio-hal/st-hal-ar": (
            "vendor-qcom-opensource-audio-hal-st-hal-ar",
            "1dcb1275256b3f43b78d342d623870324a831720"),
        "vendor/qcom/opensource/audio-hal/primary-hal-ar": (
            "vendor-qcom-opensource-audio-hal-primary-hal-ar",
            "b071e74ead44a7aecee69969003b902632cd4ab3"),
        "vendor/qcom/opensource/pal": (
            "vendor-qcom-opensource-arpal-lx",
            "44e6ad74fd34c390b053bbe19811502c132f007e"),
        "vendor/qcom/opensource/agm": (
            "vendor-qcom-opensource-agm",
            "7ad4167f2241beefd2a48b9e87453c3a80c5811b"),
        "vendor/qcom/opensource/audioreach-graphservices": (
            "vendor-qcom-opensource-audioreach-graphservices",
            "d38796b5d74ff727a5fbd9f10ecbc7f5c0335ff5"),
        "vendor/qcom/opensource/audioreach-conf": (
            "vendor-qcom-opensource-audioreach-conf",
            "5e90f9e4d6bb790fca0a092d57fdee8572d5b990"),
    }
    if (qcom_root.tag != "manifest" or len(qcom_nodes) != 8 or
            [node.tag for node in qcom_nodes] !=
            ["include", "remote"] + ["project"] * 6 or
            qcom_nodes[0].attrib != {"name": STAGES[-1][0]} or
            qcom_nodes[1].attrib != {
                "name": "sony-qcom-audio-review",
                "fetch": "https://github.com/sonyxperiadev",
            }):
        raise ValueError("unreviewed Qualcomm AudioReach candidate shape/remote")
    if [n.get("path") for n in qcom_nodes[2:]] != list(qcom_expected):
        raise ValueError("unreviewed Qualcomm AudioReach candidate source set")
    for node in qcom_nodes[2:]:
        path = node.get("path")
        name, revision = qcom_expected[path]
        expected = {
            "path": path, "name": name,
            "remote": "sony-qcom-audio-review",
            "revision": revision,
            "upstream": "refs/heads/aosp/AUDIO.LA.10.0.r1",
            "groups": "device",
        }
        if node.attrib != expected:
            raise ValueError("unreviewed Qualcomm AudioReach candidate SHA/pin")
    qcom_graph = resolve(qcom_name)
    if set(qcom_graph) != set(final) | set(qcom_expected):
        raise ValueError("Qualcomm AudioReach candidate added/removed unexpected paths")
    for path, original in final.items():
        if qcom_graph[path].attrib != original.attrib:
            raise ValueError("Qualcomm candidate altered active AOSP17 owner: " + path)
    for path in qcom_expected:
        if qcom_graph[path].attrib != {
                "path": path,
                "name": qcom_expected[path][0],
                "remote": "sony-qcom-audio-review",
                "revision": qcom_expected[path][1],
                "upstream": "refs/heads/aosp/AUDIO.LA.10.0.r1",
                "groups": "device",
        }:
            raise ValueError("Qualcomm candidate changed selected source " + path)
    if "vendor/qcom/opensource/audio-hal/st-hal" in qcom_graph:
        raise ValueError("Qualcomm candidate accidentally includes old legacy STHAL")
    # HWC3/Gralloc5 prototype is intentionally nondefault and incomplete
    # without exact SDM/DRM and mondrian display driver/vendor blobs.
    display_name = "aosp17_pe_p2_qcom_display_aidl_candidate.xml"
    display_root = ET.parse(ROOT / display_name).getroot()
    display_nodes = list(display_root)
    display_expected = {
        "path": "hardware/qcom/display",
        "name": "hardware-qcom-display",
        "remote": "sony-qcom-display-review",
        "revision": "baf61f736e2109522e3f72754ee7cfacbfa2dc6c",
        "upstream": "refs/heads/aosp/DISPLAY.LA.5.0.r1",
        "groups": "device",
    }
    if (display_root.tag != "manifest" or len(display_nodes) != 3 or
            [n.tag for n in display_nodes] !=
            ["include", "remote", "project"] or
            display_nodes[0].attrib != {"name": STAGES[-1][0]} or
            display_nodes[1].attrib != {
                "name": "sony-qcom-display-review",
                "fetch": "https://github.com/sonyxperiadev",
            } or display_nodes[2].attrib != display_expected):
        raise ValueError("unreviewed Qualcomm HWC3 display candidate shape/pin")
    display_graph = resolve(display_name)
    if set(display_graph) != set(final) | {"hardware/qcom/display"}:
        raise ValueError("Qualcomm display candidate altered source path set")
    for path, original in final.items():
        if display_graph[path].attrib != original.attrib:
            raise ValueError("Qualcomm display candidate altered active AOSP17 owner: " + path)
    if display_graph["hardware/qcom/display"].attrib != display_expected:
        raise ValueError("Qualcomm display candidate has different source checkout")
    if "vendor/qcom/opensource/display" in display_graph:
        raise ValueError("Qualcomm display candidate imported old HIDL helpers")
    # FM must stay absent even when nondefault experimental source profiles
    # are resolved, so later bring-up cannot silently import the old FM app.
    for name, graph in (
        (candidate_name, candidate),
        (se_candidate_name, se_candidate),
        (qcom_name, qcom_graph),
        (display_name, display_graph),
    ):
        reject_mondrian_fm_source(name, graph)
    print("PASS: FM broadcast source excluded from mondrian AOSP17 profiles")
    print("PASS: experimental Qualcomm HWC3 AIDL display candidate isolated/pinned")
    print("PASS: modern Qualcomm-derived AIDL six-source stack isolated/pinned")
    print("PASS: experimental official NXP SE channel-bounds security source pinned")
    print("PASS: experimental newer NFC source strictly isolated and pinned")
    print(f"PASS: safe default.xml resolves to {len(active)} reviewed project paths")

    print("PASS: all 25 AOSP17 staged profiles retain official AVB/Settings and no device trees")
    print("SOURCE/STRUCTURE ONLY: full repo sync, Soong/Make build and device boot NOT tested")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ET.ParseError, ValueError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
