#!/usr/bin/env python3
"""Source-graph regression tests for the isolated Android17 PE manifest.

Only manifest/XML ownership tests. Does not perform repo sync, build or boot.
"""
from contextlib import redirect_stdout
from pathlib import Path
import io
import shutil
import tempfile
import unittest

import validate_aosp17_base_profiles as profiles


class ManifestEntryPointTests(unittest.TestCase):
    def setUp(self):
        self.original_root = profiles.ROOT
        self.temp = tempfile.TemporaryDirectory(prefix="pe-a17-manifest-test-")
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(setattr, profiles, "ROOT", self.original_root)
        for name, _ in profiles.STAGES:
            shutil.copyfile(self.original_root / name, self.root / name)
        shutil.copyfile(
            self.original_root / "default.xml", self.root / "default.xml"
        )
        profiles.ROOT = self.root

    def rewrite(self, filename, before, after):
        path = self.root / filename
        content = path.read_text(encoding="utf-8")
        self.assertEqual(
            content.count(before), 1,
            f"expected exactly one reviewed mutation location: {filename}",
        )
        path.write_text(content.replace(before, after), encoding="utf-8")

    def check(self):
        with redirect_stdout(io.StringIO()):
            profiles.validate()

    def test_reviewed_default_and_25_profiles(self):
        self.assertEqual(len(profiles.STAGES), 25)
        self.check()

    def test_old_pe_include_must_not_reappear(self):
        self.rewrite(
            "default.xml",
            '  <include name="aosp17_pe_p2_kernel_configs.xml" />',
            '  <include name="aosp17_pe_p2_kernel_configs.xml" />\n'
            '  <include name="snippets/pixel-caf.xml" />',
        )
        with self.assertRaisesRegex(ValueError, "default.xml must include"):
            self.check()

    def test_default_cannot_silently_use_earlier_stage(self):
        self.rewrite(
            "default.xml",
            'name="aosp17_pe_p2_kernel_configs.xml"',
            'name="aosp17_pe_p2_ril.xml"',
        )
        with self.assertRaisesRegex(ValueError, "default.xml must include"):
            self.check()

    def test_kernel_config_pin_cannot_drift(self):
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            "d02620f1f46af9eef024fb41e6d911d935699492",
            "0000000000000000000000000000000000000000",
        )
        with self.assertRaisesRegex(ValueError, "bad revision/owner"):
            self.check()

    def test_p2_remote_cannot_be_redirected(self):
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            'fetch="https://github.com/PixelExperience-Reborn"',
            'fetch="https://github.com/example"',
        )
        with self.assertRaisesRegex(ValueError, "unreviewed P2 fetch remote"):
            self.check()

    def test_p2_groups_cannot_be_changed(self):
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            'groups="vts,pdk"',
            'groups="pdk"',
        )
        with self.assertRaisesRegex(ValueError, "changed P2 groups"):
            self.check()

    def test_legacy_platform_testing_owner_cannot_be_activated(self):
        # The archived PE fork differs from its Android14 AOSP parent by
        # two obsolete Make test-list deletions. Never substitute it for
        # the official Android17 platform/platform_testing source graph.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/platform_testing" />\n'
            '  <project path="platform_testing" name="platform_testing" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_legacy_extract_tools_cannot_enter_android17(self):
        # Old prebuilts contain Android14-era unverified host binaries.
        # Blob extraction is separate from compiling an AOSP17 ROM.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="prebuilts/extract-tools" '
            'name="prebuilts_extract-tools" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed host-only extract-tools activated"):
            self.check()

    def test_legacy_kernel_build_tools_cannot_enter_android17(self):
        # The 2022 kernel host-tool snapshot is not an AOSP17 ROM
        # dependency. A future mondrian kernel build graph needs review
        # separately, even when an old host binary shares a utility name.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="prebuilts/kernel-build-tools" '
            'name="prebuilts_kernel-build-tools" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "legacy kernel host prebuilts activated"):
            self.check()

    def test_legacy_custom_host_tools_cannot_enter_android17(self):
        # Archived custom cpio/Perl/dtc/lz4c belong to old host scripts,
        # not to an approved Android17 source or mondrian build graph.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="prebuilts/tools-custom" '
            'name="prebuilts_tools-custom" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "legacy custom host tools activated"):
            self.check()

    def test_unreviewed_vendor_extractor_cannot_enter_android17(self):
        # Neither the obsolete PE shell fork nor incomplete modern Python
        # host tooling belongs to the ROM graph before vendor device work.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="tools/extract-utils" '
            'name="tools_extract-utils" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed vendor extractor host source activated"):
            self.check()

    def test_android14_metalava_fork_cannot_replace_android17(self):
        # The archived PE branch is the unmodified Android14 source tree.
        # Its monolithic Metalava cannot replace the modular Android17
        # Soong host tool without breaking API/stub generation.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/tools/metalava" />\n'
            '  <project path="tools/metalava" name="tools_metalava" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_qualcomm_telephony_requires_mondrian_ims_abi_review(self):
        # Direct Qualcomm Android17 source was imported only to an
        # isolated PE branch. Do not enable it in the ROM without checking
        # proprietary Xiaomi IMS/RIL Java and HIDL/AIDL dependencies.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/codeaurora/telephony" '
            'name="vendor_codeaurora_telephony" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "unverified Qualcomm telephony source activated"):
            self.check()

    def test_duplicate_source_owner_fails_closed(self):
        self.rewrite(
            "aosp17_pe_p2_qcom_wlan.xml",
            '</manifest>',
            '  <project name="unreviewed_wifi" path="hardware/qcom/wlan" />\n'
            '</manifest>',
        )
        with self.assertRaisesRegex(ValueError, "duplicate/unnamed project"):
            self.check()


if __name__ == "__main__":
    unittest.main(verbosity=2)
