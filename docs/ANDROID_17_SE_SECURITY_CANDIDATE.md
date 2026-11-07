# Android17 Secure Element — isolated AOSP security-r3 logical-channel candidate

**Recorded:** 2026-11-07. **Status:** source-only research candidate; **NOT** active in `default.xml`, release build, device VINTF or product. Independent PixelExperience-Reborn AOSP17 / future `mondrian` (SM8475).

## Confirmed upstream vulnerability-hardening change

The official `platform/hardware/nxp/secure_element` repository is already in the reviewed manifest, so no old `vendor/nxp/secure_element` checkout or fresh NXP vendor fork is necessary.

- **Current reviewed AOSP17 r1 source:** commit `ebc3542b480e505ed67ec52ea0c3135e5902ff5e`, tree `32593f6a857cc48d52ec6f5c8e7799be2434d6b1`, tag `android-17.0.0_r1`.
- **Official security-r3 candidate:** commit `8aec22fde8121bf3f74006730ce42e9ac0366b62`, tree `60db7cd2fb71673b3d8468162eaaed6649e3c42c`, tag `android-security-17.0.0_r3` stamped 2026-11-02; underlying source commit from 2026-07-13. The later tag date is **not proof** that all November 2026 security fixes are included.
- **Git source diff:** 10 changed files, no added/removed files: `pn8x/1.0/SecureElement.cpp`, `pn8x/1.1/SecureElement.cpp`, `snxxx/1.0/{SecureElement,VirtualISO}.cpp`, `snxxx/1.1/{SecureElement,VirtualISO}.cpp`, `snxxx/1.2/{SecureElement,VirtualISO}.cpp`, `snxxx/aidl/{SecureElement,VirtualISO}.cpp`.
- **Confirmed AIDL fix:** both `snxxx/aidl/SecureElement.cpp` and `VirtualISO.cpp` now check `rspApdu.p_data[0] < mMaxChannelCount && rspApdu.p_data[0] > 0` before recording returned `openLogicalChannel` number in `mOpenedChannels`. Invalid channel numbers return `-1` with `ISecureElement::CHANNEL_NOT_AVAILABLE` rather than using an out-of-range channel number as an array index. This guards a specific channel-index operation. It does not prove all APDU response buffers are length validated or that a particular CVE is fixed.
- **Current vendor comparison:** `NXPNFCProject/nfcandroid_se_hidlimpl` branch `br_ar_17_aosp_mainline` commit `582d149bebb97e01ec071bbcfa9a05e356958f50` (NXP 17.07.00) lacks this guard in the two SE AIDL files. **Do not replace an official updated HAL with the older/unguarded vendor implementation.**

Audited patches and shell diff: [source CI #42322285010](https://github.com/PixelExperience-Reborn/vendor_nxp_secure_element/actions/runs/42322285010); [complete row174 SE audit](https://github.com/PixelExperience-Reborn/vendor_nxp_secure_element/blob/audit/a17-nxp-secure-element-aidl-20261107/docs/ANDROID_17_NXP_SE_AIDL_BOUNDARY_AUDIT.md). Official source: https://android.googlesource.com/platform/hardware/nxp/secure_element/+/refs/tags/android-security-17.0.0_r3

## Immutable candidate, preserved source graph

`aosp17_pe_p2_se_security_candidate.xml` includes the original reviewed P2 `aosp17_pe_p2_kernel_configs.xml` and removes/redeclares **only** `platform/hardware/nxp/secure_element` at checkout path `hardware/nxp/secure_element`, with unchanged `aosp` remote and `pdk` groups and the exact security-r3 commit. It makes **no changes** to official `platform/system/secure_element` (OMAPI), `platform/hardware/nxp/nfc` (NFC HAL), `platform/packages/modules/Nfc` (NFC Mainline/APEX) or `default.xml`. This is **not** a 26th active stage; 25 already reviewed profiles remain.

Strict Python source-graph validation rejects altered candidate SHA/shape, unexpected checkout changes, switching `default.xml` to this candidate or replacing system OMAPI. All old NXP P73/HIDL source names and paths remain forbidden.

## Required acceptance for an actual ROM

1. Confirm the official AOSP17 r3 security commit in full source, inspect each of the ten HIDL/AIDL code changes for boundary and response-length correctness, run static sanitizers and SE HAL VTS/unit tests.
2. Verify the selected SE AIDL **V1** service and NFC AIDL **V2**/vendor AIDL **V1** coupling, Soong/NDK, system OMAPI/ARA permissions, runtime Binder/SELinux, access to privileged APDU operations and matching VINTF/FCM.
3. Confirm actual mondrian NFCC and secure-element presence, Xiaomi firmware and device nodes, eSE/UICC routing, recovery and card/payment eligibility. Do not flash SE/JCOP, copy old `/dev/p73` configuration or enable update agent.
4. Perform a coordinated Android17 security rebase across the entire platform and Mainline NFC/SE stack; do **not** change `ro.build.version.security_patch` based on this isolated repository tag.
5. Validate real CTS/VTS, NFC/HCE/OMAPI, cold boot/suspend, OTA/recovery and hardware behavior on the independent PE-Reborn device tree.

**Decision:** preserve the verified AOSP17 r1 `default.xml` until compatible complete build/device security verification. The r3 SE candidate is a precise, security-motivated source option, not a release claim.
