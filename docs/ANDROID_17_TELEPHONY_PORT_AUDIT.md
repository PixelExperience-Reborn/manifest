# P1 — frameworks/opt/telephony, Android 17 migration audit

**Date:** 2026-11-04. **Device:** POCO F5 Pro / Redmi K60 (`mondrian`). **State:** official AOSP17 source imported and exact tree verified, with **zero historical PixelExperience code changes**. Manifest source CI staged; Android telephony build and device tests have not run.

## Provenance

- [Official Google AOSP17 tag `android-17.0.0_r1`](https://android.googlesource.com/platform/frameworks/opt/telephony/+/refs/tags/android-17.0.0_r1), annotated tag `2ea016d57c101ca263570d75953a9634faaecd39`, peeled commit `aef289516bea6118d88cd45c63742cd4abe2c596`, exact tree `84cdeedb201966bab5b28548a92b5e5e814c34bf`.
- [Import Actions #41740813124](https://github.com/PixelExperience-Reborn/frameworks_opt_telephony/actions/runs/41740813124) **PASS**; independently checked [root snapshot `548270c2e6ab41b036c670339fa0d4b04ca1ed59`](https://github.com/PixelExperience-Reborn/frameworks_opt_telephony/commit/548270c2e6ab41b036c670339fa0d4b04ca1ed59) has the exact Google source tree and no original Git ancestry.
- The old PE Android14 branch `seventeen` is intact. The new opt-in [`aosp17_pe_p1_telephony.xml`](../aosp17_pe_p1_telephony.xml) extends P1 vold and substitutes **only** `frameworks/opt/telephony`. Default manifest unchanged.
- Do **not** confuse this component with `packages/services/Telephony` or `packages/modules/Telephony`, which are separate AOSP17 projects and remain individually scheduled by the 135-repository matrix.

## Selected old PixelExperience changes compared with exact official AOSP17

| Historical PE change | Observed AOSP17 state and port decision |
| --- | --- |
| [`6461a1e3` AIDL/HIDL CDMA IMS SMS selection](https://github.com/PixelExperience-Reborn/frameworks_opt_telephony/commit/6461a1e359d7ba10dd7b01256984bf7bcecae23a) | Old PE sets `ImsSmsMessage.tech=THREE_GPP2` for CDMA and `THREE_GPP` for GSM. The official AOSP17 `RadioMessagingProxy.sendImsSms` still initializes `tech` with `THREE_GPP` and processes CDMA separately. **Not automatically ported:** needs a current Android17 radio messaging test and a demonstrated device/carrier requirement. No CDMA network test has been performed on mondrian. |
| [`3ae43d10` allow nonblocking IMS incoming-call callback](https://github.com/PixelExperience-Reborn/frameworks_opt_telephony/commit/3ae43d10f94e5a69a7c113a02c759f88e65a44db) | Official AOSP17 `ImsPhoneCallTracker.onIncomingCall` still blocks via `executeAndWaitForReturn`; old PE adds `ro.telephony.block_binder_thread_on_incoming_calls` conditional. **Defer:** changing callback semantics could break modern IMS. Requires reproducible call-setup failure and old Qualcomm IMS blob compatibility testing before a minimal patch. |
| [`5d055843` legacy SubscriptionController shim](https://github.com/PixelExperience-Reborn/frameworks_opt_telephony/commit/5d05584393acbf1e40b0e272b1550c1b75525850) | AOSP17 uses `subscription/SubscriptionManagerService` and lacks the old `SubscriptionController.java` stub. **Reject default port.** First establish whether the actual mondrian vendor IMS binary depends on the obsolete Java API; avoid artificial compatibility layers without such proof. |
| Other old fixes for legacy RIL/SIM configurations | Old PE Android14 has modifications for HIDL RadioConfig 1.0, ancient modem versions, SIM-state and call/voice behavior. | Individually compare when current source and a real mondrian log justify a change. This is **not** a full historical range-diff. |

## Integration checks and remaining requirements

1. [P1 manifest profile](../aosp17_pe_p1_telephony.xml), [targeted telephony Linux source sync](../.github/workflows/aosp17-p1-telephony-source-sync.yml), [21-project combined sync](../.github/workflows/aosp17-p0-source-sync.yml) must succeed with immutable commit SHA and Git tree. Source invariants guard that no old PE IMS workaround silently entered.
2. Build `frameworks/opt/telephony` with the complete AOSP17 Soong graph; run telephony/IMS/RIL tests. Static source checks do **not** validate working telephony.
3. Inspect vendor RIL, IMS services, manifest, carrier configs, APN and current logs. Test Kyivstar LTE voice/IMS registration, inbound/outbound calls, data on LTE and NR where supported, VoLTE icon separately (SystemUI), SMS (GSM/IMS), SIM switching, emergency call behavior, airplane mode, roaming and no-calls hang.
4. Never claim LTE+ carrier aggregation from the status-bar icon alone; use actual modem/Telephony framework CA evidence. Do not change modern AOSP17 radio policies based on old Android14 device quirks.
5. Only after positive regression evidence, create a separate reviewed A17 PE patch branch and draft PR. Keep the old `seventeen` history unchanged.

**Unverified:** complete 1069-project source checkout, Soong/Telephony compilation, CTS/VTS, modem/IMS compatibility, mondrian boot and real radio behavior. Draft manifest is not a production ROM.

## Confirmed source CI (2026-11-04)

- [Structure of 20 profiles #41741271918](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41741271918) **PASS**.
- [Targeted Linux telephony source sync #41741272123](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41741272123) **PASS**, including exact snapshot commit/tree and the unchanged current IMS source invariants.
- [Joint 21-project source sync #41741272056](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41741272056) **PASS**; [replay #41741264763](https://github.com/PixelExperience-Reborn/manifest/actions/runs/41741264763) also **PASS**. These runs are **not** telephony module compilation, CTS or a modem/IMS device test.
