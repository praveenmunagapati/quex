/* -*- C++ -*-   vim: set syntax=cpp:
 *
 * No include guards, the header might be included from multiple lexers.
 *
 * NOT: #ifndef __INCLUDE_GUARD__QUEX_LEXER_CLASS_MISC_I__
 * NOT: #define __INCLUDE_GUARD__QUEX_LEXER_CLASS_MISC_I__       */

namespace quex { 
    inline void    
    CLASS::move_forward(const size_t CharacterN)
    {
        QuexBuffer_move_forward(&this->buffer, CharacterN);
    }

    inline void    
    CLASS::move_backward(const size_t CharacterN)
    {
        QuexBuffer_move_backward(&this->buffer, CharacterN);
    }

    
    inline size_t  
    CLASS::tell()
    {
        return QuexBuffer_tell(&this->buffer);
    }

    inline void    
    CLASS::seek(const size_t CharacterIndex)
    {
        QuexBuffer_seek(&this->buffer, CharacterIndex);
    }

    inline void
    CLASS::_reset()
    {
        QuexAnalyser_reset((QuexAnalyser*)this);

#   if   defined(QUEX_OPTION_LINE_NUMBER_COUNTING)          \
           | defined(QUEX_OPTION_COLUMN_NUMBER_COUNTING)        \
           | defined(__QUEX_OPTION_INDENTATION_TRIGGER_SUPPORT)
        counter.init();
#   endif

        // empty the token queue
#   if defined(QUEX_OPTION_TOKEN_POLICY_QUEUE) || defined(QUEX_OPTION_TOKEN_POLICY_USERS_QUEUE)
        QuexTokenQueue_reset(this->_token_queue);
#   endif

        set_mode_brutally(__QUEX_SETTING_INITIAL_LEXER_MODE_ID);
    }

} // namespace quex
