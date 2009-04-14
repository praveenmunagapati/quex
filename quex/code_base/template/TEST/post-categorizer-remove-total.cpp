#include <cstdio>
#include <cstdlib>
#include <cstring>
#define QUEX_TYPE_CHARACTER char
#define QUEX_TYPE_TOKEN_ID  int
#define QUEX_OPTION_POST_CATEGORIZER
#include <quex/code_base/template/PostCategorizer.i>

using namespace quex;
void post_categorizer_setup(QuexPostCategorizer* me, int Seed);
void test(quex::QuexPostCategorizer* pc, const char* Name);

int
main(int argc, char** argv)
{
    using namespace quex;

    if( argc < 2 ) return -1;

    if( strcmp(argv[1], "--hwut-info") == 0 ) {
        printf("Post Categorizer: Remove Total;\n");
        printf("CHOICES: 1, 2, 3, 4, 5, 6, 7;\n");
        printf("SAME;\n");
        return 0;
    }
    QuexPostCategorizer  pc;

    post_categorizer_setup(&pc, atoi(argv[1]));
    
    QuexPostCategorizer_remove(&pc, "Ab");
    QuexPostCategorizer_remove(&pc, "Ad");
    QuexPostCategorizer_remove(&pc, "Af");
    QuexPostCategorizer_remove(&pc, "Ah");
    QuexPostCategorizer_remove(&pc, "Bb");
    QuexPostCategorizer_remove(&pc, "Bd");
    QuexPostCategorizer_remove(&pc, "Bf");

    QuexPostCategorizer_enter(&pc, "The only node", 77);

    QuexPostCategorizer_print_tree(pc.root, 0);
}
