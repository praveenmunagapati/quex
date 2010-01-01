#! /usr/bin/env python
import os
from   copy import copy
import time

from quex.frs_py.string_handling import blue_print
from quex.frs_py.file_in  import get_file_content_or_die, \
                                 write_safely_and_close, \
                                 get_include_guard_extension, \
                                 make_safe_identifier

import quex.lexer_mode              as lexer_mode
from   quex.input.setup             import setup as Setup

LanguageDB = Setup.language_db


def do(Modes, IndentationSupportF):
    assert lexer_mode.token_type_definition != None

    write_engine_header(Modes)
    write_configuration_header(Modes, IndentationSupportF)

def write_configuration_header(Modes, IndentationSupportF):
    OutputConfigurationFile   = Setup.output_configuration_file
    LexerClassName            = Setup.analyzer_class_name
    ConfigurationTemplateFile = os.path.normpath(Setup.QUEX_INSTALLATION_DIR 
                                   + LanguageDB["$code_base"] 
                                   + "/analyzer/configuration/CppTemplate.txt").replace("//","/")

    txt = get_file_content_or_die(ConfigurationTemplateFile)

    # -- check if exit/entry handlers have to be active
    entry_handler_active_f = False
    exit_handler_active_f = False
    for mode in Modes.values():
        if mode.get_code_fragment_list("on_entry") != []: entry_handler_active_f = True
        if mode.get_code_fragment_list("on_exit") != []:  exit_handler_active_f = True

    # Buffer filler converter (0x0 means: no buffer filler converter)
    converter_new_str = "#   define QUEX_SETTING_BUFFER_FILLERS_CONVERTER_NEW " 
    if Setup.converter_user_new_func != "": 
        converter_new_str += Setup.converter_user_new_func + "()"
        user_defined_converter_f = True
    else: 
        converter_new_str = "/* " + converter_new_str + " */"
        user_defined_converter_f = False

    namespace_main_str = make_safe_identifier(LanguageDB["$namespace-ref"](Setup.analyzer_name_space)[:-2])

    # -- determine character type according to number of bytes per ucs character code point
    #    for the internal engine.
    quex_character_type_str = { 1: "uint8_t ", 2: "uint16_t", 4: "uint32_t", 
                                   "wchar_t": "wchar_t" }[Setup.bytes_per_ucs_code_point]

    txt = __switch(txt, "QUEX_OPTION_COLUMN_NUMBER_COUNTING",        True)        
    txt = __switch(txt, "QUEX_OPTION_DEBUG_MODE_TRANSITIONS",        Setup.output_debug_f)
    txt = __switch(txt, "QUEX_OPTION_DEBUG_QUEX_PATTERN_MATCHES",    Setup.output_debug_f)
    txt = __switch(txt, "QUEX_OPTION_DEBUG_TOKEN_SENDING",           Setup.output_debug_f)
    txt = __switch(txt, "QUEX_OPTION_ENABLE_ICONV",                  Setup.converter_iconv_f)
    txt = __switch(txt, "QUEX_OPTION_ENABLE_ICU",                    Setup.converter_icu_f)
    txt = __switch(txt, "QUEX_OPTION_INCLUDE_STACK",                 Setup.include_stack_support_f)
    txt = __switch(txt, "QUEX_OPTION_LINE_NUMBER_COUNTING",          True)      
    txt = __switch(txt, "QUEX_OPTION_POST_CATEGORIZER",              Setup.post_categorizer_f)
    txt = __switch(txt, "QUEX_OPTION_RUNTIME_MODE_TRANSITION_CHECK", Setup.mode_transition_check_f)
    txt = __switch(txt, "QUEX_OPTION_STRING_ACCUMULATOR",            Setup.string_accumulator_f)
    txt = __switch(txt, "QUEX_OPTION_TOKEN_POLICY_QUEUE",            Setup.token_policy == "queue")
    txt = __switch(txt, "QUEX_OPTION_TOKEN_POLICY_USERS_QUEUE",      Setup.token_policy == "users_queue")
    txt = __switch(txt, "QUEX_OPTION_TOKEN_POLICY_USERS_TOKEN",      Setup.token_policy == "users_token")
    txt = __switch(txt, "__QUEX_OPTION_BIG_ENDIAN",                  Setup.byte_order == "big")
    txt = __switch(txt, "__QUEX_OPTION_CONVERTER_ENABLED",           user_defined_converter_f )
    txt = __switch(txt, "__QUEX_OPTION_INDENTATION_TRIGGER_SUPPORT", IndentationSupportF)     
    txt = __switch(txt, "__QUEX_OPTION_LITTLE_ENDIAN",               Setup.byte_order == "little")
    txt = __switch(txt, "__QUEX_OPTION_ON_ENTRY_HANDLER_PRESENT",    entry_handler_active_f)
    txt = __switch(txt, "__QUEX_OPTION_ON_EXIT_HANDLER_PRESENT",     exit_handler_active_f)
    txt = __switch(txt, "__QUEX_OPTION_SUPPORT_BEGIN_OF_LINE_PRE_CONDITION",  True)
    txt = __switch(txt, "__QUEX_OPTION_SYSTEM_ENDIAN",               Setup.byte_order_is_that_of_current_system_f)
    txt = __switch(txt, "__QUEX_OPTION_PLAIN_C",                    Setup.language.upper() == "C")

    # -- token class related definitions
    token_descr = lexer_mode.token_type_definition
    namespace_token_str = make_safe_identifier(LanguageDB["$namespace-ref"](token_descr.name_space))

    txt = blue_print(txt, 
            [["$$BUFFER_LIMIT_CODE$$",          "0x%X" % Setup.buffer_limit_code],
             ["$$INCLUDE_GUARD_EXTENSION$$",    get_include_guard_extension(
                                                         LanguageDB["$namespace-ref"](Setup.analyzer_name_space) 
                                                             + "__" + Setup.analyzer_class_name)],
             ["$$QUEX_VERSION$$",               Setup.QUEX_VERSION],
             ["$$QUEX_TYPE_CHARACTER$$",        quex_character_type_str],
             ["$$TOKEN_QUEUE_SAFETY_BORDER$$",  repr(Setup.token_queue_safety_border)],
             ["$$LEXER_BUILD_DATE$$",           time.asctime()],
             ["$$USER_LEXER_VERSION$$",         Setup.user_application_version_id],
             ["$$INITIAL_LEXER_MODE_ID$$",      "QUEX_NAME(QuexModeID_%s)" % lexer_mode.initial_mode.get_pure_code()],
             ["$$MAX_MODE_CLASS_N$$",           repr(len(Modes))],
             ["$$LEXER_CLASS_NAME$$",           LexerClassName],
             ["$$LEXER_DERIVED_CLASS_NAME$$",   Setup.analyzer_derived_class_name],
             ["$$TOKEN_CLASS$$",                token_descr.class_name],
             ["$$TOKEN_ID_TYPE$$",              token_descr.token_id_type.get_pure_code()],
             ["$$TOKEN_QUEUE_SIZE$$",           repr(Setup.token_queue_size)],
             ["$$NAMESPACE_MAIN$$",             LanguageDB["$namespace-ref"](Setup.analyzer_name_space)[:-2]],
             ["$$NAMESPACE_MAIN_STR$$",         namespace_main_str],
             ["$$NAMESPACE_MAIN_OPEN$$",        LanguageDB["$namespace-open"](Setup.analyzer_name_space).replace("\n", "\\\n")],
             ["$$NAMESPACE_MAIN_CLOSE$$",       LanguageDB["$namespace-close"](Setup.analyzer_name_space).replace("\n", "\\\n")],
             ["$$NAMESPACE_TOKEN$$",            LanguageDB["$namespace-ref"](token_descr.name_space)],
             ["$$NAMESPACE_TOKEN_STR$$",        namespace_token_str],
             ["$$NAMESPACE_TOKEN_OPEN$$",       LanguageDB["$namespace-open"](token_descr.name_space).replace("\n", "\\\n")],
             ["$$NAMESPACE_TOKEN_CLOSE$$",      LanguageDB["$namespace-close"](token_descr.name_space).replace("\n", "\\\n")],
             ["$$TOKEN_LINE_N_TYPE$$",          token_descr.line_number_type.get_pure_code()],
             ["$$TOKEN_COLUMN_N_TYPE$$",        token_descr.column_number_type.get_pure_code()],
             ["$$TOKEN_PREFIX$$",               Setup.token_id_prefix],
             ["$$QUEX_SETTING_BUFFER_FILLERS_CONVERTER_NEW$$", converter_new_str]])

    write_safely_and_close(OutputConfigurationFile, txt)

def __switch(txt, Name, SwitchF):
    if SwitchF: txt = txt.replace("$$SWITCH$$ %s" % Name, "#define    %s" % Name)
    else:       txt = txt.replace("$$SWITCH$$ %s" % Name, "/* #define %s */" % Name)
    return txt
    
def write_constructor_and_memento_functions(ModeDB, LexerClassName):
    FileTemplate = os.path.normpath(Setup.QUEX_INSTALLATION_DIR
                                    + LanguageDB["$code_base"] 
                                    + "/analyzer/CppTemplate_functions.txt")
    func_txt = get_file_content_or_die(FileTemplate)

    func_txt = blue_print(func_txt,
            [
                ["$$CONSTRUCTOR_EXTENSTION$$",                  lexer_mode.class_constructor_extension.get_code()],
                ["$$CONSTRUCTOR_MODE_DB_INITIALIZATION_CODE$$", get_constructor_code(ModeDB.values(), LexerClassName)],
                ["$$MEMENTO_EXTENSIONS_PACK$$",                 lexer_mode.memento_pack_extension.get_code()],
                ["$$MEMENTO_EXTENSIONS_UNPACK$$",               lexer_mode.memento_unpack_extension.get_code()],
                ])
    return func_txt

def write_engine_header(Modes):

    QuexClassHeaderFileTemplate = os.path.normpath(Setup.QUEX_INSTALLATION_DIR
                                                   + LanguageDB["$code_base"] 
                                                   + "/analyzer/CppTemplate.txt")
    QuexClassHeaderFileOutput   = Setup.output_file_stem
    LexerFileStem               = Setup.output_file_stem
    LexerClassName              = Setup.analyzer_class_name

    #    are bytes of integers Setup 'little endian' or 'big endian' ?
    if Setup.byte_order == "little":
        quex_coding_name_str = { 1: "ASCII", 2: "UCS-2LE", 4: "UCS-4LE", 
                                    "wchar_t": "WCHAR_T" }[Setup.bytes_per_ucs_code_point]
    else:
        quex_coding_name_str = { 1: "ASCII", 2: "UCS-2BE", 4: "UCS-4BE", 
                                    "wchar_t": "WCHAR_T" }[Setup.bytes_per_ucs_code_point]

    mode_id_definition_str = "" 
    # NOTE: First mode-id needs to be '1' for compatibility with flex generated engines
    i = -1
    for name in Modes.keys():
        i += 1
        mode_id_definition_str += "const int QUEX_NAME(QuexModeID_%s) = %i;\n" % (name, i)

    # -- instances of mode classes as members of the lexer
    mode_object_members_txt,     \
    mode_specific_functions_txt, \
    friend_txt =                 \
         get_mode_class_related_code_fragments(Modes.values(), LexerClassName)

    # -- define a pointer that directly has the type of the derived class
    if Setup.analyzer_derived_class_name == "":
        Setup.analyzer_derived_class_name = LexerClassName
        derived_class_type_declaration = ""
    else:
        derived_class_type_declaration = "class %s;" % Setup.analyzer_derived_class_name

    token_class_file_name = lexer_mode.token_type_definition.get_file_name()

    function_code_txt = write_constructor_and_memento_functions(Modes, LexerClassName)

    template_code_txt = get_file_content_or_die(QuexClassHeaderFileTemplate)

    txt = blue_print(template_code_txt,
            [
                ["$$CLASS_BODY_EXTENSION$$",             lexer_mode.class_body_extension.get_code()],
                ["$$CLASS_FUNCTIONS$$",                  function_code_txt],
                ["$$INCLUDE_GUARD_EXTENSION$$",          get_include_guard_extension(
                                                         LanguageDB["$namespace-ref"](Setup.analyzer_name_space) 
                                                             + "__" + Setup.analyzer_class_name)],
                ["$$LEXER_CLASS_NAME$$",                 LexerClassName],
                ["$$LEXER_CONFIG_FILE$$",                Setup.output_configuration_file],
                ["$$LEXER_DERIVED_CLASS_DECL$$",         derived_class_type_declaration],
                ["$$LEXER_DERIVED_CLASS_NAME$$",         Setup.analyzer_derived_class_name],
                ["$$QUEX_MODE_ID_DEFINITIONS$$",         mode_id_definition_str],
                ["$$MEMENTO_EXTENSIONS$$",               lexer_mode.memento_class_extension.get_code()],
                ["$$MODE_CLASS_FRIENDS$$",               friend_txt],
                ["$$MODE_OBJECTS$$",                     mode_object_members_txt],
                ["$$MODE_SPECIFIC_ANALYSER_FUNCTIONS$$", mode_specific_functions_txt],
                ["$$PRETTY_INDENTATION$$",               "     " + " " * (len(LexerClassName)*2 + 2)],
                ["$$QUEX_TEMPLATE_DIR$$",                Setup.QUEX_INSTALLATION_DIR + LanguageDB["$code_base"]],
                ["$$QUEX_VERSION$$",                     Setup.QUEX_VERSION],
                ["$$TOKEN_CLASS_DEFINITION_FILE$$",      token_class_file_name.replace("//", "/")],
                ["$$TOKEN_CLASS$$",                      lexer_mode.token_type_definition.class_name],
                ["$$TOKEN_ID_DEFINITION_FILE$$",         Setup.output_token_id_file.replace("//","/")],
                ["$$CORE_ENGINE_CHARACTER_CODING$$",     quex_coding_name_str],
                ["$$USER_DEFINED_HEADER$$",              lexer_mode.header.get_code() + "\n"],
             ])

    write_safely_and_close(QuexClassHeaderFileOutput, txt)


quex_mode_init_call_str = """
     me->$$MN$$.id   = QUEX_NAME(QuexModeID_$$MN$$);
     me->$$MN$$.name = "$$MN$$";
     me->$$MN$$.analyzer_function = $analyzer_function;
#    ifdef __QUEX_OPTION_INDENTATION_TRIGGER_SUPPORT    
     me->$$MN$$.on_indentation = $on_indentation;
#    endif
     me->$$MN$$.on_entry       = $on_entry;
     me->$$MN$$.on_exit        = $on_exit;
#    ifdef __QUEX_OPTION_RUNTIME_MODE_TRANSITION_CHECK
     me->$$MN$$.has_base       = $has_base;
     me->$$MN$$.has_entry_from = $has_entry_from;
     me->$$MN$$.has_exit_to    = $has_exit_to;
#    endif
"""

def __get_mode_init_call(mode, LexerClassName):
    
    analyzer_function = "QUEX_NAME(%s_analyzer_function)" % mode.name
    on_indentation    = "QUEX_NAME(%s_on_indentation)"    % mode.name
    on_entry          = "QUEX_NAME(%s_on_entry)"          % mode.name
    on_exit           = "QUEX_NAME(%s_on_exit)"           % mode.name
    has_base          = "QUEX_NAME(%s_has_base)"          % mode.name
    has_entry_from    = "QUEX_NAME(%s_has_entry_from)"    % mode.name
    has_exit_to       = "QUEX_NAME(%s_has_exit_to)"       % mode.name

    if mode.options["inheritable"] == "only": 
        analyzer_function = "QUEX_NAME(Mode_uncallable_analyzer_function)"

    if mode.get_code_fragment_list("on_entry") == []:
        on_entry = "QUEX_NAME(Mode_on_entry_exit_null_function)"

    if mode.get_code_fragment_list("on_exit") == []:
        on_exit = "QUEX_NAME(Mode_on_entry_exit_null_function)"

    if mode.get_code_fragment_list("on_indentation") == []:
        on_indentation = "QUEX_NAME(Mode_on_indentation_null_function)"

    txt = blue_print(quex_mode_init_call_str,
                [["$$MN$$",             mode.name],
                 ["$$CLASS$$",          LexerClassName],
                 ["$analyzer_function", analyzer_function],
                 ["$on_indentation",    on_indentation],
                 ["$on_entry",          on_entry],
                 ["$on_exit",           on_exit],
                 ["$has_base",          has_base],
                 ["$has_entry_from",    has_entry_from],
                 ["$has_exit_to",       has_exit_to]])

    return txt

def __get_mode_function_declaration(Modes, LexerClassName, FriendF=False):

    if FriendF: prolog = "    friend "
    else:       prolog = "extern "

    def __mode_functions(Prolog, ReturnType, NameList, ArgList):
        txt = ""
        for name in NameList:
            function_signature = "%s QUEX_NAME(%s_%s)(%s);" % \
                     (ReturnType, mode.name, name, ArgList)
            txt += "%s" % Prolog + "    " + function_signature + "\n"

        return txt

    txt = ""
    for mode in Modes:
        if mode.options["inheritable"] != "only":
            txt += __mode_functions(prolog, "void", ["analyzer_function"],
                                    "QUEX_TYPE_ANALYZER*")
    for mode in Modes:
        if mode.has_code_fragment_list("on_indentation"):
            txt += __mode_functions(prolog, "void", ["on_indentation"], 
                                    "QUEX_TYPE_ANALYZER*, const int")

    for mode in Modes:
        for event_name in ["on_exit", "on_entry"]:
            if not mode.has_code_fragment_list(event_name): continue
            txt += __mode_functions(prolog, "void", [event_name], 
                                    "QUEX_TYPE_ANALYZER*, const QUEX_NAME(Mode)*")

    txt += "#ifdef __QUEX_OPTION_RUNTIME_MODE_TRANSITION_CHECK\n"
    for mode in Modes:
        txt += __mode_functions(prolog, "bool", ["has_base", "has_entry_from", "has_exit_to"], 
                                "const QUEX_NAME(Mode)*")
        
    txt += "#endif\n"
    txt += "\n"

    return txt


def get_constructor_code(Modes, LexerClassName):
    L = max(map(lambda m: len(m.name), Modes))

    txt = ""
    for mode in Modes:
        txt += "        __quex_assert(QUEX_NAME(QuexModeID_%s) %s< %i);\n" % \
               (mode.name, " " * (L-len(mode.name)), len(Modes))

    for mode in Modes:
        txt += __get_mode_init_call(mode, LexerClassName)

    for mode in Modes:
        txt += "        me->mode_db[QUEX_NAME(QuexModeID_%s)]%s = &me->%s;\n" % \
               (mode.name, " " * (L-len(mode.name)), mode.name)
    return txt

def get_mode_class_related_code_fragments(Modes, LexerClassName):
    """
       RETURNS:  -- members of the lexical analyzer class for the mode classes
                 -- static member functions declaring the analyzer functions for he mode classes 
                 -- constructor init expressions (before '{'),       
                 -- constructor text to be executed at construction time 
                 -- friend declarations for the mode classes/functions

    """
    L = max(map(lambda m: len(m.name), Modes))

    members_txt = ""    
    for mode in Modes:
        members_txt += "        static QUEX_NAME(Mode)  %s;\n" % mode.name

    mode_functions_txt = __get_mode_function_declaration(Modes, LexerClassName, FriendF=False)
    friends_txt        = __get_mode_function_declaration(Modes, LexerClassName, FriendF=True)

    return members_txt,        \
           mode_functions_txt, \
           friends_txt


