from quex.blackboard import TargetStateIndices, \
                            setup as Setup
from quex.engine.analyzer.core import AnalyzerState

def do(Target, TheState, ReturnToState_Str, GotoReload_Str):
    """Generate a 'real' target action object based on a given Target that may be
       an identifier or actually a real object already.

       The approach of having 'code-ready' objects as targets makes code 
       generation much simpler. No information has to be passed down the 
       recursive call tree.
    """
    if isinstance(Target, TransitionCode): 
        return Target
    else:
        return TransitionCode(Target, TheState, ReturnToState_Str, GotoReload_Str)

class TransitionCode:
    def __init__(self, Target, TheState, ReturnToState_Str, GotoReload_Str):
        """The generation of transition code is postponed to the moment when
           the code fragment is used. This happens in order to avoid the
           generation of references to 'goto-labels' that are later not used.
           Note, that in some cases, for example 'goto drop-out' can be avoided
           by simply dropping out of an if-else clause or a switch statement.

           if self.__code is None: postponed
           else:                   not postponed
        """
        assert isinstance(TheState, AnalyzerState)
        assert ReturnToState_Str is None or isinstance(ReturnToState_Str, (str, unicode))
        assert GotoReload_Str    is None or isinstance(GotoReload_Str, (str, unicode))
        LanguageDB = Setup.language_db

        self.__target              = Target
        self.__the_state           = TheState
        self.__return_to_state_str = ReturnToState_Str

        if   Target == TargetStateIndices.RELOAD_PROCEDURE:
            self.__drop_out_f = False
            if GotoReload_Str is not None: self.__code = GotoReload_Str
            else:                          self.__code = None # postponing
        elif Target == TargetStateIndices.DROP_OUT:
            self.__code       = None # postponing
            self.__drop_out_f = True
        elif isinstance(Target, (int, long)):
            # The transition to another target state cannot possibly be cut out!
            # => no postponed code generation
            self.__code       = LanguageDB.GOTO(Target)
            self.__drop_out_f = False
        else:
            assert isinstance(Target, TransitionCode) # No change necessary
            assert False # When it hits here, we need to think what to do!

    @property
    def code(self):       
        if self.__code is not None: return self.__code
        LanguageDB = Setup.language_db

        if   self.__target == TargetStateIndices.RELOAD_PROCEDURE:
            return LanguageDB.GOTO_RELOAD(self.__the_state, self.__return_to_state_str)
        elif self.__target == TargetStateIndices.DROP_OUT:
            return LanguageDB.GOTO_DROP_OUT(self.__the_state.index)
        else:
            assert False

    @property
    def drop_out_f(self): return self.__drop_out_f

def __transition_to_reload(StateIdx, SMD, ReturnStateIndexStr=None):
    LanguageDB = Setup.language_db

def get_transition_to_terminal(Origin):
    LanguageDB = Setup.language_db

    # No unconditional case of acceptance 
    if type(Origin) == type(None): 
        get_label("$terminal-router", U=True) # Mark __TERMINAL_ROUTER as used
        return [ LanguageDB["$goto-last_acceptance"] ]

    assert Origin.is_acceptance()
    # The seek for the end of the core pattern is part of the 'normal' terminal
    # if the terminal 'is' a post conditioned pattern acceptance.
    if Origin.post_context_id() == PostContextIDs.NONE:
        return [ "goto %s;" % get_label("$terminal", Origin.state_machine_id, U=True) ]
    else:
        return [ "goto %s;" % get_label("$terminal-direct", Origin.state_machine_id, U=True) ]
