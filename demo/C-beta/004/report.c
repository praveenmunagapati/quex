#include <time.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>

#include "token-ids.h"
#if defined(ANALYZER_GENERATOR_FLEX)
#else
#    include "c_lexer"
#endif
#ifdef __cplusplus
using namespace std;
#endif

#define QUOTE_THIS(NAME) #NAME

#include "main.h"

void 
final_report(double      TimePerRun,              double      RefTimePerRun, 
             const char* FileName, 
             size_t      FileSize, size_t TokenN, double      RepetitionN,
             size_t      ExecutableSize)
{
    const double  CharN          = (double)(FileSize) / (CHARACTER_SIZE);
    const double  CycleTime      = 1.0 / (double)(CPU_FREQ_MHZ) * 1e-6;
    //
    const double  TimePerChar    = TimePerRun  / CharN;
    const double  CCC            = TimePerChar / CycleTime;
    const double  RefTimePerChar = RefTimePerRun  / CharN;
    const double  RefCCC         = RefTimePerChar / CycleTime;

    double  TimePerToken = 0;
    double  CCT          = 0;
    double  RefTimePerToken = 0;
    double  RefCCT          = 0;

    if( TokenN == 1 ) { 
        TimePerToken    = TimePerRun;
        RefTimePerToken = RefTimePerRun;
    } else { 
        TimePerToken    = TimePerRun     / (double)(TokenN);
        RefTimePerToken = RefTimePerRun  / (double)(TokenN);
    }
    // Clock Cycles per Token 
    CCT    = TimePerToken    / CycleTime;
    RefCCT = RefTimePerToken / CycleTime;

    printf("//Result:\n");
    printf("//   Time / Run:          %f\n", (float)(TimePerRun  - RefTimePerRun));
    printf("//   Time / Char:         %f\n", (float)(TimePerChar - RefTimePerChar));
    printf("//   Clock Cycles / Char: %f\n", (float)(CCC - RefCCC));
    printf("{\n");
    printf("   generator       = {" QUEX_STRING(ANALYZER_GENERATOR) "},\n");
#   if defined(ANALYZER_GENERATOR_FLEX)
#   else
    printf("   quex_version    = {" QUEX_STRING(QUEX_SETTING_VERSION) "}, \n");
#   endif
    printf("   cpu_name        = {" QUEX_STRING(CPU_NAME) "}, \n");
    printf("   cpu_code        = {" QUEX_STRING(CPU_CODE) "}, \n");
    printf("   cpu_freq_mhz    = {" QUEX_STRING(CPU_FREQ_MHZ) "}, \n");
    printf("   cc_name         = {" QUEX_STRING(CC_NAME) "}, \n");
    printf("   cc_version      = {" QUEX_STRING(CC_VERSION) "}, \n");
    printf("   cc_opt_flags    = {" QUEX_STRING(CC_OPTIMIZATION_FLAGS) "}, \n");
    printf("   executable_size = {%li},\n", (long)ExecutableSize);
    printf("   os_name         = {" QUEX_STRING(OS_NAME) "}, \n");
    printf("   tester_email    = {" QUEX_STRING(EMAIL) "}, \n");
    print_date_string();
    printf("   file_name    = {%s}, \n", FileName);
    printf("   file_size    = {%i}, \n", FileSize);
    printf("   char_size    = {" QUEX_STRING(CHARACTER_SIZE) "}, \n");
    printf("   buffer_size  = {" QUEX_STRING(QUEX_SETTING_BUFFER_SIZE) "}, \n");
#       ifdef QUEX_OPTION_LINE_NUMBER_COUNTING
    printf("   line_count   = {true},\n");
#       else
    printf("   line_count   = {false},\n");
#       endif
#       ifdef QUEX_OPTION_COLUMN_NUMBER_COUNTING
    printf("   column_count = {true},\n");
#       else
    printf("   column_count = {false},\n");
#       endif
    printf("   note         = {" QUEX_STRING(NOTE) "}, \n");
    // Result
    printf("   repetition_n               = {%li},\n", (long)(RepetitionN));
    printf("   time_per_repetition        = {%f},\n",  (float)(TimePerRun - RefTimePerRun));
    printf("   token_n                    = {%i},\n",  (int)TokenN);
    printf("   clock_cycles_per_character = {%f},\n",  (float)(CCC - RefCCC));
    printf("   clock_cycles_per_token     = {%f},\n",  (float)(CCT - RefCCT));
    printf("}\n");
}


double
report(const char* Name, double TimeDiff, double RepetitionN, size_t FileSize, size_t CharacterSize)
{ 
    const double  TimePerRun = TimeDiff / RepetitionN;

    printf("// Benchmark Results '%s'\n", Name);

    printf("//    Total Time:  %f",  (float)TimeDiff);
    printf("//    Runs:        %li", (long)RepetitionN);
    printf("//    TimePerRun:  %f",  (float)TimePerRun);

    const double  CharN          = FileSize / CHARACTER_SIZE;
    const double  CycleTime      = 1.0 / (CPU_FREQ_MHZ * 1e6);
    const double  TimePerChar    = TimePerRun  / CharN;
    const double  CCC            = TimePerChar / CycleTime;

    printf("//    Time / Char:         %f\n", (float)TimePerChar);
    printf("//    Clock Cycles / Char: %f\n", (float)CCC);

    return TimePerRun;
}

void
print_date_string()
{
    time_t       current_time     = time(NULL); 
    struct tm*   broken_down_time = gmtime(&current_time);
    
    printf("   year         = {%i}\n", broken_down_time->tm_year + 1900);
    printf("   month        = {%i}\n", broken_down_time->tm_mon  + 1   );
    printf("   day          = {%i}\n", broken_down_time->tm_mday       );
}