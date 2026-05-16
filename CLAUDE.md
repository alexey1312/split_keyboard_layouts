# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two **Vial-format keyboard layouts** (`.vil` JSON files) plus the **custom Vial-QMK firmware sources** needed to make the Corne layout work. Designed for macOS with bilingual (RU/EN) typing.

## Files

- `corne.vil` — active layout for foostan Corne rev1 (Pro Micro USB-C, ATmega32u4). Uses RuEn custom keycodes; requires the matching firmware in `firmware/`.
- `sofle.vil` — older Sofle layout, kept as a fallback. Works with stock Vial firmware (no custom keycodes needed).
- `firmware/` — custom Vial-QMK sources to be dropped into a clone of `vial-kb/vial-qmk`. See `firmware/README.md` for the apply procedure and the full RuEn keycode table.
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
- `key_override`: 8 slots. 3 active: Shift+Bspc → Del, Cmd+H → blocked, Shift+Esc → `\`.
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
MOUSEKEY=yes  EXTRAKEY=yes  COMBO=yes
VPATH += keyboards/crkbd/crkbd_ruen
SRC   += ruen.c
```

LTO is required — without it the build does not fit. Currently ~27.5 KB / 28.6 KB used (~1.2 KB free).

### Current `config.h` extras

```
VIAL_COMBO_ENTRIES 16
COMBO_TERM 50
TAPPING_TERM 180
```

Do **not** define `COMBO_COUNT` — Vial-QMK derives it from `VIAL_COMBO_ENTRIES` and a duplicate `#define` errors out.

### RuEn engine

`firmware/crkbd_ruen/ruen.{c,h}`:

- Keycode enum starts at `LG_START = QK_KB`. 36 keycodes total (see `firmware/README.md` for the full USER index → LG_* table).
- `set_lang()` sends Cmd+Space (LCtl+Space if `keymap_config.swap_lctl_lgui`) and updates `cur_lang`.
- State is **RAM-only** — boots in `LANG_EN` and `mac_layout=false`. `mac_layout=false` matches user's actual Russian keyboard layout (PC-Russian variant) per empirical testing.

### Critical architectural traps (these cost hours to debug — don't forget)

1. **Vial-QMK does NOT compile `keymap.c`.** Vial auto-generates `default_keyboard.c` from `vial.json` and links that. Anything in `keymap.c` (including `process_record_user`) is silently dropped. User hooks live in `keyboards/crkbd/crkbd.c` instead (via `crkbd.c.patch`), wiring `process_record_kb` / `pre_process_record_kb` / `housekeeping_task_kb` to call the RuEn engine.
2. **Vial `customKeycodes` map to `QK_KB` (0x7E00..0x7E3F), NOT `QK_USER` (0x7E40+).** Vial UI labels them "User 0", "User 1" which is misleading. The enum in `ruen.h` must begin with `LG_START = QK_KB`. Mismatch means `process_record_ruen` ignores the keycode silently. Diagnose by printing the keycode as 4 hex digits via `tap_code` — a `7e00` confirms the mapping.
3. **`vial.json` `customKeycodes` order must match the enum order in `ruen.h` exactly.** Index 0 in JSON = `QK_KB+0` = first enum value. Reordering one entry breaks all subsequent mappings.
4. **Changing `customKeycodes` array shape (adding/removing entries) resets the EEPROM on next boot.** Vial detects the layout-signature mismatch and clears the dynamic keymap. After such a reflash, `File → Load saved layout` is required again. Stable `vial.json` = stable EEPROM across flashes.
5. **`QK_BOOT` is on Layer 3 / Q-position** of `corne.vil`. Used for subsequent reflashes without touching the physical reset button.

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

To stay in sync between RuEn's internal `cur_lang` and the OS layout:

1. **Switch language ONLY via TD(0) tap on `corne.vil`** (which fires USER00 = `RuEn Toggle`). System Cmd+Space from MacBook keyboard will desync.
2. If desynced (RuEn punctuation is "wrong"), tap TD(0) once more — usually fixes by re-toggling.
3. To force a known state: temporarily place `RuEn Sync` / `RuEn En` / `RuEn Ru` somewhere via Vial UI and use it.
4. Last resort: unplug + replug USB — RuEn boots in `LANG_EN`, set macOS to English to match.

## What is allowed in `.claude/settings.local.json`

Pre-approved diagnostic commands (no permission prompt): `qmk --version`, `avr-gcc --version`, `avrdude -?`. Any other build/flash command will ask.
