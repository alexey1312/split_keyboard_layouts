#!/usr/bin/env bash
# =============================================================================
# bootstrap.sh — one-command build of the Corne RuEn firmware
# =============================================================================
# What it does:
#   1. Clones (or updates) vial-kb/vial-qmk into ./.vial-qmk/  (sibling to this
#      script). First run downloads ~500 MB; subsequent runs `git pull` only.
#   2. Copies firmware/crkbd_ruen/*    → keyboards/crkbd/crkbd_ruen/
#   3. Copies firmware/keymap/*        → keyboards/crkbd/keymaps/vial/
#   4. Applies firmware/crkbd.c.patch  (idempotent — skips if already applied)
#   5. Builds crkbd/rev1:vial          → produces crkbd_rev1_vial.hex
#   6. Copies the .hex out to ./build/ so you don't need to remember the path.
#
# Prerequisites (one-time):
#   brew install qmk/qmk/qmk avr-gcc@8 dfu-programmer gcc-arm-embedded
#   qmk setup        # accepts vial-qmk as the user-provided qmk_firmware tree
#
# Usage:
#   ./bootstrap.sh                # build only
#   ./bootstrap.sh --refresh      # force `git pull` on vial-qmk
#   ./bootstrap.sh --flash        # build, then prompt for double-tap reset
#                                 # and flash via qmk flash
# =============================================================================
set -euo pipefail

FIRMWARE_DIR="$(cd "$(dirname "$0")" && pwd)"
VIAL_DIR="${FIRMWARE_DIR}/.vial-qmk"
VIAL_REPO="https://github.com/vial-kb/vial-qmk.git"
VIAL_BRANCH="vial"
BUILD_DIR="${FIRMWARE_DIR}/build"

REFRESH=0
FLASH=0
for arg in "$@"; do
  case "${arg}" in
    --refresh) REFRESH=1 ;;
    --flash)   FLASH=1 ;;
    --help|-h)
      sed -n '2,25p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *) echo "Unknown flag: ${arg}" >&2; exit 1 ;;
  esac
done

# --- 0. sanity checks --------------------------------------------------------
if ! command -v avr-gcc >/dev/null 2>&1; then
  echo "❌ avr-gcc not found. Install with: brew install avr-gcc@8" >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "❌ git not found" >&2
  exit 1
fi

# --- 1. clone or refresh vial-qmk --------------------------------------------
if [[ ! -d "${VIAL_DIR}/.git" ]]; then
  echo "→ Cloning vial-qmk (~500 MB, one-time)…"
  git clone --branch "${VIAL_BRANCH}" --depth 50 \
    --recurse-submodules \
    "${VIAL_REPO}" "${VIAL_DIR}"
elif [[ ${REFRESH} -eq 1 ]]; then
  echo "→ Refreshing vial-qmk…"
  ( cd "${VIAL_DIR}" && git fetch && git checkout "${VIAL_BRANCH}" && git pull && git submodule update --init --recursive )
fi

# --- 2. sync custom sources --------------------------------------------------
echo "→ Syncing keymap + ruen engine into vial-qmk tree"
mkdir -p "${VIAL_DIR}/keyboards/crkbd/crkbd_ruen"
mkdir -p "${VIAL_DIR}/keyboards/crkbd/keymaps/vial"
command cp -f "${FIRMWARE_DIR}/crkbd_ruen/"* "${VIAL_DIR}/keyboards/crkbd/crkbd_ruen/"
command cp -f "${FIRMWARE_DIR}/keymap/"*     "${VIAL_DIR}/keyboards/crkbd/keymaps/vial/"

# --- 3. apply crkbd.c.patch (idempotent) -------------------------------------
PATCH="${FIRMWARE_DIR}/crkbd.c.patch"
if [[ -f "${PATCH}" ]]; then
  # `git apply --check` succeeds if the patch can apply cleanly. If it fails,
  # we test "--reverse --check" — that succeeds only when the patch is already
  # applied (i.e. reversing it would clean apply). That tells us to skip.
  if ( cd "${VIAL_DIR}" && git apply --check "${PATCH}" 2>/dev/null ); then
    echo "→ Applying crkbd.c.patch"
    ( cd "${VIAL_DIR}" && git apply "${PATCH}" )
  elif ( cd "${VIAL_DIR}" && git apply --reverse --check "${PATCH}" 2>/dev/null ); then
    echo "→ crkbd.c.patch already applied — skipping"
  else
    echo "⚠️  crkbd.c.patch does not apply cleanly and is not already applied." >&2
    echo "    vial-qmk's crkbd.c may have diverged. Regenerate the patch:" >&2
    echo "      cd ${VIAL_DIR} && git diff keyboards/crkbd/crkbd.c > ${PATCH}" >&2
    exit 1
  fi
fi

# --- 4. build ----------------------------------------------------------------
echo "→ Building crkbd/rev1:vial"
( cd "${VIAL_DIR}" && make crkbd/rev1:vial -j8 )

# --- 5. publish artifact -----------------------------------------------------
mkdir -p "${BUILD_DIR}"
HEX_NAME="crkbd_rev1_vial.hex"
SRC_HEX="${VIAL_DIR}/${HEX_NAME}"
if [[ ! -f "${SRC_HEX}" ]]; then
  echo "❌ build did not produce ${HEX_NAME}" >&2
  exit 1
fi
command cp -f "${SRC_HEX}" "${BUILD_DIR}/${HEX_NAME}"
echo ""
echo "✔ Built:  ${BUILD_DIR}/${HEX_NAME}"
echo "  Size:   $(wc -c < "${BUILD_DIR}/${HEX_NAME}" | tr -d ' ') bytes"

# --- 6. optional flash -------------------------------------------------------
if [[ ${FLASH} -eq 1 ]]; then
  echo ""
  echo "→ Ready to flash."
  echo "  Double-tap the reset button under the controller shield on the LEFT half."
  echo "  Press Enter once the bootloader is detected (Caterina, ~8s window)…"
  read -r _
  ( cd "${VIAL_DIR}" && qmk flash -kb crkbd/rev1 -km vial )
fi

echo ""
echo "Next steps:"
echo "  • Drag ${BUILD_DIR}/${HEX_NAME} into QMK Toolbox, enable Auto-Flash,"
echo "    double-tap reset on the LEFT half."
echo "  • Or re-run with --flash to use qmk flash directly."
