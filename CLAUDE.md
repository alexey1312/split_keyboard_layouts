# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two **Vial-format keyboard layouts** (`.vil` JSON files) plus the **custom Vial-QMK firmware sources** needed to make the Corne layout work. Designed for macOS with bilingual (RU/EN) typing.

## Files

- `corne.vil` — active layout for foostan Corne rev1 (Pro Micro USB-C, ATmega32u4). Uses RuEn custom keycodes; requires the matching firmware in `firmware/`.
- `sofle.vil` — older Sofle layout, kept as a fallback. Works with stock Vial firmware (no custom keycodes needed).
- `firmware/` — custom Vial-QMK sources to be dropped into a clone of `vial-kb/vial-qmk`. See `firmware/README.md` for the apply procedure and the full RuEn keycode table.
- `tools/qmk-hid-host/` — macOS daemon glue. Watches the active OS input source and pushes the layout index to the Corne over Raw HID, keeping `cur_lang` in sync even when the language is switched outside the keyboard (Punto Switcher, Cmd+Space from MacBook keyboard, mouse menu-bar click). See `tools/qmk-hid-host/README.md`. Optional — without the daemon, the firmware falls back to its built-in sync via `RuEn Toggle`.
- **Companion repo:** [`ruen-sync-mac`](https://github.com/alexey1312/ruen-sync-mac) — native macOS menubar app that speaks the same `[0xAC, idx]` wire protocol as qmk-hid-host. Event-driven (no polling), `SMAppService` login item, signed/notarized. Recommended over the Rust daemon for macOS-only users. Lives at `~/Developer/ruen-sync-mac/`.
- `README.md` — user-facing overview (GitHub front page).
- `CLAUDE.md` — this file.

## Hardware

- **Active board:** foostan **Corne (crkbd) rev1**, Pro Micro USB-C, **ATmega32u4**, Caterina bootloader, `MASTER_LEFT`, no encoders. 28 KB usable flash.
- **Legacy board:** Sofle (kept for parity reference — most layouts originated there).
- Only the **left half is reflashed**. The slave half can run older / stock firmware — all keymap logic runs on the master.

## Editing a `.vil` file

`.vil` is **a single line of JSON**. After editing always validate with `jq`:

```bash
jq '.' corne.vil > /dev/null && echo "JSON valid"
```

Key fields:

- `layout`: 4 layers, each 8 rows × 6 cols (Corne) or 10×6 (Sofle). Corne thumb rows use `[-1, -1, -1, key, key, key]` — `-1` marks physical non-existent matrix positions.
- `uid`: tied to the physical board. When loading a layout with mismatched UID, Vial warns "Saved keymap belongs to a different keyboard" — clicking Yes is fine. Current Corne UID = `15126841831861545787`.
- `tap_dance`: 8 slots. TD(0) in `corne.vil` is the language switch: tap = USER00 (RuEn Toggle, sends Cmd+Space and updates RuEn state), hold = LAlt.
- `combo`: 16 slots. 10 active combos for bracket pairs and `\` — see README.
- `key_override`: 8 slots. 4 active: Shift+Bspc → Del, Cmd+H → blocked (any Gui), Shift+Esc → `\`, Cmd+M → blocked (any Gui; safety net against accidental Minimize Window from home-row mod-tap on K).
- `customKeycodes` indices ("USER00" .. "USER35" in the JSON) map to `QK_KB + N` in the firmware enum — **not** `QK_USER`. See firmware section.

## Firmware (in `firmware/`)

To rebuild the firmware, the contents of `firmware/` need to be applied to a clone of [vial-kb/vial-qmk](https://github.com/vial-kb/vial-qmk) (branch `vial`):

```bash
cd ~/Developer/vial-qmk   # adjust path
cp -r .../firmware/crkbd_ruen keyboards/crkbd/crkbd_ruen
cp .../firmware/keymap/*      keyboards/crkbd/keymaps/vial/
patch -p1 < .../firmware/crkbd.c.patch
make crkbd/rev1:vial -j8
```

Flash with QMK Toolbox: open the produced `crkbd_rev1_vial.hex`, enable Auto-Flash, double-tap reset under the controller shield on the **left half**.

⚠️ **Never hot-plug TRRS while USB is connected** — can short VCC/GND.

### Current `rules.mk` shape

```
VIA_ENABLE=yes  VIAL_ENABLE=yes  LTO_ENABLE=yes
RGBLIGHT=no  RGB_MATRIX=no  OLED=no
MOUSEKEY=yes  EXTRAKEY=yes  COMBO=yes  CAPS_WORD_ENABLE=yes
VPATH += keyboards/crkbd/crkbd_ruen
SRC   += ruen.c
```

LTO is required — without it the build does not fit. Currently ~28.2 KB / 28.6 KB used (~420 B free). Raw HID is already enabled by Vial-QMK itself for the Vial protocol, so no extra flag is needed for the host sync described below.

### Current `config.h` extras

```
VIAL_COMBO_ENTRIES 16
COMBO_TERM 50
TAPPING_TERM 200
BOTH_SHIFTS_TURNS_ON_CAPS_WORD
DOUBLE_TAP_SHIFT_TURNS_ON_CAPS_WORD
```

`TAPPING_TERM` was raised from 180 to 200 to reduce false hold-triggers on home-row mods (e.g. lingering on Russian "л" = physical K = `RGUI_T(KC_K)` and producing accidental RGui+next-key combinations like Cmd+M).

**Caps Word** is activated either by holding both home-row mod-tap shifts (`F` and `J`) past `TAPPING_TERM`, or by double-tapping the plain `KC_LSHIFT` (Layer 0 row 2 col 0). Both activation methods are compiled in (~800 B of flash). The double-tap method does NOT work with mod-tap shifts — only with the bare `KC_LSFT` key.

`IGNORE_MOD_TAP_INTERRUPT` is now QMK's default behaviour — the flag was removed from QMK and **must not be set explicitly** (compile error).

`QMK_SETTINGS = no`: enabling it would add ~5.5 KB of Vial UI runtime tuning support, but firmware does not fit (overflow by ~4.3 KB on ATmega32u4). For dynamic tuning a RP2040-based controller (Elite-Pi / Liatris) would be required.

Do **not** define `COMBO_COUNT` — Vial-QMK derives it from `VIAL_COMBO_ENTRIES` and a duplicate `#define` errors out.

### RuEn engine

`firmware/crkbd_ruen/ruen.{c,h}`:

- Keycode enum starts at `LG_START = QK_KB`. 36 keycodes total (see `firmware/README.md` for the full USER index → LG_* table).
- `set_lang()` sends Cmd+Space (LCtl+Space if `keymap_config.swap_lctl_lgui`) and updates `cur_lang`.
- `lang_sync_to(uint8_t lang)` does an **absolute** set of `cur_lang` without sending Cmd+Space. Used by `raw_hid_receive_kb` when the host daemon reports an external switch.
- State is **RAM-only** — boots in `LANG_EN` and `mac_layout=false`. `mac_layout=false` matches user's actual Russian keyboard layout (PC-Russian variant) per empirical testing. The `RuEn Mac Tg` (USER28) keycode flips to `mac_layout=true` for macOS Russian variant when needed.

### Raw HID host sync (optional)

`firmware/crkbd.c.patch` defines `raw_hid_receive_kb`. It only listens for one packet shape:

```
[0xAC, idx]    // 0xAC = qmk-hid-host's _LAYOUT, idx 0 = EN, anything else = RU
```

`0xAC` matches the `_LAYOUT` enum value in [qmk-hid-host's `data_type.rs`](https://github.com/zzeneg/qmk-hid-host/blob/main/src/data_type.rs). Vial-QMK's own Raw HID protocol uses different first-byte values, so it does not collide.

When the daemon is running and connected, every external language switch (Cmd+Space from another keyboard, Punto Switcher, mouse menu-bar click) is mirrored into `cur_lang` within ~100 ms (the daemon polls TIS at that interval). When the daemon is not running, the firmware falls back to its built-in `RuEn Toggle` sync. See `tools/qmk-hid-host/`.

### Critical architectural traps (these cost hours to debug — don't forget)

1. **Vial-QMK does NOT compile `keymap.c`.** Vial auto-generates `default_keyboard.c` from `vial.json` and links that. Anything in `keymap.c` (including `process_record_user`) is silently dropped. User hooks live in `keyboards/crkbd/crkbd.c` instead (via `crkbd.c.patch`), wiring `process_record_kb` / `pre_process_record_kb` / `housekeeping_task_kb` to call the RuEn engine.
2. **Vial `customKeycodes` map to `QK_KB` (0x7E00..0x7E3F), NOT `QK_USER` (0x7E40+).** Vial UI labels them "User 0", "User 1" which is misleading. The enum in `ruen.h` must begin with `LG_START = QK_KB`. Mismatch means `process_record_ruen` ignores the keycode silently. Diagnose by printing the keycode as 4 hex digits via `tap_code` — a `7e00` confirms the mapping.
3. **`vial.json` `customKeycodes` order must match the enum order in `ruen.h` exactly.** Index 0 in JSON = `QK_KB+0` = first enum value. Reordering one entry breaks all subsequent mappings.
4. **Changing `customKeycodes` array shape (adding/removing entries) resets the EEPROM on next boot.** Vial detects the layout-signature mismatch and clears the dynamic keymap. After such a reflash, `File → Load saved layout` is required again. Stable `vial.json` = stable EEPROM across flashes.
5. **`QK_BOOT` is on Layer 3 / Q-position** of `corne.vil`. Used for subsequent reflashes without touching the physical reset button.
6. **Raw HID is shared between Vial and qmk-hid-host.** `via.c` dispatches via `raw_hid_receive`; if the command-id is not a Vial/VIA command, it forwards to `raw_hid_receive_kb`. Our `crkbd.c.patch` puts the qmk-hid-host handler there. **Do NOT define `raw_hid_receive` (without the `_kb` suffix)** — it would override Vial's entry point and break the Vial UI completely.

### Slot counts exposed to Vial UI

- Combo: 16 (stock foostan firmware has 0)
- Tap dance: 8
- Macros: 16
- Key overrides: 8
- Mouse keys: enabled
- Extrakey (consumer / media): enabled

If a Vial UI tab is missing, the corresponding feature is not compiled in.

## Loading a layout after flashing

1. Vial → **File → Load saved layout** → pick `corne.vil` or `sofle.vil`.
2. Click **Yes** on the UID mismatch warning if it appears.
3. Verify in the Keymap view that the expected keycode is shown on the expected key. If the layout looks reverted to defaults (Tab / LCtrl / LShift / Fn1 etc.), the EEPROM was reset — re-load the layout.

## RuEn sync ritual (for the user)

Two modes of operation depending on whether the `qmk-hid-host` daemon is installed.

### With qmk-hid-host daemon installed (recommended)

The daemon mirrors every OS input-source change into `cur_lang` within ~100 ms. Switch language with whatever you prefer — Cmd+Space from any keyboard, TD(0) on Corne, mouse menu-bar click, Punto Switcher hotkey or auto-conversion. RuEn stays in sync automatically. Verify with `tail -f ~/Library/Logs/qmk-hid-host.log` — every layout change should show `new layout: 'X'` and `Corne: sending [172, idx]`.

If you ever see desync with the daemon installed, in order: (1) check the daemon is actually running with `launchctl print gui/$(id -u)/com.user.qmk-hid-host | head -5`, (2) check Vial.app is NOT open (Vial owns Raw HID exclusively — the daemon then logs `exclusive access` errors until Vial is quit; the daemon auto-reconnects within ~5 s).

### Without the daemon (e.g. on another mac)

The firmware falls back to its built-in tracking — same as before this integration existed:

1. **Switch language ONLY via TD(0) tap on `corne.vil`** (which fires USER00 = `RuEn Toggle`). System Cmd+Space from MacBook keyboard will desync.
2. If desynced (RuEn punctuation is "wrong"), tap TD(0) once more — usually fixes by re-toggling.
3. To force a known state: temporarily place `RuEn Sync` / `RuEn En` / `RuEn Ru` somewhere via Vial UI and use it.
4. Last resort: unplug + replug USB — RuEn boots in `LANG_EN`, set macOS to English to match.

## qmk-hid-host daemon: install / configure / remove

Sources live in `tools/qmk-hid-host/`. The README there is the authoritative how-to; this section is the quick reference.

### Install (macOS only)

```bash
cd tools/qmk-hid-host
./install.sh
```

The script (idempotent — safe to re-run):

1. Downloads `macos.zip` from the latest release of [zzeneg/qmk-hid-host](https://github.com/zzeneg/qmk-hid-host) into a temp dir, extracts the universal binary into `~/.local/bin/qmk-hid-host`, strips `com.apple.quarantine` xattr.
2. Copies `config.json` to `~/.config/qmk-hid-host/` (skipped if already present).
3. Generates `~/Library/LaunchAgents/com.user.qmk-hid-host.plist` with `$HOME` interpolated.
4. `launchctl bootout` any prior run, then `launchctl bootstrap gui/$(id -u)` — starts the daemon and registers it for auto-start at login.

Logs go to `~/Library/Logs/qmk-hid-host.log` (stdout) and `qmk-hid-host.err.log` (stderr).

### Configure

`~/.config/qmk-hid-host/config.json`:

```json
{
  "devices": [{ "productId": "0x0001", "name": "Corne" }],
  "layouts": ["ABC", "Russian"],
  "reconnectDelay": 5000
}
```

- `productId` must match `firmware/keymap/vial.json` (`0x0001` for the current Corne).
- `layouts` is the ordered list of **suffixes** of `TISPropertyInputSourceID` (the part after the last dot). The daemon sends the index into this list, not the name. Firmware treats index 0 as English, **anything else as Russian** — so listing several Russian-variant layouts in a row is fine.
- To find suffixes for your installed layouts: `defaults read com.apple.HIToolbox AppleSelectedInputSources`, look at `KeyboardLayout Name` — that string is the suffix.

After editing the config, restart the daemon:

```bash
launchctl kickstart -k gui/$(id -u)/com.user.qmk-hid-host
```

### Verify it's working

```bash
launchctl print "gui/$(id -u)/com.user.qmk-hid-host" | head -5  # state = running
tail -f ~/Library/Logs/qmk-hid-host.log                          # watch live
```

Then switch input source through any path (menu bar mouse click, Cmd+Space, Punto). The log should print `new layout: 'X'` and `Corne: sending [172, idx]`. If you only see the `[172, idx]` line without RuEn updating, the firmware is still on the pre-daemon build — reflash.

### Remove

```bash
cd tools/qmk-hid-host
./uninstall.sh
```

This `launchctl bootout`s the agent, removes the plist and the binary. **Keeps** `~/.config/qmk-hid-host/config.json` in case you want to reinstall later — delete it manually if you don't.

### Known operational issues

- **Vial.app vs daemon mutex on Raw HID.** macOS allows one exclusive owner per HID interface. When Vial is running, the daemon logs `hid_open_path: ... exclusive access and device already open` once per second. Quit Vial to edit the keymap, then the daemon reconnects automatically within `reconnectDelay` (default 5 s). There is no way to share the interface without restructuring the firmware to expose a second Raw HID interface (not done — would break stock Vial-QMK assumptions).
- **Gatekeeper.** First launch may be blocked. The install script tries to strip `com.apple.quarantine` via `xattr -d`, which usually works; if it doesn't, run `~/.local/bin/qmk-hid-host -c ~/.config/qmk-hid-host/config.json` once manually, allow in System Settings → Privacy & Security, then re-run `install.sh`.
- **Daemon dies if Corne is unplugged.** That's expected — `KeepAlive = true` in the plist restarts it within `ThrottleInterval` (10 s). On re-plug the connection just resumes.

## What is allowed in `.claude/settings.local.json`

Pre-approved diagnostic commands (no permission prompt): `qmk --version`, `avr-gcc --version`, `avrdude -?`. Any other build/flash command will ask.
