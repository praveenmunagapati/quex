#include <data/check.h>

#ifdef __QUEX_OPTION_COUNTER
void
QUEX_NAME(TEST_MODE_counter)(QUEX_TYPE_ANALYZER* me, QUEX_TYPE_CHARACTER* LexemeBegin, QUEX_TYPE_CHARACTER* LexemeEnd)
{
#   define self (*me)
    QUEX_TYPE_CHARACTER* iterator    = LexemeBegin;
    QUEX_TYPE_CHARACTER  input       = (QUEX_TYPE_CHARACTER)0;
    __QUEX_IF_COUNT_SHIFT_VALUES();

    __quex_assert(LexemeBegin <= LexemeEnd);
    for(iterator=LexemeBegin; iterator < LexemeEnd; ) {
    input = *((iterator));
    __quex_debug("Init State\n");
    __quex_debug_state(107);
    if( input < 0x40 ) {
        switch( input ) {
            case 0x0: 
            case 0x1: 
            case 0x2: 
            case 0x3: 
            case 0x4: 
            case 0x5: 
            case 0x6: 
            case 0x7: 
            case 0x8: 
            case 0x9: goto _115;
            case 0xA: goto _116;
            case 0xB: 
            case 0xC: 
            case 0xD: 
            case 0xE: 
            case 0xF: 
            case 0x10: 
            case 0x11: 
            case 0x12: 
            case 0x13: 
            case 0x14: 
            case 0x15: 
            case 0x16: 
            case 0x17: 
            case 0x18: 
            case 0x19: 
            case 0x1A: 
            case 0x1B: 
            case 0x1C: 
            case 0x1D: 
            case 0x1E: 
            case 0x1F: 
            case 0x20: 
            case 0x21: 
            case 0x22: 
            case 0x23: 
            case 0x24: 
            case 0x25: 
            case 0x26: 
            case 0x27: 
            case 0x28: 
            case 0x29: 
            case 0x2A: 
            case 0x2B: 
            case 0x2C: 
            case 0x2D: 
            case 0x2E: 
            case 0x2F: 
            case 0x30: 
            case 0x31: 
            case 0x32: 
            case 0x33: 
            case 0x34: 
            case 0x35: 
            case 0x36: 
            case 0x37: 
            case 0x38: 
            case 0x39: 
            case 0x3A: 
            case 0x3B: goto _115;
            case 0x3C: goto _117;
            case 0x3D: goto _115;
            case 0x3E: goto _118;
            case 0x3F: goto _119;

        }
    } else {
        if( input < 0xD809 ) {
            if( input < 0xD800 ) {
                goto _115;
            } else if( input < 0xD808 ) {
                goto _120;
            } else {
                goto _121;
            }
        } else {
            if( input < 0xDC00 ) {
                goto _120;
            } else if( input < 0xE000 ) {

            } else if( input < 0x10000 ) {
                goto _115;
            } else {

            }
        }
    }
    __quex_debug_drop_out(107);

goto _123; /* TERMINAL_FAILURE */

    __quex_assert_no_passage();
_121: /* (108 from 107) */

_108:

    ++((iterator));
    input = *((iterator));
    __quex_debug_state(108);
    if( input < 0xDC02 ) {
        switch( input ) {
            case 0xDC00: goto _117;
            case 0xDC01: goto _115;

        }
    } else {
        if( input == 0xDC02 ) {
            goto _118;
        } else if( input == 0xDC03 ) {
            goto _119;
        } else if( input < 0xE000 ) {
            goto _115;
        } else {

        }
    }
    __quex_debug_drop_out(108);

goto _123; /* TERMINAL_FAILURE */

    __quex_assert_no_passage();
_120: /* (109 from 107) */

_109:

    ++((iterator));
    input = *((iterator));
    __quex_debug_state(109);
    if( input >= 0xE000 ) {

    } else if( input >= 0xDC00 ) {
        goto _115;
    } else {

    }
    __quex_debug_drop_out(109);

goto _123; /* TERMINAL_FAILURE */

    __quex_assert_no_passage();
_116: /* (110 from 107) */



    ++((iterator));
    __quex_debug_state(110);
    __quex_debug_drop_out(110);
goto TERMINAL_21;

    __quex_assert_no_passage();
_115: /* (111 from 108) (111 from 109) (111 from 107) */



    ++((iterator));
    __quex_debug_state(111);
    __quex_debug_drop_out(111);
goto TERMINAL_23;

    __quex_assert_no_passage();
_118: /* (112 from 107) (112 from 108) */



    ++((iterator));
    __quex_debug_state(112);
    __quex_debug_drop_out(112);
goto TERMINAL_22;

    __quex_assert_no_passage();
_119: /* (113 from 107) (113 from 108) */



    ++((iterator));
    __quex_debug_state(113);
    __quex_debug_drop_out(113);
goto TERMINAL_25;

    __quex_assert_no_passage();
_117: /* (114 from 108) (114 from 107) */



    ++((iterator));
    __quex_debug_state(114);
    __quex_debug_drop_out(114);
goto TERMINAL_24;
TERMINAL_21:
        __quex_debug("* terminal 21:   \n");
        __QUEX_IF_COUNT_LINES_ADD((size_t)1);
        __QUEX_IF_COUNT_COLUMNS_SET((size_t)1);
            continue;
TERMINAL_22:
        __quex_debug("* terminal 22:   \n");
        __QUEX_IF_COUNT_COLUMNS_ADD((size_t)2);
            continue;
TERMINAL_23:
        __quex_debug("* terminal 23:   \n");
        __QUEX_IF_COUNT_COLUMNS_ADD((size_t)1);
            continue;
TERMINAL_24:
        __quex_debug("* terminal 24:   \n");
                    continue;
TERMINAL_25:
        __quex_debug("* terminal 25:   \n");
        __QUEX_IF_COUNT_COLUMNS_ADD((size_t)3);
            continue;
    }
    __quex_assert(iterator == LexemeEnd); /* Otherwise, lexeme violates codec character boundaries. */
   return;
_123:
    QUEX_ERROR_EXIT("State machine failed.");
#  undef self
}
#endif /* __QUEX_OPTION_COUNTER */