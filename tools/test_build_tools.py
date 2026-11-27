#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The build script's keep-going mode and its failed action summary."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "aosp17_mondrian_build.sh"
SUMMARY = TOOLS / "summarize_build_errors.py"

# The two failed actions of a keep-going build, as soong_ui writes out/error.log.
ERROR_LOG = """\
FAILED: //external/gptfdisk:sgdisk clang++ sgdisk.cc
Outputs: out/soong/.intermediates/external/gptfdisk/sgdisk/android_arm64_armv8-5a_cortex-a76/obj/external/gptfdisk/sgdisk.o
Error: exited with code: 1
Command: /srv/.rbe/rewrapper --labels=type=compile,lang=cpp,compiler=clang """ + "-Wall " * 400 + """
Output:
external/gptfdisk/sgdisk.cc:134:16: error: 'main' should not be 'extern "C"' [-Werror,-Wmain]
  134 | extern "C" int main(int argc, char *argv[]) {
      |                ^
1 error generated.
FAILED: //packages/apps/Example:Example javac
Outputs: out/soong/.intermediates/packages/apps/Example/Example/android_common/javac/Example.jar
Error: exited with code: 1
Command: javac ...
Output:
packages/apps/Example/src/Example.java:10: error: cannot find symbol
1 error
"""


class SummarizeBuildErrorsTest(unittest.TestCase):
    def run_summary(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "error.log"
            log.write_text(text)
            p = subprocess.run([sys.executable, "-I", str(SUMMARY), str(log)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def test_lists_every_failed_action_with_its_errors(self):
        out = self.run_summary(ERROR_LOG)
        self.assertIn("== 2 failed actions", out)
        self.assertIn("[1] //external/gptfdisk:sgdisk clang++ sgdisk.cc", out)
        self.assertIn("sgdisk.cc:134:16: error: 'main' should not be 'extern \"C\"'", out)
        self.assertIn("[2] //packages/apps/Example:Example javac", out)
        self.assertIn("Example.java:10: error: cannot find symbol", out)
        self.assertIn("output: out/soong/.intermediates/external/gptfdisk/sgdisk/", out)

    def test_leaves_out_command_lines_and_caret_lines(self):
        out = self.run_summary(ERROR_LOG)
        self.assertNotIn("rewrapper", out)
        self.assertNotIn("1 error generated", out)
        self.assertTrue(all(len(line) <= 320 for line in out.splitlines()))

    def test_output_without_error_lines_shows_its_end(self):
        out = self.run_summary("FAILED: //a:b genrule\nError: exited with code: 2\nOutput:\nfirst\nlast words\n")
        self.assertIn("| last words", out)


class BuildScriptTest(unittest.TestCase):
    def test_keep_going_is_the_default_for_building_stages(self):
        script = SCRIPT.read_text()
        self.assertIn('KEEP_GOING="${KEEP_GOING:-true}"', script)
        self.assertIn('if [[ "$KEEP_GOING" == true ]]; then make_args=(-k); fi', script)
        for target in ("vendorimage", "bacon", "recoveryimage"):
            self.assertRegex(script, rf'm "\$\{{make_args\[@\]\}}" {target} 2>&1')
        # The analysis stage has nothing to keep going for.
        self.assertIn("graph)  m nothing 2>&1", script)

    def test_failed_actions_are_summarized(self):
        script = SCRIPT.read_text()
        self.assertIn('python3 "$SCRIPT_DIR/summarize_build_errors.py" out/error.log', script)
        self.assertTrue(SUMMARY.is_file())

    def test_server_build_environment_is_kept(self):
        # ServerHive terminates a build without its RBE/ninja environment.
        script = SCRIPT.read_text()
        self.assertNotRegex(script, r"(?m)^\s*(unset|export)\s+(USE_RBE|SOONG_NINJA|CUSTOM_NINJA_BIN|BASH_ENV)\b")
        self.assertNotRegex(script, r"(?m)^\s*(USE_RBE|SOONG_NINJA|CUSTOM_NINJA_BIN|BASH_ENV)=")

    def test_script_is_valid_bash(self):
        p = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == "__main__":
    unittest.main()
