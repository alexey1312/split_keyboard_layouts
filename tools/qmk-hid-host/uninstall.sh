#!/usr/bin/env bash
# Removes the qmk-hid-host LaunchAgent and binary. Leaves config in place
# in case you want to reinstall.
set -euo pipefail

PLIST_PATH="${HOME}/Library/LaunchAgents/com.user.qmk-hid-host.plist"

launchctl bootout "gui/$(id -u)/com.user.qmk-hid-host" 2>/dev/null || true
rm -f "${PLIST_PATH}"
rm -f "${HOME}/.local/bin/qmk-hid-host"

echo "Removed LaunchAgent and binary."
echo "Config kept at ${HOME}/.config/qmk-hid-host/config.json — delete by hand if you want."
