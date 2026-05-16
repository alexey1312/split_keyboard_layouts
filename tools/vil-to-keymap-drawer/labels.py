"""Human-readable labels for corne.vil keycodes.

Mirrors the USER index → LG_* mapping from `firmware/README.md`.
Anything not listed here falls through to keymap-drawer's built-in QMK map
(KC_ prefix stripped, single letters/digits stay as-is).
"""

# USER00..USER35 — RuEn custom keycodes (QK_KB+N).
# Format: short legend shown on the key. Many of these auto-switch the OS
# input source to EN, type the symbol, then switch back — that's hidden detail,
# the key just looks like the symbol it produces.
USER_LABELS = {
    "USER00": {"t": "RuEn", "s": "⇄"},
    "USER01": {"t": "RuEn", "s": "sync"},
    "USER02": {"t": "RuEn", "s": "EN"},
    "USER03": {"t": "RuEn", "s": "RU"},
    "USER04": ".",
    "USER05": ",",
    "USER06": ";",
    "USER07": ":",
    "USER08": '"',
    "USER09": "?",
    "USER10": "/",
    "USER11": "[",
    "USER12": "]",
    "USER13": "{",
    "USER14": "}",
    "USER15": "<",
    "USER16": ">",
    "USER17": "`",
    "USER18": "~",
    "USER19": "@",
    "USER20": "#",
    "USER21": "$",
    "USER22": "^",
    "USER23": "&",
    "USER24": "|",
    "USER25": "'",
    "USER26": "№",
    "USER27": "%",
    "USER28": {"t": "RuEn", "s": "Mac"},
    "USER29": "б",
    "USER30": "ю",
    "USER31": "ж",
    "USER32": "э",
    "USER33": "х",
    "USER34": "ъ",
    "USER35": "ё",
}

# Plain QMK keycodes — only overrides where the built-in mapping is ugly or
# missing. keymap-drawer already strips KC_ and knows basic punctuation.
QMK_LABELS = {
    "KC_ESCAPE": "Esc",
    "KC_TAB": "⇥",
    "KC_BSPACE": "⌫",
    "KC_ENTER": "⏎",
    "KC_SPACE": "␣",
    "KC_LSHIFT": "⇧",
    "KC_RSHIFT": "⇧",
    "KC_LCTRL": "⌃",
    "KC_RCTRL": "⌃",
    "KC_LALT": "⌥",
    "KC_RALT": "⌥",
    "KC_LGUI": "⌘",
    "KC_RGUI": "⌘",
    "KC_LBRACKET": "[",
    "KC_RBRACKET": "]",
    "KC_QUOTE": "'",
    "KC_SCOLON": ";",
    "KC_COMMA": ",",
    "KC_DOT": ".",
    "KC_SLASH": "/",
    "KC_BSLASH": "\\",
    "KC_NONUS_BSLASH": "\\",
    "KC_LEFT": "←",
    "KC_RIGHT": "→",
    "KC_UP": "↑",
    "KC_DOWN": "↓",
    "KC_MS_L": "M←",
    "KC_MS_R": "M→",
    "KC_MS_U": "M↑",
    "KC_MS_D": "M↓",
    "KC_BTN1": "M1",
    "KC_BTN2": "M2",
    "KC_VOLU": "Vol+",
    "KC_VOLD": "Vol-",
    "KC_MUTE": "Mute",
    "KC_MPLY": "Play",
    "KC_MNXT": "Next",
    "KC_MPRV": "Prev",
    "KC_KP_ASTERISK": "*",
    "KC_KP_EQUAL": "=",
    "KC_KP_MINUS": "-",
    "KC_LCPO": "(",   # Left-Ctrl-Paren-Open (used in combo output)
    "KC_RSPC": ")",   # Right-Shift-Paren-Close
    "KC_TRNS": {"t": "▽"},
    "KC_NO": "",
    "QK_BOOT": "BOOT",
}

LAYER_NAMES = ["Base", "Lower", "Raise", "Adjust"]
