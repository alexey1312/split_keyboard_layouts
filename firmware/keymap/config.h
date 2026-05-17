/*
Copyright 2019 @foostan
Copyright 2020 Drashna Jaelre <@drashna>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#pragma once

#define VIAL_KEYBOARD_UID {0x3B, 0x6B, 0xA0, 0x29, 0x80, 0x56, 0xED, 0xD1}
#define VIAL_UNLOCK_COMBO_ROWS {0, 0}
#define VIAL_UNLOCK_COMBO_COLS {0, 1}

#undef DYNAMIC_KEYMAP_LAYER_COUNT
#define DYNAMIC_KEYMAP_LAYER_COUNT 4

// Mod-tap tuning for fast typing on home-row mods.
// IGNORE_MOD_TAP_INTERRUPT is now QMK's default and the flag was removed.
// TAPPING_TERM raised from 180 to 200 to reduce false hold-trigger when
// typing fast (e.g. Russian "л" lingering and producing RGui+next-key).
#define TAPPING_TERM 200

#define VIAL_COMBO_ENTRIES 16
#define COMBO_TERM 50

// Flash diet for ATmega32u4 (~420 B free before these).
// All of the disabled features below are unused in corne.vil; LTO will drop
// the dead code paths once the macros are defined.
#define NO_ACTION_ONESHOT   // QMK one-shot mods — not used
#define NO_ACTION_MACRO     // legacy TMK MACRO() actions — Vial uses dynamic_keymap macros instead
#define NO_ACTION_FUNCTION  // legacy fn_actions[] — replaced by process_record_user long ago
// NO_DEBUG / NO_PRINT are injected on the command line by QMK's build system,
// so we guard with #ifndef as a safety net for direct (non-bootstrap) builds.
#ifndef NO_DEBUG
#    define NO_DEBUG
#endif
#ifndef NO_PRINT
#    define NO_PRINT
#endif
#define LAYER_STATE_8BIT    // we use 4 layers, 8-bit layer_state_t is enough

// Caps Word activation:
//   * Both shifts held simultaneously past TAPPING_TERM (works with our
//     home-row mod-tap shifts LSFT_T(KC_F) and RSFT_T(KC_J) — hold both
//     until the tapping term, then release).
//   * Double tap on the plain LSHIFT key (Layer 0, row 2 col 0 of corne.vil)
//     — works with KC_LSFT only, NOT with mod-tap shifts.
// Either method exits on Space, Enter, Tab, Esc, or any non-word key.
#define BOTH_SHIFTS_TURNS_ON_CAPS_WORD
#define DOUBLE_TAP_SHIFT_TURNS_ON_CAPS_WORD

//#define USE_MATRIX_I2C
#ifdef KEYBOARD_crkbd_rev1_legacy
#    undef USE_I2C
#    define USE_SERIAL
#endif

/* Select hand configuration */

#define MASTER_LEFT
// #define MASTER_RIGHT
// #define EE_HANDS

#define USE_SERIAL_PD2
#ifdef RGBLIGHT_ENABLE
#    undef RGBLIGHT_LED_COUNT
#    define RGBLIGHT_ANIMATIONS
#    define RGBLIGHT_LED_COUNT 54
#    undef RGBLED_SPLIT
#    define RGBLED_SPLIT \
        { 27, 27 }
#    define RGBLIGHT_LIMIT_VAL 120
#    define RGBLIGHT_HUE_STEP  10
#    define RGBLIGHT_SAT_STEP  17
#    define RGBLIGHT_VAL_STEP  17
#endif

#define OLED_FONT_H "keyboards/crkbd/lib/glcdfont.c"
