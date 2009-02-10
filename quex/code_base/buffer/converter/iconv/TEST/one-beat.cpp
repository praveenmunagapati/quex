#include<iostream>
#include<fstream>

#include<quex/code_base/buffer/converter/iconv/BufferFiller_IConv>
#include<quex/code_base/buffer/converter/iconv/BufferFiller_IConv.i>

using namespace std;

int
main(int argc, char** argv)
{
    using namespace std;
    using namespace quex;

    if( argc > 1 && strcmp(argv[1], "--hwut-info") == 0 ) {
        cout << "read_characters: Raw buffer size varries (UTF-8)\n";
        cout << "CHOICES: 6, 7, 8, 9;\n";
        cout << "SAME;\n";
        return 0;
    }
    assert(sizeof(QUEX_CHARACTER_TYPE) == 4);

    if( argc < 2 )  {
        printf("Missing choice argument. Use --hwut-info\n");
        return 0;
    }

    std::FILE*   fh = fopen("test.txt", "r");
    char*        target_charset = (char*)"UCS-4LE";
    size_t       raw_memory_size = 3;
    raw_memory_size = argv[1][0] - '0';
    assert(raw_memory_size >= 1);
    assert(raw_memory_size <= 9);
    const int            MemorySize = 512; /* no re-load necessary */
    QUEX_CHARACTER_TYPE  memory[MemorySize];

    QuexBufferFiller_Converter<FILE>* filler = \
        QuexBufferFiller_Converter_IConv_new(fh, "UTF8", target_charset, raw_memory_size);

    size_t loaded_n = 0;
    loaded_n = filler->base.read_characters(&filler->base, 
                                           (QUEX_CHARACTER_TYPE*)memory, MemorySize);

    cout << "## loaded character n = " << loaded_n << endl;

    for(size_t i=0; i < loaded_n ; ++i) {
        uint8_t*  raw = (uint8_t*)(memory + i);
        printf("%02X.%02X.%02X.%02X\n", (unsigned)raw[3], (unsigned)raw[2], (unsigned)raw[1], (unsigned)raw[0]);
    }
}
