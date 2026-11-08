# SM8475 / mondrian: независимая PE-Reborn AOSP17 — сверка с официальной LineageOS 24.0

**Состояние на 2026-11-08:** архитектурная сверка **только для чтения**. Официальная LineageOS и существующие деревья LF52406 **не являются исходной базой, зависимостью, CI-источником или объектом копирования** для новой PE-Reborn. Здесь не создавались device/vendor/kernel репозитории, не модифицировался AOSP17 default manifest и не собирался ROM.

## Подтверждённая аппаратная идентичность

- Устройство: **POCO F5 Pro / Redmi K60**, codename **mondrian**, настоящий SoC **Qualcomm SM8475** (Snapdragon 8+ Gen 1).
- Официальная LineageOS wiki сообщает **LineageOS 24.0 / Android 17**, kernel family **5.10**: https://lineageos.github.io/lineage_wiki/devices/mondrian/variant2/ . Различные региональные варианты требуют собственной проверки прошивки и SKU.
- Название исходной общей конфигурации **sm8450-common** и Bootloader board name **taro** в официальном BoardConfig — это **унаследованные названия Qualcomm BSP/общего семейства исходников**. Они не отменяют факт, что целевая аппаратная платформа mondrian использует **SM8475**. Не делать слепую замену исходных путей на `sm8475-common` без подтверждённых совместимых зависимостей, но не объявлять устройство «SM8450».
- Официальный installer LineageOS 24.0 требует соответствующую установленную **stock firmware Android 15**. Это условие именно их готового ROM/образов, а не автоматически определённая прошивка для будущей независимой PE-Reborn. Подтверждение vendor API/firmware для PE требуется отдельной проверкой реального OEM образа.

## Исходники официальной LineageOS — проверенный pinned reference (НЕ upstream PE)

Проверена ветка `lineage-24.0` по следующим ревизиям:

| Роль | Официальный GitHub репозиторий | Commit 2026-11-08 |
| --- | --- | --- |
| Фактическое устройство | [android_device_xiaomi_mondrian](https://github.com/LineageOS/android_device_xiaomi_mondrian) | `3c3de2c2938ed2ad2e2c49d9ed346b4d08b1d493` |
| Общие Qualcomm/Xiaomi device определения | [android_device_xiaomi_sm8450-common](https://github.com/LineageOS/android_device_xiaomi_sm8450-common) | `67a471734b636f65605102d2e7cf449b7e861d57` |
| Kernel | [android_kernel_xiaomi_sm8450](https://github.com/LineageOS/android_kernel_xiaomi_sm8450) | `eff4b40407a1b6f1b1ab84554cbb540bcb495175` |
| External kernel modules | [android_kernel_xiaomi_sm8450-modules](https://github.com/LineageOS/android_kernel_xiaomi_sm8450-modules) | `3b30ba7df6608c97c0ba2d55d679a6b5987c4c66` |
| Device tree sources / DTBO input | [android_kernel_xiaomi_sm8450-devicetrees](https://github.com/LineageOS/android_kernel_xiaomi_sm8450-devicetrees) | `2e649a7f3e762903eedad43d8256b91e28b512d8` |
| Общие Xiaomi hardware компоненты | [android_hardware_xiaomi](https://github.com/LineageOS/android_hardware_xiaomi) | `6c12251713d74a01636482c9ffbdd9943addbfbf` |

`LineageOS/android_vendor_xiaomi_sm8450-common` **не существует как публичный репозиторий организации**: их `proprietary-files.txt` + `extract-files.py` генерируют отдельные **vendor** каталоги у сборщика из внешних firmware/blob sources. Это всё равно требует для PE независимого, законного и воспроизводимого способа получения vendor бинарников, а не фиктивного пустого репозитория.

Твоя существующая реализация для сравнения структуры, **не для импорта кода**:

- [LF52406/mondrian_android_device_xiaomi_mondrian](https://github.com/LF52406/mondrian_android_device_xiaomi_mondrian), HEAD `e24166bcefa48220422d82044be89cb03affd390`.
- [LF52406/mondrian_android_device_xiaomi_sm8450-common](https://github.com/LF52406/mondrian_android_device_xiaomi_sm8450-common), HEAD `6e0022f5100e09ac97980095b6ed8528f4ff823f`.
- [LF52406/proprietary_vendor_xiaomi_sm8450-common](https://github.com/LF52406/proprietary_vendor_xiaomi_sm8450-common), HEAD `1d5437c0f615b45ad2315d78d9efa7eb78247d32`.
- Его kernel/moduletrees/devicetrees также уже разделены на три отдельных репозитория, как у официальной LineageOS. Эти факты служат подтверждением **структуры**, но не дают право переносить текущие файлы/патчи в чистую независимую PE-Reborn.

## Что именно проверено в структуре

1. **mondrian/device** — `AndroidProducts.mk`, `BoardConfig.mk`, `device.mk`, `lineage_mondrian.mk`, `lineage.dependencies`, `audio/`, `overlay/`, `properties/`, `proprietary-files.txt` и `proprietary-firmware.txt`. Официальный `lineage.dependencies` указывает **только** `android_device_xiaomi_sm8450-common` в `device/xiaomi/sm8450-common`.
2. **sm8450-common** — `BoardConfigCommon.mk`, `common.mk`, `rootdir/`, `sepolicy/`, `vintf/`, `modules.list.second_stage`, `modules.list.vendor_dlkm`, `wlan/`, `audio/`, `media/`, `sensors/`, `qcril-database/`, `configs/` и извлечение общих vendor blobs. `lineage.dependencies` указывает `hardware/xiaomi` и три отдельных kernel/source репозитория, именно по checkout путям `kernel/xiaomi/sm8450`, `kernel/xiaomi/sm8450-modules` и `kernel/xiaomi/sm8450-devicetrees`.
3. **Разделение vendor:** официальный `mondrian/device.mk` наследует `vendor/xiaomi/mondrian/mondrian-vendor.mk`, а `sm8450-common/common.mk` — `vendor/xiaomi/sm8450-common/sm8450-common-vendor.mk`. Оба набора необходимы **при соответствующей выбранной blob-конфигурации**, не могут заменять друг друга. Их актуальный источник/распространяемость и версии проверить по реальной OEM firmware.
4. **Kernel + modules + DT:** official `BoardConfigCommon.mk` ссылается на три разных checkout; не объединять их наобум. Kernel 5.10, список первых/вторых/дополнительных модулей и DT должны быть совместимы с реальным BSP, загрузчиком и vendor ABI. Смена на более новую версию kernel без совместимой ветки/драйверов/модулей недопустима.
5. **Boot/product:** официальный common описывает A/B OTA, dynamic `super`, `boot`/`recovery`/`vendor_boot`/`dtbo`/`vendor_dlkm`, boot header v4, recovery fstab и vendor ramdisk, а product использует `full_base_telephony.mk`, виртуальный A/B и аппаратные HAL. Это **сведения для последующего сравнения**, а не параметры, которые можно без проверки вставить в новый BoardConfig. `init_boot` не был обнаружен в указанном перечне OTA, и нельзя его ни автоматически добавлять, ни автоматически исключать без OEM-разметки.
6. **Android 17 интерфейсы:** common VINTF имеет как современные, так и унаследованные Qualcomm HAL; исходная распаковка общих blobs объявляет зависимости от `vendor/qcom/opensource/commonsys/display`, `commonsys-intf/display` и `dataservices`. Эти **старые конкретные исходники уже исключены из чистой PE-Reborn AOSP17 до независимой проверки**. Их наличие в LineageOS не делает их совместимыми с PE-Reborn manifest/Soong. Не копировать старые HIDL/compat шима или пропускать AIDL/FCM/SELinux проверку.
7. **Чистота:** в твоём личном устройстве по сравнению с official появились `display-settings/`, `haptic-settings/`, `sepolicy/`, `thermal/`; в личном common — `camera/`, `parts/`, `overlay-lineage/`. Они **не нужны для первой PE-Reborn независимой tree схемы** и не включаются автоматически. Некоторые исходные official `overlay/` также используют Lineage namespaces; нужны PE/AOSP-специфичные альтернативы или отсутствие оверлея, а не копирование названий.

## Рекомендуемые имена НАШИХ новых самостоятельных репозиториев

Сохраняем понятную **структуру и checkout пути** официального работающего Android17 дерева. При этом каждый новый репозиторий — новая история разработки PE-Reborn, а не форк LineageOS. Имена источников соответствуют твоим существующим репозиториям/официальной архитектуре:

| Имя нового репозитория в `PixelExperience-Reborn/` | Локальный путь | Назначение |
| --- | --- | --- |
| `android_device_xiaomi_mondrian` | `device/xiaomi/mondrian` | Только отличия mondrian, собственный `pe_mondrian` product |
| `android_device_xiaomi_sm8450-common` | `device/xiaomi/sm8450-common` | Общая аппаратная конфигурация проверенного семейства |
| `android_kernel_xiaomi_sm8450` | `kernel/xiaomi/sm8450` | Проверенное kernel дерево; ветка для mondrian SM8475 |
| `android_kernel_xiaomi_sm8450-modules` | `kernel/xiaomi/sm8450-modules` | Соответствующие external kernel modules |
| `android_kernel_xiaomi_sm8450-devicetrees` | `kernel/xiaomi/sm8450-devicetrees` | Совместимые DT/DTBO исходники |
| `proprietary_vendor_xiaomi_sm8450-common` | `vendor/xiaomi/sm8450-common` | Воспроизводимый общий vendor набор |
| `proprietary_vendor_xiaomi_mondrian` | `vendor/xiaomi/mondrian` | Только device-specific vendor набор |
| `android_hardware_xiaomi` | `hardware/xiaomi` | Только подтверждённые Xiaomi hardware/build модули |

**Обоснование восьми вместо трёх:** официальный `lineage.dependencies` подтверждает отдельный common, Kernel, module и DT источники; два vendor пути прямо наследуются в `device.mk` / `common.mk`; `hardware/xiaomi` является реальной прямой аппаратной зависимостью, а не лишним репозиторием. **Названия можно сохранить**, несмотря на маркировку `sm8450`, поскольку **конкретный target остаётся SM8475/mondrian**. Изменять их для красоты или механически на SM8475 опасно для соответствия Qualcomm BSP; при реальной реализации нужно доказать Soong/API ownership каждого пути.

В `PixelExperience-Reborn` проверены отсутствующими `android_device_xiaomi_mondrian`, `android_device_xiaomi_sm8450-common`, `android_kernel_xiaomi_sm8450`, `proprietary_vendor_xiaomi_mondrian`, `proprietary_vendor_xiaomi_sm8450-common`, `android_hardware_xiaomi` — ни один из этих проектов не создан в рамках данного аудита.

## Независимая реализация и порядок работ

- **R0: архитектурное согласование:** назначить независимые репозитории и checkout пути, не использовать `lineage.dependencies` как штатное управление зависимостями: в PE-Reborn — отдельный **неактивный** manifest профиль под mondrian со строгими SHA.
- **R1: новые репозитории:** пустые минимальные LICENSE/README/.gitignore/CI, без LineageOS Git history. Для kernel, модулей и DT при переносе *разрешённого исходного GPL/Qualcomm/Xiaomi кода* сохранять исходные лицензии, авторские права и юридическое происхождение. «Независимая разработка» не означает переписывать лицензированный Linux kernel заново, но нельзя **бездумно клонировать готовое Lineage device tree**.
- **R2: OEM hardware inventory:** собрать официальные partition tables/boot images, `ro.boot.*`, `ro.board.platform`, `uname -r`, exact kernel config, DT, module order, base firmware hashes, VINTF/FCM, ELF NEEDED ABI, system/vendor API from **реального стокового mondrian**. Для Lineage source конфигураций это только сравнительные гипотезы.
- **R3: native PE device/product skeleton:** минимальные `AndroidProducts.mk`, `pe_mondrian.mk`, `BoardConfig.mk`, `device.mk`, отдельные common/config модули. Наследовать платформу PE-Reborn + Google AOSP17, **не** `vendor/lineage/config/common_full_phone.mk`, `hardware/qcom-caf/common/common.mk` или неподтверждённые старые vendor frameworks.
- **R4: dependency/ABI closure:** пересмотреть каждый Qualcomm audio/display/media/camera, RMNET, radio, IMS, sensors, NFC, fingerprint, WFD/KeyMint, native/wireless HAL. Реальный Soong module provider, partition, AIDL/HIDL, kernel KMI и vendor ABI обязателен; никакого массового копирования Lineage `PRODUCT_PACKAGES` или overlay.
- **R5: build qualification:** только теперь подставить immutable SHAs в экспериментальный `aosp17_pe_mondrian.xml`, выполнить настоящий Google repo sync, Soong bootstrap, Android17 product lunch, kernel/modules/DT compilation, изображения, VINTF/SELinux проверки, boot logs и тесты.
- **R6: GMS:** сначала без-GMS с официальным AOSP17 Launcher3QuickStep; легально лицензированный Google сервисный продукт — только отдельная согласованная версия и после квалификации HOME/Quickstep.

**Не делать:** FM Radio, дополнительные UI и device settings, экспериментальные ядра/изменения частот, фальшивые VINTF HAL, отключение SELinux/AVB, копирование дат/Android15 fingerprints и boot/partition sizes без OEM проверок.

**Не выполнено:** создание восьми новых GitHub репозиториев, интеграция устройства, полная компиляция/загрузка Android17. Здесь завершена только официальная структурная и зависимостная сверка.
