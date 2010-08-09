from copy import copy
import os
import sys

from   quex.frs_py.file_in import error_msg, write_safely_and_close, open_file_or_die

from   quex.input.setup import setup as Setup
import quex.lexer_mode                          as lexer_mode

import quex.consistency_check                   as consistency_check
import quex.core_engine.generator.core          as     generator
from   quex.core_engine.generator.action_info   import PatternActionInfo, \
                                                       UserCodeFragment_straighten_open_line_pragmas, \
                                                       CodeFragment
import quex.input.quex_file_parser              as quex_file_parser
import quex.output.cpp.token_id_maker           as token_id_maker
import quex.output.cpp.token_class_maker        as token_class_maker
import quex.output.cpp.core                     as quex_class_out
import quex.output.cpp.action_code_formatter    as action_code_formatter
import quex.output.cpp.codec_converter_helper   as codec_converter_helper 
import quex.output.cpp.mode_classes             as mode_classes
import quex.output.graphviz.interface           as plot_generator

def do():
    """Generates state machines for all modes. Each mode results into 
       a separate state machine that is stuck into a virtual function
       of a class derived from class 'quex_mode'.
    """
    token_id_maker.prepare_default_standard_token_ids()

    mode_db = __get_mode_db(Setup)

    IndentationSupportF = lexer_mode.requires_indentation_count(mode_db)
    BeginOfLineSupportF = lexer_mode.requires_begin_of_line_condition_support(mode_db)

    # (*) Implement the 'quex' core class from a template
    # -- do the coding of the class framework
    header_engine_txt,           \
    constructor_and_memento_txt, \
    header_configuration_txt = quex_class_out.do(mode_db, IndentationSupportF, BeginOfLineSupportF)
    # NOTE: In C++, constructor_and_memento_txt == "" since the implementation of templates
    #       needs to happen inside the header files.
    mode_implementation_txt  = mode_classes.do(mode_db)

    # (*) Generate the token ids
    #     (This needs to happen after the parsing of mode_db, since during that
    #      the token_id_db is developped.)
    token_id_maker.do(Setup, IndentationSupportF) 
    map_id_to_name_function_implementation_txt = token_id_maker.do_map_id_to_name_function()

    # (*) [Optional] Make a customized token class
    token_class_maker.do()
    
    # (*) [Optional] Generate a converter helper
    codec_converter_helper.do()

    # (*) implement the lexer mode-specific analyser functions
    inheritance_info_str = ""
    analyzer_code        = ""

    # (*) Get list of modes that are actually implemented
    #     (abstract modes only serve as common base)
    mode_list      = filter(lambda mode: mode.options["inheritable"] != "only", mode_db.values())
    mode_name_list = map(lambda mode: mode.name, mode_list)

    for mode in mode_list:        
        generator.init_unused_labels()

        # accumulate inheritance information for comment
        code = get_code_for_mode(mode, mode_name_list, IndentationSupportF) 
        inheritance_info_str += mode.get_documentation()

        # Find unused labels
        analyzer_code += generator.delete_unused_labels(code)

    # generate frame for analyser code
    analyzer_code = generator.frame_this(analyzer_code)

    # Bring the info about the patterns first
    analyzer_code = Setup.language_db["$ml-comment"](inheritance_info_str) + "\n" + analyzer_code

    # write code to a header file
    write_safely_and_close(Setup.output_configuration_file,
                           header_configuration_txt)
    write_safely_and_close(Setup.output_file_stem,
                           header_engine_txt)
    write_safely_and_close(Setup.output_code_file, 
                             mode_implementation_txt                    + "\n" 
                           + constructor_and_memento_txt                + "\n" 
                           + map_id_to_name_function_implementation_txt + "\n" 
                           + analyzer_code)

    UserCodeFragment_straighten_open_line_pragmas(Setup.output_file_stem, "C")
    UserCodeFragment_straighten_open_line_pragmas(Setup.output_code_file, "C")

    assert lexer_mode.token_type_definition != None
    UserCodeFragment_straighten_open_line_pragmas(lexer_mode.token_type_definition.get_file_name(), "C")

def get_code_for_mode(Mode, ModeNameList, IndentationSupportF):

    implement_skippers(Mode)

    # -- some modes only define event handlers that are inherited
    if len(Mode.get_pattern_action_pair_list()) == 0: return "", ""

    # -- 'end of stream' action
    if not Mode.has_code_fragment_list("on_end_of_stream"):
        # We cannot make any assumptions about the token class, i.e. whether
        # it can take a lexeme or not. Thus, no passing of lexeme here.
        txt  = "self_send(__QUEX_SETTING_TOKEN_ID_TERMINATION);\n"
        txt += "RETURN;\n"
        Mode.set_code_fragment_list("on_end_of_stream", CodeFragment(txt))

    end_of_stream_action = action_code_formatter.do(Mode, 
                                                    Mode.get_code_fragment_list("on_end_of_stream"), 
                                                    "on_end_of_stream", None, EOF_ActionF=True, 
                                                    IndentationSupportF=IndentationSupportF)
    # -- 'on failure' action (nothing matched)
    if not Mode.has_code_fragment_list("on_failure"):
        txt  = "QUEX_ERROR_EXIT(\"\\n    Match failure in mode '%s'.\\n\"\n" % Mode.name 
        txt += "                \"    No 'on_failure' section provided for this mode.\\n\"\n"
        txt += "                \"    Proposal: Define 'on_failure' and analyze 'Lexeme'.\\n\");\n"
        Mode.set_code_fragment_list("on_failure", CodeFragment(txt))

    on_failure_action = action_code_formatter.do(Mode, 
                                              Mode.get_code_fragment_list("on_failure"), 
                                              "on_failure", None, Default_ActionF=True, 
                                              IndentationSupportF=IndentationSupportF)

    # -- adapt pattern-action pair information so that it can be treated
    #    by the code generator.
    pattern_action_pair_list = get_generator_input(Mode, IndentationSupportF)

    analyzer_code = generator.do(pattern_action_pair_list, 
                                 OnFailureAction                = PatternActionInfo(None, on_failure_action), 
                                 EndOfStreamAction              = PatternActionInfo(None, end_of_stream_action),
                                 PrintStateMachineF             = True,
                                 StateMachineName               = Mode.name,
                                 AnalyserStateClassName         = Setup.analyzer_class_name,
                                 StandAloneAnalyserF            = False, 
                                 QuexEngineHeaderDefinitionFile = Setup.output_file_stem,
                                 ModeNameList                   = ModeNameList)

    return analyzer_code


from quex.core_engine.generator.state_coder.skipper_core import create_skip_code, create_skip_range_code

def implement_skippers(mode):
    """Code generation for skippers.

       The pattern-action pair for the skippers has been setup before.  This
       function creates code for the skippers. The code is then assigned as
       action for the skipper's pattern-action pair.

       Also, the code generator keeps track of defined and unused labels per
       mode. For this, the skipper code generation must happen together with
       the code generation for the mode-- not as it was before when the
       skippers are parsed.  
    """

    def get_action(Mode, PatternStr):
        for x in Mode.get_pattern_action_pair_list():
            if x.pattern == PatternStr:
                return x.action()
        assert False, \
               "quex/core.py: implement_skippers() pattern string reference not found."

    for info in mode.options["skip"]:
        pattern_str = info[0]
        trigger_set = info[1]

        action = get_action(mode, pattern_str)
        action.set_code(create_skip_code(trigger_set))

    for info in mode.options["skip_range"]:
        pattern_str     = info[0]
        closer_sequence = info[1]

        action = get_action(mode, pattern_str)
        action.set_code(create_skip_range_code(closer_sequence))

def get_generator_input(Mode, IndentationSupportF):
    """The module 'quex.core_engine.generator.core' produces the code for the 
       state machine. However, it requires a certain data format. This function
       adapts the mode information to this format. Additional code is added 

       -- for counting newlines and column numbers. This happens inside
          the function ACTION_ENTRY().
       -- (optional) for a virtual function call 'on_action_entry()'.
       -- (optional) for debug output that tells the line number and column number.
    """
    assert isinstance(Mode, lexer_mode.Mode)
    pattern_action_pair_list = Mode.get_pattern_action_pair_list()
    # Assume pattern-action pairs (matches) are sorted and their pattern state
    # machine ids reflect the sequence of pattern precedence.

    ## prepared_pattern_action_pair_list = []

    for pattern_info in pattern_action_pair_list:
        safe_pattern_str      = pattern_info.pattern.replace("\"", "\\\"")
        pattern_state_machine = pattern_info.pattern_state_machine()

        # Prepare the action code for the analyzer engine. For this purpose several things
        # are be added to the user's code.
        prepared_action = action_code_formatter.do(Mode, pattern_info.action(), safe_pattern_str,
                                                   pattern_state_machine,
                                                   IndentationSupportF=IndentationSupportF)

        pattern_info.set_action(prepared_action)

        ## prepared_pattern_action_pair_list.append(action_info)
    
    return pattern_action_pair_list

def __get_post_context_n(match_info_list):
    n = 0
    for info in MatchInfoList:
        if info.pattern_state_machine().core().post_context_id() != -1L:
            n += 1
    return n

def do_plot():

    mode_db             = __get_mode_db(Setup)
    IndentationSupportF = lexer_mode.requires_indentation_count(mode_db)

    for mode in mode_db.values():        
        # -- some modes only define event handlers that are inherited
        if len(mode.get_pattern_action_pair_list()) == 0: continue

        # -- adapt pattern-action pair information so that it can be treated
        #    by the code generator.
        pattern_action_pair_list = get_generator_input(mode, IndentationSupportF)

        plotter = plot_generator.Generator(pattern_action_pair_list, 
                                           StateMachineName = mode.name,
                                           GraphicFormat    = Setup.plot_graphic_format)
        plotter.do(Option=Setup.plot_character_display)

def __get_mode_db(Setup):
    # (0) check basic assumptions
    if Setup.input_mode_files == []: error_msg("No input files.")
    
    # (1) input: do the pattern analysis, in case exact counting of newlines is required
    #            (this might speed up the lexer, but nobody might care ...)
    #            pattern_db = analyse_patterns.do(pattern_file)    
    mode_description_db = quex_file_parser.do(Setup.input_mode_files)

    # (*) Translate each mode description int a 'real' mode
    for mode_name, mode_descr in mode_description_db.items():
        lexer_mode.mode_db[mode_name] = lexer_mode.Mode(mode_descr)

    # (*) perform consistency check 
    consistency_check.do(lexer_mode.mode_db)

    return lexer_mode.mode_db


#########################################################################################
# Allow to check wether the exception handlers are all in place
def _exception_checker():
    if       len(sys.argv) != 3: return
    elif     sys.argv[1] != "<<TEST:Exceptions/function>>" \
         and sys.argv[1] != "<<TEST:Exceptions/on-import>>":   return

    exception = sys.argv[2]
    if   exception == "KeyboardInterrupt": raise KeyboardInterrupt()
    elif exception == "AssertionError":    raise AssertionError()
    elif exception == "Exception":         raise Exception()

# Double check wether exception handlers are in place:
if len(sys.argv) == 3 and sys.argv[1] == "<<TEST:Exceptions/on-import>>":
    _exception_checker()

