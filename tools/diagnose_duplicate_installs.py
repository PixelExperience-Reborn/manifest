#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explain duplicate install rules of an Android build (Kati: "overriding
commands for target").

Kati stops at the first duplicate and names only the installed path. This
lists every installed path that two rules of out/soong/installs-<product>.mk
produce, the file each rule copies (which names the module and its variant),
and, for a module built from source, the modules whose build statements in
out/soong/build.<product>*.ninja use that variant: the reason it is installed.

    diagnose_duplicate_installs.py OUT_DIR PRODUCT
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

RULE = re.compile(r"^(out/target/product/\S+?):\s+(.*)$")
INTERMEDIATE = re.compile(r"out/soong/\.intermediates/(.+?/(?:android|linux)_[^/]+)/")


def duplicate_installs(installs):
    rules = defaultdict(list)
    for number, line in enumerate(installs.read_text(errors="ignore").splitlines(), 1):
        match = RULE.match(line)
        if match:
            sources = [s for s in match[2].replace("|", " ").split() if s.startswith("out/")]
            rules[match[1]].append((number, sources[0] if sources else match[2].strip()))
    return {target: found for target, found in rules.items() if len(found) > 1}


def users(ninja_files, variant_dir, limit=25):
    """Outputs of the build statements that read files of variant_dir."""
    if not ninja_files:
        return []
    needle = f"/.intermediates/{variant_dir}/"
    grep = subprocess.run(["grep", "-h", "-F", needle, *map(str, ninja_files)],
                          capture_output=True, text=True, errors="ignore")
    found = []
    for line in grep.stdout.splitlines():
        if not line.startswith("build "):
            continue
        output = line[6:].split(":", 1)[0].split()[0]
        if needle in output:  # the module's own outputs
            continue
        module = INTERMEDIATE.search(output)
        name = module[1] if module else output
        if name not in found:
            found.append(name)
        if len(found) >= limit:
            break
    return found


def chain(ninja_files, variant_dir, depth, seen, max_depth=3, budget=None):
    """Print the users of a module variant, and theirs, up to max_depth.
    Each level is a grep of the whole ninja file: budget caps their number."""
    budget = budget if budget is not None else [12]
    if budget[0] <= 0:
        return
    budget[0] -= 1
    for user in users(ninja_files, variant_dir):
        print(f"{'    ' * (depth + 1)}used by {user}", flush=True)
        if user not in seen and depth < max_depth and user.endswith("_shared"):
            seen.add(user)
            chain(ninja_files, user, depth + 1, seen, max_depth, budget)


def main():
    out_dir, product = Path(sys.argv[1]), sys.argv[2]
    installs = out_dir / f"soong/installs-{product}.mk"
    if not installs.is_file():
        print(f"no {installs}")
        return 1
    ninja_files = sorted((out_dir / "soong").glob(f"build.{product}*.ninja"))
    duplicates = duplicate_installs(installs)
    print(f"== {len(duplicates)} installed paths with more than one rule ({installs.name})")
    for target, found in sorted(duplicates.items()):
        print(f"\n{target}")
        for number, source in found:
            print(f"  line {number}: {source}")
            variant = INTERMEDIATE.search(source)
            if variant and "/vendor/xiaomi/" not in source:
                chain(ninja_files, variant[1], depth=1, seen=set())
    return 0


if __name__ == "__main__":
    sys.exit(main())
