#!/usr/bin/env python3
"""Cross-check 135 historical PE repos against three manifest snippets."""
from collections import Counter
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SNIPPETS = {"pixel.xml": 64, "pixel-extras.xml": 24, "pixel-caf.xml": 47}
PRIORITIES = {"P0": 20, "P1": 26, "P2": 85, "P3": 4}
LINK = re.compile(r"^\[([^\]]+)\]\(https://github\.com/PixelExperience-Reborn/([^/\s)]+)(?:/[^)]*)?\)$")


def main():
    original = {}
    for file_name, count in SNIPPETS.items():
        root = ET.parse(ROOT / "snippets" / file_name).getroot()
        projects = root.findall("project")
        assert len(projects) == count, (file_name, len(projects), count)
        for entry in projects:
            path, name = entry.get("path"), entry.get("name")
            assert entry.get("remote") == "reborn"
            assert path and name and path not in original, (file_name, path)
            original[path] = name
    assert len(original) == 135
    assert len(set(original.values())) == 135, "duplicate GitHub repo names"

    counts = Counter()
    matrix = {}
    lines = (ROOT / "docs/ANDROID_17_135_REPOSITORY_PORT_MATRIX.md").read_text().splitlines()
    for line_number, line in enumerate(lines, 1):
        if not re.match(r"^\| P[0-3] \|", line):
            continue
        # Markdown allows escaped pipes inside code/text cells. Do not split
        # e.g. an Android permission protectionLevel: signature\\|privileged.
        cells = [v.strip().replace(r"\\|", "|") for v in
                 re.split(r"(?<!\\\\)\\|", line.strip().strip("|"))]
        assert len(cells) == 6, (line_number, "wrong column count")
        priority, path, link, classification, action, status = cells
        assert path.startswith("`") and path.endswith("`"), (line_number, path)
        path = path[1:-1]
        match = LINK.fullmatch(link)
        assert match is not None, (line_number, link)
        label, github_repo = match.groups()
        assert label == github_repo, (line_number, link)
        assert path not in matrix, (line_number, "duplicate project", path)
        assert classification and action and status, (line_number, "missing audit fields")
        # Reviewed entries have descriptive classifications, not only the
        # original two inventory labels. Preserve strict path/link/count checks.
        assert (classification.startswith(("Заменяет AOSP17", "Дополнение PE"))
                or (len(classification) >= 25 and
                    not classification.startswith("Не проверен"))), (line_number, classification)
        matrix[path] = github_repo
        counts[priority] += 1

    assert dict(counts) == PRIORITIES, (dict(counts), PRIORITIES)
    assert len(matrix) == 135, len(matrix)
    assert matrix == original, {
        "missing": sorted(set(original) - set(matrix)),
        "extra": sorted(set(matrix) - set(original)),
        "wrong": sorted(k for k in original if matrix.get(k) != original[k]),
    }
    pending = sum(v.startswith("Не проверен") for line in lines
                  if re.match(r"^\| P[0-3] \|", line)
                  for v in [line.strip().split("|")[-2].strip()])
    print("PASS: 135 unique PE repository paths and GitHub names mapped correctly")
    print("PASS: P0=20, P1=26, P2=85, P3=4")
    print(f"INVENTORY ONLY: {pending} rows remain unreviewed; no Android build is implied")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ET.ParseError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
