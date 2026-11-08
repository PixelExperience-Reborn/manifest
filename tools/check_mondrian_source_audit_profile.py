#!/usr/bin/env python3
"""Fail-closed AOSP17 mondrian source-profile verifier.

This validates *source graph + product wiring*, not Soong, kernel compilation,
partition layouts, Qualcomm ABI, vendor firmware, AVB or device boot.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "aosp17_pe_mondrian_source_audit.xml"
EXPECTED = {
    "device/xiaomi/mondrian": ("android_device_xiaomi_mondrian", "7e768d2b4f57dd1d4bc5595013c87c2c84c3ec54"),
    "device/xiaomi/sm8450-common": ("android_device_xiaomi_sm8450-common", "9374ff3fc1e26bd81a819730ce52ff7777cd8797"),
    "kernel/xiaomi/sm8450": ("android_kernel_xiaomi_sm8450", "769d4b03b4203c48ae2615b8b56389e2612ed237"),
    "kernel/xiaomi/sm8450-modules": ("android_kernel_xiaomi_sm8450-modules", "11505e89ed42004e346facebf695d1682dead8d0"),
    "kernel/xiaomi/sm8450-devicetrees": ("android_kernel_xiaomi_sm8450-devicetrees", "bd1874c9345707695867c694d55567da1f6d3f15"),
}
VENDOR_SHA = "38bf62440be54eb86b4f5c6ccc888e467b5a9a53"
SHA = re.compile(r"^[a-f0-9]{40}$")


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def parse_profile(path):
    visiting = set()
    nodes = []

    def walk(filename):
        require(filename not in visiting, f"recursive include: {filename}")
        require(filename.endswith(".xml") and "/" not in filename, f"unsafe include: {filename}")
        p = path / filename
        require(p.is_file(), f"missing included manifest: {filename}")
        visiting.add(filename)
        root = ET.parse(p).getroot()
        require(root.tag == "manifest", f"invalid manifest root: {filename}")
        for child in root:
            if child.tag == "include":
                walk(child.attrib["name"])
            else:
                nodes.append((filename, child))
        visiting.remove(filename)

    walk(PROFILE)
    return nodes


def audit_manifest():
    nodes = parse_profile(ROOT)
    local = ET.parse(ROOT / PROFILE).getroot()
    projects = [p for p in local if p.tag == "project"]
    require(len(projects) == 5, "audit profile must include exactly five PE BSP projects")
    by_path = {p.get("path"): p for p in projects}
    require(set(by_path) == set(EXPECTED), "unexpected checkout path in mondrian profile")
    for path, (repo, sha) in EXPECTED.items():
        p = by_path[path]
        require(p.get("name") == repo, f"wrong repository: {path}")
        require(p.get("revision") == sha and bool(SHA.fullmatch(sha)), f"unreviewed commit: {path}")
        require(p.get("remote") == "reborn-mondrian", f"wrong remote: {path}")
        require(p.get("upstream", "").startswith("refs/heads/"), f"upstream missing: {path}")
    require(
        [x.get("name") for x in local if x.tag == "include"] ==
        ["aosp17_pe_p2_kernel_configs.xml"],
        "audit profile must inherit the staged AOSP17 base",
    )
    require(
        any(n.tag == "default" and n.get("revision") == "refs/tags/android-17.0.0_r1"
            for _, n in nodes),
        "Android 17 r1 source base not present",
    )
    vendors = [n for _, n in nodes if n.tag == "project" and n.get("path") == "vendor/aosp"]
    require(len(vendors) == 1 and vendors[0].get("revision") == VENDOR_SHA,
            "incorrect reviewed Android17 vendor/aosp pin")
    for _, node in nodes:
        if node.tag != "project":
            continue
        path = node.get("path") or ""
        require(path not in ("vendor/xiaomi/mondrian", "vendor/xiaomi/sm8450-common",
                             "hardware/xiaomi"),
                f"unreviewed proprietary/Hardware HAL included: {path}")
    print("[PASS] opt-in AOSP17 profile, reviewed PE vendor and five immutable BSP references")


def active_lines(path):
    return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                     if line.strip() and not line.lstrip().startswith("#"))


def check_checkout(base):
    paths = dict(EXPECTED)
    paths["vendor/aosp"] = ("vendor_aosp", VENDOR_SHA)
    for path, (_, expected_sha) in paths.items():
        checkout = base / path
        require(checkout.is_dir(), f"missing source checkout: {path}")
        result = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                                check=True, text=True, capture_output=True)
        require(result.stdout.strip() == expected_sha,
                f"SHA mismatch in {path}: {result.stdout.strip()} != {expected_sha}")
    device_dir = base / "device/xiaomi/mondrian"
    common_dir = base / "device/xiaomi/sm8450-common"
    product = active_lines(device_dir / "pe_mondrian.mk")
    product_registration = active_lines(device_dir / "AndroidProducts.mk")
    device_mk = active_lines(device_dir / "device.mk")
    board = active_lines(device_dir / "BoardConfig.mk")
    common_board = active_lines(common_dir / "BoardConfigCommon.mk")
    vendor_common = active_lines(base / "vendor/aosp/config/common.mk")
    require("$(LOCAL_DIR)/pe_mondrian.mk" in product_registration,
            "mondrian not registered")
    require("PRODUCT_NAME := pe_mondrian" in product, "wrong product")
    require("PRODUCT_DEVICE := mondrian" in product, "wrong device")
    require("device/xiaomi/mondrian/device.mk" in product, "missing device inheritance")
    require("vendor/aosp/config/common_full_phone.mk" in product, "missing reviewed PE product")
    require("device/xiaomi/sm8450-common/common.mk" in device_mk, "wrong common product")
    require("device/xiaomi/sm8450-common/BoardConfigCommon.mk" in board, "wrong common board")
    require("TARGET_BOARD_PLATFORM := taro" in common_board, "unexpected platform")
    require("Launcher3QuickStep" in vendor_common, "AOSP17 launcher selection missing")
    for key in ("vendor/lineage", "org.lineageos", "lineage_mondrian",
                "fm-commonsys", "FMRadio"):
        for label, text in (("mondrian product", product), ("mondrian device", device_mk),
                            ("common board", common_board)):
            require(key.lower() not in text.lower(), f"unreviewed {key} in {label}")
    k = json.loads((base / "kernel/xiaomi/sm8450/source-candidates.json").read_text())
    m = json.loads((base / "kernel/xiaomi/sm8450-modules/modules-bsp-candidates.json").read_text())
    d = json.loads((base / "kernel/xiaomi/sm8450-devicetrees/dtbo-bsp-candidates.json").read_text())
    require(k["target"]["device"] == "mondrian" and not k["target"]["build_proven"],
            "kernel falsely marked build-ready")
    require(k["selected_kernel_source"] is None and not any(k["gates"].values()),
            "kernel import gate bypass")
    require(m["required_qualification"]["kernel_source_commit"] is None, "modules prematurely selected")
    require(d["required_qualification"]["kernel_commit"] is None, "DTBO prematurely selected")
    require((base / "build/make/target/product/core_64_bit.mk").is_file(),
            "AOSP17 core_64_bit.mk not present")
    require((base / "build/make/target/product/full_base_telephony.mk").is_file(),
            "AOSP17 full_base_telephony.mk not present")
    print("[PASS] pinned source checkouts, native PE product inheritance, AOSP17 Make prerequisites")
    print("[NOTE] This is not an AOSP17 Soong or kernel build and has no vendor blobs/boot test")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--checkout-root", type=Path)
        args = parser.parse_args()
        audit_manifest()
        if args.checkout_root:
            check_checkout(args.checkout_root.resolve())
    except (ValueError, OSError, ET.ParseError, subprocess.CalledProcessError,
            json.JSONDecodeError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        sys.exit(1)
