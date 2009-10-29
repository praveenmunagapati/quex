/* -*- C++ -*- vim: set syntax=cpp: */
#ifndef __INCLUDE_GUARD_QUEX__CODE_BASE__MEMORY_MANAGER_I__
#define __INCLUDE_GUARD_QUEX__CODE_BASE__MEMORY_MANAGER_I__

#include <quex/code_base/definitions>
#include <quex/code_base/buffer/plain/BufferFiller_Plain>
#include <quex/code_base/buffer/converter/BufferFiller_Converter>
#if defined (QUEX_OPTION_ENABLE_ICU)
#   include <quex/code_base/buffer/converter/icu/Converter_ICU>
#endif
#if defined (QUEX_OPTION_ENABLE_ICONV)
#   include <quex/code_base/buffer/converter/iconv/Converter_IConv>
#endif

#include <quex/code_base/temporary_macros_on>
 
QUEX_NAMESPACE_MAIN_OPEN

    struct __QuexBufferFiller_tag;

    /* CONCEPT: -- All allocator functions receive an argument 'ByteN' that indicates
     *             the number of required bytes. 
     *          -- All allocator functions return a pointer to the allocated memory
     *             or '0x0' in case of failure.
     *
     *          By means of the name of the function only the 'place' of the memory
     *          might be determined easier, or an according buffer-pool strategy might
     *          be applied.                                                              */
    QUEX_INLINE QUEX_TYPE_CHARACTER*
    QUEX_NAME(MemoryManager_BufferMemory_allocate)(const size_t ByteN)
    { return (QUEX_TYPE_CHARACTER*)__QUEX_ALLOCATE_MEMORY(ByteN); }

    QUEX_INLINE void
    QUEX_NAME(QUEX_NAME(MemoryManager_BufferMemory_free))(QUEX_TYPE_CHARACTER* memory)
    { if( memory != 0x0 ) __QUEX_FREE_MEMORY((uint8_t*)memory); }

    TEMPLATE_IN(InputHandleT) void*
    QUEX_NAME(MemoryManager_BufferFiller_allocate)()(const size_t ByteN)
    { return __QUEX_ALLOCATE_MEMORY(ByteN); }

    TEMPLATE_IN(InputHandleT) void
    QUEX_NAME(MemoryManager_BufferFiller_free)(void* memory)
    { if( memory != 0x0 ) __QUEX_FREE_MEMORY((uint8_t*)memory); }

    QUEX_INLINE uint8_t*
    QUEX_NAME(MemoryManager_BufferFiller_RawBuffer_allocate)(const size_t ByteN)
    { return __QUEX_ALLOCATE_MEMORY(ByteN); }

    QUEX_INLINE void
    QUEX_NAME(MemoryManager_BufferFiller_RawBuffer_free)(uint8_t* memory)
    { if( memory != 0x0 ) __QUEX_FREE_MEMORY(memory); }

    QUEX_INLINE void*
    QUEX_NAME(MemoryManager_Converter_allocate)(const size_t ByteN)
    { return __QUEX_ALLOCATE_MEMORY(ByteN); }

    QUEX_INLINE void
    QUEX_NAME(MemoryManager_Converter_free)(void* memory)
    { if( memory != 0x0 ) __QUEX_FREE_MEMORY((uint8_t*)memory); }

#   ifdef QUEX_OPTION_STRING_ACCUMULATOR
    QUEX_INLINE QUEX_TYPE_CHARACTER*
    QUEX_NAME(MemoryManager_AccumulatorText_allocate)(const size_t ByteN)
    { return __QUEX_ALLOCATE_MEMORY(ByteN); }

    QUEX_INLINE void
    QUEX_NAME(MemoryManager_AccumulatorText_free)(QUEX_TYPE_CHARACTER* memory)
    { if( memory != 0x0 ) __QUEX_FREE_MEMORY((uint8_t*)memory); }
#   endif

#   ifdef QUEX_OPTION_POST_CATEGORIZER
    QUEX_INLINE  QUEX_TYPE_POST_CATEGORIZER_NODE*  
    QUEX_NAME(MemoryManager_PostCategorizerNode_allocate)(size_t RemainderL)
    {
        /* Allocate in one beat: base and remainder: 
         *
         *   [Base   |Remainder             ]
         *
         * Then bend the base->name_remainder to the Remainder part of the allocated
         * memory. Note, that this is not very efficient, since one should try to allocate
         * the small node objects and refer to the remainder only when necessary. This
         * would reduce cache misses.                                                      */
        const size_t   BaseSize      = sizeof(QUEX_TYPE_POST_CATEGORIZER_NODE);
        /* Length + 1 == memory size (terminating zero) */
        const size_t   RemainderSize = sizeof(QUEX_TYPE_CHARACTER) * (RemainderL + 1);
        uint8_t*       base          = __QUEX_ALLOCATE_MEMORY(BaseSize + RemainderSize);
        ((QUEX_TYPE_POST_CATEGORIZER_NODE*)base)->name_remainder = (const QUEX_TYPE_CHARACTER*)(base + BaseSize);
        return (QUEX_TYPE_POST_CATEGORIZER_NODE*)base;
    }

    QUEX_INLINE  void 
    QUEX_NAME(MemoryManager_PostCategorizerNode_free)(QUEX_TYPE_POST_CATEGORIZER_NODE* node)
    { if( node != 0x0 ) __QUEX_FREE_MEMORY((uint8_t*)node); }
#   endif

    QUEX_INLINE size_t
    QUEX_NAME(MemoryManager_insert)(uint8_t* drain_begin_p,  uint8_t* drain_end_p,
                                    uint8_t* source_begin_p, uint8_t* source_end_p)
        /* Inserts as many bytes as possible into the array from 'drain_begin_p'
         * to 'drain_end_p'. The source of bytes starts at 'source_begin_p' and
         * ends at 'source_end_p'.
         *
         * RETURNS: Number of bytes that have been copied.                      */
    {
        /* Determine the insertion size. */
        const size_t DrainSize = drain_end_p  - drain_begin_p;
        size_t       size      = source_end_p - source_begin_p;
        if( DrainSize < size ) size = DrainSize;

        /* memcpy() might fail if the source and drain domain overlap! */
#       ifdef QUEX_OPTION_ASSERTS 
        if( drain_begin_p > source_begin_p ) __quex_assert(drain_begin_p >= source_begin_p + size);
        else                                 __quex_assert(drain_begin_p <= source_begin_p - size);
#       endif
        __QUEX_STD_memcpy(drain_begin_p, source_begin_p, size);

        return size;
    }

QUEX_NAMESPACE_MAIN_CLOSE
 
#include <quex/code_base/temporary_macros_off>

#endif /* __INCLUDE_GUARD_QUEX__CODE_BASE__MEMORY_MANAGER_I__ */

