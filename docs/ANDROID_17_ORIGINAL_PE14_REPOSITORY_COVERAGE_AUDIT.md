# Original PixelExperience 14 vs PE-Reborn AOSP17 — аудит полноты форков

**Дата проверки:** 2026-11-08. **Исходник:** [PixelExperience/manifest](https://github.com/PixelExperience/manifest/tree/136aee696422bda841eb5c6a3c9279bbb6bbef02), pinned commit `136aee696422bda841eb5c6a3c9279bbb6bbef02` (2024-03-06).
**Сопоставление:** [матрица 135 PE-Reborn](ANDROID_17_135_REPOSITORY_PORT_MATRIX.md) на ветке `port/a17-aosp17-manifest-20261102`; официальный [`aosp17_reference.xml`](../aosp17_reference.xml) закреплён на Android `android-17.0.0_r1`.

**Полный аудит публичной GitHub-организации:** [373 оригинальных репозитория против 135 форков PE-Reborn, классификация отсутствующих 238](ANDROID_17_ORIGINAL_PE_GITHUB_373_REPOSITORY_GAP_AUDIT.md). Ни одно из этих чисел не является оценкой готовности прошивки.

## Уточнение границ прежнего аудита

- **185** объявлений project в трёх сниппетах исходной PE14, непосредственно включённых оригинальным `default.xml`: 71 `pixel.xml`, 29 `pixel-extras.xml`, 85 `pixel-caf.xml`.
- **135** из этих 185 были форкнуты в PixelExperience-Reborn и учтены нашей первоначальной таблицей (64 / 24 / 47).
- **50** исходных PE14 проектов **не входят** в эту таблицу: 7 / 5 / 38 соответственно. Это пробел *в полном историческом перечне*, но не доказательство отсутствия обязательной зависимости AOSP17.
- **5** дополнительных OEM проектов объявлены в `pixel-extras-dependencies.xml`; в оригинальном PE14 `default.xml` этот файл **не включён**, поэтому считать их обязательными активными проектами было бы ошибкой.
- Итого в четырёх исторических сниппетах **190** объявлений, из них 185 в основных. Состояние `135/135` означает закрытие **выбранного набора форков**, а не полный аудит всех репозиториев оригинального GitHub-аккаунта.

## Отдельная проверка лаунчера

1. В [PixelExperience/manifest Android14](https://github.com/PixelExperience/manifest/blob/136aee696422bda841eb5c6a3c9279bbb6bbef02/default.xml) путь `packages/apps/Launcher3` имел владельца `platform/packages/apps/Launcher3` (Google AOSP). PE-сниппеты **не форкали этот путь**.
2. В [PixelExperience/packages_apps_Launcher3](https://github.com/PixelExperience/packages_apps_Launcher3) присутствует **старый архивный Launcher3** с единственной веткой `oreo-mr1`, commit `637ad2e7aaf948390516edac57db715faf44e9ce` (2018-10-14). Веток `fourteen` или `thirteen` нет. Это **не** рабочий исходник PE14 и не причина создавать его форк для Android17.
3. В [исходном PE14 vendor_aosp/config/common.mk](https://github.com/PixelExperience/vendor_aosp/blob/5002afb5177d57e65248d1333312346b689a8802/config/common.mk) `NexusLauncherRelease` и `SystemUIGoogle` перечислены **в `PRODUCT_DEXPREOPT_SPEED_APPS`, а не в `PRODUCT_PACKAGES`**; файл также наследует `vendor/gms/products/gms.mk`. [`rro_overlays.mk`](https://github.com/PixelExperience/vendor_aosp/blob/5002afb5177d57e65248d1333312346b689a8802/config/rro_overlays.mk) запрашивал `PixelLauncherCustomOverlay`. Значит, исходный PE14 продукт **предусматривал Google Pixel Launcher для dexpreopt и отдельную GMS-зависимость**, но источник APK и фактическое добавление `NexusLauncherRelease` в `PRODUCT_PACKAGES` без проверки исторического `vendor/gms` **не установлены**. Своего AOSP14 Launcher3-форка в основном PE14 manifest не было.
4. У PE-Reborn есть [vendor_aosp](https://github.com/PixelExperience-Reborn/vendor_aosp) (исторический `seventeen` совпадает с PE14 commit `5002afb5177d57e65248d1333312346b689a8802`). Но `vendor/gms` в оригинале шёл из **PixelExperience GitLab**; его лицензированный источник не подтверждён. [Адаптационный PR](https://github.com/PixelExperience-Reborn/vendor_aosp/pull/1) уже ограждает GMS флагом `WITH_GMS=true`. Без-GMS AOSP17 launcher должен выбираться и собираться отдельно, после анализа product modules.
5. Текущий AOSP17 reference содержит оригинальный `packages/apps/Launcher3`, но наличие Git-проекта **не доказывает**, что модуль домашнего экрана установлен выбранным продуктом или собран.

## Отсутствующие 50 исторических PE14 записей и 5 необязательных OEM

**Таблица фиксирует пропуск из 135 выбранных форков, а не требование немедленно создавать все форки.** Никакие старые HAL, vendor/gms, FM Radio или аппаратные деревья автоматически подключать нельзя.

### snippets/pixel.xml — основной набор — 7 вне таблицы

| Путь | Репозиторий оригинальной PE | AOSP17 путь | Решение |
|---|---|---|---|
| `device/google/cuttlefish` | `device_google_cuttlefish` | Да, Google | Официальный AOSP17 уже содержит этот путь; старый форк не требуется для платформы |
| `device/google/contexthub` | `device_google_contexthub` | Да, Google | Официальный AOSP17 уже содержит этот путь; старый форк не требуется для платформы |
| `hardware/qcom/sm7250/display` | `hardware_qcom_sm7250_display` | Нет | Исторический QCOM sm7250/sm8150; не включать в чистую платформу |
| `hardware/qcom/sm7250/media` | `hardware_qcom_sm7250_media` | Нет | Исторический QCOM sm7250/sm8150; не включать в чистую платформу |
| `hardware/qcom/sm8150/data/ipacfg-mgr` | `hardware_qcom_sm8150_data_ipacfg-mgr` | Нет | Исторический QCOM sm7250/sm8150; не включать в чистую платформу |
| `hardware/qcom/sm8150/display` | `hardware_qcom_sm8150_display` | Нет | Исторический QCOM sm7250/sm8150; не включать в чистую платформу |
| `hardware/qcom/sm8150/media` | `hardware_qcom_sm8150_media` | Нет | Исторический QCOM sm7250/sm8150; не включать в чистую платформу |

### snippets/pixel-extras.xml — дополнительные компоненты — 5 вне таблицы

| Путь | Репозиторий оригинальной PE | AOSP17 путь | Решение |
|---|---|---|---|
| `external/faceunlock` | `external_faceunlock` | Нет | GitLab: необязательный Face Unlock; отложить |
| `vendor/gms` | `vendor_gms` | Нет | GitLab: GMS; NexusLauncherRelease упомянут в dexpreopt, но источник APK не доказан; лицензия и Android17 отдельно |
| `hardware/qcom/sdm845/data/ipacfg-mgr` | `hardware_qcom_sdm845_data_ipacfg-mgr` | Нет | Исторические Snapdragon 845 HAL; не переносить как платформенную основу |
| `hardware/qcom/sdm845/display` | `hardware_qcom_sdm845_display` | Нет | Исторические Snapdragon 845 HAL; не переносить как платформенную основу |
| `hardware/qcom/sdm845/media` | `hardware_qcom_sdm845_media` | Нет | Исторические Snapdragon 845 HAL; не переносить как платформенную основу |

### snippets/pixel-caf.xml — Qualcomm CAF — 38 вне таблицы

| Путь | Репозиторий оригинальной PE | AOSP17 путь | Решение |
|---|---|---|---|
| `device/qcom/sepolicy-legacy-um` | `device_qcom_sepolicy-legacy-um` | Нет | Старые или иные Qualcomm SEPolicy; не импортировать в чистую AOSP17 |
| `device/qcom/sepolicy_vndr/legacy-um` | `device_qcom_sepolicy_vndr_legacy-um` | Нет | Старые или иные Qualcomm SEPolicy; не импортировать в чистую AOSP17 |
| `device/qcom/sepolicy_vndr/sm8550` | `device_qcom_sepolicy_vndr_sm8550` | Нет | Старые или иные Qualcomm SEPolicy; не импортировать в чистую AOSP17 |
| `hardware/qcom-caf/msm8953/audio` | `hardware_qcom-caf_msm8953_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8953/display` | `hardware_qcom-caf_msm8953_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8953/media` | `hardware_qcom-caf_msm8953_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8996/audio` | `hardware_qcom-caf_msm8996_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8996/display` | `hardware_qcom-caf_msm8996_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8996/media` | `hardware_qcom-caf_msm8996_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8998/audio` | `hardware_qcom-caf_msm8998_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8998/display` | `hardware_qcom-caf_msm8998_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/msm8998/media` | `hardware_qcom-caf_msm8998_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sdm660/audio` | `hardware_qcom-caf_sdm660_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sdm660/display` | `hardware_qcom-caf_sdm660_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sdm660/media` | `hardware_qcom-caf_sdm660_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sdm845/audio` | `hardware_qcom-caf_sdm845_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sdm845/display` | `hardware_qcom-caf_sdm845_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sdm845/media` | `hardware_qcom-caf_sdm845_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8150/audio` | `hardware_qcom-caf_sm8150_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8150/display` | `hardware_qcom-caf_sm8150_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8150/media` | `hardware_qcom-caf_sm8150_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8250/audio` | `hardware_qcom-caf_sm8250_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8250/display` | `hardware_qcom-caf_sm8250_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8250/media` | `hardware_qcom-caf_sm8250_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/bengal/audio` | `hardware_qcom-caf_bengal_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/bengal/display` | `hardware_qcom-caf_bengal_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/bengal/media` | `hardware_qcom-caf_bengal_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8350/audio` | `hardware_qcom-caf_sm8350_audio` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8350/display` | `hardware_qcom-caf_sm8350_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8350/media` | `hardware_qcom-caf_sm8350_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8550/audio/agm` | `hardware_qcom-caf_sm8550_audio_agm` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8550/audio/pal` | `hardware_qcom-caf_sm8550_audio_pal` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8550/audio/primary-hal` | `hardware_qcom-caf_sm8550_audio_primary-hal` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8550/data-ipa-cfg-mgr` | `hardware_qcom-caf_sm8550_data-ipa-cfg-mgr` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8550/dataipa` | `hardware_qcom-caf_sm8550_dataipa` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8550/display` | `hardware_qcom-caf_sm8550_display` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `hardware/qcom-caf/sm8550/media` | `hardware_qcom-caf_sm8550_media` | Нет | HAL для другого Qualcomm семейства; исключён из текущего платформенного этапа |
| `vendor/qcom/opensource/data-ipa-cfg-mgr-legacy-um` | `vendor_qcom_opensource_data-ipa-cfg-mgr-legacy-um` | Нет | Старый Qualcomm legacy-um; не импортировать без потребителя |

### snippets/pixel-extras-dependencies.xml — НЕ включён в default — 5 вне таблицы

| Путь | Репозиторий оригинальной PE | AOSP17 путь | Решение |
|---|---|---|---|
| `hardware/motorola` | `hardware_motorola` | Нет | Дополнительная OEM-библиотека другого производителя; для этой базы не нужна |
| `hardware/oneplus` | `hardware_oneplus` | Нет | Дополнительная OEM-библиотека другого производителя; для этой базы не нужна |
| `hardware/oplus` | `hardware_oplus` | Нет | Дополнительная OEM-библиотека другого производителя; для этой базы не нужна |
| `hardware/samsung` | `hardware_samsung` | Нет | Дополнительная OEM-библиотека другого производителя; для этой базы не нужна |
| `hardware/xiaomi` | `hardware_xiaomi` | Нет | Дополнительная OEM-библиотека; только последующая аппаратная квалификация |

## Практический приоритет после проверки списка

1. **P0 — корректное product/Launcher3/GMS разделение:** убедиться, что чистая AOSP17 собирает работоспособный HOME модуль без проприетарного `vendor/gms`; сохранить возможность отдельно проверенного GMS-варианта позднее, без автоматической загрузки старых бинарников.
2. **P0 — проверка рабочего manifest и сборки Soong:** исторический реестр репозиториев не заменяет `repo manifest`, реальный `repo sync` и запуск компиляции.
3. **Не включать** 34 чужих Qualcomm CAF audio/display/media проекта, старые QSSI/IPA/SDM845/sm8150 платформы только ради совпадения с PE14. Решение — по конкретному API/Soong потребителю, а не по имени чипсета.
4. **OEM hardware/xiaomi** из невключённого `pixel-extras-dependencies.xml` не является деревом устройства и **не требуется** для чистой платформенной базы. Его очередь наступит только при отдельной аппаратной квалификации, после окончания платформы.
5. **Не требуется** восстанавливать `packages_apps_Launcher3` из Android8 или старые приложения из других исторических веток (Updates, Snap, CarrierConfig, FMRadio и др.), которых нет в PE14 default. Ранее согласованное исключение FM Radio сохраняется.

## Воспроизводимость и ограничения

- Скрипт [`tools/audit_original_pe_fourteen_coverage.py`](../tools/audit_original_pe_fourteen_coverage.py) сравнивает SHA-pinned оригинальный PE14 manifest с нашей таблицей, проверяет все пути, имена, 185/135/50 и пять OEM и контрольный AOSP17 Launcher3.
- Исторический `PixelExperience/manifest` проверяется только чтением XML, без выполнения чужих сборочных скриптов, загрузки vendor blobs или LineageOS device trees.
- Это **manifest coverage audit**, а не проверка всех GitHub-репозиториев, существовавших за 2018–2024 годы вне PE14 manifest; и не свидетельство реальной компиляции Android17, Soong, GMS или Launcher3.
