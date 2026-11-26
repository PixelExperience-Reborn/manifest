#!/usr/bin/env bash
# Real AOSP 17 build of aosp_mondrian (PE product of mondrian) on the project's ServerHive runner.
#
# STAGE=graph : repo sync + lunch + `m nothing` (full Soong/Kati analysis)
# STAGE=vendor: ... + `m vendorimage`
# STAGE=full  : ... + `m` (all images)
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

case "$STAGE" in graph|vendor|full) ;; *) echo "::error::unknown STAGE $STAGE"; exit 2;; esac
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
if [[ -d vendor/gapps ]] && git -C vendor/gapps lfs ls-files | grep -q ' - '; then
    echo "::error::vendor/gapps still has Git LFS pointers instead of files; run git lfs pull there"
    exit 1
fi
repo manifest -r -o "$LOGS/resolved-manifest.xml"
summary "### aosp_mondrian AOSP 17 build ($STAGE)"
summary "- manifest: \`$MANIFEST_BRANCH\` / \`$MANIFEST_FILE\`, projects: $(grep -c '<project' "$LOGS/resolved-manifest.xml")"

# No Google remote build execution (RBE) here: everything builds locally
# on ServerHive. AOSP enables RBE when USE_RBE is not explicitly false.
export USE_RBE=false

set +u
# shellcheck disable=SC1091
source build/envsetup.sh > "$LOGS/envsetup.log" 2>&1
target="aosp_mondrian-$RELEASE-$VARIANT"
status=0
# lunch must run in this shell, not in a pipeline subshell: it exports
# TARGET_PRODUCT, TARGET_RELEASE and TARGET_BUILD_VARIANT for m.
lunch "$target" > "$LOGS/lunch.log" 2>&1 || status=$?
cat "$LOGS/lunch.log"
echo "TARGET_PRODUCT=${TARGET_PRODUCT:-} TARGET_RELEASE=${TARGET_RELEASE:-} TARGET_BUILD_VARIANT=${TARGET_BUILD_VARIANT:-}"
if ((status == 0)); then
    case "$STAGE" in
        graph)  m nothing 2>&1 | tee "$LOGS/build.log" || status=$? ;;
        vendor) m vendorimage 2>&1 | tee "$LOGS/build.log" || status=$? ;;
        full)   m 2>&1 | tee "$LOGS/build.log" || status=$? ;;
    esac
fi
set -u
for f in error.log soong.log verbose.log.gz build.trace.gz; do
    [[ -f "out/$f" ]] && cp "out/$f" "$LOGS/" || true
done
if ((status == 0)); then
    summary "- [PASS] \`lunch $target\` and the $STAGE stage"
else
    summary "- [FAIL] \`lunch $target\` / $STAGE stage, first errors:"
    summary '```'
    { grep -m40 -E "error:|FAILED:|Error|error " "$LOGS/build.log" "$LOGS/lunch.log" 2>/dev/null || true; } \
        | cut -c1-300 >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
    summary '```'
fi
exit "$status"
