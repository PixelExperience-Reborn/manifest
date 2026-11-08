#!/usr/bin/env python3
"""Fail-closed check for opt-in AOSP17 source-bearing mondrian BSP trial.

No repo sync or kernel compilation is implied. The trial sources are pinned
hardware references and must not replace the production PE source owners.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "aosp17_pe_mondrian_bsp_trial.xml"
AUDIT = ROOT / "aosp17_pe_mondrian_source_audit.xml"

PINS = {
    "kernel/xiaomi/sm8450": (
        "android_kernel_xiaomi_sm8450",
        "283772ceb84491fd446e340fd211d45fb9dd9a36",
    ),
    "kernel/xiaomi/sm8450-modules": (
        "android_kernel_xiaomi_sm8450-modules",
        "91cdb1347970ae98291986926eb16bf1b172138e",
    ),
    "kernel/xiaomi/sm8450-devicetrees": (
        "android_kernel_xiaomi_sm8450-devicetrees",
        "99f1330d8dce0c80de5a19f425d0a118b2eb7fe3",
    ),
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def verify():
    t = ET.parse(TRIAL).getroot()
    a = ET.parse(AUDIT).getroot()
    require(t.tag == "manifest" and a.tag == "manifest", "invalid manifest")
    includes = [c.get("name") for c in t if c.tag == "include"]
    require(includes == [AUDIT.name], "trial not layered on existing reviewed AOSP17 profile")
    removals = [c.get("name") for c in t if c.tag == "remove-project"]
    require(set(removals) == {p[0] for p in PINS.values()} and len(removals) == 3,
            "not exactly three audit-only repos removed")
    remotes = [c for c in t if c.tag == "remote"]
    require(len(remotes) == 1 and remotes[0].get("name") == "lf-bsp-trial"
            and remotes[0].get("fetch") == "https://github.com/LF52406",
            "unreviewed source remote")
    ps = [c for c in t if c.tag == "project"]
    require(len(ps) == 3, "trial must add exactly three real source trees")
    by_path = {p.get("path"): p for p in ps}
    require(len(by_path) == len(ps) and set(by_path) == set(PINS),
            "incorrect source checkout locations")
    for path, (repo, sha) in PINS.items():
        p = by_path[path]
        require(p.get("name") == repo and p.get("remote") == "lf-bsp-trial",
                f"unreviewed repository: {path}")
        require(p.get("revision") == sha, f"unpinned or wrong source: {path}")
        require(p.get("upstream") == "refs/heads/lineage-24.0",
                f"wrong public history: {path}")
        require("notdefault" not in p.get("groups", ""),
                "trial project is silently excluded from repo sync")
    own = {c.get("path"): c for c in a if c.tag == "project"}
    require("device/xiaomi/mondrian" in own and "device/xiaomi/sm8450-common" in own,
            "independent PE device trees have been lost")
    require(set(PINS).issubset(own), "base audit source pin not present")
    require(not any("vendor/xiaomi" in c.get("path", "")
                    or c.get("path", "") == "hardware/xiaomi"
                    for c in ps), "proprietary or HAL source implicitly activated")
    # The trial manifest is merely a transport for the same kernel/module/DT
    # revisions recorded by our independently maintained kernel source lock.
    import json
    lock = json.loads((ROOT / "bsp_trial_lock.json").read_text(encoding="utf-8"))
    expected_by_role = {
        "kernel": "kernel/xiaomi/sm8450",
        "modules": "kernel/xiaomi/sm8450-modules",
        "devicetrees": "kernel/xiaomi/sm8450-devicetrees",
    }
    require(lock["status"] == "TRIAL_SOURCE_ONLY_NOT_SELECTED_FOR_RELEASE",
            "trial source lock incorrectly promoted")
    require(not any(lock["gates"].values()), "build gates incorrectly promoted")
    for source in lock["sources"]:
        path = expected_by_role[source["role"]]
        actual = by_path[path]
        require(actual.get("revision") == source["commit_sha"],
                f"manifest and immutable BSP source lock disagree: {path}")
        require("LF52406/" + actual.get("name") == source["repository"],
                f"source lock repository owner changed: {path}")
    require(not any(c.tag == "project" for c in t if c.get("name", "").startswith("lineage_")),
            "a ROM product slipped into the trial")
    print("[PASS] independent PE AOSP17 device base preserved; three full LF BSP trees locked")
    print("[NOTE] source trial only; needs ACK, compiler, matching KMI, vendor blobs, AVB and boot")


if __name__ == "__main__":
    try:
        verify()
    except (ValueError, ET.ParseError, OSError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        sys.exit(1)
