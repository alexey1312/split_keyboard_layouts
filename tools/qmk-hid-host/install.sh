#!/usr/bin/env bash
# Installs qmk-hid-host as a LaunchAgent that keeps Corne RuEn cur_lang in
# sync with the macOS active input source. See README.md for context.
set -euo pipefail

# --- 0. sanity checks ------------------------------------------------------
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is macOS-only. For Linux/Windows see qmk-hid-host README." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required" >&2
  exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
CFG_DIR="${HOME}/.config/qmk-hid-host"
PLIST_DIR="${HOME}/Library/LaunchAgents"
PLIST_NAME="com.user.qmk-hid-host.plist"
PLIST_PATH="${PLIST_DIR}/${PLIST_NAME}"

mkdir -p "${BIN_DIR}" "${CFG_DIR}" "${PLIST_DIR}"

# --- 1. download and extract binary ----------------------------------------
# zzeneg/qmk-hid-host ships a single macos.zip with a universal binary
# (works on both arm64 and x86_64). Releases are rolling: tag is literally
# 'latest' and there is no semantic-version `latest/download/...` redirect.
URL="https://github.com/zzeneg/qmk-hid-host/releases/download/latest/macos.zip"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "Downloading ${URL}"
curl -fL --progress-bar -o "${TMP_DIR}/macos.zip" "${URL}"
unzip -o -q "${TMP_DIR}/macos.zip" -d "${TMP_DIR}"

if [[ ! -f "${TMP_DIR}/qmk-hid-host" ]]; then
  echo "Downloaded archive does not contain qmk-hid-host binary" >&2
  exit 1
fi

mv "${TMP_DIR}/qmk-hid-host" "${BIN_DIR}/qmk-hid-host"
chmod +x "${BIN_DIR}/qmk-hid-host"
# Strip macOS quarantine flag so the LaunchAgent can run it without prompting.
xattr -d com.apple.quarantine "${BIN_DIR}/qmk-hid-host" 2>/dev/null || true

# --- 2. install config (do not clobber existing) ---------------------------
if [[ -f "${CFG_DIR}/config.json" ]]; then
  echo "Config already exists at ${CFG_DIR}/config.json — leaving untouched."
else
  cp "${REPO_DIR}/config.json" "${CFG_DIR}/config.json"
  echo "Installed config to ${CFG_DIR}/config.json"
fi

# --- 3. install LaunchAgent with HOME interpolation -----------------------
sed "s|__HOME__|${HOME}|g" "${REPO_DIR}/${PLIST_NAME}" > "${PLIST_PATH}"
echo "Installed LaunchAgent to ${PLIST_PATH}"

# Replace any prior run, then start
launchctl bootout "gui/$(id -u)/com.user.qmk-hid-host" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "${PLIST_PATH}"

echo ""
echo "Installation complete."
echo ""
echo "  binary: ${BIN_DIR}/qmk-hid-host"
echo "  config: ${CFG_DIR}/config.json"
echo "  agent:  ${PLIST_PATH}"
echo "  logs:   ${HOME}/Library/Logs/qmk-hid-host.log"
echo ""
echo "Verify with:"
echo "  launchctl print gui/\$(id -u)/com.user.qmk-hid-host | head -20"
echo "  tail -f ${HOME}/Library/Logs/qmk-hid-host.log"
