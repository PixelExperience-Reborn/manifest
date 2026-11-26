# База PixelExperience-Reborn Android 17: что было в PE 14, что есть сейчас, что делаем

Проверены все слои базы, которые видит пользователь и которые связывают
её с устройством: фреймворк и SystemUI, Settings, лаунчер, сервисы
Google, `vendor/aosp`, `vendor/pixel-framework`, sepolicy и PE-приложения.
Эталон — официальный PE 14 (`fourteen`, сейчас ветки `seventeen` форков
организации; в архиве у PixelExperience). Его функции переносятся на
Android 17 заново, на современных API, без старого кода; то, что Android
17 уже умеет сам, не переносится.

## Сейчас в сборочном профиле Android 17

| Слой | Сейчас | В PE 14 было |
|---|---|---|
| `frameworks/base` (фреймворк и SystemUI) | AOSP 17 + одна правка PE (скруглённые toast) | ~209 изменений PE поверх AOSP 14 |
| `packages/apps/Settings` | чистый AOSP 17 | ~80 изменений PE |
| `vendor/pixel-framework` (SettingsGoogle, SystemUIGoogle) | не подключён | Pixel-интерфейс: Smartspace, Now Playing, Quick Tap, адаптивная зарядка, ресурсы SettingsGoogle (855 файлов) |
| `vendor/gms` (приложения Google и Pixel) | нет источника: `WITH_GMS=true` останавливает сборку | был на GitLab PE, сейчас недоступен |
| лаунчер | Launcher3QuickStep (AOSP); NexusLauncher — только с GMS | Pixel Launcher из `vendor/gms` |
| `vendor/aosp` | перенесён (каркас: брендинг, анимация, шрифты, RRO-оверлеи, OTA, порт генератора Soong) | ~72 изменения PE |
| `device/custom/sepolicy`, `hardware/custom/*`, `vendor/custom-preference` | не перенесены | sepolicy и HAL PE-функций, общие preference |
| PE-приложения: FaceUnlockService, TouchGestures, Aperture, devicesettings | не перенесены (Face Unlock требует `external/faceunlock` с GitLab — недоступен) | были |
| HAL Qualcomm SM8450 (`hardware_qcom-caf_sm8450_*`, `vendor_qcom_opensource_*`) | в профиль не входят; перенесены thermal, health, interfaces, telephony | были |
| `device/qcom/sepolicy_vndr/sm8450` | не перенесён | был |

Итог: сейчас база Android 17 — это AOSP 17 с каркасом `vendor/aosp`.
Чтобы она была PixelExperience, нужно перенести слой Google/Pixel и
функции PE.

## Функции PE 14 и решение для Android 17

### Сервисы Google и Pixel-интерфейс (основа PE)

| Функция PE 14 | Где | Решение |
|---|---|---|
| Приложения Google и Pixel (GmsCore, Play, Pixel Launcher, обои, темы, SettingsIntelligence, SetupWizard) | `vendor/gms` | нужен новый источник для Android 17 (см. «Решение по GMS») |
| PixelPropsUtils / PixelDropUtils (Play Integrity, Google Фото) | frameworks/base | переписать под Android 17; параметры обновляемые через оверлей |
| Разрешения приложений Google (privapp, default-permissions) | frameworks/base, vendor/gms | в Android 17 — XML в самом GMS-пакете; патчи фреймворка не нужны |
| SettingsGoogle и SystemUIGoogle (Smartspace, Now Playing, Quick Tap, адаптивная зарядка, AmbientIndication) | `vendor/pixel-framework` | перенос на Android 17 после GMS: зависит от внутренних API SystemUI/Settings |
| RRO-оверлеи Pixel, шрифты, рингтоны, обои, анимация загрузки | `vendor/aosp` | есть в порте; сверить с Android 17 |

### Функции, нужные mondrian

| Функция PE 14 | Где | Решение |
|---|---|---|
| UDFPS: затемнение/подсветка, режим дисплея, иконка при регистрации | SystemUI, frameworks | перенести; в mondrian отпечаток под экраном с LHBM (`mondrian_fod.c` в ядре) |
| Частота обновления: выбор пиковой и минимальной, 60 Гц в энергосбережении | Settings, frameworks | перенести; в настройках 60/90/120 Гц |
| Жесты на выключенном экране (двойной тап, одиночный тап UDFPS) | SystemUI doze, TouchGestures | реализовать через Xiaomi touch HAL (`android_hardware_xiaomi`) |
| Высокая частота опроса тача | Settings, frameworks | через Xiaomi touch HAL |
| Управление зарядкой (лимит, обход) | Settings, Health | через наш health-порт (`healthd-ext`) |
| Кнопки громкости: курсор, скриншот | frameworks | перенести то, что нужно для устройства без аппаратных кнопок навигации |
| Плитка NFC по умолчанию | SystemUI | оверлей |
| Камеры aux для сторонних приложений | frameworks camera | перенести (Aperture/сторонние камеры видят все 4 камеры) |

### Не переносится (устарело или не нужно mondrian)

Moto Mods, DisplayPort-аудио и внешние дисплеи, подсветка аппаратных
кнопок, перестановка ёмкостных кнопок, Android Beam, исправления
Android 7–13, сделанные в Android 17 самим AOSP, старые HIDL-интерфейсы
(заменены AIDL).

## Что дерево устройства даёт базе

| База ждёт | Дерево mondrian |
|---|---|
| продукт `aosp_mondrian`, наследование `vendor/aosp/config/common_full_phone.mk`, `TARGET_BOOT_ANIMATION_RES` | есть |
| `PRODUCT_GMS_CLIENTID_BASE` | есть (`android-xiaomi`) |
| оверлеи фреймворка: частоты 60/90/120, яркость, вырез, скругления, power_profile, UDFPS (позиция, размер, цвет), автояркость | нужно (из стока и DT) |
| sepolicy устройства поверх `device/qcom/sepolicy_vndr/sm8450` | нужно |
| VINTF-манифест, совместимый с `vendor/aosp/config/device_framework_matrix.xml` | нужно |
| HAL Xiaomi (отпечаток, тач, ИК) для функций PE | нужно |
| Health с управлением зарядкой | нужно |

## Порядок работы

1. Дерево устройства и связь с базой: оверлеи, sepolicy, VINTF, init,
   HAL — по `device/xiaomi/mondrian/docs/DEVICE_TREE_COMPLETENESS.md`.
2. Перенос HAL Qualcomm SM8450 и sepolicy на Android 17 (в профиль сборки).
3. GMS для Android 17 и PixelPropsUtils.
4. Функции PE для mondrian в frameworks/base и Settings (UDFPS,
   частоты, жесты, зарядка).
5. `vendor/pixel-framework` (SettingsGoogle/SystemUIGoogle) на Android 17.

## Решение по GMS

Нужен источник приложений Google для Android 17. Варианты:

- **Свой `vendor_gms` из образа Pixel для Android 17**, как делал PE:
  полный набор, включая Pixel Launcher, обои, темы. Требует отдельного
  закрытого репозитория (приложения Google нельзя распространять
  публично).
- **MindTheGapps для Android 17**: открытый, поддерживается, но
  минимальный набор (без Pixel Launcher и Pixel-приложений).
