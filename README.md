# Custom keyboard layouts

Vial keymaps for split keyboards, optimised for **macOS** (Russian/English typing) with home-row mods, layer-tap thumb cluster, combos for brackets, and a built-in RuEn engine for unified punctuation between layouts.

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

### RuEn keycodes

36 custom keycodes (visible in Vial **User** tab as `RuEn Toggle`, `RuEn .`, `RuEn [` …). Full list in [`firmware/README.md`](firmware/README.md).

## Hardware

- **Corne (crkbd) rev1** — Pro Micro USB-C, ATmega32u4, Caterina bootloader. MASTER_LEFT.
- Only the **left half** runs this firmware. The right half can stay on stock firmware as long as it speaks the same TRRS serial protocol — all keymap logic runs on the master.

⚠️ Never hot-plug TRRS while USB is connected.
