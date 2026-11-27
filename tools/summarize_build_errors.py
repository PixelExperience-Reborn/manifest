#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""List the failed actions of an Android build with their first errors.

soong_ui writes every failed action to out/error.log:

    FAILED: <description>
    Outputs: <files>
    Error: exited with code: 1
    Command: <command line>
    Output:
    <what the action printed>

With keep-going (m -k) one build can fail many actions. This prints one
block per action: its description, its first output file, and the first
error lines it printed (compiler, javac, kotlinc, linker, metalava ...),
without the command lines, which run to thousands of characters.

    summarize_build_errors.py out/error.log [MAX_ERRORS_PER_ACTION]
"""
import re
import sys
from pathlib import Path

ERROR = re.compile(r"\berror\b[:\s]|^e: |\bfatal\b|undefined (symbol|reference)|\bFAILED\b|Error:|"
                   r"^\S+:\d+(:\d+)?: (error|fatal)", re.I)
NOISE = re.compile(r"^\d+ errors? generated\.|^\s*\d+ \||^\s*\|")
WIDTH = 300


def actions(text):
    """Split error.log into (description, outputs, error, output lines)."""
    found = []
    for block in re.split(r"(?m)^(?=FAILED: )", text):
        if not block.startswith("FAILED: "):
            continue
        lines = block.splitlines()
        description, outputs, error, output = lines[0][8:].strip(), "", "", []
        in_output = False
        for line in lines[1:]:
            if in_output:
                output.append(line)
            elif line.startswith("Outputs: "):
                outputs = line[9:].strip()
            elif line.startswith("Error: "):
                error = line[7:].strip()
            elif line.startswith("Output:"):
                in_output = True
                rest = line[7:].strip()
                if rest:
                    output.append(rest)
        found.append((description, outputs, error, output))
    return found


def first_errors(output, limit):
    picked = []
    for line in output:
        line = line.rstrip()
        if not line or line.startswith(("Command: ", "*** ")) or len(line) > 4 * WIDTH:
            continue
        if ERROR.search(line) and not NOISE.search(line):
            picked.append(line[:WIDTH])
            if len(picked) >= limit:
                break
    if not picked:  # nothing looks like an error: show the end of the output
        picked = [l.rstrip()[:WIDTH] for l in output if l.strip()][-limit:]
    return picked


def main():
    log = Path(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    found = actions(log.read_text(errors="ignore"))
    print(f"== {len(found)} failed actions ({log})")
    for number, (description, outputs, error, output) in enumerate(found, 1):
        print(f"\n[{number}] {description}")
        if outputs:
            print(f"    output: {outputs.split()[0]}")
        if error:
            print(f"    {error}")
        for line in first_errors(output, limit):
            print(f"    | {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
