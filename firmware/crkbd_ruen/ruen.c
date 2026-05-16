#include "ruen.h"

static uint8_t  cur_lang         = LANG_EN;
static bool     mac_layout       = false;
static bool     should_revert_ru = false;
static uint32_t revert_time      = 0;

uint8_t get_cur_lang(void) {
    return cur_lang;
}

void set_ruen_mac_layout(bool layout) {
    mac_layout = layout;
}

bool get_ruen_mac_layout(void) {
    return mac_layout;
}

static void set_lang(uint8_t lang) {
    if (cur_lang == lang) return;
    uint8_t mods = get_mods();
    if (mods != 0) del_mods(mods);
    if (keymap_config.swap_lctl_lgui) {
        register_code(KC_LCTL);
        tap_code(KC_SPACE);
        wait_ms(50);
        unregister_code(KC_LCTL);
        wait_ms(50);
    } else {
        register_code(KC_LGUI);
        tap_code(KC_SPACE);
        wait_ms(50);
        unregister_code(KC_LGUI);
        wait_ms(50);
    }
    if (mods != 0) add_mods(mods);
    cur_lang = lang;
}

static void lang_toggle(void) {
    set_lang(cur_lang == LANG_EN ? LANG_RU : LANG_EN);
}

static void lang_sync(void) {
    cur_lang = (cur_lang == LANG_EN) ? LANG_RU : LANG_EN;
}

static const uint16_t en_table[] = {
    KC_LBRC,  // LG_LBR
    KC_RBRC,  // LG_RBR
    KC_LCBR,  // LG_LCBR
    KC_RCBR,  // LG_RCBR
    KC_LT,    // LG_LT
    KC_GT,    // LG_GT
    KC_GRAVE, // LG_GRAVE
    KC_TILD,  // LG_TILD
    KC_AT,    // LG_AT
    KC_HASH,  // LG_HASH
    KC_DLR,   // LG_DLR
    KC_CIRC,  // LG_CIRC
    KC_AMPR,  // LG_AMPR
    KC_PIPE,  // LG_PIPE
    KC_QUOT,  // LG_QUOTE
};

bool pre_process_record_ruen(uint16_t keycode, keyrecord_t *record) {
    if (!record->event.pressed) return true;

    switch (keycode) {
        case KC_A ... KC_Z:
        case S(KC_A)... S(KC_Z):
        case KC_LBRC ... KC_RBRC:
        case S(KC_LBRC)... S(KC_RBRC):
        case KC_SCLN ... KC_SLSH:
        case S(KC_SCLN)... S(KC_SLSH):
            if (should_revert_ru) {
                should_revert_ru = false;
                set_lang(LANG_RU);
            }
            break;
        case LG_SET_EN:
        case LG_TOGGLE:
            if (should_revert_ru) {
                should_revert_ru = false;
                set_lang(LANG_EN);
            }
            break;
    }

    return true;
}

static bool process_russian_letter(uint8_t keycode) {
    if (cur_lang == LANG_RU) {
        tap_code(keycode);
    }
    return false;
}

bool process_record_ruen(uint16_t keycode, keyrecord_t *record) {
    if (!(LG_START <= keycode && keycode < LG_END)) return true;
    if (!record->event.pressed) return false;

    switch (keycode) {
        case LG_TOGGLE:
            lang_toggle();
            return false;

        case LG_SYNC:
            lang_sync();
            return false;

        case LG_SET_EN:
            set_lang(LANG_EN);
            return false;

        case LG_SET_RU:
            set_lang(LANG_RU);
            return false;

        case LG_DOT:
            tap_code16(cur_lang == LANG_EN ? KC_DOT : mac_layout ? S(KC_7) : KC_SLASH);
            return false;

        case LG_COMMA:
            tap_code16(cur_lang == LANG_EN ? KC_COMMA : mac_layout ? S(KC_6) : S(KC_SLASH));
            return false;

        case LG_SCLN:
            tap_code16(cur_lang == LANG_EN ? KC_SCLN : mac_layout ? S(KC_8) : S(KC_4));
            return false;

        case LG_COLON:
            tap_code16(cur_lang == LANG_EN ? KC_COLON : mac_layout ? S(KC_5) : S(KC_6));
            return false;

        case LG_DQUO:
            tap_code16(cur_lang == LANG_EN ? KC_DQUO : S(KC_2));
            return false;

        case LG_QUES:
            tap_code16(cur_lang == LANG_EN || mac_layout ? KC_QUES : S(KC_7));
            return false;

        case LG_SLASH:
            tap_code16(cur_lang == LANG_EN || mac_layout ? KC_SLASH : LSFT(KC_BSLS));
            return false;

        case LG_PERC:
            tap_code16(cur_lang == LANG_RU && mac_layout ? LSFT(KC_4) : LSFT(KC_5));
            return false;

        case LG_TG_MAC:
            mac_layout = !mac_layout;
            return false;

        case LG_EN_START ... LG_EN_END: {
            if (cur_lang == LANG_RU) {
                set_lang(LANG_EN);
                should_revert_ru = true;
            }
            tap_code16(en_table[keycode - LG_EN_START]);
            revert_time = timer_read32();
            return false;
        }

        case LG_NUM: {
            uint8_t lang = cur_lang;
            set_lang(LANG_RU);
            tap_code16(LSFT(KC_3));
            set_lang(lang);
            return false;
        }

        case LG_RU_BE:
            return process_russian_letter(KC_COMMA);
        case LG_RU_YU:
            return process_russian_letter(KC_DOT);
        case LG_RU_ZHE:
            return process_russian_letter(KC_SCLN);
        case LG_RU_E:
            return process_russian_letter(KC_QUOT);
        case LG_RU_HRD_SGN:
            return process_russian_letter(KC_RBRC);
        case LG_RU_KHA:
            return process_russian_letter(KC_LBRC);
        case LG_RU_YO:
            return process_russian_letter(KC_GRAVE);
    }

    return true;
}

void housekeeping_task_ruen(void) {
    if (timer_elapsed32(revert_time) < 500) return;

    if (should_revert_ru) {
        should_revert_ru = false;
        set_lang(LANG_RU);
    }
}

// User hooks are wired in keyboards/crkbd/crkbd.c via process_record_kb.
