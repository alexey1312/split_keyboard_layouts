# qmk-hid-host integration

[qmk-hid-host](https://github.com/zzeneg/qmk-hid-host) is a small cross-platform
Rust daemon that watches the OS-side input source and ships the current
layout over Raw HID to the keyboard. This folder wires it up to the Corne
firmware's RuEn engine so that **any** language switch — Cmd+Space from the
MacBook keyboard, mouse-click on the menu bar input source picker, Punto /
Caramba auto-conversion — keeps `cur_lang` in sync. The classic RuEn desync
goes away.

## How it fits together

```
   ┌──────────────────────────┐
   │  macOS Input Source      │
   │  (Cmd+Space, Punto, …)   │
   └────────────┬─────────────┘
                │  TIS notification
                ▼
   ┌──────────────────────────┐
   │  qmk-hid-host (daemon)   │  reads via TISCopyCurrentKeyboardLayoutInputSource
   └────────────┬─────────────┘
                │  USB Raw HID:  [0xAC, idx]
                ▼
   ┌──────────────────────────┐
   │  crkbd.c::raw_hid_receive_kb │  calls lang_sync_to(idx==0 ? LANG_EN : LANG_RU)
   └────────────┬─────────────┘
                ▼
        cur_lang  (RuEn state)
```

Single byte protocol, no return channel needed. Firmware never sends
Cmd+Space in response, so there is no feedback loop.

## Install (macOS)

```bash
cd tools/qmk-hid-host
./install.sh
```

The script:

1. Downloads the latest qmk-hid-host binary for your CPU (arm64 / x86_64)
   into `~/.local/bin/`.
2. Copies `config.json` into `~/.config/qmk-hid-host/` (skipped if it
   already exists).
3. Installs `com.user.qmk-hid-host.plist` LaunchAgent into
   `~/Library/LaunchAgents/` with `$HOME` interpolated, and starts it via
   `launchctl bootstrap`.
4. Logs are written to `~/Library/Logs/qmk-hid-host.log` (stdout) and
   `qmk-hid-host.err.log` (stderr).

To remove:

```bash
./uninstall.sh
```

## Configuration

`config.json` ships with two entries that match the default macOS layouts
installed on the development machine:

```json
{
  "devices": [{ "productId": "0x0001", "name": "Corne" }],
  "layouts": ["ABC", "Russian"]
}
```

- `productId` matches the Corne (set in `firmware/keymap/vial.json`).
- `layouts` is an ordered list of suffixes of `TISPropertyInputSourceID`
  (the part after the last dot). The daemon sends the **index** of the
  active layout in this array, not the name. So:
    - `ABC` (`com.apple.keylayout.ABC`) → index 0 → firmware sees `LANG_EN`
    - `Russian` (`com.apple.keylayout.Russian`) → index 1 → `LANG_RU`

If you switch to the Ilya Birman Typography Layout, change `layouts` to
something like `["English-IlyaBirmanTypography", "Russian-IlyaBirmanTypography"]`.
The firmware treats `data[1] == 0` as English and **anything else** as
Russian, so the exact non-zero index doesn't matter — you can list as many
Russian-variant layouts as you want at indices 1, 2, 3 and they will all
sync to `LANG_RU`.

To discover the suffix for any layout currently selected:

```bash
defaults read com.apple.HIToolbox AppleSelectedInputSources
```

Look at `KeyboardLayout Name` (it is the last segment of the
`InputSourceID`).

## How to know it works

After install:

```bash
tail -f ~/Library/Logs/qmk-hid-host.log
```

You should see a line like `new layout: 'Russian', layout list: ["ABC", "Russian"]`
every time you switch the OS input source. Then in TextEdit press
`RuEn .` (USER04 on Layer 1): in English layout it types `.`, in Russian
layout it types whatever the engine maps to (depending on `mac_layout`,
either `ю` via `KC_DOT` or a Russian-aware variant). The firmware decides
based on its (now correctly synced) `cur_lang`.

If the punctuation comes out wrong, log into the file above and you'll see
why — most often `layouts` is mis-spelled or the current input source name
isn't in the array.

## Caveats

- **Vial.app and the daemon are mutually exclusive.** Raw HID on macOS is
  single-owner per interface — if Vial is running and connected to the
  Corne, the daemon cannot open the endpoint and logs
  `hid_open_path: ... exclusive access and device already open` once per
  second. Quit Vial when you want sync; reopen Vial when you want to edit
  the keymap. The daemon auto-reconnects within ~5 seconds.
  Quick diagnostic: `ps aux | grep -iE "vial|qmk-hid" | grep -v grep`.
- **No daemon, no sync.** On another mac that doesn't run qmk-hid-host the
  firmware falls back to its built-in `cur_lang` tracking (`RuEn Toggle`
  via `TD(0)` is still authoritative there). The keyboard is otherwise
  fully functional — RuEn just goes back to its pre-daemon behaviour.
- **Layouts list is ordered.** Don't reorder it without updating any
  remote machines using the same config — the firmware only cares about
  index, not name.
- **Daemon polls every 100 ms.** Not event-driven (qmk-hid-host upstream
  uses polling on macOS). Up to a 100 ms lag between OS layout change and
  firmware state — invisible in practice.
- **macOS gatekeeper.** First launch of the downloaded binary may be
  blocked by Gatekeeper. If `launchctl bootstrap` fails with an
  "operation not permitted" error, run the binary once manually
  (`~/.local/bin/qmk-hid-host -c ~/.config/qmk-hid-host/config.json`),
  approve in System Settings → Privacy & Security, then re-run
  `./install.sh`.
