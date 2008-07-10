// : -*- C++ -*-  vim: set syntax=cpp:
//
// (C) 2007 Frank-Rene Schaefer
//
#ifndef __INCLUDE_GUARD_QUEX_BUFFER_BUFFER_I_
#define __INCLUDE_GUARD_QUEX_BUFFER_BUFFER_I_

#include <cstring>
#include <quex/code_base/buffer/FixedSizeCharacterStream>

namespace quex {
#   define TEMPLATE_IN  template<class CharacterCarrierType> inline
#   define CLASS        Buffer<CharacterCarrierType>   

#   ifdef QUEX_OPTION_ACTIVATE_ASSERTS
#       define  QUEX_BUFFER_ASSERT_CONSISTENCY()                                             \
        {                                                                                    \
            /* NOTE: No assumptions can be made in general on the relation between    */     \
            /*       _current_p and _lexeme_start_p, since for forwards lexing        */     \
            /*       _current_p comes before _lexeme_start_p, wherelse for back-      */     \
            /*       ward lexing this is vice versa.                                  */     \
            /*       See "code_base/core_engine/definitions-quex-buffer.h"            */     \
            __quex_assert(_memory.front()    <  _memory.back());                             \
            __quex_assert(_current_p         >= _memory.front());                            \
            __quex_assert(_lexeme_start_p    >= _memory.front());                            \
            __quex_assert(*(_memory.front()) == CLASS::BLC );                                \
            __quex_assert(*(_memory.back())  == CLASS::BLC );                                \
            if( _end_of_file_p == 0x0 ) {                                                    \
                __quex_assert(_current_p      <= _memory.back());                            \
                __quex_assert(_lexeme_start_p <= _memory.back());                            \
            } else {                                                                         \
                __quex_assert(_current_p      <= _end_of_file_p);                            \
                __quex_assert(_lexeme_start_p <= _end_of_file_p);                            \
                /**/                                                                         \
                __quex_assert(_end_of_file_p  >= content_front());                           \
                __quex_assert(_end_of_file_p  <= _memory.back());                            \
                /**/                                                                         \
                __quex_assert(*_end_of_file_p == CLASS::BLC);                                \
            }                                                                                \
        }
#   else
#      define  QUEX_BUFFER_ASSERT_CONSISTENCY()  /* empty */
#   endif

#   if defined(__QUEX_OPTION_UNIT_TEST) && defined(__QUEX_OPTION_UNIT_TEST_QUEX_BUFFER_LOADS)
#      define QUEX_BUFFER_SHOW_BUFFER_LOAD(InfoStr)   \
        {                                 \
            std::cout << InfoStr << "\n"; \
            show_content();               \
        }
#   else
#      define QUEX_BUFFER_SHOW_BUFFER_LOAD(InfoStr) /* empty */
#   endif

    TEMPLATE_IN 
    CLASS::Buffer(FixedSizeCharacterStream<CharacterCarrierType>* _input_strategy, 
                  size_t         BufferSize   /* = 65536 */, 
                  size_t         MinFallbackN /* = 64 */,
                  character_type Value_BLC    /* = DEFAULT_BUFFER_LIMIT_CODE */)
    : BLC(Value_BLC)
    {
        __constructor_core(_input_strategy, 0x0, BufferSize, MinFallbackN);
    }

    TEMPLATE_IN 
    CLASS::Buffer(FixedSizeCharacterStream<CharacterCarrierType>* _input_strategy, 
                  CharacterCarrierType* memory_chunk,
                  size_t                ChunkSize, 
                  size_t                MinFallbackN  /* = 64 */,
                  character_type        Value_BLC     /* = DEFAULT_BUFFER_LIMIT_CODE */)
    : BLC(Value_BLC)
    {
        __constructor_core(_input_strategy, memory_chunk, ChunkSize, MinFallbackN);
    }
                  

    TEMPLATE_IN  void  
    CLASS::__constructor_core(FixedSizeCharacterStream<CharacterCarrierType>* _input_strategy, 
                              CharacterCarrierType* buffer_memory, size_t BufferSize, 
                              size_t MinFallBackN) 
    {
        __quex_assert(BufferSize > 2); 
        __quex_assert(MinFallBackN < BufferSize - 2);  // '-2' because of the border chars.
        //___________________________________________________________________________
        //
        // NOTE: The borders are filled with buffer limit codes. Thus, the
        // buffer's volume is two elements greater then the buffer's content.
        //
        if( buffer_memory == 0x0 ) {
            _memory.setup(new character_type[BufferSize], BufferSize, /* ExternalOwnerF */ false, BLC);      
        }
        else {
            _memory.setup(buffer_memory, BufferSize, /* ExternalOwnerF */ true, BLC);      
        }

        // -- current = 1 before content, 
        //    because we always read '_current_p + 1' as next char.
        //    (but: the first state does not advance the input)
        _current_p      = content_front();     
        // -- initial lexeme start, of course, at the start
        _lexeme_start_p = content_front();

        // -- how many characters of the old content shall be left in the
        //    buffer when new content is loaded?
        _min_fallback_n = MinFallBackN;

        // -- for a later 'map_to_stream_position(character_index), the strategy might
        //    have some plans.
        _input = _input_strategy;
        _input->register_begin_of_file();

        // -- load initial content starting from position zero
        const size_t LoadedN = _input->read_characters(content_front(), content_size());
        __quex_assert(LoadedN <= content_size());

        _character_index_at_front = 0;

#       ifdef __QUEX_OPTION_UNIT_TEST
        _SHOW_current_fallback_n = FallBackN; // onyl used for 'show'
#       endif

        // -- end of file / end of buffer:
        if( LoadedN != content_size() ) 
            __end_of_file_set(content_front() + LoadedN); // end of file
        else
            __end_of_file_unset();                        // buffer limit

        // -- function pointer for overflow handling
        on_overflow = 0x0;
        // TODO: on_overflow = default_memory_on_overflow_handler<CharacterCarrierType>;

        QUEX_BUFFER_ASSERT_CONSISTENCY();
    }

    TEMPLATE_IN CLASS::~buffer() 
    {
        // if buffer was provided from outside, then we should better not delete it
        if( _memory._external_owner_f ) return;

        delete [] _memory._front; 
    }

    TEMPLATE_IN  int CLASS::load_forward() 
    {
        // PURPOSE: This function is to be called as a reaction to a buffer limit code 'BLC'
        //          as returned by 'get_forward()'. Its task is to load new content into the 
        //          buffer such that 'get_forward() can continue iterating. This means that the 
        //          '_current_p' points to one of the following positions:
        //
        //          (1) Beginning of the Buffer: In this case, no reload needs to take place.
        //              It can basically only appear if 'load_forward()' is called after
        //              'get_backward()'---and this does not make sense. But returning a '0'
        //              (which is >= 0 and indicates that everything is ok) tells the application 
        //              that nothing has been loaded, and the next 'get_forward()' will work 
        //              normally.
        //
        //          (2) End of File Pointer: (which may be equal to the end of the buffer) 
        //              In this case no further content can be loaded. The function returns '0'.
        //
        //          (3) End of Buffer (if it is != End of File Pointer): Here a 'normal' load of
        //              new data into the buffer can happen.
        //
        // RETURNS: '>= 0'   number of characters that were loaded forward in the stream.
        //          '-1'     if forward loading was not possible (end of file)
        QUEX_BUFFER_SHOW_BUFFER_LOAD("LOAD FORWARD(entry)");

        // (*) Check for the three possibilities mentioned above
        if     ( _current_p == _memory.front() ) { return 0; }      // (1)
        else if( _current_p == _end_of_file_p )  { return 0; }      // (2)
        else if( _current_p != _memory.back() ) {                     
            throw std::range_error("Call to 'load_forward() but '_current_p' not on buffer border.\n" 
                                   "(Check character encoding)");  
        }
        //                                                          // (3)

        //
        // HERE: current_p == END OF THE BUFFER!
        // 

        // (*) Double check on consistency
        //     -- 'load_forward()' should only be called, if the '_current_p' reached a border.
        //        Since we know from above, that we did not reach end of file, it can be assumed
        //        that the _end_of_file_p == 0x0 (buffer does not contain EOF).
        __quex_assert(_end_of_file_p == 0x0);
        QUEX_BUFFER_ASSERT_CONSISTENCY();

        //___________________________________________________________________________________
        // (1) Fallback: A certain region of the current buffer is copied in front such that
        //               if necessary the stream can go backwards without a backward load.
        //
        //                            fallback_n
        //                               :
        //                |11111111111111:22222222222222222222222222222222222222|
        //                  copy of      :   new loaded content of buffer
        //                  end of old   
        //                  buffer      
        //
        //     The fallback region is related to the lexeme start pointer. The lexeme start 
        //     pointer always needs to lie inside the buffer, because applications might read
        //     their characters from it. The 'stretch' [lexeme start, current_p] must be 
        //     contained in the new buffer (precisely in the fallback region).
        __quex_assert(_current_p >= _lexeme_start_p);
        const size_t MinFallbackN = _current_p - _lexeme_start_p;

        // (*) Fallback region = max(default size, necessary size)
        const size_t FallBackN = _memory.min_fallback_n() > MinFallbackN ? 
                                 _memory.min_fallback_n() : MinFallbackN;

        // (*) Copy fallback region
        //     If there is no 'overlap' from source and drain than the faster memcpy() can 
        //     used instead of memmove().
        character_type*  source = content_back() - FallBackN + 1;
        character_type*  drain  = content_front();
        if( drain + FallBackN >= source  ) {
            std::memmove(drain, source, FallBackN * sizeof(character_type));
        } else { 
            std::memcpy(drain, source, FallBackN * sizeof(character_type));
        }
#       ifdef __QUEX_OPTION_UNIT_TEST
        _SHOW_current_fallback_n = FallBackN; // onyl used for 'show'
#       endif

        //___________________________________________________________________________________
        // (2) Load new content
        //
        // The _input object simulates a stream of characters of constant width, independtly 
        // of the character coding that is used. Thus, it is safe to compute the position at the
        // end of the buffer by simple addition of 'content size' to '_character_index_at_front'.
        //
        const size_t CharacterIndexAtEnd = (size_t)(_character_index_at_front + content_size());
        if( _input->tell_character_index() != CharacterIndexAtEnd  ) { 
            _input->seek_character_index(CharacterIndexAtEnd);
        }

        const size_t    LoadN = content_size() - FallBackN;
        // (*) If more characters need to be loaded than the buffer can hold,
        //     then this is a critical overflow. Example: If lexeme extends over 
        //     the whole buffer (==> MinFallbackN >= content_size).
        if( LoadN == 0 ) { 
            if( on_overflow == 0x0 ) {
                throw std::range_error("Distance between lexeme start and current pointer exceeds buffer size.\n"
                                       "(tried to load buffer in forward direction)");
            }
            else if( on_overflow(this, /* ForwardF */true) == false ) {
                return 0; 
            }
        }

        character_type* new_content = content_front() + FallBackN;
        const size_t    LoadedN     = _input->read_characters(new_content, LoadN);

        //     If end of file has been reached, then the 'end of file' pointer needs to be set
        if( LoadedN != LoadN ) __end_of_file_set(content_front() + FallBackN + LoadedN);
        else                   __end_of_file_unset();

        _character_index_at_front += content_size() - FallBackN;

        //___________________________________________________________________________________
        // (3) Pointer adaption
        //     Next char to be read: '_current_p + 1'
        _current_p      = content_front() + FallBackN - 1;   
        //     MinFallbackN = distance from '_current_p' to '_lexeme_start_p'
        //     NOTE: _current_p is set to (_current_p - 1) so that the next get_forward()
        //           reads the _current_p.
        _lexeme_start_p = (_current_p + 1) - MinFallbackN; 

        QUEX_BUFFER_SHOW_BUFFER_LOAD("LOAD FORWARD(exit)");
        QUEX_BUFFER_ASSERT_CONSISTENCY();
        // NOTE: Return value used for adaptions of memory addresses. The same rule as for
        //       _lexeme_start_p holds for those addresses.
        return LoadN;
    }

    TEMPLATE_IN  int  CLASS::load_backward() 
    {
        // PURPOSE: This function is to be called as a reaction to a buffer limit code 'BLC'
        //          as returned by 'get_backward()'. Its task is the same as the one of 
        //          'load_forward()'--only in opposite direction. Here only two cases need 
        //          to be distinguished. The current_p points to 
        //
        //          (1) End of Buffer or End of File pointer: No backward load needs to 
        //              happen. This can only occur if a 'get_forward()' was called right
        //              before.
        //
        //          (2) Begin of the buffer and the buffer is the 'start buffer':
        //              in this case no backward load can happen, because we are at the 
        //              beginning. The function returns -1.
        //
        //          (3) Begin of buffer and _begin_of_file_f is not set!: This is the case
        //              where this function, actually, has some work to do. It loads the
        //              buffer with 'earlier' content from the file.
        //
        //
        // RETURNS: Distance that was loaded backwards.
        //          -1 in case of backward loading is not possible (begin of file)
        //     
        // COMMENT: 
        //     
        // For normal cases the fallback region, i.e. the 'FALLBACK_N' buffer bytes 
        // allows to go a certain distance backwards immediately. If still the begin 
        // of the buffer is reached, then this is an indication that something is
        // 'off-the-norm'. Lexical analysis is not supposed to go longtimes
        // backwards. For such cases we step a long stretch backwards: A
        // THIRD of the buffer's size! 
        //
        // A meaningful fallback_n would be 64 Bytes. If the buffer's size
        // is for example 512 kB then the backwards_distance of A THIRD means 170
        // kB. This leaves a  safety region which is about 2730 times
        // greater than normal (64 Bytes). After all, lexical analysis means
        // to go **mainly forward** and not backwards.
        //
        QUEX_BUFFER_SHOW_BUFFER_LOAD("LOAD BACKWARD(entry)");
        QUEX_BUFFER_ASSERT_CONSISTENCY();

        // (*) Check for the three possibilities mentioned above
        if     ( _current_p == _memory.back() )  { return 0; }   // (1)
        else if( _current_p == _end_of_file_p )  { return 0; }   // (1)
        else if( _current_p != _memory.front() ) {
            throw std::range_error("Call to 'load_backward() but '_current_p' not on buffer border.\n" 
                                   "(Check character encoding)");  
        }
        else if( _character_index_at_front == 0 ) { return 0; } // (2)
        //                                                      // (3)
        // HERE: current_p == FRONT OF THE BUFFER!
        //

        //_______________________________________________________________________________
        // (1) Compute distance to go backwards
        //
        //     We need to make sure, that the lexeme start pointer remains inside the
        //     buffer, so that we do not loose the reference. From current_p == buffer begin
        //     it is safe to say that _lexeme_start_p > _current_p (the lexeme starts
        //     on a letter not the buffer limit).
        __quex_assert(_lexeme_start_p > _current_p);
        const size_t IntendedBackwardDistance = (size_t)(content_size() / 3);   

        //     Before:    |C      L                  |
        //
        //     After:     |       C      L           |
        //                 ------->
        //                 backward distance
        //
        //     Lexeme start pointer L shall lie inside the buffer. Thus, it is required:
        //
        //               backward distance + (C - L) < size
        //           =>            backward distance < size - (C - L)
        //          
        if( _lexeme_start_p == content_back() ) {
            if( on_overflow == 0x0 ) {
                throw std::range_error("Distance between lexeme start and current pointer exceeds buffer size.\n"
                                       "(tried to load buffer in backward direction)");
            }
            else if( on_overflow(this, /* ForwardF */false) == false ) {
                return 0; 
            }
        }
        const int    MaxBackwardDistance_pre = content_size() - (int)(_lexeme_start_p - _current_p);
        // NOTE: Split the minimum operation, because 'size_t' might be defined as 'unsigned'
        // NOTE: It holds: _character_index_at_front >= 0
        const size_t MaxBackwardDistance =
                            MaxBackwardDistance_pre < 0 ?                          MaxBackwardDistance_pre 
                  : (size_t)MaxBackwardDistance_pre < _character_index_at_front ?  MaxBackwardDistance_pre 
                  : _character_index_at_front;

        const int BackwardDistance = IntendedBackwardDistance > MaxBackwardDistance ? 
                                     MaxBackwardDistance : IntendedBackwardDistance;

        //_______________________________________________________________________________
        // (2) Compute the stream position of the 'start to read' 
        //
        // It is not safe to assume that the character size is fixed. Thus it is up to
        // the input strategy to determine the input position that belongs to a character
        // position.
        int start_character_index = _character_index_at_front - BackwardDistance;
        __quex_assert( start_character_index >= 0 );

        // (*) copy content that is already there to its new position.
        //     (copying is much faster then loading new content from file)
        std::memmove(content_front() + BackwardDistance,
                     content_front(), content_size() - BackwardDistance);

        //_______________________________________________________________________________
        // (3) Load content
        //
        _input->seek_character_index(start_character_index);
#       ifdef QUEX_OPTION_ACTIVATE_ASSERTS
        const size_t LoadedN = // avoid unused variable in case '__quex_assert()' is deactivated
#       endif
        // -- If file content < buffer size, then the start position of the stream to which
        //    the buffer refers is always 0 and no backward loading will ever happen.
        // -- If the file content >= buffer size, then backward loading must always fill
        //    the buffer. 
        _input->read_characters(content_front(), BackwardDistance);

        __quex_assert(LoadedN == (size_t)BackwardDistance);

        // -- end of file / end of buffer:
        if( _end_of_file_p ) {
            character_type*   NewEndOfFileP = _end_of_file_p + BackwardDistance;
            if( NewEndOfFileP < _memory.back() ) __end_of_file_set(NewEndOfFileP);
            else                                 __end_of_file_unset();
        }
        // -- character index of begin of buffer = where we started reading new content
        _character_index_at_front = start_character_index;

        //________________________________________________________________________________
        // (4) Adapt pointers
        //
        _current_p      += BackwardDistance + 1; 
        _lexeme_start_p += BackwardDistance;

        QUEX_BUFFER_SHOW_BUFFER_LOAD("LOAD BACKWARD(exit)");
        QUEX_BUFFER_ASSERT_CONSISTENCY();
        return BackwardDistance;
    }

    TEMPLATE_IN  bool  CLASS::is_end_of_file() 
    {
        QUEX_BUFFER_ASSERT_CONSISTENCY();
        // if the end of file pointer is not set, then there is no EOF inside the buffer
        if( _end_of_file_p == 0x0 )        { return false; }

        // if the 'current' pointer points to the place of EOF then, that's what is to say about it
        if( _current_p == _end_of_file_p ) { return true; }

        return false;
    }

    TEMPLATE_IN  bool  CLASS::is_begin_of_file() 
    {
        QUEX_BUFFER_ASSERT_CONSISTENCY();
        // if buffer does not start at 'begin of file', then there is no way that we're there
        if( _character_index_at_front != 0 ) { return false; }

        // if we're at the beginning of the buffer, then this is also the beginning of the file
        if( _current_p == _memory.front() ) { return true; }

        return false;
    }

    TEMPLATE_IN  bool  CLASS::is_begin_of_memory()
    {
        QUEX_BUFFER_ASSERT_CONSISTENCY();
        return _current_p == _memory.front();
    }

    TEMPLATE_IN  bool  CLASS::is_end_of_memory()
    {
        QUEX_BUFFER_ASSERT_CONSISTENCY();
        return _current_p == _memory.back();
    }

    TEMPLATE_IN  void CLASS::set_current_character(const CharacterCarrierType Value) 
    { QUEX_BUFFER_ASSERT_CONSISTENCY(); *(_current_p) = Value; }

    TEMPLATE_IN  void CLASS::set_current_p(character_type* Adr)     
    { _current_p = Adr; QUEX_BUFFER_ASSERT_CONSISTENCY(); }

    TEMPLATE_IN  typename CLASS::character_type    
        CLASS::get_previous_character() 
        { QUEX_BUFFER_ASSERT_CONSISTENCY(); return *(_current_p - 1); }

    TEMPLATE_IN  typename CLASS::character_type    
        CLASS::get_current_character() 
        { QUEX_BUFFER_ASSERT_CONSISTENCY(); return *_current_p; }

    TEMPLATE_IN void CLASS::mark_lexeme_start() 
    { 
        _lexeme_start_p = _current_p;  // pointing to the next character to be read   
        QUEX_BUFFER_ASSERT_CONSISTENCY();
    }


    TEMPLATE_IN void CLASS::__end_of_file_set(character_type* EOF_p)
    {
        _end_of_file_p  = EOF_p; 
        *_end_of_file_p = CLASS::BLC; 
        // NOT YET: QUEX_BUFFER_ASSERT_CONSISTENCY();
        __quex_assert(_end_of_file_p >  _memory.front());
        __quex_assert(_end_of_file_p <= _memory.back());
    }

    TEMPLATE_IN  void CLASS::__end_of_file_unset()
    {
        _end_of_file_p   = 0x0; 
        QUEX_BUFFER_ASSERT_CONSISTENCY();
    }


    TEMPLATE_IN  typename CLASS::character_type* CLASS::get_lexeme_start_p()
    {
        QUEX_BUFFER_ASSERT_CONSISTENCY();
        return _lexeme_start_p;
    }

    TEMPLATE_IN  typename CLASS::memory_position CLASS::tell_adr()
    {
        QUEX_BUFFER_ASSERT_CONSISTENCY();
#       ifdef QUEX_OPTION_ACTIVATE_ASSERTS
        return memory_position_mimiker<CharacterCarrierType>(_current_p, _character_index_at_front);
#       else
        return memory_position(_current_p);
#       endif
    }

    TEMPLATE_IN  void CLASS::seek_adr(const memory_position Adr)
    {
#       ifdef QUEX_OPTION_ACTIVATE_ASSERTS
        // Check wether the memory_position is relative to the current start position 
        // of the stream. That means, that the tell_adr() command was called on the
        // same buffer setting or the positions have been adapted using the += operator.
        __quex_assert(Adr.buffer_start_position == _character_index_at_front);
        _current_p = Adr.address;
#       else
        _current_p = Adr;
#       endif
        QUEX_BUFFER_ASSERT_CONSISTENCY();
    }

    TEMPLATE_IN  void CLASS::seek_offset(const int Offset)
    {
        _current_p += Offset;

        QUEX_BUFFER_ASSERT_CONSISTENCY();
    }

    TEMPLATE_IN  void CLASS::move_forward(const size_t Distance)
        // NOTE: This function is not to be called during the lexical analyzer process
        //       They should only be called by the user during pattern actions.
    {
        // Assume: The distance is mostly small with respect to the buffer size, so 
        // that one buffer load ahead is sufficient for most cases. In cases that this
        // does not hold it loads the buffer contents stepwise. A direct jump to more
        // then one load ahead would require a different load function. Please, consider
        // that different input strategies might rely on dynamic character length codings
        // 
        size_t remaining_distance_to_target = Distance;
        while( 1 + 1 == 2 ) {
            QUEX_BUFFER_ASSERT_CONSISTENCY();
            if( _end_of_file_p != 0x0 ) {
                if( _current_p + remaining_distance_to_target >= _end_of_file_p ) {
                    _current_p      = _end_of_file_p;
                    _lexeme_start_p = _current_p;
                    QUEX_BUFFER_ASSERT_CONSISTENCY();
                    return;
                } 
            } else {
                if( _current_p + remaining_distance_to_target < _memory.back() ) {
                    _current_p      += remaining_distance_to_target;
                    _lexeme_start_p  = _current_p + 1;
                    QUEX_BUFFER_ASSERT_CONSISTENCY();
                    return;
                }
            }

            // move current_p to end of the buffer, thus decrease the remaining distance
            remaining_distance_to_target -= (_memory.back() - _current_p);
            _current_p      = _memory.back();
            _lexeme_start_p = _memory.back();

            // load subsequent segment into buffer
            load_forward();
            QUEX_BUFFER_ASSERT_CONSISTENCY();
        }
    }

    TEMPLATE_IN  void CLASS::move_backward(const size_t Distance)
        // NOTE: This function is not to be called during the lexical analyzer process
        //       They should only be called by the user during pattern actions.
    {
        // Assume: The distance is mostly small with respect to the buffer size, so 
        // that one buffer load ahead is sufficient for most cases. In cases that this
        // does not hold it loads the buffer contents stepwise. A direct jump to more
        // then one load ahead would require a different load function. Please, consider
        // that different input strategies might rely on dynamic character length codings.
        size_t remaining_distance_to_target = Distance;
        while( 1 + 1 == 2 ) {
            QUEX_BUFFER_ASSERT_CONSISTENCY();
            if( _current_p - remaining_distance_to_target <= content_front() ) {
                if( *(_memory.front()) == CLASS::BLC ) {
                    _current_p      = content_front();
                    _lexeme_start_p = content_front() + 1; 
                    QUEX_BUFFER_ASSERT_CONSISTENCY();
                    return;
                }
            }
            // move current_p to begin of the buffer, thus decrease the remaining distance
            remaining_distance_to_target -= (_current_p - content_front());
            _current_p      = content_front();
            _lexeme_start_p = content_front() + 1;

            load_backward();
        }
    }

    TEMPLATE_IN  void CLASS::_reset()
    {
        // Reload the 'front' of the file into the 'front'!
        // ALWAYS! --- independent of current position! This is so, since the
        // __constructor_core() will set the 'base' to the current input position
        // of the stream.
        _input->seek_begin_of_file();

        // What happens here is exactly the same as when constructing a new
        // buffer with a given bunch of memory (the currently used one). Then
        // however, one needs to set the flag 'external memory' according to
        // what it was before.
        const bool Tmp = _memory._external_owner_f;
        CLASS::__constructor_core(_input, _memory.front(), _memory.size(), _memory.min_fallback_n());
        _memory._external_owner_f = Tmp;
    }

#undef TEMPLATE_IN
#undef CLASS
}

#endif // __INCLUDE_GUARD_QUEX_BUFFER_BUFFER_I_
