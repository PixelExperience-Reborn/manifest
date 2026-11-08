# PixelExperience GitHub: 373 репозитория против выбранных 135 PE-Reborn

**Снимок каталога:** 8 ноября 2026 года. Сопоставлены публичные GitHub-организации [PixelExperience](https://github.com/PixelExperience) и [PixelExperience-Reborn](https://github.com/PixelExperience-Reborn) со всеми страницами публичного каталога репозиториев; исторический PE14 manifest закреплён на [136aee69](https://github.com/PixelExperience/manifest/tree/136aee696422bda841eb5c6a3c9279bbb6bbef02) (2024-03-06). Это **сверка наличия репозиториев и manifest**, НЕ компиляция, лицензирование или технический аудит исходников 373 проектов.

## Инвентаризация на момент проверки

| Группа | Количество |
|---|---:|
| Все публичные репозитории оригинальной PixelExperience | 373 |
| Все публичные репозитории PixelExperience-Reborn | 135 |
| Репозитории Reborn, не соответствующие именам оригинальной PixelExperience | 0 |
| Оригинальные GitHub-репозитории, не имеющие копии в Reborn | **238** |
| Из 238: PE14 активные GitHub-сниппеты `pixel/pixel-extras/pixel-caf` | **48** |
| Из 238: отдельный `pixel-extras-dependencies.xml`, не включённый в default | **5** |
| Из 238: прочие старые или не входившие в PE14 default репозитории | **185** |
| Отдельные PE14 main записи на GitLab, а не GitHub | **2** |

**Важно:** строка 238 не означает 238 обязательных недостающих исходников для Android17. 50 записей основного PE14 manifest вне первоначальной 135-матрицы состоят из **48** оригинальных GitHub-проектов и **2** GitLab-проектов.

## Pixel Launcher и другие действительно значимые границы

- Отдельный старый [PixelExperience/packages_apps_Launcher3](https://github.com/PixelExperience/packages_apps_Launcher3) **есть**, но его единственная ветка `oreo-mr1`, последний commit 637ad2e7aaf948390516edac57db715faf44e9ce (2018-10-14). Он не содержится в PE14 manifest. AOSP14, как и наш AOSP17, предоставляет `packages/apps/Launcher3` из `platform/packages/apps/Launcher3`.
- Реальный оригинальный PE14 `vendor/aosp/config/common.mk` указывает `NexusLauncherRelease` и `SystemUIGoogle` как **`PRODUCT_DEXPREOPT_SPEED_APPS`**, а не как `PRODUCT_PACKAGES`; он также наследует `vendor/gms/products/gms.mk`. `config/rro_overlays.mk` включает `PixelLauncherCustomOverlay`. То есть исходный продукт ссылается на Google Launcher и отдельный GMS-продукт, **но точный источник/установка APK без доступного исторического vendor/gms не доказаны**. PE-Reborn `vendor_aosp` уже имеется; [PR #1](https://github.com/PixelExperience-Reborn/vendor_aosp/pull/1) ограждает проприетарный GMS флагом `WITH_GMS=true`, а старые overlays — отдельным `PE_A17_PORT_LEGACY_OVERLAYS`.
- Репозитории `external_faceunlock` и `vendor_gms` объявлены через `pixel-gitlab` в оригинальном PE14, **не** через GitHub-организацию. Их нет среди 373 GH-репозиториев; автоматически скачивать и распространять GMS нельзя. Чистый AOSP17 должен компилироваться без этого набора.
- `hardware_xiaomi` из отдельного `pixel-extras-dependencies.xml` является OEM hardware-проектом, не деревом устройства и **не** частью трёх сниппетов оригинального default PE14. Для самостоятельной платформы не нужен, возможен отдельный аудит позже.
- Дополнительные приложения прошлых лет, такие как `packages_apps_Updates`, `packages_apps_Recorder`, `packages_apps_Snap`, `packages_apps_CarrierConfig`, `packages_apps_Stk`, были в старых ветках, но не являются обязательными форками PE14. FM Radio остаётся исключённым.

## 48 проектов основного оригинального PE14, находящихся на GitHub, но отсутствующих в Reborn

| Исходный PE14 путь | Исходный репозиторий | Решение сейчас |
|---|---|---|
| `device/google/contexthub` | [`device_google_contexthub`](https://github.com/PixelExperience/device_google_contexthub) | AOSP17 официальный путь; не требуется форк |
| `device/google/cuttlefish` | [`device_google_cuttlefish`](https://github.com/PixelExperience/device_google_cuttlefish) | AOSP17 официальный путь; не требуется форк |
| `device/qcom/sepolicy_vndr/legacy-um` | [`device_qcom_sepolicy_vndr_legacy-um`](https://github.com/PixelExperience/device_qcom_sepolicy_vndr_legacy-um) | Исторический QCOM SELinux; только по реальной нужде |
| `device/qcom/sepolicy_vndr/sm8550` | [`device_qcom_sepolicy_vndr_sm8550`](https://github.com/PixelExperience/device_qcom_sepolicy_vndr_sm8550) | Исторический QCOM SELinux; только по реальной нужде |
| `device/qcom/sepolicy-legacy-um` | [`device_qcom_sepolicy-legacy-um`](https://github.com/PixelExperience/device_qcom_sepolicy-legacy-um) | Исторический QCOM SELinux; только по реальной нужде |
| `hardware/qcom-caf/bengal/audio` | [`hardware_qcom-caf_bengal_audio`](https://github.com/PixelExperience/hardware_qcom-caf_bengal_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/bengal/display` | [`hardware_qcom-caf_bengal_display`](https://github.com/PixelExperience/hardware_qcom-caf_bengal_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/bengal/media` | [`hardware_qcom-caf_bengal_media`](https://github.com/PixelExperience/hardware_qcom-caf_bengal_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8953/audio` | [`hardware_qcom-caf_msm8953_audio`](https://github.com/PixelExperience/hardware_qcom-caf_msm8953_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8953/display` | [`hardware_qcom-caf_msm8953_display`](https://github.com/PixelExperience/hardware_qcom-caf_msm8953_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8953/media` | [`hardware_qcom-caf_msm8953_media`](https://github.com/PixelExperience/hardware_qcom-caf_msm8953_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8996/audio` | [`hardware_qcom-caf_msm8996_audio`](https://github.com/PixelExperience/hardware_qcom-caf_msm8996_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8996/display` | [`hardware_qcom-caf_msm8996_display`](https://github.com/PixelExperience/hardware_qcom-caf_msm8996_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8996/media` | [`hardware_qcom-caf_msm8996_media`](https://github.com/PixelExperience/hardware_qcom-caf_msm8996_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8998/audio` | [`hardware_qcom-caf_msm8998_audio`](https://github.com/PixelExperience/hardware_qcom-caf_msm8998_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8998/display` | [`hardware_qcom-caf_msm8998_display`](https://github.com/PixelExperience/hardware_qcom-caf_msm8998_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/msm8998/media` | [`hardware_qcom-caf_msm8998_media`](https://github.com/PixelExperience/hardware_qcom-caf_msm8998_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sdm660/audio` | [`hardware_qcom-caf_sdm660_audio`](https://github.com/PixelExperience/hardware_qcom-caf_sdm660_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sdm660/display` | [`hardware_qcom-caf_sdm660_display`](https://github.com/PixelExperience/hardware_qcom-caf_sdm660_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sdm660/media` | [`hardware_qcom-caf_sdm660_media`](https://github.com/PixelExperience/hardware_qcom-caf_sdm660_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sdm845/audio` | [`hardware_qcom-caf_sdm845_audio`](https://github.com/PixelExperience/hardware_qcom-caf_sdm845_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sdm845/display` | [`hardware_qcom-caf_sdm845_display`](https://github.com/PixelExperience/hardware_qcom-caf_sdm845_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sdm845/media` | [`hardware_qcom-caf_sdm845_media`](https://github.com/PixelExperience/hardware_qcom-caf_sdm845_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8150/audio` | [`hardware_qcom-caf_sm8150_audio`](https://github.com/PixelExperience/hardware_qcom-caf_sm8150_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8150/display` | [`hardware_qcom-caf_sm8150_display`](https://github.com/PixelExperience/hardware_qcom-caf_sm8150_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8150/media` | [`hardware_qcom-caf_sm8150_media`](https://github.com/PixelExperience/hardware_qcom-caf_sm8150_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8250/audio` | [`hardware_qcom-caf_sm8250_audio`](https://github.com/PixelExperience/hardware_qcom-caf_sm8250_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8250/display` | [`hardware_qcom-caf_sm8250_display`](https://github.com/PixelExperience/hardware_qcom-caf_sm8250_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8250/media` | [`hardware_qcom-caf_sm8250_media`](https://github.com/PixelExperience/hardware_qcom-caf_sm8250_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8350/audio` | [`hardware_qcom-caf_sm8350_audio`](https://github.com/PixelExperience/hardware_qcom-caf_sm8350_audio) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8350/display` | [`hardware_qcom-caf_sm8350_display`](https://github.com/PixelExperience/hardware_qcom-caf_sm8350_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8350/media` | [`hardware_qcom-caf_sm8350_media`](https://github.com/PixelExperience/hardware_qcom-caf_sm8350_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8550/audio/agm` | [`hardware_qcom-caf_sm8550_audio_agm`](https://github.com/PixelExperience/hardware_qcom-caf_sm8550_audio_agm) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8550/audio/pal` | [`hardware_qcom-caf_sm8550_audio_pal`](https://github.com/PixelExperience/hardware_qcom-caf_sm8550_audio_pal) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8550/audio/primary-hal` | [`hardware_qcom-caf_sm8550_audio_primary-hal`](https://github.com/PixelExperience/hardware_qcom-caf_sm8550_audio_primary-hal) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8550/data-ipa-cfg-mgr` | [`hardware_qcom-caf_sm8550_data-ipa-cfg-mgr`](https://github.com/PixelExperience/hardware_qcom-caf_sm8550_data-ipa-cfg-mgr) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8550/dataipa` | [`hardware_qcom-caf_sm8550_dataipa`](https://github.com/PixelExperience/hardware_qcom-caf_sm8550_dataipa) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8550/display` | [`hardware_qcom-caf_sm8550_display`](https://github.com/PixelExperience/hardware_qcom-caf_sm8550_display) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom-caf/sm8550/media` | [`hardware_qcom-caf_sm8550_media`](https://github.com/PixelExperience/hardware_qcom-caf_sm8550_media) | Исторический Qualcomm HAL другого семейства; не основа Android17 |
| `hardware/qcom/sdm845/data/ipacfg-mgr` | [`hardware_qcom_sdm845_data_ipacfg-mgr`](https://github.com/PixelExperience/hardware_qcom_sdm845_data_ipacfg-mgr) | Исторический HAL для другого поколения Qualcomm |
| `hardware/qcom/sdm845/display` | [`hardware_qcom_sdm845_display`](https://github.com/PixelExperience/hardware_qcom_sdm845_display) | Исторический HAL для другого поколения Qualcomm |
| `hardware/qcom/sdm845/media` | [`hardware_qcom_sdm845_media`](https://github.com/PixelExperience/hardware_qcom_sdm845_media) | Исторический HAL для другого поколения Qualcomm |
| `hardware/qcom/sm7250/display` | [`hardware_qcom_sm7250_display`](https://github.com/PixelExperience/hardware_qcom_sm7250_display) | Исторический HAL для другого поколения Qualcomm |
| `hardware/qcom/sm7250/media` | [`hardware_qcom_sm7250_media`](https://github.com/PixelExperience/hardware_qcom_sm7250_media) | Исторический HAL для другого поколения Qualcomm |
| `hardware/qcom/sm8150/data/ipacfg-mgr` | [`hardware_qcom_sm8150_data_ipacfg-mgr`](https://github.com/PixelExperience/hardware_qcom_sm8150_data_ipacfg-mgr) | Исторический HAL для другого поколения Qualcomm |
| `hardware/qcom/sm8150/display` | [`hardware_qcom_sm8150_display`](https://github.com/PixelExperience/hardware_qcom_sm8150_display) | Исторический HAL для другого поколения Qualcomm |
| `hardware/qcom/sm8150/media` | [`hardware_qcom_sm8150_media`](https://github.com/PixelExperience/hardware_qcom_sm8150_media) | Исторический HAL для другого поколения Qualcomm |
| `vendor/qcom/opensource/data-ipa-cfg-mgr-legacy-um` | [`vendor_qcom_opensource_data-ipa-cfg-mgr-legacy-um`](https://github.com/PixelExperience/vendor_qcom_opensource_data-ipa-cfg-mgr-legacy-um) | Наследие старых Qualcomm платформ |

## Два внешних GitLab-проекта в оригинальном PE14

| PE14 путь | Оригинальное имя | Статус |
|---|---|---|
| `external/faceunlock` | `external_faceunlock` | Face Unlock — необязательная дополнительная возможность |
| `vendor/gms` | `vendor_gms` | GMS/Google Pixel Launcher — лицензия и Android17 продукт отдельно |

## Пять необязательных OEM-проектов (оригинальный PE14 default их не включал)

| Путь | Архивный оригинал | Статус |
|---|---|---|
| `hardware/motorola` | [`hardware_motorola`](https://github.com/PixelExperience/hardware_motorola) | Другой OEM; не включать в текущую платформу |
| `hardware/oneplus` | [`hardware_oneplus`](https://github.com/PixelExperience/hardware_oneplus) | Другой OEM; не включать в текущую платформу |
| `hardware/oplus` | [`hardware_oplus`](https://github.com/PixelExperience/hardware_oplus) | Другой OEM; не включать в текущую платформу |
| `hardware/samsung` | [`hardware_samsung`](https://github.com/PixelExperience/hardware_samsung) | Другой OEM; не включать в текущую платформу |
| `hardware/xiaomi` | [`hardware_xiaomi`](https://github.com/PixelExperience/hardware_xiaomi) | Поздняя аппаратная квалификация; не включать в базу |

## Прочие 185 оригинальных GitHub-репозиториев вне PE14 default

Это старые/сторонние/вспомогательные проекты исходной организации. Их наличие в GitHub **не** означает необходимость форка для независимой AOSP17. Указаны только имя и основная ветка; пригодность для Android17 в этом аудите **не проверялась**.

| Исторический репозиторий | Ветка оригинала |
|---|---|
| [`android-issues`](https://github.com/PixelExperience/android-issues) | `main` |
| [`build_blueprint`](https://github.com/PixelExperience/build_blueprint) | `thirteen` |
| [`crowdin`](https://github.com/PixelExperience/crowdin) | `master` |
| [`cts`](https://github.com/PixelExperience/cts) | `thirteen` |
| [`device_mediatek_sepolicy_vndr`](https://github.com/PixelExperience/device_mediatek_sepolicy_vndr) | `thirteen` |
| [`device_qcom_common`](https://github.com/PixelExperience/device_qcom_common) | `pie-caf` |
| [`device_qcom_sepolicy_vndr`](https://github.com/PixelExperience/device_qcom_sepolicy_vndr) | `fourteen` |
| [`device_qcom_sepolicy_vndr-legacy-um`](https://github.com/PixelExperience/device_qcom_sepolicy_vndr-legacy-um) | `thirteen` |
| [`device_qcom_sepolicy-legacy`](https://github.com/PixelExperience/device_qcom_sepolicy-legacy) | `twelve` |
| [`device_qcom_wlan`](https://github.com/PixelExperience/device_qcom_wlan) | `thirteen` |
| [`device_samsung_slsi_sepolicy`](https://github.com/PixelExperience/device_samsung_slsi_sepolicy) | `thirteen` |
| [`docs`](https://github.com/PixelExperience/docs) | `master` |
| [`external_aac`](https://github.com/PixelExperience/external_aac) | `ten` |
| [`external_ant-wireless_antradio-library`](https://github.com/PixelExperience/external_ant-wireless_antradio-library) | `twelve` |
| [`external_asus_stitchimage`](https://github.com/PixelExperience/external_asus_stitchimage) | `ten-plus` |
| [`external_boringssl`](https://github.com/PixelExperience/external_boringssl) | `thirteen` |
| [`external_chromium-libpac`](https://github.com/PixelExperience/external_chromium-libpac) | `pie` |
| [`external_cldr`](https://github.com/PixelExperience/external_cldr) | `thirteen` |
| [`external_dwarves`](https://github.com/PixelExperience/external_dwarves) | `thirteen` |
| [`external_elfutils`](https://github.com/PixelExperience/external_elfutils) | `pie-caf` |
| [`external_exfat`](https://github.com/PixelExperience/external_exfat) | `eleven` |
| [`external_exfatprogs`](https://github.com/PixelExperience/external_exfatprogs) | `twelve` |
| [`external_expat`](https://github.com/PixelExperience/external_expat) | `twelve` |
| [`external_f2fs-tools`](https://github.com/PixelExperience/external_f2fs-tools) | `pie-caf` |
| [`external_freetype`](https://github.com/PixelExperience/external_freetype) | `ten` |
| [`external_guice`](https://github.com/PixelExperience/external_guice) | `thirteen` |
| [`external_ImageMagick`](https://github.com/PixelExperience/external_ImageMagick) | `pie` |
| [`external_jemalloc_new`](https://github.com/PixelExperience/external_jemalloc_new) | `thirteen` |
| [`external_libaom`](https://github.com/PixelExperience/external_libaom) | `ten` |
| [`external_libcups`](https://github.com/PixelExperience/external_libcups) | `pie` |
| [`external_libexif`](https://github.com/PixelExperience/external_libexif) | `ten` |
| [`external_libhevc`](https://github.com/PixelExperience/external_libhevc) | `ten` |
| [`external_libjpeg-turbo`](https://github.com/PixelExperience/external_libjpeg-turbo) | `pie` |
| [`external_libnfc-nxp`](https://github.com/PixelExperience/external_libnfc-nxp) | `thirteen` |
| [`external_libtextclassifier`](https://github.com/PixelExperience/external_libtextclassifier) | `ten` |
| [`external_libxml2`](https://github.com/PixelExperience/external_libxml2) | `thirteen` |
| [`external_lottie`](https://github.com/PixelExperience/external_lottie) | `eleven` |
| [`external_motorola_faceunlock-res`](https://github.com/PixelExperience/external_motorola_faceunlock-res) | `ten` |
| [`external_openssh`](https://github.com/PixelExperience/external_openssh) | `eleven` |
| [`external_pdfium`](https://github.com/PixelExperience/external_pdfium) | `thirteen` |
| [`external_perfetto`](https://github.com/PixelExperience/external_perfetto) | `thirteen` |
| [`external_proguard`](https://github.com/PixelExperience/external_proguard) | `pie-caf` |
| [`external_robolectric-shadows`](https://github.com/PixelExperience/external_robolectric-shadows) | `eleven` |
| [`external_selinux`](https://github.com/PixelExperience/external_selinux) | `thirteen` |
| [`external_skia`](https://github.com/PixelExperience/external_skia) | `ten` |
| [`external_sonivox`](https://github.com/PixelExperience/external_sonivox) | `ten` |
| [`external_sqlite`](https://github.com/PixelExperience/external_sqlite) | `pie` |
| [`external_tinyalsa`](https://github.com/PixelExperience/external_tinyalsa) | `thirteen` |
| [`external_toybox`](https://github.com/PixelExperience/external_toybox) | `thirteen` |
| [`external_tremolo`](https://github.com/PixelExperience/external_tremolo) | `eleven` |
| [`external_v8`](https://github.com/PixelExperience/external_v8) | `pie` |
| [`external_webp`](https://github.com/PixelExperience/external_webp) | `thirteen` |
| [`frameworks_hwkeys-support`](https://github.com/PixelExperience/frameworks_hwkeys-support) | `oreo-mr1` |
| [`frameworks_opt_net_ims`](https://github.com/PixelExperience/frameworks_opt_net_ims) | `thirteen` |
| [`frameworks_opt_net_voip`](https://github.com/PixelExperience/frameworks_opt_net_voip) | `pie` |
| [`frameworks_opt_net_wifi`](https://github.com/PixelExperience/frameworks_opt_net_wifi) | `thirteen` |
| [`gerrit_manifest`](https://github.com/PixelExperience/gerrit_manifest) | `master` |
| [`gerrit-css-theme`](https://github.com/PixelExperience/gerrit-css-theme) | `master` |
| [`hardware_broadcom_nfc`](https://github.com/PixelExperience/hardware_broadcom_nfc) | `thirteen` |
| [`hardware_custom_keydisabler`](https://github.com/PixelExperience/hardware_custom_keydisabler) | `pie` |
| [`hardware_custom-interfaces`](https://github.com/PixelExperience/hardware_custom-interfaces) | `oreo-mr1` |
| [`hardware_knowles_athletico_sound_trigger_hal`](https://github.com/PixelExperience/hardware_knowles_athletico_sound_trigger_hal) | `thirteen` |
| [`hardware_libhardware_legacy`](https://github.com/PixelExperience/hardware_libhardware_legacy) | `thirteen` |
| [`hardware_lineage_livedisplay`](https://github.com/PixelExperience/hardware_lineage_livedisplay) | `thirteen-plus` |
| [`hardware_mediatek`](https://github.com/PixelExperience/hardware_mediatek) | `thirteen` |
| [`hardware_nxp_nfc`](https://github.com/PixelExperience/hardware_nxp_nfc) | `thirteen` |
| [`hardware_qcom_audio-caf_msm8996`](https://github.com/PixelExperience/hardware_qcom_audio-caf_msm8996) | `pie-caf` |
| [`hardware_qcom_audio-caf_msm8998`](https://github.com/PixelExperience/hardware_qcom_audio-caf_msm8998) | `pie-caf` |
| [`hardware_qcom_audio-caf_sdm845`](https://github.com/PixelExperience/hardware_qcom_audio-caf_sdm845) | `pie-caf` |
| [`hardware_qcom_audio-caf_sm8150`](https://github.com/PixelExperience/hardware_qcom_audio-caf_sm8150) | `pie-caf` |
| [`hardware_qcom_bootctrl`](https://github.com/PixelExperience/hardware_qcom_bootctrl) | `ten` |
| [`hardware_qcom_bt`](https://github.com/PixelExperience/hardware_qcom_bt) | `ten` |
| [`hardware_qcom_display_sde`](https://github.com/PixelExperience/hardware_qcom_display_sde) | `master` |
| [`hardware_qcom_display-caf_headers`](https://github.com/PixelExperience/hardware_qcom_display-caf_headers) | `pie` |
| [`hardware_qcom_display-caf_msm8996`](https://github.com/PixelExperience/hardware_qcom_display-caf_msm8996) | `pie-caf` |
| [`hardware_qcom_display-caf_msm8998`](https://github.com/PixelExperience/hardware_qcom_display-caf_msm8998) | `pie-caf` |
| [`hardware_qcom_display-caf_sdm845`](https://github.com/PixelExperience/hardware_qcom_display-caf_sdm845) | `pie-caf` |
| [`hardware_qcom_display-caf_sm8150`](https://github.com/PixelExperience/hardware_qcom_display-caf_sm8150) | `pie-caf` |
| [`hardware_qcom_fm`](https://github.com/PixelExperience/hardware_qcom_fm) | `pie` |
| [`hardware_qcom_keymaster`](https://github.com/PixelExperience/hardware_qcom_keymaster) | `thirteen` |
| [`hardware_qcom_media-caf_msm8996`](https://github.com/PixelExperience/hardware_qcom_media-caf_msm8996) | `pie-caf` |
| [`hardware_qcom_media-caf_msm8998`](https://github.com/PixelExperience/hardware_qcom_media-caf_msm8998) | `pie-caf` |
| [`hardware_qcom_media-caf_sdm845`](https://github.com/PixelExperience/hardware_qcom_media-caf_sdm845) | `pie-caf` |
| [`hardware_qcom_media-caf_sm8150`](https://github.com/PixelExperience/hardware_qcom_media-caf_sm8150) | `pie-caf` |
| [`hardware_qcom_msm8998`](https://github.com/PixelExperience/hardware_qcom_msm8998) | `thirteen` |
| [`hardware_qcom_msm8x84`](https://github.com/PixelExperience/hardware_qcom_msm8x84) | `oreo-mr1` |
| [`hardware_qcom_power`](https://github.com/PixelExperience/hardware_qcom_power) | `pie` |
| [`hardware_qcom-caf_bengal_gps`](https://github.com/PixelExperience/hardware_qcom-caf_bengal_gps) | `thirteen` |
| [`hardware_qcom-caf_bt`](https://github.com/PixelExperience/hardware_qcom-caf_bt) | `twelve` |
| [`hardware_qcom-caf_msm8996-r_audio`](https://github.com/PixelExperience/hardware_qcom-caf_msm8996-r_audio) | `twelve` |
| [`hardware_qcom-caf_msm8996-r_display`](https://github.com/PixelExperience/hardware_qcom-caf_msm8996-r_display) | `twelve` |
| [`hardware_qcom-caf_msm8996-r_media`](https://github.com/PixelExperience/hardware_qcom-caf_msm8996-r_media) | `twelve` |
| [`hardware_qcom-caf_sm8150-common_audio`](https://github.com/PixelExperience/hardware_qcom-caf_sm8150-common_audio) | `thirteen` |
| [`hardware_qcom-caf_sm8150-common_display`](https://github.com/PixelExperience/hardware_qcom-caf_sm8150-common_display) | `thirteen` |
| [`hardware_qcom-caf_sm8150-common_gps`](https://github.com/PixelExperience/hardware_qcom-caf_sm8150-common_gps) | `main` |
| [`hardware_qcom-caf_sm8150-common_media`](https://github.com/PixelExperience/hardware_qcom-caf_sm8150-common_media) | `thirteen` |
| [`hardware_samsung_slsi_libbt`](https://github.com/PixelExperience/hardware_samsung_slsi_libbt) | `thirteen` |
| [`hardware_st_nfc`](https://github.com/PixelExperience/hardware_st_nfc) | `thirteen` |
| [`libcore`](https://github.com/PixelExperience/libcore) | `thirteen` |
| [`official_devices`](https://github.com/PixelExperience/official_devices) | `master` |
| [`old_frameworks_base`](https://github.com/PixelExperience/old_frameworks_base) | `pie` |
| [`old_system_core`](https://github.com/PixelExperience/old_system_core) | `pie` |
| [`packages_apps_Bluetooth`](https://github.com/PixelExperience/packages_apps_Bluetooth) | `twelve` |
| [`packages_apps_Car_Settings`](https://github.com/PixelExperience/packages_apps_Car_Settings) | `ten` |
| [`packages_apps_CarrierConfig`](https://github.com/PixelExperience/packages_apps_CarrierConfig) | `thirteen` |
| [`packages_apps_CellBroadcastReceiver`](https://github.com/PixelExperience/packages_apps_CellBroadcastReceiver) | `oreo-mr1` |
| [`packages_apps_CertInstaller`](https://github.com/PixelExperience/packages_apps_CertInstaller) | `ten` |
| [`packages_apps_CustomSettings`](https://github.com/PixelExperience/packages_apps_CustomSettings) | `oreo-mr1` |
| [`packages_apps_DocumentsUI`](https://github.com/PixelExperience/packages_apps_DocumentsUI) | `ten` |
| [`packages_apps_ElmyraService`](https://github.com/PixelExperience/packages_apps_ElmyraService) | `eleven` |
| [`packages_apps_EmergencyInfo`](https://github.com/PixelExperience/packages_apps_EmergencyInfo) | `ten` |
| [`packages_apps_FMRadio`](https://github.com/PixelExperience/packages_apps_FMRadio) | `thirteen` |
| [`packages_apps_KeyChain`](https://github.com/PixelExperience/packages_apps_KeyChain) | `eleven` |
| [`packages_apps_Launcher3`](https://github.com/PixelExperience/packages_apps_Launcher3) | `oreo-mr1` |
| [`packages_apps_Longshot`](https://github.com/PixelExperience/packages_apps_Longshot) | `pie-plus` |
| [`packages_apps_ManagedProvisioning`](https://github.com/PixelExperience/packages_apps_ManagedProvisioning) | `eleven` |
| [`packages_apps_MusicFX`](https://github.com/PixelExperience/packages_apps_MusicFX) | `oreo-mr1` |
| [`packages_apps_PackageInstaller`](https://github.com/PixelExperience/packages_apps_PackageInstaller) | `ten` |
| [`packages_apps_ParanoidGlyph`](https://github.com/PixelExperience/packages_apps_ParanoidGlyph) | `thirteen` |
| [`packages_apps_PermissionController`](https://github.com/PixelExperience/packages_apps_PermissionController) | `eleven` |
| [`packages_apps_PhoneCommon`](https://github.com/PixelExperience/packages_apps_PhoneCommon) | `thirteen` |
| [`packages_apps_Recorder`](https://github.com/PixelExperience/packages_apps_Recorder) | `ten` |
| [`packages_apps_RepainterService`](https://github.com/PixelExperience/packages_apps_RepainterService) | `thirteen-plus` |
| [`packages_apps_SettingsIntelligence`](https://github.com/PixelExperience/packages_apps_SettingsIntelligence) | `ten` |
| [`packages_apps_SimpleDeviceConfig`](https://github.com/PixelExperience/packages_apps_SimpleDeviceConfig) | `thirteen` |
| [`packages_apps_Snap`](https://github.com/PixelExperience/packages_apps_Snap) | `eleven` |
| [`packages_apps_Stk`](https://github.com/PixelExperience/packages_apps_Stk) | `thirteen` |
| [`packages_apps_Traceur`](https://github.com/PixelExperience/packages_apps_Traceur) | `thirteen` |
| [`packages_apps_Updates`](https://github.com/PixelExperience/packages_apps_Updates) | `thirteen` |
| [`packages_modules_CaptivePortalLogin`](https://github.com/PixelExperience/packages_modules_CaptivePortalLogin) | `eleven` |
| [`packages_modules_DnsResolver`](https://github.com/PixelExperience/packages_modules_DnsResolver) | `thirteen` |
| [`packages_modules_NetworkStack`](https://github.com/PixelExperience/packages_modules_NetworkStack) | `thirteen` |
| [`packages_modules_StatsD`](https://github.com/PixelExperience/packages_modules_StatsD) | `thirteen` |
| [`packages_modules_Virtualization`](https://github.com/PixelExperience/packages_modules_Virtualization) | `thirteen` |
| [`packages_overlays_ThemeIcons`](https://github.com/PixelExperience/packages_overlays_ThemeIcons) | `thirteen-plus` |
| [`packages_providers_AmbientPlayHistoryProvider`](https://github.com/PixelExperience/packages_providers_AmbientPlayHistoryProvider) | `pie` |
| [`packages_providers_ContactsProvider`](https://github.com/PixelExperience/packages_providers_ContactsProvider) | `twelve` |
| [`packages_providers_TelephonyProvider`](https://github.com/PixelExperience/packages_providers_TelephonyProvider) | `twelve` |
| [`packages_providers_TvProvider`](https://github.com/PixelExperience/packages_providers_TvProvider) | `pie` |
| [`packages_resources_devicesettings-custom`](https://github.com/PixelExperience/packages_resources_devicesettings-custom) | `eleven` |
| [`packages_services_BuiltInPrintService`](https://github.com/PixelExperience/packages_services_BuiltInPrintService) | `thirteen` |
| [`patches`](https://github.com/PixelExperience/patches) | `ten` |
| [`prebuilts_abi-dumps_vndk`](https://github.com/PixelExperience/prebuilts_abi-dumps_vndk) | `eleven` |
| [`prebuilts_clang_host_linux-x86`](https://github.com/PixelExperience/prebuilts_clang_host_linux-x86) | `pie` |
| [`prebuilts_gcc_darwin-x86_aarch64_aarch64-linux-android-4.9`](https://github.com/PixelExperience/prebuilts_gcc_darwin-x86_aarch64_aarch64-linux-android-4.9) | `thirteen` |
| [`prebuilts_gcc_darwin-x86_arm_arm-linux-androideabi-4.9`](https://github.com/PixelExperience/prebuilts_gcc_darwin-x86_arm_arm-linux-androideabi-4.9) | `thirteen` |
| [`prebuilts_gcc_darwin-x86_x86_x86_64-linux-android-4.9`](https://github.com/PixelExperience/prebuilts_gcc_darwin-x86_x86_x86_64-linux-android-4.9) | `thirteen` |
| [`prebuilts_r8`](https://github.com/PixelExperience/prebuilts_r8) | `ten` |
| [`status`](https://github.com/PixelExperience/status) | `master` |
| [`system_apex`](https://github.com/PixelExperience/system_apex) | `thirteen` |
| [`system_bt`](https://github.com/PixelExperience/system_bt) | `twelve` |
| [`system_ca-certificates`](https://github.com/PixelExperience/system_ca-certificates) | `thirteen` |
| [`system_hardware_interfaces`](https://github.com/PixelExperience/system_hardware_interfaces) | `ten` |
| [`system_incremental_delivery`](https://github.com/PixelExperience/system_incremental_delivery) | `thirteen` |
| [`system_keymaster`](https://github.com/PixelExperience/system_keymaster) | `ten` |
| [`system_libufdt`](https://github.com/PixelExperience/system_libufdt) | `thirteen` |
| [`system_libvintf`](https://github.com/PixelExperience/system_libvintf) | `oreo-mr1` |
| [`system_memory_lmkd`](https://github.com/PixelExperience/system_memory_lmkd) | `thirteen` |
| [`system_netd`](https://github.com/PixelExperience/system_netd) | `thirteen` |
| [`system_nfc`](https://github.com/PixelExperience/system_nfc) | `thirteen` |
| [`system_qcom`](https://github.com/PixelExperience/system_qcom) | `thirteen` |
| [`system_timezone`](https://github.com/PixelExperience/system_timezone) | `thirteen` |
| [`system_tools_aidl`](https://github.com/PixelExperience/system_tools_aidl) | `eleven` |
| [`system_tools_hidl`](https://github.com/PixelExperience/system_tools_hidl) | `thirteen` |
| [`tools_apksig`](https://github.com/PixelExperience/tools_apksig) | `thirteen` |
| [`vendor_codeaurora_commonsys_telephony`](https://github.com/PixelExperience/vendor_codeaurora_commonsys_telephony) | `pie-caf` |
| [`vendor_gapps`](https://github.com/PixelExperience/vendor_gapps) | `main` |
| [`vendor_google-customization`](https://github.com/PixelExperience/vendor_google-customization) | `ten` |
| [`vendor_mediatek_hardware_interfaces`](https://github.com/PixelExperience/vendor_mediatek_hardware_interfaces) | `ten` |
| [`vendor_mediatek_hardware_telephony-ext`](https://github.com/PixelExperience/vendor_mediatek_hardware_telephony-ext) | `ten` |
| [`vendor_opengapps_build`](https://github.com/PixelExperience/vendor_opengapps_build) | `oreo-mr1` |
| [`vendor_pixelstyle`](https://github.com/PixelExperience/vendor_pixelstyle) | `ten` |
| [`vendor_qcom_opensource_audio`](https://github.com/PixelExperience/vendor_qcom_opensource_audio) | `thirteen` |
| [`vendor_qcom_opensource_commonsys_bluetooth`](https://github.com/PixelExperience/vendor_qcom_opensource_commonsys_bluetooth) | `pie-caf` |
| [`vendor_qcom_opensource_commonsys_bluetooth_ext`](https://github.com/PixelExperience/vendor_qcom_opensource_commonsys_bluetooth_ext) | `twelve` |
| [`vendor_qcom_opensource_commonsys_cryptfs_hw`](https://github.com/PixelExperience/vendor_qcom_opensource_commonsys_cryptfs_hw) | `pie-caf` |
| [`vendor_qcom_opensource_commonsys_dpm`](https://github.com/PixelExperience/vendor_qcom_opensource_commonsys_dpm) | `thirteen` |
| [`vendor_qcom_opensource_commonsys_packages_apps_Bluetooth`](https://github.com/PixelExperience/vendor_qcom_opensource_commonsys_packages_apps_Bluetooth) | `twelve` |
| [`vendor_qcom_opensource_commonsys_system_bt`](https://github.com/PixelExperience/vendor_qcom_opensource_commonsys_system_bt) | `twelve` |
| [`vendor_qcom_opensource_commonsys-intf_bluetooth`](https://github.com/PixelExperience/vendor_qcom_opensource_commonsys-intf_bluetooth) | `thirteen` |
| [`vendor_qcom_opensource_cryptfs_hw`](https://github.com/PixelExperience/vendor_qcom_opensource_cryptfs_hw) | `thirteen` |
| [`vendor_qcom_opensource_data-ipa-cfg-mgr`](https://github.com/PixelExperience/vendor_qcom_opensource_data-ipa-cfg-mgr) | `thirteen` |
| [`vendor_themes`](https://github.com/PixelExperience/vendor_themes) | `pie-plus` |
| [`WeatherClient`](https://github.com/PixelExperience/WeatherClient) | `master` |
| [`wiki`](https://github.com/PixelExperience/wiki) | `master` |

## Решения для дальнейшего восстановления платформы

1. Не расширять AOSP17 manifest механически до 373 старых форков: многие относятся к Android8–14, неподходящим Qualcomm поколениям или другим производителям.
2. Проверить выбранный AOSP17 launcher и PRODUCT_PACKAGES в **чистой, без-GMS** сборке, затем отдельно — лицензированный Google Pixel Launcher вариант, если принято решение его поддерживать.
3. По отсутствующим *реальным* Soong/API зависимостям обращаться к современным источникам Google AOSP17 и Qualcomm, сохраняя проверяемые SHA и лицензионные условия. Ни один из 48 исторических PE14 GitHub-проектов не признан обязательным только по имени.
4. Действующие 135/135 — завершённые **первичные аудиты выбранного набора**, не показатель полноты организации или готовности платформы к компиляции.

Основной [сверочный отчёт о 185/135/50 + 5](ANDROID_17_ORIGINAL_PE14_REPOSITORY_COVERAGE_AUDIT.md). [Тест закреплённого оригинального PE14 manifest](../tools/audit_original_pe_fourteen_coverage.py).
