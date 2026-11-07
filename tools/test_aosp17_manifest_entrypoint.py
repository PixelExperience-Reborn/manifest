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
            self.original_root / "aosp17_pe_p2_nfc_security_candidate.xml",
            self.root / "aosp17_pe_p2_nfc_security_candidate.xml",
        )
        shutil.copyfile(
            self.original_root / "aosp17_pe_p2_se_security_candidate.xml",
            self.root / "aosp17_pe_p2_se_security_candidate.xml",
        )
        shutil.copyfile(
            self.original_root / "aosp17_pe_p2_qcom_audio_aidl_candidate.xml",
            self.root / "aosp17_pe_p2_qcom_audio_aidl_candidate.xml",
        )
        shutil.copyfile(
            self.original_root / "aosp17_pe_p2_qcom_display_aidl_candidate.xml",
            self.root / "aosp17_pe_p2_qcom_display_aidl_candidate.xml",
        )
        shutil.copyfile(
            self.original_root / "aosp17_pe_p2_qcom_health_aidl_candidate.xml",
            self.root / "aosp17_pe_p2_qcom_health_aidl_candidate.xml",
        )
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

    def test_legacy_custom_preference_not_activated_without_android17_redesign(self):
        # The 2022 library depends on LineageHardwareManager, an old
        # privileged broadcast protocol and 2022-era Preference callbacks.
        # Official AOSP17 Settings does not need this dependency.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/custom-preference" '
            'name="vendor_custom-preference" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed legacy preference library activated"):
            self.check()

    def test_unreviewed_legacy_nxp_hidl_cannot_enter_android17(self):
        # Archived vendor/nxp/nfc forces PN81T and a second HIDL 1.2
        # INfc/default provider. Mondrian uses an NXP AIDL HAL instead.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/nfc" '
            'name="vendor_nxp_nfc" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed legacy PN8x NXP NFC HAL activated"):
            self.check()

    def test_nxp_hidl_fork_cannot_replace_aosp17_hardware_nxp(self):
        # Even reusing the official checkout path cannot replace its
        # Android17 owner with the obsolete PE/HIDL repo.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/nfc" />\n'
            '  <project path="hardware/nxp/nfc" '
            'name="vendor_nxp_nfc" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_nxp_legacy_libnfc_nci_cannot_enter_android17(self):
        # The 2022 NXP SN100x HIDL library is not a proven drop-in
        # replacement for AOSP17's NFC Mainline native/APEX stack.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/commonsys/external/libnfc-nci" '
            'name="vendor_nxp_opensource_commonsys_external_libnfc-nci" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "legacy NXP libnfc-nci stack activated"):
            self.check()

    def test_nxp_legacy_libnfc_nci_must_not_reown_mainline_nfc(self):
        # Replacing the official package path with old NFC source must
        # fail ownership validation even when the path count is unchanged.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/packages/modules/Nfc" />\n'
            '  <project path="packages/modules/Nfc" '
            'name="vendor_nxp_opensource_commonsys_external_libnfc-nci" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_legacy_nxp_java_nfc_framework_cannot_enter_android17(self):
        # Archived NXP service extensions contain device-specific Binder
        # routing, SEMS and WLC APIs with no proven AOSP17 consumer.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/commonsys/frameworks" '
            'name="vendor_nxp_opensource_commonsys_frameworks" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed NXP NFC Java framework activated"):
            self.check()

    def test_nxp_java_framework_must_not_replace_aosp17_secure_element(self):
        # Enabling old proprietary Java/SEMS wrappers may not silently
        # take ownership of the modern native OMAPI implementation.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/system/secure_element" />\n'
            '  <project path="system/secure_element" '
            'name="vendor_nxp_opensource_commonsys_frameworks" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_legacy_nxp_nfc_apk_cannot_enter_android17(self):
        # Archived NQNfcNci carries its own com.android.nfc service, JNI
        # and HIDL dependencies; never install next to AOSP17 NFC Mainline.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/commonsys/packages/apps/Nfc" '
            'name="vendor_nxp_opensource_commonsys_packages_apps_Nfc" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "legacy NXP NFC application activated"):
            self.check()

    def test_legacy_nxp_nfc_apk_cannot_replace_mainline(self):
        # Re-owning packages/modules/Nfc by archived QSSI implementation
        # must be rejected even if the manifest path count stays constant.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/packages/modules/Nfc" />\n'
            '  <project path="packages/modules/Nfc" '
            'name="vendor_nxp_opensource_commonsys_packages_apps_Nfc" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_nfc_security_candidate_revision_is_strictly_pinned(self):
        # Experiment must not silently advance to another tag/SHA or
        # claim a security patch which has not been inspected.
        self.rewrite(
            "aosp17_pe_p2_nfc_security_candidate.xml",
            "6f3a074cf6c87a2dcc3970c03462a6970b06f9cd",
            "0000000000000000000000000000000000000000",
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed NFC security candidate manifest shape or pin"):
            self.check()

    def test_nfc_security_candidate_must_not_switch_default_profile(self):
        # Newer NFC source is test-only until security, APEX and
        # actual device validation; the 25-stage default must remain safe.
        self.rewrite(
            "default.xml",
            'name="aosp17_pe_p2_kernel_configs.xml"',
            'name="aosp17_pe_p2_nfc_security_candidate.xml"',
        )
        with self.assertRaisesRegex(ValueError, "default.xml must include"):
            self.check()

    def test_archived_nxp_hidl_interfaces_cannot_enter_android17(self):
        # Historical 2020 1.0/1.1/2.0 HIDL modules are not replacements
        # for NFC AIDL 2 or the frozen NXP vendor extension AIDL 1.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/interfaces/nfc" '
            'name="vendor_nxp_opensource_interfaces_nfc" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived NXP NFC HIDL interfaces activated"):
            self.check()

    def test_archived_nxp_hidl_must_not_replace_current_nxp_hal(self):
        # Mainline-compatible hardware/nxp/nfc source must keep its
        # official AOSP17 owner rather than an unreviewed old HIDL tree.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/nfc" />\n'
            '  <project path="hardware/nxp/nfc" '
            'name="vendor_nxp_opensource_interfaces_nfc" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_archived_pn5xx_hidl_hal_must_not_enter_android17(self):
        # Old PN5xx HIDL 1.2, JCOP, eSE and PN81T board examples cannot
        # enter a modern AOSP17 AIDL NFC source graph as an extra checkout.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/pn5xx/halimpl" '
            'name="vendor_nxp_opensource_pn5xx_halimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived PN5xx NXP HIDL HAL activated"):
            self.check()

    def test_archived_pn5xx_hidl_cannot_replace_aosp17_nxp_hal(self):
        # Replacement of official NXP HAL with the legacy HAL is a
        # source-ownership violation, not a legitimate new PE device port.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/nfc" />\n'
            '  <project path="hardware/nxp/nfc" '
            'name="vendor_nxp_opensource_pn5xx_halimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_archived_pn5xx_hidl_service_cannot_enter_android17(self):
        # 2020 HIDL NFC 1.2 + NXP/legacy service wrappers and old native
        # HAL shall not become a second NFC HAL source in AOSP17.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/pn5xx/hidlimpl" '
            'name="vendor_nxp_opensource_pn5xx_hidlimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived PN5xx NFC HIDL service activated"):
            self.check()

    def test_archived_pn5xx_hidl_service_cannot_replace_aosp17_hal(self):
        # A HIDL implementation cannot silently take the official
        # Android17 AIDL hardware/nxp/nfc source owner.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/nfc" />\n'
            '  <project path="hardware/nxp/nfc" '
            'name="vendor_nxp_opensource_pn5xx_hidlimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_archived_sn100x_hal_cannot_enter_android17(self):
        # Archive uses NFC HIDL1.2, eSE/JCOP clients, unverified NFCC
        # defaults and old NXP HAL modules. Never import into AOSP17.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/sn100x/halimpl" '
            'name="vendor_nxp_opensource_sn100x_halimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived SN100x NXP NFC HAL activated"):
            self.check()

    def test_archived_sn100x_hal_cannot_replace_official_aosp17_hal(self):
        # A legacy HIDL HAL and boot-time SE loader must not become owner
        # of the verified official Android17 native NXP NFC AIDL source.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/nfc" />\n'
            '  <project path="hardware/nxp/nfc" '
            'name="vendor_nxp_opensource_sn100x_halimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_archived_sn100x_hidl_service_cannot_enter_android17(self):
        # These wrappers register system NFC HIDL1.2 plus vendor HIDL,
        # and require the old HIDL native stack, not NFC AIDL V2.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/opensource/sn100x/hidlimpl" '
            'name="vendor_nxp_opensource_sn100x_hidlimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived SN100x NFC HIDL services activated"):
            self.check()

    def test_archived_sn100x_hidl_cannot_replace_aosp17_nxp_hal(self):
        # A native NFC HIDL service source cannot replace the official
        # independent Android17 NXP NFC HAL stable-AIDL owner.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/nfc" />\n'
            '  <project path="hardware/nxp/nfc" '
            'name="vendor_nxp_opensource_sn100x_hidlimpl" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_legacy_nxp_p73_hidl_se_cannot_enter_android17(self):
        # Old SE HIDL1.2 advertises unverified eSE1/SIM1/SIM2 and can
        # trigger JCOP/SPI updater. It is not AOSP17 SE AIDL V1.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/secure_element" '
            'name="vendor_nxp_secure_element" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived NXP P73 Secure Element HAL activated"):
            self.check()

    def test_legacy_nxp_p73_cannot_take_official_aosp17_se_hal(self):
        # Official hardware/nxp/secure_element must remain the AOSP17
        # AIDL SE HAL owner, not a historic vendor HIDL implementation.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/secure_element" />\n'
            '  <project path="hardware/nxp/secure_element" '
            'name="vendor_nxp_secure_element" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_legacy_nxp_p73_cannot_take_system_omapi_owner(self):
        # Vendor SPI/P73 libraries are not the system OMAPI service.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/system/secure_element" />\n'
            '  <project path="system/secure_element" '
            'name="vendor_nxp_secure_element" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_se_security_candidate_is_immutable_exact_aosp17_sha(self):
        # This is the real official AOSP17 channel-index bounds fix tree,
        # not any mutable tag HEAD, and not an active ROM security SPL.
        self.rewrite(
            "aosp17_pe_p2_se_security_candidate.xml",
            "8aec22fde8121bf3f74006730ce42e9ac0366b62",
            "0000000000000000000000000000000000000000",
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed NXP SE security candidate manifest shape or pin"):
            self.check()

    def test_se_security_candidate_does_not_take_over_default(self):
        # A new SE security source alone cannot justify switching the
        # full-platform build or claiming current Android security SPL.
        self.rewrite(
            "default.xml",
            'name="aosp17_pe_p2_kernel_configs.xml"',
            'name="aosp17_pe_p2_se_security_candidate.xml"',
        )
        with self.assertRaisesRegex(ValueError, "default.xml must include"):
            self.check()

    def test_se_security_candidate_must_not_modify_system_omapi(self):
        # SE HAL AIDL source is distinct from system OMAPI; only one
        # exact hardware/nxp/secure_element checkout may be modified.
        self.rewrite(
            "aosp17_pe_p2_se_security_candidate.xml",
            '  <remove-project name="platform/hardware/nxp/secure_element" />',
            '  <remove-project name="platform/system/secure_element" />',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed NXP SE security candidate manifest shape or pin"):
            self.check()

    def test_old_nxp_jcop_ese_client_cannot_enter_aosp17(self):
        # 2022 old ese_client controls JCOP update scripts and eSE state.
        # Source-only AOSP17 must not install it as a HAL dependency.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/nxp/secure_element_extns" '
            'name="vendor_nxp_secure_element_extns" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived NXP JCOP eSE client activated"):
            self.check()

    def test_old_nxp_jcop_client_cannot_replace_official_se_aidl(self):
        # The standalone JCOP updater is not the secure element AIDL V1 HAL.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/hardware/nxp/secure_element" />\n'
            '  <project path="hardware/nxp/secure_element" '
            'name="vendor_nxp_secure_element_extns" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_old_nxp_jcop_client_cannot_replace_system_omapi(self):
        # System OMAPI/SE access policy must keep its official AOSP17 owner.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="platform/system/secure_element" />\n'
            '  <project path="system/secure_element" '
            'name="vendor_nxp_secure_element_extns" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "replaced critical AOSP17 owner"):
            self.check()

    def test_old_qualcomm_legacy_sthal_not_enabled_in_android17(self):
        # Legacy C LSM/GCS sound_trigger.primary.* is not the frozen
        # Android17 SoundTrigger3 AIDL service, and requires old kernel ABI.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/qcom/opensource/audio-hal/st-hal" '
            'name="vendor_qcom_opensource_audio-hal_st-hal" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived Qualcomm legacy Sound Trigger HAL activated"):
            self.check()

    def test_qualcomm_modern_six_repo_candidate_sha_is_immutable(self):
        # A mutable Qualcomm-derived branch alone is insufficient for a
        # stable, auditable six-repository AudioReach base.
        self.rewrite(
            "aosp17_pe_p2_qcom_audio_aidl_candidate.xml",
            "1dcb1275256b3f43b78d342d623870324a831720",
            "0000000000000000000000000000000000000000",
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed Qualcomm AudioReach candidate SHA/pin"):
            self.check()

    def test_qualcomm_modern_candidate_requires_complete_source_set(self):
        # The AIDL SoundTrigger factory cannot be treated as working
        # without PAL, AGM, DSP graph service, configuration and primary.
        self.rewrite(
            "aosp17_pe_p2_qcom_audio_aidl_candidate.xml",
            '  <project path="vendor/qcom/opensource/pal"',
            '  <project path="vendor/qcom/opensource/pal-missing"',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed Qualcomm AudioReach candidate source set"):
            self.check()

    def test_qualcomm_modern_candidate_cannot_replace_safe_default(self):
        # Six unbuilt device-facing sources may not silently become an
        # installed ROM without Soong/VINTF/SELinux and SM8475 vendor ABI.
        self.rewrite(
            "default.xml",
            'name="aosp17_pe_p2_kernel_configs.xml"',
            'name="aosp17_pe_p2_qcom_audio_aidl_candidate.xml"',
        )
        with self.assertRaisesRegex(ValueError, "default.xml must include"):
            self.check()

    def test_old_qualcomm_pal_sthal_ar_not_enabled_in_android17(self):
        # This AudioReach variant is still sound_trigger.primary.* C API,
        # not modern frozen SoundTrigger3 AIDL/NDK Binder service.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/qcom/opensource/audio-hal/st-hal-ar" '
            'name="vendor_qcom_opensource_audio-hal_st-hal-ar" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived Qualcomm PAL legacy Sound Trigger HAL activated"):
            self.check()

    def test_new_qualcomm_aidl_candidate_cannot_use_old_pal_hal_owner(self):
        # Same checkout path, different actual implementation generation.
        # The preview must pin Sony-hosted Qualcomm-derived AIDL source,
        # never the 2024 PE legacy sound_trigger.primary.* module.
        self.rewrite(
            "aosp17_pe_p2_qcom_audio_aidl_candidate.xml",
            'name="vendor-qcom-opensource-audio-hal-st-hal-ar"',
            'name="vendor_qcom_opensource_audio-hal_st-hal-ar"',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed Qualcomm AudioReach candidate SHA/pin"):
            self.check()

    def test_archived_qualcomm_hidl_display_helpers_not_active(self):
        # Old 2021 mapper@4 and vendor.display.config@2 client shims
        # must never be installed as new AOSP17 HWC3/gralloc HALs.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/qcom/opensource/display" '
            'name="vendor_qcom_opensource_display" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(
                ValueError, "archived Qualcomm HIDL display helpers activated"):
            self.check()

    def test_archived_qualcomm_display_cannot_replace_aosp17_graphics(self):
        # Old vendor gralloc metadata code cannot own frozen official
        # AOSP17 Composer3 V5 / Allocator V3 graphics interface source.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <remove-project name="hardware_interfaces" />\n'
            '  <project path="hardware/interfaces" '
            'name="vendor_qcom_opensource_display" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "unexpected historical repo"):
            self.check()

    def test_qualcomm_hwc3_candidate_requires_exact_git_commit(self):
        self.rewrite(
            "aosp17_pe_p2_qcom_display_aidl_candidate.xml",
            "baf61f736e2109522e3f72754ee7cfacbfa2dc6c",
            "0000000000000000000000000000000000000000",
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed Qualcomm HWC3 display candidate shape/pin"):
            self.check()

    def test_qualcomm_hwc3_candidate_cannot_become_default(self):
        # A source tree without verified SDM modules, vendor blobs,
        # VINTF and physical panel cannot become an active product.
        self.rewrite(
            "default.xml",
            'name="aosp17_pe_p2_kernel_configs.xml"',
            'name="aosp17_pe_p2_qcom_display_aidl_candidate.xml"',
        )
        with self.assertRaisesRegex(ValueError, "default.xml must include"):
            self.check()

    def test_qualcomm_hwc3_candidate_cannot_add_vendor_display(self):
        # A source-only HWC3 preview must not silently include the
        # old HIDL vendor display namespace with duplicate libraries.
        self.rewrite(
            "aosp17_pe_p2_qcom_display_aidl_candidate.xml",
            '  <project path="hardware/qcom/display"',
            '  <project path="vendor/qcom/opensource/display"',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed Qualcomm HWC3 display candidate shape/pin"):
            self.check()

    def test_mondrian_fm_commonsys_cannot_be_imported(self):
        # Optional FM broadcast radio is outside this product scope, even
        # if a later Qualcomm or historical PE checkout becomes available.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/qcom/opensource/fm-commonsys" '
            'name="vendor_qcom_opensource_fm-commonsys" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "FM broadcast source excluded"):
            self.check()

    def test_mondrian_fm_jni_alias_cannot_hide_at_other_checkout_path(self):
        # Check repository ownership, not only the canonical checkout
        # path; aliasing libfmjni under an arbitrary path must not bypass it.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/unreviewed/radio-jni" '
            'name="vendor_qcom_opensource_libfmjni" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "FM broadcast source excluded"):
            self.check()

    def test_archived_qcom_interfaces_cannot_enter_active_source(self):
        # The historical mixed HIDL repository also contains FM@1.0.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/qcom/opensource/interfaces" '
            'name="vendor_qcom_opensource_interfaces" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "archived Qualcomm interfaces source excluded"):
            self.check()

    def test_archived_qcom_interfaces_alias_cannot_enter_active_source(self):
        # Catch historical repository aliases even at nonstandard paths.
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/external/qti-interfaces" '
            'name="android_vendor_qcom_opensource_interfaces" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "archived Qualcomm interfaces source excluded"):
            self.check()

    def test_mondrian_fm_jni_canonical_path_cannot_enter_source(self):
        self.rewrite(
            "aosp17_pe_p2_kernel_configs.xml",
            '  <remove-project name="kernel/configs" />',
            '  <project path="vendor/qcom/opensource/libfmjni" '
            'name="vendor_qcom_opensource_libfmjni" />\n'
            '  <remove-project name="kernel/configs" />',
        )
        with self.assertRaisesRegex(ValueError, "FM broadcast source excluded"):
            self.check()

    def test_qualcomm_health_aidl_v5_pin_cannot_drift(self):
        self.rewrite(
            "aosp17_pe_p2_qcom_health_aidl_candidate.xml",
            "cfb2ea5aafeaf2ac177453c95ffd628cfa023742",
            "0000000000000000000000000000000000000000",
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed Qualcomm Health AIDL V5 candidate"):
            self.check()

    def test_qualcomm_health_aidl_v5_cannot_replace_platform_health(self):
        self.rewrite(
            "aosp17_pe_p2_qcom_health_aidl_candidate.xml",
            '  <project path="vendor/qcom/opensource/healthd-ext"',
            '  <remove-project name="hardware_interfaces" />\n'
            '  <project path="vendor/qcom/opensource/healthd-ext"',
        )
        with self.assertRaisesRegex(
                ValueError, "unreviewed Qualcomm Health AIDL V5 candidate"):
            self.check()

    def test_qualcomm_health_aidl_v5_cannot_become_default(self):
        self.rewrite(
            "default.xml",
            'name="aosp17_pe_p2_kernel_configs.xml"',
            'name="aosp17_pe_p2_qcom_health_aidl_candidate.xml"',
        )
        with self.assertRaisesRegex(ValueError, "default.xml must include"):
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
