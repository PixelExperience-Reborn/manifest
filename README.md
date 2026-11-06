# PixelExperience-Reborn — Android 17 (source staging)

This branch is an **independent AOSP Android 17 bring-up**, based on the immutable
official `android-17.0.0_r1` source graph. It is **not** a completed ROM,
a supported device build, or an OTA/recovery release.

**Source branch:** `port/a17-aosp17-manifest-20261102`. The historical
`seventeen` PixelExperience branches and original PE snippets are kept for
review; most are **not** Android 17-compatible and must not be imported blindly.

## Source-only checkout

Use the reviewed Android 17 manifest, not the old PixelExperience Android 14
`fourteen` branch:

```bash
mkdir -p pe-reborn-a17 && cd pe-reborn-a17
repo init -u https://github.com/PixelExperience-Reborn/manifest \
  -b port/a17-aosp17-manifest-20261102 \
  -m default.xml --no-clone-bundle
repo manifest -o resolved.xml
```

The working `default.xml` is an **include-only entrypoint** to
`aosp17_pe_p2_kernel_configs.xml` (the last audited, immutable-source-pin
profile). It resolves the official AOSP17 baseline and reviewed PE source
forks **without auto-loading unported CAF HALs, historical PE app overrides,
or Xiaomi device trees**.

To examine one earlier compatibility step, use its explicit profile:

```bash
repo init -u https://github.com/PixelExperience-Reborn/manifest \
  -b port/a17-aosp17-manifest-20261102 \
  -m aosp17_pe_p2_ril.xml --no-clone-bundle
repo manifest -o resolved.xml
```

Before running any full sync on a properly provisioned Linux build machine,
first review the source profile, dependencies, required disk space and
applicable AOSP proprietary-component restrictions. If needed for validation,
use ordinary `repo sync -c -j4 --no-clone-bundle`; **do not** use
`--force-sync` against an existing development checkout without a backup.

## Verification (source graph, not device)

From this manifest repository:

```bash
python3 tools/validate_aosp17_base_profiles.py
python3 tools/validate_135_repository_matrix.py
```

These are offline structural tests, not a replacement for official `repo`,
full `repo sync`, Soong/Make, CTS/VTS, enforcing SELinux, VINTF,
device boot or radio/camera/graphics validation. The 25 current staged
profiles deliberately exclude mondrian device and proprietary vendor sources;
there is **no valid `lunch` target or ROM build command advertised here**.

The upstream Android 17 reference is `aosp17_reference.xml`. The old
`snippets/pixel*.xml` files are retained as a PE feature and repository
migration inventory; they must not be automatically applied to the default
Android 17 graph.

## Technical records

- [AOSP17 staged source profiles](docs/ANDROID_17_BOOTSTRAP_PROFILES.md)
- [135-repository porting matrix](docs/ANDROID_17_135_REPOSITORY_PORT_MATRIX.md)
- [Current manifest entrypoint/ownership audit](docs/ANDROID_17_MANIFEST_ENTRYPOINT_AUDIT.md)
- [Mondrian native device bring-up plan](docs/ANDROID_17_MONDRIAN_NATIVE_DEVICE_TREE_PLAN.md)

**Change policy:** maintain original Git histories, isolate every AOSP17 port,
review single source owners and conflicts, keep incomplete sources outside the
default graph, and require real build/boot tests before declaring readiness.
