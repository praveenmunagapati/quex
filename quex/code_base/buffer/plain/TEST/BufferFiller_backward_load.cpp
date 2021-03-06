#include <quex/code_base/test_environment/TestAnalyzer-configuration>
#include <quex/code_base/definitions>
#include <quex/code_base/buffer/Buffer.i>
#include <quex/code_base/buffer/BufferFiller.i>
#include <quex/code_base/buffer/plain/BufferFiller_Plain.i>

#include "test-helper.h"

int
main(int argc, char** argv)
{
    using namespace quex;
    if( cl_has(argc, argv, "--hwut-info") ) {
        printf("Load Backward: Character=%i Byte(s), Fallback=%i\n", 
               sizeof(QUEX_TYPE_CHARACTER), (int)QUEX_SETTING_BUFFER_MIN_FALLBACK_N);
        return 0;
    }
    FILE*             fh = prepare_input();
    QUEX_NAME(Buffer) buffer;
    const size_t      MemorySize = 12;
    const size_t      BeginIdx = 15;

    fseek(fh, BeginIdx * sizeof(QUEX_TYPE_CHARACTER), SEEK_SET); 

    QUEX_NAME(Buffer_construct)(&buffer, fh, 0x0, MemorySize, 0x0, 0x0, 0, false);

    /* Simulate, as if we started at 0, and now reached '15' */
    buffer._content_character_index_begin = 15;
    buffer._content_character_index_end   = buffer._content_character_index_begin + (MemorySize-2);
    QUEX_NAME(BufferFiller_Plain)<FILE>*  filler = (QUEX_NAME(BufferFiller_Plain)<FILE>*)buffer.filler;
    //filler->_character_index       = buffer._content_character_index_begin + (MemorySize-2);
    filler->_last_stream_position  = ftell(fh);
    filler->start_position         = 0;

    do {
        printf("------------------------------------------------------------\n");
        QUEX_NAME(Buffer_show_byte_content)(&buffer, 5);
        printf("     ");
        QUEX_NAME(Buffer_show_content_intern)(&buffer);
        printf("\n");
        if( buffer._content_character_index_begin == 0 ) break;
        buffer._input_p        = buffer._memory._front;
        buffer._lexeme_start_p = buffer._memory._front + 1;
        /**/
        QUEX_NAME(BufferFiller_load_backward)(&buffer);
        printf("\n");
    } while( 1 + 1 == 2 );

    fclose(fh); /* this deletes the temporary file (see description of 'tmpfile()') */
}


