# Глобальный аудит базы PixelExperience-Reborn для Android 17 / mondrian

**Дата:** 25 ноября 2026. **Охват:** все 143 репозитория организации, оригинальная организация PixelExperience, AOSP `android-17.0.0_r1` и теги `android-security-17.0.0_r*`.
**Цель:** стабильная база PE на Android 17 только для mondrian (POCO F5 Pro / Redmi K60, SM8475), собранная из исходников, с минимумом закрытых файлов OS3.0.8.0.

Метод: `git ls-remote` всех веток наших репозиториев и их оригиналов в `github.com/PixelExperience`; сравнение деревьев рабочих веток с `seventeen` (частичные клоны без блобов); развёртка сборочного профиля `aosp17_pe_mondrian_build.xml`; сверка тегов AOSP по всем 1047 проектам профиля. Скрипты лежат в сессии и воспроизводимы; выводы ниже проверены на данных, а не по названиям веток.

## 1. Основные ветки (`seventeen`)

- Во всех 143 репозиториях ветка по умолчанию — `seventeen`.
- **135 форков PixelExperience: `seventeen` побайтно совпадает с оригинальной веткой `fourteen` PixelExperience** (тот же коммит). Это Android 14 (PE14, AOSP `android-14.0.0_r22`), а не Android 17. Ветка просто переименована.
- 8 собственных репозиториев (device ×2, kernel ×3, proprietary ×2, `android_hardware_xiaomi`) оригинала не имеют; у PixelExperience-Devices mondrian никогда не было.
- **`manifest/seventeen` = манифест PE14** (`136aee6`, 06.03.2024): AOSP `android-14.0.0_r22`, ремоут `pixel` указывает на **оригинальную** организацию `github.com/PixelExperience`, а `pixel-gitlab` и `pixel-devices-blobs` — на `gitlab.pixelexperience.org`, который **не отвечает (502)**. Из него брались `vendor/gms` и `external/faceunlock`. Итог: `repo init -b seventeen` даёт дерево Android 14 из чужой организации, а синхронизация падает на GitLab.
- Вся работа под A17 лежит в боковых ветках (`port/`, `integrate/`, `audit/`, `bringup/` …) и в открытой цепочке PR манифеста #1 → #2 → #3.

## 2. Что реально есть в A17-ветках

Разобрано 132 рабочие A17-ветки (тяжёлые P0-форки `frameworks/*`, `art`, `bionic`, `system/*`, `packages/modules/*` сверены отдельно, см. п. 3):

- **88 веток — только документы, тесты или один скрипт-«проверялка»** (`tools/verify_a17_*_legacy.py`, `audit/check_*.py`). Кода A17 в них нет; содержимое `seventeen` (A14) они не меняют.
- **44 ветки с кодом**: 26 — наши device/kernel/proprietary, 18 — форки PE: `hardware_qcom-caf_common`, `hardware_qcom-caf_thermal`, `hardware_qcom_wlan`, `hardware_ril`, `external_tinycompress`, `kernel_configs`, `vendor_aosp`, `vendor_codeaurora_telephony`, `tools_extract-utils`, `packages_resources_devicesettings` (fix), `vendor_qcom_opensource_{healthd-ext, interfaces, power, thermal-engine, usb, vibrator, wfd-commonsys, libfmjni}`.

## 3. Что реально собирается

Профиль `aosp17_pe_mondrian_build.xml` разворачивается в **1077 проектов = 1047 AOSP `android-17.0.0_r1` + 30 наших** (25 форков PE на A17-ветках + 5 mondrian). **Ни один проект не берётся из `seventeen`** — профиль чистый. Остальные ~105 форков в сборку не входят.

**«PE» в A17 почти пуст.** В A14 у PixelExperience были сотни собственных коммитов (с 08.2023: `frameworks_base` ≈227, `packages_apps_Settings` ≈80, `system_core` ≈36, `build_soong` ≈34, `frameworks_native` ≈20). В A17 перенесено около двух десятков мелких правок: `frameworks_base` — только скруглённый toast; `frameworks_av`, `packages_modules_Bluetooth`, `hardware_interfaces` — по одной защитной правке; `bootable_recovery` — заголовок с кодовым именем и разбор стадии; `build_soong` — баннер и очистка OTA. Сейчас база — это чистый AOSP 17 + продуктовый слой `vendor_aosp`.

Для mondrian из PE14 важны в первую очередь не функции интерфейса, а сборочные правки `build_soong` (`generated_kernel_headers`, `PRODUCT_SOONG_NAMESPACES` в dumpvars, `PathForSourceRelaxed`), без которых не собираются Qualcomm-HAL из `hardware/qcom-caf`. **Не переносится:** подмена свойств устройства для обхода проверки целостности Google (PixelPropsUtils, «SafetyNet spoofing» в `system/core/init`) — это обход защитного механизма, в базу не включаем.

## 4. Патч безопасности

- `android-17.0.0_r1` — релиз **`cp2a`**, `RELEASE_PLATFORM_SECURITY_PATCH = 2026-06-05`. Других релизных тегов AOSP 17 пока нет.
- Google публикует ежемесячные исправления тегами **`android-security-17.0.0_r1/r2/r3`** (13.07, 05.08 и 03.09.2026 — июль, август, сентябрь). **Исправлений за октябрь и ноябрь в AOSP ещё нет**, поэтому самый свежий доступный уровень — сентябрь 2026.
- Теги безопасности ответвлены раньше `r1` (общий предок — 16.04.2026), поэтому их **нельзя просто подставить** вместо `r1`: потеряются коммиты релиза. Как у LineageOS и раньше у PE, их нужно **сливать** (merge).
- r3 отличается от r1 в 100 проектах AOSP; реальные исправления — **285 в 58 проектах**: 34 проекта — fast-forward (ревизию можно заменить на тег), 12 — merge в наши A17-форки, 12 — нужен форк + merge (`build/make`, `packages/apps/Settings`, `packages/modules/Nfc`, Telecomm, Telephony, TelephonyProvider, `external/wpa_supplicant_8`, Uwb, `system/fs/fs_mgr`…).
- Уровень патча поднимается через свою карту релиз-конфигурации в `vendor/aosp` (флаг `RELEASE_PLATFORM_SECURITY_PATCH = 2026-09-01`), а не правкой `build/release` AOSP.
- **Сборка должна идти с `cp2a`, а не с `trunk_staging`:** `trunk_staging` включает экспериментальные флаги и не является стабильным релизом этого тега.

| Проект | Исправлений r1→r3 | Коммитов только в r1 | Способ |
|---|---|---|---|
| `frameworks/base` | 97 | 42 | merge в наш форк |
| `packages/modules/Nfc` | 17 | 3 | нужен форк + merge |
| `build/make` | 16 | 68 | нужен форк + merge |
| `frameworks/av` | 13 | 5 | merge в наш форк |
| `packages/modules/Bluetooth` | 13 | 6 | merge в наш форк |
| `packages/apps/Settings` | 10 | 7 | нужен форк + merge |
| `packages/providers/MediaProvider` | 9 | 0 | ревизия = тег (fast-forward) |
| `packages/modules/Wifi` | 7 | 0 | merge в наш форк |
| `packages/providers/TelephonyProvider` | 6 | 1 | нужен форк + merge |
| `frameworks/opt/telephony` | 6 | 4 | merge в наш форк |
| `external/libpng` | 5 | 0 | ревизия = тег (fast-forward) |
| `external/wpa_supplicant_8` | 5 | 1 | нужен форк + merge |
| `hardware/nxp/nfc` | 4 | 0 | ревизия = тег (fast-forward) |
| `packages/providers/DownloadProvider` | 4 | 0 | ревизия = тег (fast-forward) |
| `packages/services/Telecomm` | 4 | 1 | нужен форк + merge |
| `frameworks/native` | 4 | 4 | merge в наш форк |
| `external/freetype` | 3 | 0 | ревизия = тег (fast-forward) |
| `packages/apps/TV` | 3 | 0 | ревизия = тег (fast-forward) |
| `packages/services/Mms` | 3 | 0 | ревизия = тег (fast-forward) |
| `packages/services/Telephony` | 3 | 2 | нужен форк + merge |
| `hardware/interfaces` | 3 | 2 | merge в наш форк |
| `development` | 2 | 1 | нужен форк + merge |
| `external/exfatprogs` | 2 | 0 | ревизия = тег (fast-forward) |
| `external/libopenapv` | 2 | 1 | нужен форк + merge |
| `hardware/st/nfc` | 2 | 0 | ревизия = тег (fast-forward) |
| `packages/apps/Car/Settings` | 2 | 0 | ревизия = тег (fast-forward) |
| `packages/apps/ContactsPicker` | 2 | 0 | ревизия = тег (fast-forward) |
| `packages/modules/Telephony` | 2 | 0 | ревизия = тег (fast-forward) |
| `packages/modules/Uwb` | 2 | 4 | нужен форк + merge |
| `packages/providers/ContactsProvider` | 2 | 0 | ревизия = тег (fast-forward) |
| `packages/services/BuiltInPrintService` | 2 | 0 | ревизия = тег (fast-forward) |
| `system/fs/fs_mgr` | 2 | 1 | нужен форк + merge |
| `packages/modules/adb` | 2 | 0 | merge в наш форк |
| `system/core` | 2 | 1 | merge в наш форк |
| `external/aac` | 1 | 0 | ревизия = тег (fast-forward) |
| `external/avb` | 1 | 0 | ревизия = тег (fast-forward) |
| `external/hplip` | 1 | 0 | ревизия = тег (fast-forward) |
| `external/libcupsfilters` | 1 | 0 | ревизия = тег (fast-forward) |
| `external/libhevc` | 1 | 0 | ревизия = тег (fast-forward) |
| `external/libjxl` | 1 | 0 | ревизия = тег (fast-forward) |
| `external/libppd` | 1 | 0 | ревизия = тег (fast-forward) |
| `external/rust/beto-rust` | 1 | 1 | нужен форк + merge |
| `external/tremolo` | 1 | 0 | ревизия = тег (fast-forward) |
| `hardware/nxp/secure_element` | 1 | 0 | ревизия = тег (fast-forward) |
| `packages/apps/Contacts` | 1 | 0 | ревизия = тег (fast-forward) |
| `packages/apps/ManagedProvisioning` | 1 | 0 | ревизия = тег (fast-forward) |
| `packages/apps/TvSettings` | 1 | 0 | ревизия = тег (fast-forward) |
| `packages/modules/IntentResolver` | 1 | 0 | ревизия = тег (fast-forward) |
| `packages/modules/NeuralNetworks` | 1 | 0 | ревизия = тег (fast-forward) |
| `packages/modules/Profiling` | 1 | 0 | ревизия = тег (fast-forward) |
| `packages/services/Iwlan` | 1 | 0 | ревизия = тег (fast-forward) |
| `system/gsid` | 1 | 0 | ревизия = тег (fast-forward) |
| `system/libfmq` | 1 | 0 | ревизия = тег (fast-forward) |
| `system/libufdt` | 1 | 0 | ревизия = тег (fast-forward) |
| `trusty/user/base` | 1 | 0 | ревизия = тег (fast-forward) |
| `art` | 1 | 2 | merge в наш форк |
| `bionic` | 1 | 0 | merge в наш форк |
| `packages/modules/Connectivity` | 1 | 10 | merge в наш форк |

## 5. Google-сервисы

- Источник GMS PE14 (`vendor/gms` на GitLab PE) недоступен. В 135 форках GMS нет.
- В A17-ветке `vendor_aosp` GMS сделан опциональным: без `WITH_GMS=true` собирается AOSP-вариант с Launcher3QuickStep; с `WITH_GMS=true` требуется `vendor/gms/products/gms.mk`, иначе сборка останавливается с понятной ошибкой. Свойства Google, Gboard, SetupWizard условны.
- **Действующий источник для A17:** MindTheGapps, ветка **`cinnamonbun`** (Android 17, обновлена 30.06.2026; структура `vendor/gapps/arm64/arm64-vendor.mk`, GmsCore, Phonesky, SetupWizard, Velvet и т. д.). Подключается только опционально (`WITH_GMS=true`) через локальный манифест; APK Google в наши публичные репозитории не копируются.
- Решение, выпускать ли сборки с GMS и из какого источника, остаётся за владельцем проекта.

## 6. Сборочные несоответствия для mondrian

1. **Компилятор ядра.** Ядро в CI собрано clang `r614150` (23.0.1), которого нет в AOSP 17 r1 (`clang-r584948`, `r584948b`, `r596125`). Внутренний `kernel.mk` `vendor_aosp` по умолчанию берёт `clang-r487747c` (нет в A17) и `prebuilts/tools-custom` (нет в профиле). Нужно либо явно задать `TARGET_KERNEL_CLANG_VERSION` из AOSP 17 и проверить ядро им, либо подавать в сборку ядро, собранное нашим CI.
2. **Имя продукта.** Инструменты PE (`breakfast`, `CUSTOM_BUILD`, `org.pixelexperience.device`) рассчитаны на `aosp_<device>`; наш продукт назывался `pe_mondrian`. **Исправлено:** продукт `aosp_mondrian` (device `9bcdd23`), бутанимация 1440p под панель 1440×3200, варианты lunch `aosp_mondrian-cp2a-*`.
3. **Qualcomm-слой.** 26 нужных mondrian форков (`hardware/qcom-caf/sm8450/*`, `qcom-caf/common`, bootctrl, `vendor/qcom/opensource/*`, sepolicy_vndr) имеют в `seventeen` код A14 (Lineage-21 CAF / `LA.VENDOR.1.0.r1-…-WAIPIO`); A17-работа есть только в `common`, `thermal` и нескольких `vendor/qcom/opensource/*`. В сборку они пока не входят. Вендор OS3 — Android 12 (API 31, VINTF target-level 6), поэтому HAL из исходников должны оставаться совместимыми с интерфейсами блобов OS3.
4. **NFC.** У mondrian NXP SN100/SN220; в AOSP 17 есть `hardware/nxp/nfc` (AIDL) и `hardware/nxp/secure_element`, поэтому старые NXP-форки (HIDL, PN5xx, NfcNci) не нужны.
5. **GitHub Actions в `manifest`.** С 4 ноября ни один push в этом форке не создаёт запуск (у коммита нет check-suite Actions), хотя в device-репозиториях push и ручной запуск работают. Нужно включить Actions в самом репозитории `manifest` (вкладка Actions → «I understand my workflows…» либо Settings → Actions → General → Allow all actions).

## 7. План (порядок работ)

1. Включить Actions в `manifest` и прогнать реальную стадию `graph` на ServerHive с релизом `cp2a`.
2. ~~Привести продукт к `aosp_mondrian`~~ (сделано); задать компилятор ядра из AOSP 17.
3. Патч безопасности: 34 проекта — ревизия на `android-security-17.0.0_r3`; 24 — merge (наши форки и новые форки); флаг уровня патча `2026-09-01` в `vendor/aosp`. Каждый следующий месяц — тот же процесс со следующим тегом.
4. Qualcomm-слой mondrian: по одному форку переносить на A17 (неверные правила Soong, `-ndk_platform` → `-ndk`, AIDL), добавлять в профиль и проверять сборкой `m vendorimage`.
5. Перенос в основные ветки: когда сборка проходит, `seventeen` каждого используемого форка получает A17-содержимое **merge-коммитом без force-push** (история A14 остаётся в `fourteen`); `manifest/seventeen` получает A17-манифест. Ненужные mondrian форки остаются как есть и не входят в манифест.
6. Функции PE (Settings, TouchGestures, devicesettings, custom-preference, pixel-framework) — переносить на A17 после первой загрузки устройства.

## 8. Решение по каждому из 135 форков

| Репозиторий | Путь | Сниппет PE14 | Путь AOSP17 | seventeen = оригинал PE fourteen | A17-веток | Ветки с переносом кода | Решение для mondrian |
|---|---|---|---|---|---|---|---|
| `art` | `art` | pixel | да | да | 0 | — | в сборке: port/a17-art-aosp17-base-20261103 |
| `bionic` | `bionic` | pixel | да | да | 0 | — | в сборке: port/a17-bionic-aosp17-base-20261103 |
| `bootable_recovery` | `bootable/recovery` | pixel | да | да | 0 | — | в сборке: port/a17-recovery-pe-20261103 |
| `build` | `build/make` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `build_soong` | `build/soong` | pixel | да | да | 0 | — | в сборке: port/a17-soong-dumpvars-20261103 |
| `development` | `development` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `device_custom_sepolicy` | `device/custom/sepolicy` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `device_qcom_sepolicy` | `device/qcom/sepolicy` | pixel-caf | нет | да | 1 | — | проверить: нужен только для QTI system_ext-сервисов, которых в сборке нет |
| `device_qcom_sepolicy_vndr_sm8450` | `device/qcom/sepolicy_vndr/sm8450` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `external_ant-wireless_ant_client` | `external/ant-wireless/ant_client` | pixel-caf | нет | да | 1 | — | не нужен: ANT+ в mondrian нет |
| `external_ant-wireless_ant_native` | `external/ant-wireless/ant_native` | pixel-caf | нет | да | 1 | — | не нужен: ANT+ в mondrian нет |
| `external_ant-wireless_ant_service` | `external/ant-wireless/ant_service` | pixel-caf | нет | да | 1 | — | не нужен: ANT+ в mondrian нет |
| `external_ant-wireless_hidl` | `external/ant-wireless/hidl` | pixel-caf | нет | да | 1 | — | не нужен: ANT+ в mondrian нет |
| `external_avb` | `external/avb` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_bson` | `external/bson` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `external_connectivity` | `external/connectivity` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `external_cronet` | `external/cronet` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_dtc` | `external/dtc` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_e2fsprogs` | `external/e2fsprogs` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_gptfdisk` | `external/gptfdisk` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_icu` | `external/icu` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_json-c` | `external/json-c` | pixel-extras | нет | да | 0 | — | функция PE: перенос на A17 (A17-работы нет) |
| `external_libcxx` | `external/libcxx` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_libnl` | `external/libnl` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_mksh` | `external/mksh` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `external_ntfs-3g` | `external/ntfs-3g` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `external_tinycompress` | `external/tinycompress` | pixel | да | да | 1 | integrate/a17-tinycompress-20261105 | в сборке: integrate/a17-tinycompress-20261105 |
| `external_tinyxml` | `external/tinyxml` | pixel-extras | нет | да | 0 | — | функция PE: перенос на A17 (A17-работы нет) |
| `external_wpa_supplicant_8` | `external/wpa_supplicant_8` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `frameworks_av` | `frameworks/av` | pixel | да | да | 0 | — | в сборке: port/a17-frameworks-av-pe-20261103 |
| `frameworks_base` | `frameworks/base` | pixel | да | да | 0 | — | в сборке: port/a17-frameworks-base-pe-20261103 |
| `frameworks_native` | `frameworks/native` | pixel | да | да | 0 | — | в сборке: port/a17-frameworks-native-aosp17-base-20261103 |
| `frameworks_opt_telephony` | `frameworks/opt/telephony` | pixel | да | да | 0 | — | в сборке: port/a17-telephony-aosp17-base-20261104 |
| `frameworks_opt_timezonepicker` | `frameworks/opt/timezonepicker` | pixel | да | да | 0 | — | в сборке: port/a17-timezonepicker-aosp17-base-20261104 |
| `hardware_broadcom_libbt` | `hardware/broadcom/libbt` | pixel | да | да | 0 | — | не нужен: Bluetooth mondrian — Qualcomm, не Broadcom |
| `hardware_custom_compat` | `hardware/custom/compat` | pixel-extras | нет | да | 0 | — | функция PE: перенос на A17 (A17-работы нет) |
| `hardware_custom_interfaces` | `hardware/custom/interfaces` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `hardware_google_pixel` | `hardware/google/pixel` | pixel | нет | да | 0 | — | не нужен: HAL Pixel (Tensor/PowerStats) не для Qualcomm-устройства |
| `hardware_interfaces` | `hardware/interfaces` | pixel | да | да | 0 | — | в сборке: port/a17-hardware-interfaces-pe-20261103 |
| `hardware_libhardware` | `hardware/libhardware` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `hardware_qcom-caf_bootctrl` | `hardware/qcom-caf/bootctrl` | pixel-caf | нет | да | 0 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom-caf_common` | `hardware/qcom-caf/common` | pixel-caf | нет | да | 1 | integrate/a17-sm8450-qcom-common-20261105 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть integrate/a17-sm8450-qcom-common-20261105) |
| `hardware_qcom-caf_sm8450_audio_agm` | `hardware/qcom-caf/sm8450/audio/agm` | pixel-caf | нет | да | 0 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom-caf_sm8450_audio_pal` | `hardware/qcom-caf/sm8450/audio/pal` | pixel-caf | нет | да | 0 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom-caf_sm8450_audio_primary-hal` | `hardware/qcom-caf/sm8450/audio/primary-hal` | pixel-caf | нет | да | 0 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom-caf_sm8450_data-ipa-cfg-mgr` | `hardware/qcom-caf/sm8450/data-ipa-cfg-mgr` | pixel-caf | нет | да | 0 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom-caf_sm8450_display` | `hardware/qcom-caf/sm8450/display` | pixel-caf | нет | да | 0 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom-caf_sm8450_media` | `hardware/qcom-caf/sm8450/media` | pixel-caf | нет | да | 0 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom-caf_thermal` | `hardware/qcom-caf/thermal` | pixel-caf | нет | да | 1 | integrate/a17-qcom-thermal-aidl-20261105 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть integrate/a17-qcom-thermal-aidl-20261105) |
| `hardware_qcom-caf_vr` | `hardware/qcom-caf/vr` | pixel-caf | нет | да | 1 | — | не нужен: VR HAL не нужен |
| `hardware_qcom-caf_wlan` | `hardware/qcom-caf/wlan` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `hardware_qcom_audio` | `hardware/qcom/audio` | pixel | нет | да | 1 | — | не нужен: старый HAL msm8xxx; для taro — hardware/qcom-caf/sm8450/audio |
| `hardware_qcom_camera` | `hardware/qcom/camera` | pixel | нет | да | 1 | — | не нужен: старый HAL msm8xxx; камера mondrian — HAL Xiaomi/Qualcomm (блобы) |
| `hardware_qcom_data_ipacfg-mgr` | `hardware/qcom/data/ipacfg-mgr` | pixel | нет | да | 1 | — | не нужен: старый ipacfg; для taro — hardware/qcom-caf/sm8450/data-ipa-cfg-mgr |
| `hardware_qcom_display` | `hardware/qcom/display` | pixel | нет | да | 1 | — | не нужен: старый HAL msm8xxx; для taro — hardware/qcom-caf/sm8450/display |
| `hardware_qcom_gps` | `hardware/qcom/gps` | pixel | нет | да | 1 | — | не нужен: старый loc HAL; GNSS taro — блобы Qualcomm AIDL |
| `hardware_qcom_media` | `hardware/qcom/media` | pixel | нет | да | 1 | — | не нужен: старый HAL msm8xxx; для taro — hardware/qcom-caf/sm8450/media |
| `hardware_qcom_wlan` | `hardware/qcom/wlan` | pixel | да | да | 1 | integrate/a17-aosp17-qcom-wlan-20261105 | в сборке: integrate/a17-aosp17-qcom-wlan-20261105 |
| `hardware_ril` | `hardware/ril` | pixel | да | да | 1 | integrate/a17-aosp17-ril-20261105 | в сборке: integrate/a17-aosp17-ril-20261105 |
| `kernel_configs` | `kernel/configs` | pixel | да | да | 1 | audit/a17-kernel-configs-source-20261105 | в сборке: audit/a17-kernel-configs-source-20261105 |
| `manifest` | `manifest` | pixel | нет | да | 0 | — | основная ветка = манифест PE14; A17 — в port/bringup ветках (см. отчёт) |
| `packages_apps_Aperture` | `packages/apps/Aperture` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `packages_apps_Camera2` | `packages/apps/Camera2` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `packages_apps_FaceUnlockService` | `packages/apps/FaceUnlockService` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `packages_apps_Nfc` | `packages/apps/Nfc` | pixel | нет | да | 1 | — | не нужен: в A17 NFC — модуль packages/modules/Nfc из AOSP |
| `packages_apps_Settings` | `packages/apps/Settings` | pixel | да | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `packages_apps_TouchGestures` | `packages/apps/TouchGestures` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `packages_modules_Bluetooth` | `packages/modules/Bluetooth` | pixel | да | да | 0 | — | в сборке: port/a17-bluetooth-pe-20261103 |
| `packages_modules_Connectivity` | `packages/modules/Connectivity` | pixel | да | да | 0 | — | в сборке: port/a17-connectivity-aosp17-base-20261103 |
| `packages_modules_Permission` | `packages/modules/Permission` | pixel | да | да | 0 | — | в сборке: port/a17-permission-aosp17-base-20261103 |
| `packages_modules_Wifi` | `packages/modules/Wifi` | pixel | да | да | 0 | — | в сборке: port/a17-wifi-aosp17-base-20261103 |
| `packages_modules_adb` | `packages/modules/adb` | pixel | да | да | 0 | — | в сборке: port/a17-adb-aosp17-base-20261103 |
| `packages_providers_DownloadProvider` | `packages/providers/DownloadProvider` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `packages_providers_MediaProvider` | `packages/providers/MediaProvider` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `packages_resources_devicesettings` | `packages/resources/devicesettings` | pixel-extras | нет | да | 2 | fix/a17-pe-devicesettings-resource-collisions-20261104 | функция PE: перенос на A17 (есть fix/a17-pe-devicesettings-resource-collisions-20261104) |
| `packages_services_Telecomm` | `packages/services/Telecomm` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `packages_services_Telephony` | `packages/services/Telephony` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `platform_testing` | `platform_testing` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `prebuilts_build-tools` | `prebuilts/build-tools` | pixel | да | да | 0 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `prebuilts_clang_kernel_linux-x86_clang-r416183b` | `prebuilts/clang/kernel/linux-x86/clang-r416183b` | pixel-extras | нет | да | 1 | — | не нужен: clang r416183b (Android 12) не используется; ядро — clang из AOSP17 |
| `prebuilts_extract-tools` | `prebuilts/extract-tools` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `prebuilts_gcc_linux-x86_aarch64_aarch64-linux-android-4.9` | `prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9` | pixel-extras | нет | да | 1 | — | не нужен: GCC 4.9 не нужен: ядро 5.10 собирается только clang |
| `prebuilts_gcc_linux-x86_arm_arm-linux-androideabi-4.9` | `prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9` | pixel-extras | нет | да | 1 | — | не нужен: GCC 4.9 не нужен: ядро 5.10 собирается только clang |
| `prebuilts_gcc_linux-x86_x86_x86_64-linux-android-4.9` | `prebuilts/gcc/linux-x86/x86/x86_64-linux-android-4.9` | pixel-extras | нет | да | 1 | — | не нужен: GCC 4.9 не нужен: ядро 5.10 собирается только clang |
| `prebuilts_kernel-build-tools` | `prebuilts/kernel-build-tools` | pixel-extras | нет | да | 1 | — | нужен, если ядро собирается в дереве через vendor/aosp kernel.mk |
| `prebuilts_tools-custom` | `prebuilts/tools-custom` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `system_bpf` | `system/bpf` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_core` | `system/core` | pixel | да | да | 0 | — | в сборке: port/a17-system-core-aosp17-base-20261103 |
| `system_extras` | `system/extras` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_libhidl` | `system/libhidl` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_libhwbinder` | `system/libhwbinder` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_libziparchive` | `system/libziparchive` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_logging` | `system/logging` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_media` | `system/media` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_security` | `system/security` | pixel | да | да | 0 | — | в сборке: port/a17-system-security-aosp17-base-20261103 |
| `system_sepolicy` | `system/sepolicy` | pixel | да | да | 0 | — | в сборке: port/a17-sepolicy-aosp17-base-20261103 |
| `system_tools_dtbtool` | `system/tools/dtbtool` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `system_tools_mkbootimg` | `system/tools/mkbootimg` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `system_update_engine` | `system/update_engine` | pixel | да | да | 0 | — | в сборке: port/a17-update-engine-aosp17-base-20261103 |
| `system_vold` | `system/vold` | pixel | да | да | 0 | — | в сборке: port/a17-vold-aosp17-base-20261104 |
| `tools_extract-utils` | `tools/extract-utils` | pixel-extras | нет | да | 2 | integrate/a17-python-extract-utils-20261106 | функция PE: перенос на A17 (есть integrate/a17-python-extract-utils-20261106) |
| `tools_metalava` | `tools/metalava` | pixel | да | да | 1 | — | AOSP-путь: брать чистый AOSP17, PE-дельту переносить по необходимости |
| `vendor_aosp` | `vendor/aosp` | pixel-extras | нет | да | 1 | port/a17-vendor-envsetup-20261102 | в сборке: port/a17-vendor-envsetup-20261102 |
| `vendor_codeaurora_telephony` | `vendor/codeaurora/telephony` | pixel-caf | нет | да | 2 | integrate/a17-qti-telephony-source-20261106 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть integrate/a17-qti-telephony-source-20261106) |
| `vendor_custom-preference` | `vendor/custom-preference` | pixel-extras | нет | да | 1 | — | функция PE: перенос на A17 (A17-работы нет) |
| `vendor_nxp_nfc` | `vendor/nxp/nfc` | pixel-caf | нет | да | 1 | — | не нужен: NFC SN100/SN220 закрывается AOSP17 hardware/nxp/nfc (AIDL) |
| `vendor_nxp_opensource_commonsys_external_libnfc-nci` | `vendor/nxp/opensource/commonsys/external/libnfc-nci` | pixel-caf | нет | да | 1 | — | не нужен: стек NFC в A17 — mainline packages/modules/Nfc |
| `vendor_nxp_opensource_commonsys_frameworks` | `vendor/nxp/opensource/commonsys/frameworks` | pixel-caf | нет | да | 1 | — | не нужен: расширения NXP для старого NfcNci не нужны в A17 |
| `vendor_nxp_opensource_commonsys_packages_apps_Nfc` | `vendor/nxp/opensource/commonsys/packages/apps/Nfc` | pixel-caf | нет | да | 1 | — | не нужен: в A17 NFC — модуль packages/modules/Nfc из AOSP |
| `vendor_nxp_opensource_interfaces_nfc` | `vendor/nxp/opensource/interfaces/nfc` | pixel-caf | нет | да | 1 | — | не нужен: HIDL vendor.nxp.nfc заменяется AOSP17 hardware/nxp/nfc (AIDL) |
| `vendor_nxp_opensource_pn5xx_halimpl` | `vendor/nxp/opensource/pn5xx/halimpl` | pixel-caf | нет | да | 1 | — | не нужен: NFC mondrian — NXP SN100/SN220, не PN5xx |
| `vendor_nxp_opensource_pn5xx_hidlimpl` | `vendor/nxp/opensource/pn5xx/hidlimpl` | pixel-caf | нет | да | 1 | — | не нужен: NFC mondrian — NXP SN100/SN220, не PN5xx |
| `vendor_nxp_opensource_sn100x_halimpl` | `vendor/nxp/opensource/sn100x/halimpl` | pixel-caf | нет | да | 1 | — | не нужен: SN100/SN220 закрывается AOSP17 hardware/nxp/nfc (AIDL) |
| `vendor_nxp_opensource_sn100x_hidlimpl` | `vendor/nxp/opensource/sn100x/hidlimpl` | pixel-caf | нет | да | 1 | — | не нужен: SN100/SN220 закрывается AOSP17 hardware/nxp/nfc (AIDL) |
| `vendor_nxp_secure_element` | `vendor/nxp/secure_element` | pixel-caf | нет | да | 1 | — | не нужен: eSE — AOSP17 hardware/nxp/secure_element |
| `vendor_nxp_secure_element_extns` | `vendor/nxp/secure_element_extns` | pixel-caf | нет | да | 1 | — | не нужен: JCOP-расширения NXP не нужны; eSE — AOSP17 hardware/nxp/secure_element |
| `vendor_pixel-framework` | `vendor/pixel-framework` | pixel-extras | нет | да | 2 | — | функция PE: перенос на A17 (A17-работы нет) |
| `vendor_qcom_opensource_audio-hal_st-hal` | `vendor/qcom/opensource/audio-hal/st-hal` | pixel-caf | нет | да | 1 | — | не нужен: старый soundtrigger; для AudioReach — st-hal-ar |
| `vendor_qcom_opensource_audio-hal_st-hal-ar` | `vendor/qcom/opensource/audio-hal/st-hal-ar` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_commonsys-intf_display` | `vendor/qcom/opensource/commonsys-intf/display` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_commonsys_display` | `vendor/qcom/opensource/commonsys/display` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_core-utils` | `vendor/qcom/opensource/core-utils` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_core-utils-sys` | `vendor/qcom/opensource/core-utils-sys` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_core-utils-vendor` | `vendor/qcom/opensource/core-utils-vendor` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_dataservices` | `vendor/qcom/opensource/dataservices` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_display` | `vendor/qcom/opensource/display` | pixel-caf | нет | да | 1 | — | нужен mondrian (Qualcomm SM8450): перенести на A17 (A17-работы нет) |
| `vendor_qcom_opensource_fm-commonsys` | `vendor/qcom/opensource/fm-commonsys` | pixel-caf | нет | да | 1 | — | не нужен: FM-радио в mondrian нет |
| `vendor_qcom_opensource_healthd-ext` | `vendor/qcom/opensource/healthd-ext` | pixel-caf | нет | да | 1 | port/a17-health-aidl-v5-mondrian-20261107 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть port/a17-health-aidl-v5-mondrian-20261107) |
| `vendor_qcom_opensource_interfaces` | `vendor/qcom/opensource/interfaces` | pixel-caf | нет | да | 1 | port/a17-mondrian-qcom-interfaces-aidl-20261107 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть port/a17-mondrian-qcom-interfaces-aidl-20261107) |
| `vendor_qcom_opensource_libfmjni` | `vendor/qcom/opensource/libfmjni` | pixel-caf | нет | да | 1 | guard/a17-mondrian-fm-jni-excluded-20261107 | не нужен: FM-радио в mondrian нет |
| `vendor_qcom_opensource_power` | `vendor/qcom/opensource/power` | pixel-caf | нет | да | 1 | port/a17-mondrian-power-aidl-adpf-guard-20261107 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть port/a17-mondrian-power-aidl-adpf-guard-20261107) |
| `vendor_qcom_opensource_thermal-engine` | `vendor/qcom/opensource/thermal-engine` | pixel-caf | нет | да | 1 | port/a17-mondrian-thermal-client-header-20261107 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть port/a17-mondrian-thermal-client-header-20261107) |
| `vendor_qcom_opensource_usb` | `vendor/qcom/opensource/usb` | pixel-caf | нет | да | 1 | port/a17-mondrian-usb-aidl-legacy-guard-20261107 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть port/a17-mondrian-usb-aidl-legacy-guard-20261107) |
| `vendor_qcom_opensource_vibrator` | `vendor/qcom/opensource/vibrator` | pixel-caf | нет | да | 1 | port/a17-mondrian-vibrator-aidl-offload-safety-20261108 | нужен mondrian (Qualcomm SM8450): перенести на A17 (есть port/a17-mondrian-vibrator-aidl-offload-safety-20261108) |
| `vendor_qcom_opensource_wfd-commonsys` | `vendor/qcom/opensource/wfd-commonsys` | pixel-caf | нет | да | 1 | port/a17-mondrian-wfdaac-ownership-buffers-20261108 | не нужен: Wi-Fi Display требует закрытых QTI system-блобов, которые мы не берём |
