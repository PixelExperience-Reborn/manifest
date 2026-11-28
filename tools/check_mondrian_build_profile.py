#!/usr/bin/env python3
"""Structural check of the opt-in pe_mondrian real-build profile.

The build profile must extend the reviewed source-audit profile, and every
mondrian project it pins must be an immutable 40-hex commit of a
PixelExperience-Reborn repository with its bring-up branch recorded.
"""
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "aosp17_pe_mondrian_build.xml"
PINNED = {
    "device/xiaomi/mondrian": "android_device_xiaomi_mondrian",
    "device/xiaomi/sm8450-common": "android_device_xiaomi_sm8450-common",
    "kernel/xiaomi/sm8450": "android_kernel_xiaomi_sm8450",
    "kernel/xiaomi/sm8450-modules": "android_kernel_xiaomi_sm8450-modules",
    "kernel/xiaomi/sm8450-devicetrees": "android_kernel_xiaomi_sm8450-devicetrees",
    "vendor/aosp": "vendor_aosp",
    "vendor/xiaomi/sm8450-common": "proprietary_vendor_xiaomi_sm8450-common",
    "vendor/xiaomi/mondrian": "proprietary_vendor_xiaomi_mondrian",
}
# Projects outside the organization, each at an immutable commit of its
# recorded branch.
EXTERNAL = {
    "vendor/gapps": ("vendor_gapps", "mindthegapps", "refs/heads/cinnamonbun"),
}
# Applications the build profile adds to the source-audit profile: an
# organization commit of a recorded port branch each.
ADDED = {
    # Camera app: LineageOS Aperture of lineage-24.0 (Android 17); it
    # overrides AOSP Camera2 when the device sets PE_A17_PORT_APERTURE.
    "packages/apps/Aperture": "packages_apps_Aperture",
    # Qualcomm AIDL boot control of LineageOS lineage-24.0-caf, for vendor
    # and recovery (sideload, fastbootd set_active).
    "hardware/qcom-caf/bootctrl": "hardware_qcom-caf_bootctrl",
    # Qualcomm telephony Java libraries (LA.QSSI.17.0) the stock IMS apps of
    # sm8450-common use; the base stages keep rejecting this project.
    "vendor/codeaurora/telephony": "vendor_codeaurora_telephony",
    # xiaomi-telephony-stub, a boot jar of sm8450-common (root Soong namespace).
    "hardware/xiaomi": "android_hardware_xiaomi",
}
# The prebuilt kernel release lives on the default branch of its repository.
KERNEL_RELEASE = ("device/xiaomi/mondrian-kernel", "android_device_xiaomi_mondrian-kernel")
RESTORED_AOSP = {
    "device/google/contexthub",
    "device/google/cuttlefish",
    "device/google/cuttlefish_prebuilts",
    "device/google/cuttlefish_vmm",
}


def resolve(name):
    """Projects of a manifest with includes and remove-project applied."""
    projects = {}
    for element in ET.parse(ROOT / name).getroot():
        if element.tag == "include":
            projects.update(resolve(element.get("name")))
        elif element.tag == "remove-project":
            for path, project in list(projects.items()):
                if project.get("name") == element.get("name"):
                    del projects[path]
        elif element.tag == "project":
            projects[element.get("path") or element.get("name")] = element
        elif element.tag == "extend-project":
            for path, project in projects.items():
                if project.get("name") == element.get("name"):
                    project.set("revision", element.get("revision"))
    return projects


def main():
    root = ET.parse(PROFILE).getroot()
    includes = [e.get("name") for e in root if e.tag == "include"]
    if includes != ["aosp17_pe_mondrian_source_audit.xml"]:
        sys.exit(f"build profile must include only the source-audit profile, got {includes}")
    base, build = resolve("aosp17_pe_mondrian_source_audit.xml"), resolve(PROFILE.name)
    for path, name in PINNED.items():
        project = build.get(path)
        if project is None or project.get("name") != name:
            sys.exit(f"{path}: expected project {name}")
        if not re.fullmatch(r"[0-9a-f]{40}", project.get("revision", "")):
            sys.exit(f"{path}: revision must be an immutable 40-hex commit")
        if not (project.get("upstream", "").startswith("refs/heads/bringup/")):
            sys.exit(f"{path}: upstream must record the bring-up branch")
        if project.get("remote") != "reborn-mondrian":
            sys.exit(f"{path}: must come from the PixelExperience-Reborn remote")
    path, name = KERNEL_RELEASE
    project = build.get(path)
    if (project is None or project.get("name") != name or project.get("remote") != "reborn-mondrian"
            or not project.get("upstream", "").startswith(("refs/heads/seventeen", "refs/heads/bringup/"))
            or not re.fullmatch(r"[0-9a-f]{40}", project.get("revision", ""))):
        sys.exit(f"{path}: expected {name} at a 40-hex commit of seventeen or a bring-up branch")
    for path, (name, remote, upstream) in EXTERNAL.items():
        project = build.get(path)
        if (project is None or project.get("name") != name or project.get("remote") != remote
                or project.get("upstream") != upstream
                or not re.fullmatch(r"[0-9a-f]{40}", project.get("revision", ""))):
            sys.exit(f"{path}: expected {remote}/{name} at a 40-hex commit of {upstream}")
    for path, name in ADDED.items():
        project = build.get(path)
        if (project is None or project.get("name") != name or project.get("remote") != "reborn-mondrian"
                or not re.fullmatch(r"[0-9a-f]{40}", project.get("revision", ""))
                or not re.fullmatch(r"refs/heads/port/[\w.-]+", project.get("upstream", ""))):
            sys.exit(f"{path}: expected {name} at an organization commit of a port branch")
    # Security bulletin updates may only move AOSP projects to an
    # android-security-17 tag; they never add paths or change remotes.
    known = {p.get("name") for p in base.values()}
    for e in (e for e in root if e.tag == "extend-project"):
        name, rev = e.get("name"), e.get("revision", "")
        if name not in known:
            sys.exit(f"extend-project {name}: not a project of the source-audit profile")
        if set(e.attrib) != {"name", "revision"} or not re.fullmatch(r"refs/tags/android-security-17\.0\.0_r[0-9]+", rev):
            sys.exit(f"extend-project {name}: only a revision android-security-17.0.0_rN is allowed")
    # Organization copies replacing projects of the source-audit profile
    # (security bulletin merges, PE changes): immutable commits of a recorded
    # branch, from the organization.
    for e in (e for e in root if e.tag == "project"):
        path = e.get("path") or e.get("name")
        if path not in base or path in PINNED:
            continue
        if (e.get("remote") != "reborn-mondrian"
                or not re.fullmatch(r"[0-9a-f]{40}", e.get("revision", ""))
                or not re.fullmatch(r"refs/heads/(bringup|port|feature)/[\w.-]+", e.get("upstream", ""))):
            sys.exit(f"{path}: a replaced project must be an organization commit of a recorded branch")
    # Unmodified AOSP 17 projects that the bootstrap profile removes but other
    # AOSP projects depend on: they must come from AOSP at the default tag.
    for path in RESTORED_AOSP:
        project = build.get(path)
        if project is None or project.get("name") != path:
            sys.exit(f"{path}: expected the AOSP project {path}")
        if project.get("remote") or project.get("revision"):
            sys.exit(f"{path}: must be unmodified AOSP at the default revision")
    added = sorted(set(build) - set(base) - RESTORED_AOSP - set(EXTERNAL) - {KERNEL_RELEASE[0]} - set(PINNED)
                   - set(ADDED))
    if added:
        sys.exit(f"build profile adds unreviewed paths: {added}")
    paths = [p for p in build]
    if len(paths) != len(set(paths)):
        sys.exit("duplicate checkout paths")
    print(f"[PASS] pe_mondrian build profile: {len(build)} projects, {len(PINNED)} mondrian pins")


if __name__ == "__main__":
    main()
