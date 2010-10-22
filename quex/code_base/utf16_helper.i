#ifndef __QUEX_INCLUDE_GUARD__UTF16_HELPER_I
#define __QUEX_INCLUDE_GUARD__UTF16_HELPER_I
/* -*- C++ -*- vim: set syntax=cpp:
 *
 * (C) 2005-2010 Frank-Rene Schaefer                                                */

QUEX_NAMESPACE_MAIN_OPEN

QUEX_INLINE uint8_t*
QUEX_NAME(utf16_to_utf8_string)(const QUEX_TYPE_CHARACTER* Source, size_t SourceSize,
                                uint8_t* Drain, size_t DrainSize)
{
}

QUEX_INLINE uint32_t*
QUEX_NAME(utf16_to_ucs4_string)(const QUEX_TYPE_CHARACTER* Source, size_t SourceSize,
                                uint32_t* Drain, size_t DrainSize)
{
}

#if ! defined(__QUEX_OPTION_PLAIN_C)
QUEX_INLINE std::string
QUEX_NAME(utf16_to_utf8_string)(const std::basic_string<QUEX_TYPE_CHARACTER>& Source)
{ 
}

QUEX_INLINE std::basic_string<uint32_t>
QUEX_NAME(utf16_to_ucs4_string)(const std::basic_string<QUEX_TYPE_CHARACTER>& Source)
{
}

#endif /* __QUEX_OPTION_PLAIN_C */

QUEX_NAMESPACE_MAIN_CLOSE

#endif /* __QUEX_INCLUDE_GUARD__UTF16_HELPER_I */

