#!/usr/bin/env python3
"""Cross-check the audited 135 projects against the original PE14 manifest.

Original PE manifest MUST be a separate read-only checkout pinned to
136aee696422bda841eb5c6a3c9279bbb6bbef02. This parses XML only.
It never imports historical source or any GMS/device code into AOSP17.
"""
import argparse
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_COMMIT = "136aee696422bda841eb5c6a3c9279bbb6bbef02"
MAIN = ("snippets/pixel.xml", "snippets/pixel-extras.xml", "snippets/pixel-caf.xml")
OPTIONAL = "snippets/pixel-extras-dependencies.xml"
MATRIX = "docs/ANDROID_17_135_REPOSITORY_PORT_MATRIX.md"
PROJECT_PATTERN = re.compile(
    r"^\|\s*P[0-3]\s*\|\s*\x60([^\x60]+)\x60\s*\|"
    r"\s*\[([^\]]+)\]\(https://github\.com/PixelExperience-Reborn/([^)]+)\)"
)


def project_map(filename):
    root = ET.parse(filename).getroot()
    if root.tag != "manifest":
        raise ValueError("expected manifest: " + str(filename))
    projects = {}
    for project in root.findall("project"):
        path = project.get("path") or project.get("name")
        name = project.get("name")
        if not path or not name or path in projects:
            raise ValueError("invalid or duplicate project in " + str(filename))
        projects[path] = name
    return projects


def validate(original):
    original = Path(original)
    head = subprocess.run(
        ["git", "-C", str(original), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if head != ORIGINAL_COMMIT:
        raise ValueError("unverified original PE14 SHA: " + head)

    original_root = ET.parse(original / "default.xml").getroot()
    includes = [e.get("name") for e in original_root.findall("include")]
    for path in (*MAIN, "snippets/remove.xml"):
        if path not in includes:
            raise AssertionError("original default omits " + path)
    if OPTIONAL in includes:
        raise AssertionError("optional OEM dependencies unexpectedly in original default")

    groups, all_projects = {}, {}
    for xml in MAIN:
        group = project_map(original / xml)
        if set(group).intersection(all_projects):
            raise AssertionError("overlapping original PE14 snippet paths")
        all_projects.update(group)
        groups[xml] = group
    optional = project_map(original / OPTIONAL)
    if set(optional).intersection(all_projects):
        raise AssertionError("optional paths overlap main PE manifest")

    matrix = {}
    for line in (ROOT / MATRIX).read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*P[0-3]\s*\|", line):
            continue
        found = PROJECT_PATTERN.match(line)
        if not found:
            raise AssertionError("invalid matrix project row: " + line[:110])
        path, label, repo = found.groups()
        if label != repo or path in matrix:
            raise AssertionError("bad link or duplicate checkout: " + path)
        matrix[path] = repo
    if len(matrix) != 135:
        raise AssertionError("selected audit matrix changed from 135 rows")
    for path, name in matrix.items():
        if all_projects.get(path) != name:
            raise AssertionError("matrix entry does not match original PE14: " + path)

    expected = {
        "snippets/pixel.xml": (71, 64),
        "snippets/pixel-extras.xml": (29, 24),
        "snippets/pixel-caf.xml": (85, 47),
    }
    for source, (total, audited) in expected.items():
        group = groups[source]
        if len(group) != total or len(set(group) & set(matrix)) != audited:
            raise AssertionError("source scope drift in " + source)
    if len(all_projects) != 185 or len(optional) != 5:
        raise AssertionError("original main or optional project count drift")

    missing = {p: n for p, n in all_projects.items() if p not in matrix}
    if len(missing) != 50:
        raise AssertionError("missing list changed: " + str(len(missing)))

    official = project_map(ROOT / "aosp17_reference.xml")
    expected_launcher = "platform/packages/apps/Launcher3"
    if official.get("packages/apps/Launcher3") != expected_launcher:
        raise AssertionError("AOSP17 Launcher3 project owner changed")
    if project_map(original / "default.xml").get("packages/apps/Launcher3") != expected_launcher:
        raise AssertionError("original PE14 no longer inherits AOSP Launcher3")
    if "packages/apps/Launcher3" in all_projects or "packages/apps/Launcher3" in optional:
        raise AssertionError("PE14 Launcher3 is not a separate PE14 snippet project")
    if missing.get("vendor/gms") != "vendor_gms":
        raise AssertionError("GMS GitLab dependency origin changed")
    if optional.get("hardware/xiaomi") != "hardware_xiaomi":
        raise AssertionError("optional Xiaomi dependency changed")
    return groups, optional, missing, official


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True)
    args = parser.parse_args()
    groups, optional, missing, official = validate(args.original)
    for xml, entries in groups.items():
        untracked = {p: n for p, n in entries.items() if p in missing}
        print(f"{xml}: {len(entries)} in PE14, {len(entries)-len(untracked)} in selected 135, "
              f"{len(untracked)} outside")
        for path, name in untracked.items():
            print(f"  OUTSIDE_MATRIX {path} | {name} | official AOSP17: {path in official}")
    print(f"Optional OEM paths (not default): {len(optional)}")
    for path, name in optional.items():
        print(f"  OPTIONAL {path} | {name}")
    print("PASS: 135/185 original PE14 projects audited; 50 outside scope, 5 optional OEM")
    print("PASS: original PE14 and AOSP17 both use Google-owned Launcher3 source")
    print("NOTE: source inventory is NOT full repo sync, Soong build or ROM boot")


if __name__ == "__main__":
    main()
