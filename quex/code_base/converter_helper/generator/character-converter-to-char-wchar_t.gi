/* -*- C++ -*- vim: set syntax=cpp:
 * PURPOSE: 
 *
 * Generate string converter functions which convert a string from one 
 * character codec into 'char' or 'wchar'. The conversion is implemented by means
 * of a character converter function given by:
 *
 *            __QUEX_CONVERTER_CHAR(FROM, TO)(in, out); 
 *
 * which converts only a single character. The converter function must
 * be defined before the inclusion of this file. This file implements default
 * converters for char and wchar. So for 'char' utf8 us used for 'wchar' utf16
 * or utf32 are used depending on the system's settings.
 *
 * This generator is a special case of what is implemented in 'string-converter.gi'.
 *
 * (C) 2010-2012 Frank-Rene Schaefer 
 * ABSOLUTELY NO WARRANTY                                                    */

#if   ! defined(__QUEX_FROM)
#   error "__QUEX_FROM must be defined!"
#elif ! defined(__QUEX_FROM_TYPE)
#   error "__QUEX_FROM_TYPE must be defined!"
#elif   defined(__QUEX_TO_TYPE) 
#   error "__QUEX_TO_TYPE must NOT be defined!"
#elif   defined(__QUEX_TO) 
#   error "__QUEX_TO must NOT be defined!"
#elif   defined(__QUEX_TO_CODEC)
#   error "__QUEX_TO_CODEC must NOT be defined!"
#endif

QUEX_INLINE void
__QUEX_CONVERTER_CHAR(__QUEX_FROM, char)(const __QUEX_FROM_TYPE**  source_pp, 
                                         char**                    drain_pp)  
{
    switch( sizeof(char) )
    {
    case 1:
        __QUEX_CONVERTER_CHAR(__QUEX_FROM, utf8)(source_pp, (uint8_t**)drain_pp);
        break;
    case 2:
        __QUEX_CONVERTER_CHAR(__QUEX_FROM, utf16)(source_pp, (uint16_t**)drain_pp);
        break;
    case 4:
        __QUEX_CONVERTER_CHAR(__QUEX_FROM, utf32)(source_pp, (uint32_t**)drain_pp);
        break;
    default:
        /* Cannot be handled */
        __quex_assert(false);
}

#if ! defined(__QUEX_OPTION_WCHAR_T_DISABLED)
    QUEX_INLINE void
    __QUEX_CONVERTER_CHAR(__QUEX_FROM, wchar_t)(const __QUEX_FROM_TYPE**  source_pp, 
                                                wchar_t**                 drain_pp)  
    {
        switch( sizeof(wchar_t) )
        {
        case 1:
            __QUEX_CONVERTER_CHAR(__QUEX_FROM, utf8)(source_pp, (uint8_t**)drain_pp);
            break;
        case 2:
            __QUEX_CONVERTER_CHAR(__QUEX_FROM, utf16)(source_pp, (uint16_t**)drain_pp);
            break;
        case 4:
            __quex_assert(sizeof(char) == 4);
            __QUEX_CONVERTER_CHAR(__QUEX_FROM, utf32)(source_pp, (uint32_t**)drain_pp);
            break;
        default:
            __quex_assert(false); /* Cannot be handled */
        }
    }
#endif

