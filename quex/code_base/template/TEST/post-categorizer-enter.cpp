#include <cstdio>
#include <cstdlib>
#include <cstring>
#define QUEX_TYPE_CHARACTER char
#define QUEX_TYPE_TOKEN_ID  int
#define QUEX_OPTION_POST_CATEGORIZER
#include <quex/code_base/template/PostCategorizer.i>

/* See: post-categorizer-common.c */
void post_categorizer_setup(QuexPostCategorizer* me, int Seed);

int
main(int argc, char** argv)
{
    using namespace quex;

    if( argc < 2 ) return -1;

    if( strcmp(argv[1], "--hwut-info") == 0 ) {
        printf("Post Categorizer: Enter;\n");
        printf("CHOICES: 0, 1, 2, 3, 4, 5, 6;\n");
        return 0;
    }
    const int Start = atoi(argv[1]);
    QuexPostCategorizer  pc;

    QuexPostCategorizer_print_tree(pc.root, 0);
}
