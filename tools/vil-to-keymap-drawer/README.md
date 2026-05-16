# vil-to-keymap-drawer

Renders `corne.vil` into a per-layer SVG diagram (`imgs/corne-layout.svg`)
using [caksoylar/keymap-drawer](https://github.com/caksoylar/keymap-drawer).
Knows about the 36 RuEn `USER00..USER35` keycodes from
[`firmware/README.md`](../../firmware/README.md) and renders each with its
human-readable label (`RuEn ⇄`, `[`, `}`, `б`, …).

## Setup

`keymap-drawer` needs Python 3.12+. Quickest path:

```sh
pipx install keymap-drawer
```

Or in a venv:

```sh
python3.12 -m venv .venv
.venv/bin/pip install keymap-drawer
export KEYMAP=$PWD/.venv/bin/keymap
```

## Run

```sh
./render.sh
```

Writes `corne.yaml` next to the script (intermediate, gitignored) and
`imgs/corne-layout.svg` at the repo root. Re-run after every `corne.vil`
edit.

Override Python / keymap binaries via env vars: `PYTHON=python3.12 KEYMAP=./.venv/bin/keymap ./render.sh`.

## What's in here

- `vil2yaml.py` — converter `.vil` → keymap-drawer YAML. Flattens the 8×6
  `.vil` matrix into the physical 42-key Corne order (right half reversed
  from matrix-scan), unwraps `LCTL_T()`, `LT1()`, `MO()`, `TD()`, `SGUI()`,
  `LSFT(KC_N)` (shifted-symbols), and `USERnn` references.
- `labels.py` — `USER00..USER35` → label map, plus QMK keycode overrides
  for nicer glyphs (`⌫`, `⏎`, `⌘`, etc.). Edit here to change any legend.
- `render.sh` — convenience runner.

## Adding a new RuEn keycode

1. Append it to the enum in `firmware/crkbd_ruen/ruen.h` and
   `firmware/keymap/vial.json` (per the rules in `firmware/README.md`).
2. Add a `"USER<NN>": "<label>"` entry to `labels.py`.
3. Re-run `./render.sh`.

## Limitations

- Layout is fixed to Corne split_3x6_3 (3 main rows + 3 thumbs per side).
  Sofle is not supported by this script.
- Combos are assumed to live on the Base layer only.
- No PNG output — render the SVG in a browser or convert with
  `rsvg-convert imgs/corne-layout.svg -o imgs/corne-layout.png`.
