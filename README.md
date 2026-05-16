# split_keyboard_layouts

[![Vial](https://img.shields.io/badge/Vial-QMK-blue)](https://get.vial.today)
[![Corne](https://img.shields.io/badge/Keyboard-foostan%20Corne-orange)](https://github.com/foostan/crkbd)
[![macOS](https://img.shields.io/badge/Target-macOS-lightgrey)](https://www.apple.com/macos/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Vial keymaps and custom Vial-QMK firmware for split keyboards (Corne + Sofle),
tuned for **bilingual EN/RU typing on macOS**. Home-row mods, layer-tap thumb
cluster, 10 combos for brackets, and a **built-in RuEn engine** that gives you
unified punctuation regardless of the OS input source.

> **Companion app:** [RuEnSync](https://github.com/alexey1312/ruen-sync-mac) — a
> native macOS menubar app that watches the system input source and keeps the
> firmware's `cur_lang` in sync over Raw HID. Recommended over the
> [qmk-hid-host](https://github.com/zzeneg/qmk-hid-host) Rust daemon if you're on
> macOS only (event-driven, signed, login-item via SMAppService).

## Layouts

- **`corne.vil`** — active layout for foostan Corne (crkbd rev1), 42 keys, Pro Micro / Elite-C (ATmega32u4). Uses the custom RuEn firmware (see `firmware/`).
- **`sofle.vil`** — older Sofle layout, kept for reference / fallback. Works with stock Vial firmware (no custom keycodes needed).

Load either file via Vial → **File → Load saved layout**. If Vial warns about a different keyboard UID, click **Yes** — it will rewrite the UID on save.

## Firmware

Custom Vial-QMK build with:

- **RuEn engine** — Mac-aware language switching, auto-EN-switching brackets `[ ] { } < >`, unified punctuation
- **Combos** (16 slots)
- **Mouse keys**, **Extrakeys** (volume/media), **Tap dance** (8 slots), **Key overrides** (8 slots)

See [`firmware/README.md`](firmware/README.md) for build & flash instructions and the full RuEn keycode table.

## Features at a glance

### Base layer (Corne)

- **Home-row mods** on both halves: Ctrl/Alt/Gui/Shift on ASDF (left) and JKL; (right)
- **Tap dance** on left thumb: tap = `RuEn Toggle` (Cmd+Space + sync), hold = `LAlt`
- **Layer-tap** on right thumb: `LT(1, Space)` and `MO(2)`

### Combos (any layout)

- `R+T` → `(`
- `Y+U` → `)`
- `V+B` → `<`
- `N+M` → `>`
- `F+G` → `{`
- `H+J` → `}`
- `E+R+T` → `[`
- `Y+U+I` → `]`
- `Esc+Q` → `\`
- `TD(0)+LGui` → `LCtrl`

### Key overrides

- `Shift + Backspace` → `Delete`
- `Cmd + H` → blocked (prevents accidental window hide)
- `Shift + Esc` → `\`
- `Cmd + M` → blocked (prevents accidental Minimize Window — usually triggered by RGui mod-tap on `K` lingering during fast typing)

### RuEn keycodes

36 custom keycodes (visible in Vial **User** tab as `RuEn Toggle`, `RuEn .`, `RuEn [` …). Full list in [`firmware/README.md`](firmware/README.md).

## macOS setup

The keyboard is designed for this exact macOS configuration:

1. **System Settings → Keyboard → Keyboard Shortcuts → Input Sources → "Select the previous input source"** = `⌘ + Space`. (Reassign Spotlight to another shortcut — e.g. `⌃ + Space`.) Without this, `RuEn Toggle` won't switch languages; it'll open Spotlight instead.
2. **System Settings → Keyboard → Input Sources** should contain **English (ABC)** and **Russian**. The firmware default is `mac_layout=false` (Russian-PC behaviour). Press `RuEn Mac Tg` (USER28) on-demand if a particular text needs Mac Russian variant.
3. Disable system shortcuts that collide with combos / key overrides (e.g. `⌘ + H` is blocked by the firmware, so disable any macOS apps that rely on it).

## Layer map (Corne, `corne.vil`)

Notation: `mod/key` = mod-tap (hold = mod, tap = key); `LT(N, key)` = layer-tap; `RuEn …` = RuEn custom keycode.

### Layer 0 — Base (QWERTY)

```
┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐         ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ Esc     │ Q       │ W       │ E       │ R       │ T       │         │ Y       │ U       │ I       │ O       │ P       │ [       │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤         ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Hyp/Tab │ Ctl/A   │ Alt/S   │ Gui/D   │ Sft/F   │ G       │         │ H       │ Sft/J   │ Gui/K   │ Alt/L   │ Ctl/;   │ ]       │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤         ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Shift   │ Z       │ X       │ C       │ V       │ B       │         │ N       │ M       │ ,       │ .       │ /       │ '       │
└─────────┴─────────┴─────────┼─────────┼─────────┼─────────┤         ├─────────┼─────────┼─────────┴─────────┴─────────┴─────────┘
                              │ TD(0)   │ LGui    │LT1/Spc  │         │ Ctl/Bsp │ MO(2)   │ Alt/Ent │
                              └─────────┴─────────┴─────────┘         └─────────┴─────────┴─────────┘
```

- `Hyp/Tab` = `ALL_T(KC_TAB)` — tap Tab, hold = Hyper (Ctrl+Alt+Shift+Gui)
- `TD(0)` = tap = **RuEn Toggle**, hold = LAlt
- `LT1/Spc` = `LT(1, Space)` — tap Space, hold = Layer 1
- `Ctl/Bsp` = `LCTL_T(KC_BSPACE)` — tap Bspc, hold = LCtrl
- `MO(2)` = momentary Layer 2 while held

### Layer 1 — LOWER (hold right thumb `MO(2)`)

```
┌────┬────┬────┬────┬────┬────┐               ┌─────────┬────┬────┬────┬────┬────┐
│    │ !  │RuEn│ #  │ $  │ %  │               │ RuEn    │ )  │ (  │ *  │ &  │ ^  │
│    │    │ @  │    │    │    │               │ Mac Tg  │    │    │    │    │    │
├────┼────┼────┼────┼────┼────┤               ├─────────┼────┼────┼────┼────┼────┤
│    │    │    │    │    │    │               │RuEn Sync│ \\  │ >  │ <  │ =  │ -  │
├────┼────┼────┼────┼────┼────┤               ├─────────┼────┼────┼────┼────┼────┤
│    │    │    │    │    │ \  │               │         │ |  │RuEn│RuEn│ +  │ _  │
│    │    │    │    │    │    │               │         │    │ .  │ ,  │    │    │
└────┴────┴────┼────┼────┼────┤               ├─────────┼────┼────┴────┴────┴────┘
               │    │    │    │               │         │MO(3)│
               └────┴────┴────┘               └─────────┴────┘
```

Numbers with shift = symbols (`!@#$%^&*()`), navigation symbols on right hand. Hold both LT1 + MO(2) → Layer 3.

### Layer 2 — RAISE (hold `LT1(Space)` thumb)

```
┌────┬────┬────┬────┬────┬────┐               ┌────┬────┬────┬────┬────┬────┐
│    │ 1  │ 2  │ 3  │ 4  │ 5  │               │    │ 6  │ 7  │ 8  │ 9  │ 0  │
├────┼────┼────┼────┼────┼────┤               ├────┼────┼────┼────┼────┼────┤
│    │Ctl │Alt │Gui │Sft │    │               │    │Ctl │Sft │Gui │Alt │ ←  │
│    │ms← │ms↑ │ms↓ │ms→ │    │               │    │ —  │ ↓  │ ↑  │ →  │    │
├────┼────┼────┼────┼────┼────┤               ├────┼────┼────┼────┼────┼────┤
│    │    │    │ms↓ │    │    │               │    │    │    │    │    │    │
└────┴────┴────┼────┼────┼────┤               ├────┼────┼────┴────┴────┴────┘
               │Alt │Gui │MO(3)│              │    │    │
               │btn2│btn1│    │               │    │    │
               └────┴────┴────┘               └────┴────┘
```

Numbers, mouse keys on left home row, arrows on right home row. `MO(3)` on left center thumb activates Layer 3.

### Layer 3 — ADJUST (Layer 1 + Layer 2)

```
┌────┬────┬────┬────┬────┬────┐               ┌────┬────┬────┬────┬────┬────┐
│ F1 │ F2 │ F3 │ F4 │ F5 │ F6 │               │ F7 │ F8 │ F9 │ F10│ F11│ F12│
├────┼────┼────┼────┼────┼────┤               ├────┼────┼────┼────┼────┼────┤
│    │BOOT│    │⇧⌘3 │⇧⌘4 │    │               │    │    │Vol↓│Mute│Vol↑│    │
├────┼────┼────┼────┼────┼────┤               ├────┼────┼────┼────┼────┼────┤
│    │    │    │    │    │⇧⌘6 │               │    │Prev│Play│    │Next│    │
└────┴────┴────┼────┼────┼────┤               ├────┼────┼────┴────┴────┴────┘
               │    │    │    │               │    │    │
               └────┴────┴────┘               └────┴────┘
```

- `BOOT` = `QK_BOOT` — enter DFU bootloader (for next reflash without touching the physical reset)
- `⇧⌘3` / `⇧⌘4` / `⇧⌘6` — macOS screenshots
- Media + volume on right hand

## RuEn sync ritual

RuEn keeps an internal `cur_lang` flag (RAM-only) that tracks which OS layout is active. It can desync if you switch languages outside the keyboard.

**Golden rule:** switch languages ONLY by tapping `TD(0)` (left center thumb) — this fires `RuEn Toggle` which sends Cmd+Space **and** updates `cur_lang` atomically.

**If desync happens** (RuEn punctuation prints the wrong thing — e.g. Russian letters instead of `.`/`,`):

1. Tap `TD(0)` once more — usually re-syncs by toggling back.
2. If still off, the keyboard has `RuEn Sync` (USER01) bound on Layer 1 right home row pinky position. Hold `MO(2)` + tap that key to flip `cur_lang` without sending Cmd+Space.
3. Worst case: unplug + replug USB. RuEn boots in `LANG_EN`. Set macOS to English to match.

**System Cmd+Space from MacBook keyboard will desync** — avoid using it during a session, **unless** you have the `qmk-hid-host` daemon running (see below).

## Optional: automatic OS-side sync

The firmware exposes a 1-byte Raw HID handshake (`[0xAC, idx]`) that any host-side
program can use to push the current macOS input source into `cur_lang`. With it
running, the desync described above stops being possible: Cmd+Space from the
MacBook keyboard, Punto Switcher's auto-conversion, mouse-click on the menu bar
— anything that flips the OS layout — also flips the firmware state.

Two compatible host apps:

| App | When | How |
| --- | --- | --- |
| [**RuEnSync**](https://github.com/alexey1312/ruen-sync-mac) (recommended) | macOS only | Native menubar app. Event-driven, login-item via `SMAppService`. Just open it once. |
| [qmk-hid-host](https://github.com/zzeneg/qmk-hid-host) | Linux / Windows / macOS | Cross-platform Rust daemon. Install on macOS via `cd tools/qmk-hid-host && ./install.sh`. Polls every 100 ms. |

Either works with the **same unmodified firmware** — they speak identical wire
protocol. Pick one (running both at once fights for exclusive HID access).

The firmware works fine without any host app — RuEn falls back to its built-in
`TD(0)` sync ritual.

## Caps Word

Temporary CAPS that auto-exits at the end of the word (Space, Enter, Esc, or any non-letter / non-digit / non-`-`). Inside the word, `-` becomes `_` — handy for `SCREAMING_SNAKE_CASE`.

Two activation methods, pick whichever feels natural:

- **Hold both shifts** (`F` and `J` home-row mods) past `TAPPING_TERM` (200 ms), then release.
- **Double-tap plain Left Shift** (bottom-left corner of the base layer) — works only with `KC_LSFT`, not with mod-tap shifts.

## Hardware

- **Corne (crkbd) rev1** — Pro Micro USB-C, ATmega32u4, Caterina bootloader. MASTER_LEFT.
- Only the **left half** runs this firmware. The right half can stay on stock firmware as long as it speaks the same TRRS serial protocol — all keymap logic runs on the master.

⚠️ Never hot-plug TRRS while USB is connected.
