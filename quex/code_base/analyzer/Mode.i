/* -*- C++ -*-  vim:set syntax=cpp: 
 *
 * (C) 2004-2010 Frank-Rene Schaefer
 * ABSOLUTELY NO WARRANTY              */
#ifndef __QUEX_INCLUDE_GUARD__ANALYZER__MODE_I
#define __QUEX_INCLUDE_GUARD__ANALYZER__MODE_I

QUEX_NAMESPACE_MAIN_OPEN

    QUEX_INLINE __QUEX_TYPE_ANALYZER_RETURN_VALUE
    QUEX_NAME(Mode_uncallable_analyzer_function)(QUEX_TYPE_ANALYZER* me)
    { 
        __quex_assert(0); 
#       if defined (QUEX_OPTION_TOKEN_POLICY_QUEUE)
        return; 
#       else
        return (__QUEX_TYPE_ANALYZER_RETURN_VALUE)0;
#       endif
    }

#   ifdef __QUEX_OPTION_INDENTATION_TRIGGER_SUPPORT        
    QUEX_INLINE void
    QUEX_NAME(Mode_on_indent_null_function)(QUEX_TYPE_ANALYZER*    me, 
                                            QUEX_TYPE_CHARACTER*   LexemeBegin, 
                                            QUEX_TYPE_CHARACTER*   LexemeEnd)

    { }
    QUEX_INLINE void
    QUEX_NAME(Mode_on_dedent_null_function)(QUEX_TYPE_ANALYZER*    me, 
                                            size_t                 ClosedN, 
                                            QUEX_TYPE_CHARACTER*   LexemeBegin, 
                                            QUEX_TYPE_CHARACTER*   LexemeEnd)

    { }
    QUEX_INLINE void
    QUEX_NAME(Mode_on_nodent_null_function)(QUEX_TYPE_ANALYZER*   me, 
                                            QUEX_TYPE_CHARACTER*  LexemeBegin, 
                                            QUEX_TYPE_CHARACTER*  LexemeEnd)
    { }
#   endif

    QUEX_INLINE void
    QUEX_NAME(Mode_on_entry_exit_null_function)(QUEX_TYPE_ANALYZER* me, 
                                                const QUEX_NAME(Mode)* TheMode) 
    { }

QUEX_NAMESPACE_MAIN_CLOSE

#endif /* __QUEX_INCLUDE_GUARD__ANALYZER__MODE_I */
