#pragma once
#include "quantum.h"

enum ruen_custom_keycodes {
    LG_START = QK_KB,  // Vial maps customKeycodes to QK_KB range (0x7E00..0x7E3F), not QK_USER

    LG_TOGGLE = LG_START,
    LG_SYNC,
    LG_SET_EN,
    LG_SET_RU,

    // Punctuation with same physical position in EN and RU
    LG_DOT,
    LG_COMMA,
    LG_SCLN,
    LG_COLON,
    LG_DQUO,
    LG_QUES,
    LG_SLASH,

    // Symbols that only exist in English layout — keyboard auto-switches to EN to type them
    LG_EN_START,
    LG_LBR = LG_EN_START,
    LG_RBR,
    LG_LCBR,
    LG_RCBR,
    LG_LT,
    LG_GT,
    LG_GRAVE,
    LG_TILD,
    LG_AT,
    LG_HASH,
    LG_DLR,
    LG_CIRC,
    LG_AMPR,
    LG_PIPE,
    LG_QUOTE,

    LG_EN_END = LG_QUOTE,

    // Russian-only symbol
    LG_NUM,

    // Mac-specific
    LG_PERC,
    LG_TG_MAC,

    // Russian letters that share physical position with EN punctuation
    LG_RU_BE,       // , -> б
    LG_RU_YU,       // . -> ю
    LG_RU_ZHE,      // ; -> ж
    LG_RU_E,        // ' -> э
    LG_RU_KHA,      // [ -> х
    LG_RU_HRD_SGN,  // ] -> ъ
    LG_RU_YO,       // ` -> ё

    LG_END,
};

enum { LANG_EN = 0, LANG_RU };

bool pre_process_record_ruen(uint16_t keycode, keyrecord_t *record);
bool process_record_ruen(uint16_t keycode, keyrecord_t *record);
void housekeeping_task_ruen(void);

uint8_t get_cur_lang(void);
void    set_ruen_mac_layout(bool mac_layout);
bool    get_ruen_mac_layout(void);
