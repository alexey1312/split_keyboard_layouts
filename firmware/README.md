# Firmware sources

Custom Vial-QMK firmware for **Corne (crkbd) rev1** with:

- **RuEn engine** — Mac language switching aware of internal `cur_lang` state, with auto-EN-switching bracket keycodes and unified punctuation across Russian/English layouts.
- **Caps Word** — temporary CAPS that auto-exits on word break (Space/Enter/Esc or any non-letter/non-digit). Activates by holding both home-row mod-tap shifts past `TAPPING_TERM`, or by double-tapping the plain `KC_LSFT`. `-` becomes `_` inside the word.
- **Raw HID host sync** — `raw_hid_receive_kb` accepts two packet shapes from the host:
  - `[0xAC, idx]` — layout sync (qmk-hid-host `_LAYOUT`). Updates `cur_lang` without sending Cmd+Space. Closes the classic RuEn desync when language is switched outside the keyboard (Punto, Cmd+Space from MacBook keyboard, mouse menu bar click).
  - `[0xB0, 'M','A','C','\0']` — OS-type announcement (RuEnSync extension, magic format from [nomis/qmk-hid-identify](https://github.com/nomis/qmk-hid-identify)). On the **first** such packet after boot, sets `mac_layout = true` so Russian punctuation matches macOS-Russian without requiring a manual `RuEn Mac Tg` toggle after every reflash. Subsequent `0xB0` packets in the same boot are ignored — a user-pressed `RuEn Mac Tg` override survives daemon reconnects.

  Compatible host apps: [**RuEnSync**](https://github.com/alexey1312/ruen-sync-mac) (native macOS menubar app, sends both packet shapes, recommended) or [qmk-hid-host](https://github.com/zzeneg/qmk-hid-host) (cross-platform Rust daemon, sends only `0xAC`).
- **Combos** (16 slots), **Mouse keys**, **Extrakeys** (consumer / media), **Tap dance** (8 slots), **Key overrides** (8 slots).
- **Tri-layer** — holding both SYM (1) and NAV (2) at the same time activates FUN (3). Removes the need for an explicit `MO(3)` keycode in either source layer. Implemented via `layer_state_set_kb` calling `update_tri_layer_state(state, 1, 2, 3)` in `crkbd.c.patch`.
- **No RGB, no OLED** — disabled to fit 28 KB ATmega32u4 flash.

Final flash usage: ~26.0 KB of 28.0 KB available (~2.6 KB free).

## How to build

### Quick start (recommended)

```bash
./bootstrap.sh        # first run downloads ~500 MB of vial-qmk; subsequent runs are seconds
```

The script clones [vial-kb/vial-qmk](https://github.com/vial-kb/vial-qmk) into
`firmware/.vial-qmk/`, syncs our sources, applies `crkbd.c.patch`, runs
`make crkbd/rev1:vial`, and drops the result at
`firmware/build/crkbd_rev1_vial.hex`.

Flags:

- `./bootstrap.sh --refresh` — `git pull` vial-qmk before building
- `./bootstrap.sh --flash` — build, then prompt for reset and `qmk flash`

Prereqs (one-time): `brew install avr-gcc@8 dfu-programmer qmk/qmk/qmk`.

### Manual ritual (advanced)

If you prefer to keep vial-qmk in a custom location or to use it for other
keyboards, do the same steps by hand:

```bash
# 1. Clone vial-qmk (if you don't have it already)
git clone --recurse-submodules https://github.com/vial-kb/vial-qmk.git ~/Developer/vial-qmk
cd ~/Developer/vial-qmk
git checkout vial

# 2. Apply our changes
cp -r /path/to/this/repo/firmware/crkbd_ruen ~/Developer/vial-qmk/keyboards/crkbd/crkbd_ruen
cp /path/to/this/repo/firmware/keymap/*    ~/Developer/vial-qmk/keyboards/crkbd/keymaps/vial/
patch -p1 < /path/to/this/repo/firmware/crkbd.c.patch

# 3. Build
make crkbd/rev1:vial -j8
# Produces crkbd_rev1_vial.hex in vial-qmk root
```

## How to flash

Use QMK Toolbox (https://qmk.fm/toolbox):

1. Open the produced `crkbd_rev1_vial.hex`.
2. Enable **Auto-Flash**.
3. Connect the **left half** USB-C to your computer (TRRS unplugged).
4. Double-tap the reset button on the PCB (it's under the controller shield — use tweezers).
5. Caterina bootloader will enumerate; Auto-Flash writes within a few seconds.

The right half does not need to be reflashed if it already runs working firmware — only the master half processes the keymap.

⚠️ **Never hot-plug TRRS while USB is connected** — you can short VCC/GND and damage the controller.

## File layout

```
firmware/
├── README.md             # this file
├── bootstrap.sh          # one-command clone-sync-patch-build pipeline
├── crkbd_ruen/           # → keyboards/crkbd/crkbd_ruen/
│   ├── ruen.h            # RuEn keycode enum (starts at QK_KB, not QK_USER)
│   └── ruen.c            # RuEn engine: set_lang(), per-keycode handlers
├── keymap/               # → keyboards/crkbd/keymaps/vial/
│   ├── rules.mk          # COMBO/MOUSEKEY/EXTRAKEY enabled, LTO required
│   ├── config.h          # VIAL_COMBO_ENTRIES=16, TAPPING_TERM=180
│   ├── vial.json         # 36 customKeycodes definitions (RuEn ...)
│   └── keymap.c          # NOTE: Vial-QMK does NOT compile this in current arch
└── crkbd.c.patch         # patch for keyboards/crkbd/crkbd.c — wires process_record_kb
                          # to call RuEn engine (because keymap.c is bypassed)
```

## Critical architectural notes

1. **Vial-QMK does NOT compile `keymap.c`.** It auto-generates `default_keyboard.c` from `vial.json` and links that. User hooks (`process_record_user`, `housekeeping_task_user`) placed in `keymap.c` are silently dropped. That's why our `process_record_kb` wiring lives in `crkbd.c` (via the patch) — that file is part of the keyboard core and does get compiled.

2. **Vial `customKeycodes` (in `vial.json`) map to `QK_KB` (0x7E00..0x7E3F), NOT `QK_USER` (0x7E40+)** — despite Vial UI labelling them "User 0", "User 1". The enum in `ruen.h` must begin with `LG_START = QK_KB`.

3. **`vial.json` `customKeycodes` order must match the enum order in `ruen.h` exactly.** Index 0 in JSON = `QK_KB+0` = first enum value. Reordering one entry breaks all subsequent mappings.

4. **Changing `customKeycodes` array shape (adding/removing entries) resets the EEPROM on next boot.** Vial detects the layout-signature mismatch and clears the dynamic keymap. After such a reflash, you must `File → Load saved layout` in Vial again.

5. **Do NOT define `COMBO_COUNT`** in `config.h` — Vial-QMK derives it from `VIAL_COMBO_ENTRIES` and a duplicate `#define` errors out. Only set `VIAL_COMBO_ENTRIES`.

## USER index → RuEn keycode mapping

Must stay consistent across `ruen.h` enum, `vial.json` `customKeycodes`, and any `.vil` files that reference USER00..USER35:

| USER | LG_*          | Behaviour                                           |
|------|---------------|-----------------------------------------------------|
| 00   | LG_TOGGLE     | Toggle layout (sends Cmd+Space, updates cur_lang)   |
| 01   | LG_SYNC       | Sync cur_lang without sending keys                  |
| 02   | LG_SET_EN     | Force English                                       |
| 03   | LG_SET_RU     | Force Russian                                       |
| 04   | LG_DOT        | `.` in both layouts                                 |
| 05   | LG_COMMA      | `,`                                                 |
| 06   | LG_SCLN       | `;`                                                 |
| 07   | LG_COLON      | `:`                                                 |
| 08   | LG_DQUO       | `"`                                                 |
| 09   | LG_QUES       | `?`                                                 |
| 10   | LG_SLASH      | `/`                                                 |
| 11   | LG_LBR        | `[` (auto-switch to EN, type, switch back)          |
| 12   | LG_RBR        | `]`                                                 |
| 13   | LG_LCBR       | `{`                                                 |
| 14   | LG_RCBR       | `}`                                                 |
| 15   | LG_LT         | `<`                                                 |
| 16   | LG_GT         | `>`                                                 |
| 17   | LG_GRAVE      | `` ` ``                                             |
| 18   | LG_TILD       | `~`                                                 |
| 19   | LG_AT         | `@`                                                 |
| 20   | LG_HASH       | `#`                                                 |
| 21   | LG_DLR        | `$`                                                 |
| 22   | LG_CIRC       | `^`                                                 |
| 23   | LG_AMPR       | `&`                                                 |
| 24   | LG_PIPE       | `\|`                                                |
| 25   | LG_QUOTE      | `'`                                                 |
| 26   | LG_NUM        | `№` (Russian-only)                                  |
| 27   | LG_PERC       | `%`                                                 |
| 28   | LG_TG_MAC     | Toggle Mac vs Russian-PC variant for punctuation    |
| 29   | LG_RU_BE      | `б` (sends KC_COMMA when in RU)                     |
| 30   | LG_RU_YU      | `ю` (KC_DOT)                                        |
| 31   | LG_RU_ZHE     | `ж` (KC_SCLN)                                       |
| 32   | LG_RU_E       | `э` (KC_QUOT)                                       |
| 33   | LG_RU_KHA     | `х` (KC_LBRC)                                       |
| 34   | LG_RU_HRD_SGN | `ъ` (KC_RBRC)                                       |
| 35   | LG_RU_YO      | `ё` (KC_GRAVE)                                      |

## RuEn behaviour

State is RAM-only (no EEPROM persistence). At boot:
- `cur_lang = LANG_EN`
- `mac_layout = false`

`set_lang()` sends `Cmd+Space` (or `Ctrl+Space` if `keymap_config.swap_lctl_lgui` is set) and updates `cur_lang`. To stay in sync, **switch language only via `RuEn Toggle`** — using the system Cmd+Space directly will desync the engine.

If desynced, use `RuEn Sync` (USER01) to flip the internal flag without sending keys, or `RuEn En` / `RuEn Ru` to force a specific state.

`RuEn Mac Tg` (USER28) toggles between Mac Russian and Russian-PC variants. Default at boot is Russian-PC (`mac_layout=false`). When the [RuEnSync](https://github.com/alexey1312/ruen-sync-mac) daemon is running, it auto-pushes a `[0xB0, MAC\0]` packet on its first connect after boot which flips the flag to `true` — USER28 then acts as a manual override / fallback (useful on machines without the daemon, or for users whose system Russian variant is `Russian — PC`). The auto-flip only applies the first time per boot, so a USER28 override is preserved across daemon reconnects.
