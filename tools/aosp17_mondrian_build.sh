#!/usr/bin/env bash
# Real AOSP 17 build of aosp_mondrian (PE product of mondrian) on the project's ServerHive runner.
#
# STAGE=graph : repo sync + lunch + `m nothing` (full Soong/Kati analysis)
# STAGE=vendor: ... + `m vendorimage`
# STAGE=full  : ... + `m` (all images)
# STAGE=bacon : ... + `m bacon` (the PixelExperience release package)
# STAGE=recovery: ... + `m recoveryimage` (the PE recovery and its modules)
#
# The source tree lives next to the runner work directories so that it
# survives between jobs: the first sync downloads 100+ GB, later ones are
# incremental. The ServerHive job sandbox mounts / read-only, so host
# packages must be installed on the server beforehand (see the error text).
set -euo pipefail

STAGE="${STAGE:-graph}"
RELEASE="${RELEASE:-cp2a}"
VARIANT="${VARIANT:-userdebug}"
DO_SYNC="${DO_SYNC:-true}"
MANIFEST_URL="https://github.com/PixelExperience-Reborn/manifest"
MANIFEST_BRANCH="${MANIFEST_BRANCH:?branch of this manifest repository}"
MANIFEST_FILE="aosp17_pe_mondrian_build.xml"
REPO_LAUNCHER_URL="https://storage.googleapis.com/git-repo-downloads/repo"
REPO_LAUNCHER_SHA256="05f571deafd6ed6da0d20fa707dde29aa5624dbf35553d697a40dbdd4c8d178a"  # repo launcher 2.71
MIN_FREE_GB=500

: "${RUNNER_WORKSPACE:?run inside GitHub Actions}"
: "${RUNNER_TEMP:?run inside GitHub Actions}"
TREE="$(dirname "$RUNNER_WORKSPACE")/pe-aosp17-mondrian"
LOGS="$RUNNER_TEMP/aosp17-logs"
mkdir -p "$TREE/.bin" "$LOGS"
summary() { echo "$*" >> "${GITHUB_STEP_SUMMARY:-/dev/null}"; }

case "$STAGE" in graph|vendor|full|bacon|recovery) ;; *) echo "::error::unknown STAGE $STAGE"; exit 2;; esac
case "$VARIANT" in user|userdebug|eng) ;; *) echo "::error::unknown VARIANT $VARIANT"; exit 2;; esac
[[ "$RELEASE" =~ ^[a-z0-9_]+$ ]] || { echo "::error::invalid RELEASE $RELEASE"; exit 2; }

# Host prerequisites (AOSP "Establishing a build environment" package set).
missing=()
for tool in git git-lfs python3 curl zip unzip rsync flex bison gcc g++ make xsltproc xmllint fc-list; do
    command -v "$tool" >/dev/null 2>&1 || missing+=("$tool")
done
if ((${#missing[@]})); then
    echo "::error::missing host tools on ServerHive: ${missing[*]}"
    echo "Install once on the server (outside the job sandbox):"
    echo "  sudo apt-get install -y git-core gnupg flex bison build-essential zip unzip curl zlib1g-dev \\"
    echo "    libc6-dev-i386 x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc \\"
    echo "    fontconfig rsync python3 git-lfs"
    exit 1
fi
free_gb=$(df --output=avail -BG "$TREE" | tail -1 | tr -dc '0-9')
echo "free space for $TREE: ${free_gb} GB, CPUs: $(nproc), memory: $(free -g | awk '/^Mem:/{print $2}') GB"
if ((free_gb < MIN_FREE_GB)); then
    echo "::error::only ${free_gb} GB free next to the runner, at least ${MIN_FREE_GB} GB are required"
    exit 1
fi

# Pinned repo launcher.
if ! echo "$REPO_LAUNCHER_SHA256  $TREE/.bin/repo" | sha256sum -c --status 2>/dev/null; then
    curl -fsSL "$REPO_LAUNCHER_URL" -o "$TREE/.bin/repo.new"
    echo "$REPO_LAUNCHER_SHA256  $TREE/.bin/repo.new" | sha256sum -c --quiet
    mv "$TREE/.bin/repo.new" "$TREE/.bin/repo"
    chmod +x "$TREE/.bin/repo"
fi
export PATH="$TREE/.bin:$PATH"
git config --global user.name >/dev/null || git config --global user.name "PE-Reborn CI"
git config --global user.email >/dev/null || git config --global user.email "ci@pe-reborn.invalid"
git config --global color.ui false

cd "$TREE"
jobs=$(( $(nproc) > 32 ? 32 : $(nproc) ))
if [[ "$DO_SYNC" == "true" ]]; then
    lfs=()
    command -v git-lfs >/dev/null 2>&1 && lfs=(--git-lfs)
    repo init -u "$MANIFEST_URL" -b "$MANIFEST_BRANCH" -m "$MANIFEST_FILE" \
        --depth=1 --no-clone-bundle "${lfs[@]}" 2>&1 | tee "$LOGS/repo-init.log"
    # The tree belongs to CI only: discard local edits so every build matches the manifest.
    repo sync -c -j"$jobs" --no-tags --no-clone-bundle --optimized-fetch --retry-fetches=3 \
        --force-sync --force-remove-dirty 2>&1 | tee "$LOGS/repo-sync.log"
    # MindTheGapps keeps its APEX and APK files in Git LFS.
    git -C vendor/gapps lfs install --local >/dev/null
    git -C vendor/gapps lfs pull 2>&1 | tee "$LOGS/gapps-lfs.log"
fi
# Stock OS3.0.8.0 proprietary files: reproduced from the official OTA
# (only the vendor and odm partitions are downloaded) and hash-checked.
mkdir -p "$TREE/.cache"
python3 device/xiaomi/sm8450-common/tools/extract_proprietary.py \
    --work "$TREE/.cache" 2>&1 | tee "$LOGS/proprietary.log"
if [[ -d vendor/gapps ]] && git -C vendor/gapps lfs ls-files | grep -q ' - '; then
    echo "::error::vendor/gapps still has Git LFS pointers instead of files; run git lfs pull there"
    exit 1
fi
repo manifest -r -o "$LOGS/resolved-manifest.xml"
summary '<img src="https://github.com/PixelExperience-Reborn.png" width="72" align="left" alt="PixelExperience-Reborn">'
summary ""
summary "### PixelExperience-Reborn — aosp_mondrian, Android 17 ($STAGE)"
summary '<br clear="left">'
summary ""
summary "- manifest: \`$MANIFEST_BRANCH\` / \`$MANIFEST_FILE\`, projects: $(grep -c '<project' "$LOGS/resolved-manifest.xml")"

# Everything builds locally on ServerHive: no Google remote build execution
# (RBE, it needs Google credentials) and the classic ninja executor (AOSP 17
# defaults to Siso). The runner's environment must not change that: show
# what it sets, and drop BASH_ENV/ENV, which every child bash (soong_ui.bash
# among them) would source again, overriding the exports below.
for var in USE_RBE SOONG_NINJA ANDROID_BUILD_ENVIRONMENT_CONFIG BASH_ENV ENV; do
    echo "runner environment: $var=${!var-<unset>}"
done
unset BASH_ENV ENV ANDROID_BUILD_ENVIRONMENT_CONFIG
export USE_RBE=false
export SOONG_NINJA=ninja
# Builds of the organization's build server are the official ones.
export CUSTOM_BUILD_TYPE=OFFICIAL

set +u
# shellcheck disable=SC1091
source build/envsetup.sh > "$LOGS/envsetup.log" 2>&1
target="aosp_mondrian-$RELEASE-$VARIANT"
status=0
# lunch must run in this shell, not in a pipeline subshell: it exports
# TARGET_PRODUCT, TARGET_RELEASE and TARGET_BUILD_VARIANT for m.
lunch "$target" > "$LOGS/lunch.log" 2>&1 || status=$?
# The product configuration is printed once, by the build itself; lunch's
# copy stays in lunch.log unless lunch fails.
if ((status != 0)); then
    cat "$LOGS/lunch.log"
elif grep -q '^USE_RBE=true' "$LOGS/lunch.log"; then
    echo "::error::RBE is still enabled (USE_RBE=true) although this script disables it; see the runner environment above"
    status=1
else
    echo "lunch $target: TARGET_PRODUCT=$TARGET_PRODUCT TARGET_RELEASE=$TARGET_RELEASE TARGET_BUILD_VARIANT=$TARGET_BUILD_VARIANT"
fi
banner() { python3 vendor/aosp/tools/pe_banner.py "$@" || true; }
# GApps build (WITH_GMS := true, CUSTOM_GAPPS names the package) or Vanilla.
edition() { if [[ -n "$1" ]]; then echo "GApps ($1)"; else echo "Vanilla (no Google apps)"; fi; }
info=()
if ((status == 0)); then
    pe_version="$(get_build_var CUSTOM_VERSION)"
    info=("Device=$(get_build_var TARGET_DEVICE) (POCO F5 Pro / Redmi K60)"
          "Version=$pe_version"
          "Edition=$(edition "$(get_build_var CUSTOM_GAPPS)")"
          "Android=$(get_build_var PLATFORM_VERSION) (${TARGET_RELEASE:-$RELEASE})"
          "Android security patch=$(get_build_var PLATFORM_SECURITY_PATCH)"
          "Vendor security patch=$(get_build_var VENDOR_SECURITY_PATCH) (stock OS3.0.8.0 vendor)"
          "Maintainer=$(get_build_var CUSTOM_MAINTAINER)"
          "CPU=$(get_build_var TARGET_ARCH_VARIANT) / $(get_build_var TARGET_CPU_VARIANT)"
          "Build ID=$(get_build_var BUILD_ID)"
          "Build type=$(get_build_var TARGET_BUILD_VARIANT)"
          "Stage=$STAGE")
    # Leave out what the product does not define (pe_banner skips empty values).
    args=(); for item in "${info[@]}"; do if [[ -n "${item#*=}" ]]; then args+=(--info "$item"); fi; done
    banner --title "PixelExperience build started on ServerHive" "${args[@]}"
fi
start=$SECONDS
if ((status == 0)); then
    case "$STAGE" in
        graph)  m nothing 2>&1 | tee "$LOGS/build.log" || status=$? ;;
        vendor) m vendorimage 2>&1 | tee "$LOGS/build.log" || status=$? ;;
        full)   m 2>&1 | tee "$LOGS/build.log" || status=$? ;;
        bacon)  m bacon 2>&1 | tee "$LOGS/build.log" || status=$? ;;
        recovery) m recoveryimage 2>&1 | tee "$LOGS/build.log" || status=$? ;;
    esac
fi
elapsed=$((SECONDS - start))
# Kati names only the installed path of a duplicate install. Keep both
# rules of each one (their prerequisites name the Soong modules) in the logs.
if ((status != 0)) && grep -q "overriding commands for target" "$LOGS/build.log" 2>/dev/null; then
    grep -o "out/soong/installs-[^:]*:[0-9]*: error: overriding commands for target \`[^']*', previously defined at [^:]*:[0-9]*" "$LOGS/build.log" |
    while read -r line; do
        file="${line%%:*}"; first="${line#*:}"; first="${first%%:*}"; second="${line##*:}"
        for n in "$first" "$second"; do
            echo "== $file:$n"; sed -n "$((n > 3 ? n - 3 : 1)),$((n + 6))p" "$file"
        done
    done > "$LOGS/duplicate-installs.txt" 2>&1 || true
fi
duration="$(printf '%02d:%02d:%02d' $((elapsed / 3600)) $(((elapsed % 3600) / 60)) $((elapsed % 60)))"
package=""
if ((status == 0)) && [[ "$STAGE" == bacon ]]; then
    package="$(get_build_var PRODUCT_OUT)/$pe_version.zip"
    [[ -f "$package" ]] && info+=("Package=$(basename "$package")" "Size=$(du -h "$package" | cut -f1)"
                                  "SHA-256=$(sha256sum "$package" | cut -d' ' -f1)")
fi
info+=("Time=$duration")
args=(--status "$status"); for item in "${info[@]}"; do args+=(--info "$item"); done
banner --title "PixelExperience build finished" "${args[@]}"
set -u
for f in error.log soong.log verbose.log.gz build.trace.gz; do
    [[ -f "out/$f" ]] && cp "out/$f" "$LOGS/" || true
done
if ((${#info[@]})); then
    summary "| | |"
    summary "|---|---|"
    for item in "${info[@]}"; do if [[ -n "${item#*=}" ]]; then summary "| ${item%%=*} | \`${item#*=}\` |"; fi; done
    summary ""
fi
if ((status == 0)); then
    summary "- [PASS] \`lunch $target\` and the $STAGE stage in $duration"
else
    summary "- [FAIL] \`lunch $target\` / $STAGE stage, first errors:"
    summary '```'
    { grep -m40 -E "error:|FAILED:|Error|error " "$LOGS/build.log" "$LOGS/lunch.log" 2>/dev/null || true; } \
        | cut -c1-300 >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
    summary '```'
fi
exit "$status"
