#!/usr/bin/env python3
"""Convert a Vial `.vil` keymap to keymap-drawer YAML.

Specialised for the foostan Corne (crkbd) split_3x6_3 layout that lives in
`corne.vil` — i.e. 4 layers × 8 rows × 6 cols where rows 0-3 are the left
half (top, home, bottom, thumbs) and rows 4-7 are the right half stored in
matrix-scan order (outer pinky → inner index).

Usage:
    vil2yaml.py <input.vil> -o <output.yaml>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from labels import LAYER_NAMES, QMK_LABELS, USER_LABELS

# ---------------------------------------------------------------------------
# Keycode → keymap-drawer key spec
# ---------------------------------------------------------------------------

MOD_TAP_RE = re.compile(r"^(LCTL|RCTL|LSFT|RSFT|LALT|RALT|LGUI|RGUI|ALL|MEH)_T\((.+)\)$")
MOD_TAP_HOLD = {
    "LCTL": "⌃", "RCTL": "⌃",
    "LSFT": "⇧", "RSFT": "⇧",
    "LALT": "⌥", "RALT": "⌥",
    "LGUI": "⌘", "RGUI": "⌘",
    "ALL": "Hyper",
    "MEH": "Meh",
}

LT_RE = re.compile(r"^LT(\d+)\((.+)\)$")
LT_FULL_RE = re.compile(r"^LT\(\s*(\d+)\s*,\s*(.+)\s*\)$")
MO_RE = re.compile(r"^MO\((\d+)\)$")
TO_RE = re.compile(r"^TO\((\d+)\)$")
TG_RE = re.compile(r"^TG\((\d+)\)$")
TD_RE = re.compile(r"^TD\((\d+)\)$")
SGUI_RE = re.compile(r"^SGUI\((.+)\)$")  # Shift+Gui+key
LSFT_RE = re.compile(r"^LSFT\((.+)\)$")  # Shift+key — used for shifted symbols


SHIFTED = {
    "KC_1": "!", "KC_2": "@", "KC_3": "#", "KC_4": "$", "KC_5": "%",
    "KC_6": "^", "KC_7": "&", "KC_8": "*", "KC_9": "(", "KC_0": ")",
    "KC_MINUS": "_", "KC_EQUAL": "+",
    "KC_LBRACKET": "{", "KC_RBRACKET": "}",
    "KC_BSLASH": "|", "KC_SCOLON": ":", "KC_QUOTE": '"',
    "KC_COMMA": "<", "KC_DOT": ">", "KC_SLASH": "?",
    "KC_GRAVE": "~",
}


def _base_label(kc: str) -> str | dict:
    """Map a leaf keycode (no wrappers) to a label."""
    if kc in USER_LABELS:
        return USER_LABELS[kc]
    if kc in QMK_LABELS:
        return QMK_LABELS[kc]
    if kc.startswith("KC_") and len(kc) == 4:
        return kc[3]  # KC_A → A, KC_1 → 1
    if kc.startswith("KC_F") and kc[3:].isdigit():
        return kc[3:]  # KC_F12 → F12 — but we want "F12" — keep prefix? No, just return last part.
    if kc.startswith("KC_"):
        return kc[3:]
    return kc


def keycode_to_keyspec(kc: str, tap_dance: list) -> dict | str:
    """Turn a single .vil keycode string into a keymap-drawer key spec.

    Returns either a plain string (single legend) or a dict with t/h/s keys
    (tap / hold / shifted legends).
    """
    if kc == -1 or kc is None:
        return {"t": ""}
    if not isinstance(kc, str) or kc in ("KC_NO", ""):
        return ""

    m = MOD_TAP_RE.match(kc)
    if m:
        mod, inner = m.group(1), m.group(2)
        tap = _base_label(inner)
        tap_str = tap if isinstance(tap, str) else tap.get("t", "")
        return {"t": tap_str, "h": MOD_TAP_HOLD[mod]}

    m = LT_RE.match(kc) or LT_FULL_RE.match(kc)
    if m:
        layer_idx, inner = int(m.group(1)), m.group(2).strip()
        tap = _base_label(inner)
        tap_str = tap if isinstance(tap, str) else tap.get("t", "")
        layer_name = LAYER_NAMES[layer_idx] if layer_idx < len(LAYER_NAMES) else f"L{layer_idx}"
        return {"t": tap_str, "h": layer_name}

    m = MO_RE.match(kc)
    if m:
        layer_idx = int(m.group(1))
        layer_name = LAYER_NAMES[layer_idx] if layer_idx < len(LAYER_NAMES) else f"L{layer_idx}"
        return {"t": layer_name, "type": "layer"}

    m = TO_RE.match(kc) or TG_RE.match(kc)
    if m:
        layer_idx = int(m.group(1))
        layer_name = LAYER_NAMES[layer_idx] if layer_idx < len(LAYER_NAMES) else f"L{layer_idx}"
        return {"t": layer_name, "type": "layer"}

    m = TD_RE.match(kc)
    if m:
        idx = int(m.group(1))
        if idx < len(tap_dance):
            slot = tap_dance[idx]
            tap_kc, hold_kc = slot[0], slot[1]
            tap = _base_label(tap_kc)
            hold = _base_label(hold_kc)
            tap_str = tap if isinstance(tap, str) else tap.get("t", "")
            hold_str = hold if isinstance(hold, str) else hold.get("t", "")
            return {"t": tap_str, "h": hold_str}
        return f"TD({idx})"

    m = SGUI_RE.match(kc)
    if m:
        inner = m.group(1).strip()
        inner_label = _base_label(inner)
        inner_str = inner_label if isinstance(inner_label, str) else inner_label.get("t", "")
        return f"⇧⌘{inner_str}"

    m = LSFT_RE.match(kc)
    if m:
        inner = m.group(1).strip()
        if inner in SHIFTED:
            return SHIFTED[inner]
        inner_label = _base_label(inner)
        inner_str = inner_label if isinstance(inner_label, str) else inner_label.get("t", "")
        return f"⇧{inner_str}"

    return _base_label(kc)


# ---------------------------------------------------------------------------
# Layout flattening: 8×6 .vil matrix → 42 physical keys
# ---------------------------------------------------------------------------

def flatten_layer(layer: list[list]) -> list:
    """Return 42 keycodes in keymap-drawer LAYOUT_split_3x6_3 order.

    Right-half rows in .vil are stored outer-pinky-first (matrix-scan), so
    they need reversing to read left-to-right physically.
    """
    out = []
    # 3 main rows: left half (already L→R) + right half (reversed to L→R)
    for left_row, right_row in [(0, 4), (1, 5), (2, 6)]:
        out.extend(layer[left_row])
        out.extend(reversed(layer[right_row]))
    # Thumb cluster: 3 left + 3 right (right is reversed too)
    out.extend(layer[3][3:6])
    out.extend(reversed(layer[7][3:6]))
    return out


# ---------------------------------------------------------------------------
# Combo positions
# ---------------------------------------------------------------------------

def find_position(kc: str, flat_layer: list) -> int | None:
    """First index of `kc` in the flattened layer. None if absent."""
    try:
        return flat_layer.index(kc)
    except ValueError:
        return None


def build_combos(combo_list: list, flat_base: list, tap_dance: list) -> list[dict]:
    """Build keymap-drawer `combos` entries. Empty slots (all KC_NO) are skipped."""
    combos = []
    for slot in combo_list:
        keys, result = slot[:-1], slot[-1]
        live_keys = [k for k in keys if k != "KC_NO"]
        if not live_keys or result == "KC_NO":
            continue
        positions = [find_position(k, flat_base) for k in live_keys]
        if any(p is None for p in positions):
            sys.stderr.write(
                f"warn: combo {live_keys}→{result} skipped (key not found on base layer)\n"
            )
            continue
        label = keycode_to_keyspec(result, tap_dance)
        label_str = label if isinstance(label, str) else label.get("t", "")
        combos.append({"p": positions, "k": label_str, "l": [LAYER_NAMES[0]]})
    return combos


# ---------------------------------------------------------------------------
# YAML emission (no PyYAML dependency — output is simple enough to hand-emit)
# ---------------------------------------------------------------------------

_SAFE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_+\-]*$")
_YAML_KEYWORDS = {"null", "true", "false", "yes", "no", "on", "off", "~"}


def yaml_scalar(v) -> str:
    """Emit a YAML scalar, single-quoting anything that isn't trivially safe.

    Single quotes only need escaping of `'` itself (→ `''`), which is simpler
    than tracking the full set of plain-style YAML pitfalls (=, \\, <, >, *,
    &, |, leading -, reserved words, …).
    """
    if v is None or v == "":
        return "''"
    s = str(v)
    if _SAFE_RE.match(s) and s not in _YAML_KEYWORDS:
        return s
    return "'" + s.replace("'", "''") + "'"


def emit_key(spec) -> str:
    if isinstance(spec, str):
        return yaml_scalar(spec)
    parts = []
    for key in ("t", "h", "s"):
        if key in spec:
            parts.append(f"{key}: {yaml_scalar(spec[key])}")
    if "type" in spec:
        parts.append(f"type: {yaml_scalar(spec['type'])}")
    return "{ " + ", ".join(parts) + " }"


def emit_yaml(layers_spec: dict, combos: list[dict]) -> str:
    lines = []
    lines.append("layout:")
    lines.append("  ortho_layout:")
    lines.append("    split: true")
    lines.append("    rows: 3")
    lines.append("    columns: 6")
    lines.append("    thumbs: 3")
    lines.append("")
    lines.append("layers:")
    for name, keys in layers_spec.items():
        lines.append(f"  {name}:")
        for k in keys:
            lines.append(f"    - {emit_key(k)}")
    if combos:
        lines.append("")
        lines.append("combos:")
        for c in combos:
            pos = ", ".join(str(p) for p in c["p"])
            layers_field = ", ".join(yaml_scalar(l) for l in c["l"])
            lines.append(f"  - {{ p: [{pos}], k: {yaml_scalar(c['k'])}, l: [{layers_field}] }}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("vil", type=Path, help="Input .vil file")
    ap.add_argument("-o", "--output", type=Path, required=True, help="Output YAML")
    args = ap.parse_args()

    data = json.loads(args.vil.read_text())
    layout = data["layout"]
    tap_dance = data.get("tap_dance", [])
    combo = data.get("combo", [])

    flat_layers = [flatten_layer(layer) for layer in layout]
    layers_spec = {
        LAYER_NAMES[i]: [keycode_to_keyspec(kc, tap_dance) for kc in flat]
        for i, flat in enumerate(flat_layers)
    }
    combos = build_combos(combo, flat_layers[0], tap_dance)

    args.output.write_text(emit_yaml(layers_spec, combos))
    print(f"wrote {args.output} ({len(layers_spec)} layers, {len(combos)} combos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
