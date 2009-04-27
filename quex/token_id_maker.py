#! /usr/bin/env python
import time
import os
import sys
import re

from GetPot import GetPot

import quex.frs_py.file_in  as file_in
import quex.lexer_mode      as lexer_mode

from quex.frs_py.string_handling import blue_print

class TokenInfo:
    def __init__(self, Name, ID, TypeName=None, Filename="", LineN=-1):
        self.name         = Name
        self.number       = ID
        self.related_type = TypeName
        self.positions    = [ Filename, LineN ]
        self.id           = None

class Setup:
    def __init__(self, GlobalSetup):

        self.output_file      = GlobalSetup.output_token_id_file
        self.token_class_file = GlobalSetup.input_token_class_file
        self.token_class      = GlobalSetup.input_token_class_name
        self.token_prefix     = GlobalSetup.input_token_id_prefix
        self.id_count_offset  = GlobalSetup.input_token_counter_offset
        self.input_foreign_token_id_file = GlobalSetup.input_foreign_token_id_file
        
file_str = \
"""// -*- C++ -*- vim: set syntax=cpp:
// PURPOSE: File containing definition of token-identifier and
//          a function that maps token identifiers to a string
//          name.
//
// NOTE: This file has been created automatically by a
//       quex program.
//
// DATE: $$DATE$$
//
/////////////////////////////////////////////////////////////////////////////////////////
#ifndef __INCLUDE_GUARD__QUEX__TOKEN_IDS__AUTO_$$DATE_IG$$__
#define __INCLUDE_GUARD__QUEX__TOKEN_IDS__AUTO_$$DATE_IG$$__

#include<cstdio> // for: 'std::sprintf'

/* Definition of essential token identifiers that the analyser engine requires. */
#if defined(__QUEX_TOKEN_ID_TERMINATION) || defined(__QUEX_TOKEN_ID_UNINITIALIZED)
#    error \"Token identifiers for 'termination' and/or 'unilitialized' have been defined previously. This indicates that the inclusion sequence is incorrect. For example the file 'quex/code_base/definitions' shall **not** be included before this file.\"
#endif
/* Note, we can very well refer in macros to things that are defined below. */
#define __QUEX_TOKEN_ID_TERMINATION    ($$TOKEN_PREFIX$$TERMINATION)
#define __QUEX_TOKEN_ID_UNINITIALIZED  ($$TOKEN_PREFIX$$UNINITIALIZED)

/* The token class definition file can only be included after the two token identifiers have
 * been defined. Otherwise, it would rely on default values. */
#include "$$TOKEN_CLASS_DEFINITION_FILE$$"

$$TOKEN_ID_DEFINITIONS$$

namespace quex {

$$CONTENT$$

}
#endif // __INCLUDE_GUARD__QUEX__TOKEN_IDS__AUTO_GENERATED__
"""

func_str = \
"""
    inline const char*
    $$TOKEN_CLASS$$::map_id_to_name(const QUEX_TYPE_TOKEN_ID TokenID)
    {
       static char  error_string[64];
       static const char  uninitialized_string[] = "<UNINITIALIZED>";
       static const char  termination_string[]   = "<TERMINATION>";
$$TOKEN_NAMES$$       
       /* NOTE: This implementation works only for token id types that are 
        *       some type of integer or enum. In case an alien type is to
        *       used, this function needs to be redefined.                  */
       switch( TokenID ) {
       default: {
           std::snprintf(error_string, 63, "<UNKNOWN TOKEN-ID: %i>", int(TokenID));
           return error_string;
       }
       case __QUEX_TOKEN_ID_TERMINATION:   return termination_string;
       case __QUEX_TOKEN_ID_UNINITIALIZED: return uninitialized_string;
$$TOKEN_ID_CASES$$
       }
    }
"""

def do(global_setup):
    """Creates a file of token-ids from a given set of names.
       Creates also a function:

       const string& $$token$$::map_id_to_name().
    """
    global file_str
    assert lexer_mode.token_id_db.has_key("TERMINATION"), \
           "TERMINATION token id must be defined by setup or user."
    assert lexer_mode.token_id_db.has_key("UNINITIALIZED"), \
           "UNINITIALIZED token id must be defined by setup or user."
    # (*) Token ID File ________________________________________________________________
    #
    #     The token id file can either be specified as database of
    #     token-id names, or as a file that directly assigns the token-ids
    #     to variables. If the flag '--user-token-id-file' is defined, then
    #     then the token-id file is provided by the user. Otherwise, the
    #     token id file is created by the token-id maker.
    #
    #     The token id maker considers the file passed by the option '-t'
    #     as the database file and creates a C++ file with the output filestem
    #     plus the suffix "--token-ids". Note, that the token id file is a
    #     header file.
    #
    setup = Setup(global_setup)
    if len(lexer_mode.token_id_db.keys()) == 2:
        # TERMINATION + UNINITIALIZED = 2 token ids. If they are the only ones nothing can be done.
        print "error: No token id other than %sTERMINATION and %sUNINITIALIZED are defined. " % \
              (setup.token_prefix, setup.token_prefix)
        print "error: Quex refuses to proceed. Please, use the 'token { ... }' section to "
        print "error: specify at least one other token id."
        sys.exit(-1)

    if global_setup.input_user_token_id_file != "":
        ## print "(0) token ids provided by user"
        ## print "   '%s'" % global_setup.input_user_token_id_file
        global_setup.output_token_id_file = global_setup.input_user_token_id_file
        return
    
    ## print "   token class file = '%s'" % global_setup.input_token_class_file
    ## print "   => '%s'" % global_setup.output_token_id_file
    
    #______________________________________________________________________________________
    L = max(map(lambda name: len(name), lexer_mode.token_id_db.keys()))
    def space(Name):
        return " " * (L - len(Name))

    # -- define values for the token ids
    # NO LONGER: token_id_txt  = "namespace quex {\n"  
    token_id_txt = ""
    if setup.input_foreign_token_id_file != "":
        token_id_txt += "#include\"%s\"\n" % setup.input_foreign_token_id_file

    else:
        token_names = lexer_mode.token_id_db.keys()
        token_names.sort()

        i = setup.id_count_offset
        for token_name in token_names:
            token_info = lexer_mode.token_id_db[token_name] 
            if token_info.number == None: 
                token_info.number = i; i+= 1
            token_id_txt += "#define %s%s %s((QUEX_TYPE_TOKEN_ID)%i)\n" % (setup.token_prefix,
                                                                           token_name, space(token_name), 
                                                                           token_info.number)
    # NO LONGER: token_id_txt += "} // namespace quex\n" 

    # -- define the function for token names
    switch_cases = ""
    token_names  = ""
    for token_name in lexer_mode.token_id_db.keys():
        if token_name in ["TERMINATION", "UNINITIALIZED"]: continue
        switch_cases += "       case %s%s:%s return token_id_str_%s;\n" % \
                        (setup.token_prefix, token_name, space(token_name), token_name)
        token_names  += "       static const char  token_id_str_%s[]%s = \"%s\";\n" % \
                        (token_name, space(token_name), token_name)
    
    t = time.localtime()
    date_str = "%iy%im%id_%ih%02im%02is" % (t[0], t[1], t[2], t[3], t[4], t[5])

    
    file_str = file_str.replace("$$CONTENT$$", func_str)
    content = blue_print(file_str,
                         [["$$TOKEN_ID_DEFINITIONS$$",        token_id_txt],
                          ["$$DATE$$",                        time.asctime()],
                          ["$$TOKEN_CLASS_DEFINITION_FILE$$", setup.token_class_file],
                          ["$$DATE_IG$$",                     date_str],
                          ["$$TOKEN_ID_CASES$$",              switch_cases],
                          ["$$TOKEN_NAMES$$",                 token_names],
                          ["$$TOKEN_PREFIX$$",                setup.token_prefix],
                          ["$$TOKEN_CLASS$$",                 setup.token_class]])

    fh = open_file_or_die(Setup.output_file, Mode="wb")
    if os.linesep != "\n": content = content.replace("\n", os.linesep)
    fh.write(content)
    fh.close()

def parse_token_id_file(ForeignTokenIdFile, TokenPrefix, CommentDelimiterList, IncludeRE):
    """This function somehow interprets the user defined token id file--if there is
       one. It does this in order to find the names of defined token ids. It does
       some basic interpretation and include file following, but: **it is in no
       way perfect**. Since its only purpose is to avoid warnings about token ids
       that are not defined it is not essential that it may fail sometimes.

       It is more like a nice feature that quex tries to find definitions on its own.
       
       Nevertheless, it should work in the large majority of cases.
    """
    include_re_obj = re.compile(IncludeRE)

    # validate(...) ensured, that the file exists.
    work_list    = [ ForeignTokenIdFile ] 
    done_list    = []
    unfound_list = []
    while work_list != []:
        fh = open_file_or_die(work_list.pop(), Mode="rb")
        content = fh.read()
        fh.close()

        # delete any comment inside the file
        for opener, closer in CommentDelimiterList:
            content = file_in.delete_comment(content, opener, closer, LeaveNewlineDelimiter=True)

        # add any found token id to the list
        token_id_finding_list = file_in.extract_identifiers_with_specific_prefix(content, TokenPrefix)
        for token_name, line_n in token_id_finding_list:
            prefix_less_token_name = token_name[len(TokenPrefix):]
            # NOTE: The line number might be wrong, because of the comment deletion
            lexer_mode.token_id_db[prefix_less_token_name] = \
                    TokenInfo(prefix_less_token_name, None, None, fh.name, line_n) 
        
        # find "#include" statements
        include_file_list = include_re_obj.findall(content)
        include_file_list = filter(lambda file: file not in done_list,    include_file_list)
        include_file_list = filter(lambda file: os.access(file, os.F_OK), include_file_list)
        work_list.extend(include_file_list)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "error: missing command line parameter: input 'token file'"
        sys.exit(-1)

    cl = GetPot(sys.argv)
    input_file       = cl.follow("", "-i")
    token_class_file = cl.follow("", "-t")
    token_class      = cl.follow("token", "--token-class-name")
    token_counter_offset = cl.follow(1000, "--offset")
    output_file          = cl.follow("", "-o")
    token_prefix         = cl.follow("TKN_", "--tp")
    
    if "" in [input_file, output_file]:
        print "error: please specify input (option '-i') and output file (option '-o')"
        sys.exit(-1)
        
    do(Setup(input_file, output_file, token_class_file, token_class, token_prefix, token_counter_offset))

