"""Template Compression _______________________________________________________

   Consider the file 'core_engine/state_machine/compression/templates.py' for 
   a detailed explanation of template compression


   Code Generation ____________________________________________________________

   If there is a template consisting of a (adaptable) transition map such as 

                    [0, 32)    -> drop 
                    [32]       -> Target0  
                    [33, 64)   -> 721
                    [64, 103)  -> Target1
                    [103, 255) -> Target2

   where Target0, Target1, and Target2 are defined dependent on the involved
   states 4711, 2123, and 8912 as

                        4711   3123  8912
              Target0:   891   drop   213   
              Target1:   718   718    721
              Target2:   718   drop   711

   Then, the code generator need to create:

     (1) Transition Target Data Structures: 

             Target0 = { 891, 718, 718 };
             Target1 = {  -1, 718,  -1 };
             Target2 = { 213, 721, 711 };

         There might be multiple templates, so actually 'Target0' must be
         implemented as 'Template66_Target0' if the current template is '66'.
         The above writing is chosen for simplicity.

    (2) Templated State Entries:

            STATE_4711: 
               key = 0; goto TEMPLATE_STATE_111;
            STATE_3123: 
               key = 1; goto TEMPLATE_STATE_111;
            STATE_8912: 
               key = 2; goto TEMPLATE_STATE_111;

        this way the 'gotos' to templated states remain identical to the gotos
        of non-templated states. The 'key' lets the template behave according
        to a particular state.

    (3) Templated State (with its transition map, etc.):

            STATE_111: 
              input = get();

              if input in [0, 32)    then drop 
              if input in [32]       then Target0[key]  
              if input in [33, 64)   then 721          
              if input in [64, 103)  then Target1[key]
              if input in [103, 255) then Target2[key]

              ...

         The key is basically the index in the involved state list, e.g. '0' is
         the key for state '4711' above, '1' is the key for state '3123' and
         '2' is the key for '8912'.

    (4) State Router:
    
        A state router, all states in the target maps must be map-able if no
        computed goto is used.
        
            switch( state_index ) {
            case 4711: goto STATE_4711;
            case 3214: goto STATE_3214;
            ...
            }
"""
from   quex.core_engine.generator.state_machine_decorator import StateMachineDecorator

import quex.core_engine.generator.state_coder.core            as state_coder
import quex.core_engine.generator.state_coder.transition      as transition
import quex.core_engine.generator.state_coder.input_block      as input_block
import quex.core_engine.generator.state_coder.acceptance_info  as acceptance_info
import quex.core_engine.generator.state_coder.transition_block as transition_block
import quex.core_engine.generator.state_coder.drop_out         as drop_out
import quex.core_engine.state_machine.index              as index
import quex.core_engine.state_machine.core               as state_machine

import quex.core_engine.state_machine.compression.templates as templates 


from copy import deepcopy
from quex.input.setup import setup as Setup


LanguageDB = None # Set during call to 'do()', not earlier

def do(SMD, CostCoefficient):
    """RETURNS: Array 'x'

       x[0] transition target definitions 
       x[1] code for templates and state entries
       x[2] state router for template targets
       x[3] involved_state_index_list
    """
    assert isinstance(SMD, StateMachineDecorator)
          
    # (1) Find possible state combinations
    combination_list = templates.do(SMD.sm(), CostCoefficient)

    # (2) Implement code for template combinations
    transition_target_definition, \
    code,                         \
    router,                       \
    involved_state_index_list     =  _do(combination_list, SMD)

    prolog = transition_target_definition \
             + ["QUEX_TYPE_GOTO_LABEL target_state_index;\n", \
                "int                  template_state_key;\n"]

    return "".join(code + router), "".join(prolog), \
           involved_state_index_list

def _do(CombinationList, SMD):
    """-- Returns generated code for all templates.
       -- Sets the template_compression_db in SMD.
    """
    global LanguageDB 

    assert type(CombinationList) == list
    assert isinstance(SMD, StateMachineDecorator)

    LanguageDB = Setup.language_db
    state_db   = SMD.sm().states

    # -- Collect all indices of states involved in templates
    involved_state_index_list = set([])
    # -- Collect all indices of targets states in the 'adaption table'
    target_state_index_list   = set([])
    # -- Generate 'TemplatedState's for each TemplateCombination
    template_list             = []
    for combination in CombinationList:
        assert isinstance(combination, templates.TemplateCombination)

        # Two Scenarios for settings at state entry (last_acceptance_position, ...)
        # 
        #   (i) All state entries are uniform: 
        #       -- Then, a representive state entry can be implemented at the 
        #          template entry. 
        #       -- Recursion happens to the template entry.
        #
        #   (ii) One or more state entry are different (non-uniform):
        #       -- The particularities of each state entry need to be implemented
        #          at state entry.
        #       -- Recursion is routed to entries of involved states.
        #      
        involved_state_list = combination.involved_state_list()
        prototype           = state_db.get(involved_state_list[0])
        prev_state          = prototype
        for state_index in involved_state_list[1:]:
            state = state_db.get(state_index)
            assert state != None
            if    prev_state.core().is_equivalent(state.core())       == False \
               or prev_state.origins().is_equivalent(state.origins()) == False:
                prototype = None
                break

        # -- create template state for combination object
        #    prototype == None, tells that there state entries differ and there
        #                       is no representive state.
        template = TemplateState(combination, SMD.sm().get_id(), index.get(), prototype)
        template_list.append(template)

        # -- collect indices of involved states
        involved_state_index_list.update(involved_state_list)

        # -- collect indices of target states
        for state_index in template.transitions().get_target_state_index_list():
            if state_index != None: 
                target_state_index_list.add(state_index)
            else:
                # 'goto drop-out' is coded in state index list as 'minus template index'
                target_state_index_list.add(- template.core().state_index)

        # -- if the template is non-uniform, then we need a router that maps to
        #    each state entry of involved states (e.g. for recursion and after reload).
        if not template.uniform_state_entries_f():
            target_state_index_list.update(involved_state_list)

    # -- transition target definition for each templated state
    transition_target_definition = []
    for template in template_list:
        __transition_target_data_structures(transition_target_definition, 
                                            template)

    # -- template state entries
    # -- template state
    code = []
    for template in template_list:
        __templated_state_entries(code, template, SMD)
        __template_state(code, template, SMD)

    # -- state router
    router = __state_router(target_state_index_list, SMD)

    return transition_target_definition, code, router, involved_state_index_list

class TemplateTarget:
    def __init__(self, TemplateIndex, TargetIndex=None, UniformStateEntriesF=False):
        """TemplateIndex identifies the template that 'hosts' the transition.

           TargetIndex identifies the target number (Target0, Target1, ... in
                       the example on the top of this file).

           The transition code generator will later on generate code of the 
           form 
           
                       goto Template$X$_Target$Y$[state_key];

           Where '$X$' is replaced with TemplateIndex and $Y$ is replaced
           with TargetIndex.
        """
        self.template_index = TemplateIndex
        self.target_index   = TargetIndex
        self.__uniform_state_entries_f = UniformStateEntriesF

    def recursive(self):
        return self.target_index == None

    def uniform_state_entries_f(self):
        """If the state entries are not uniform, then recursion must
           jump to state entries, rather the template entry.
        """
        return self.__uniform_state_entries_f

class TransitionMapMimiker:
    """Class that mimiks the TransitionMap of module

                   quex.core_engine.state_machine.transition_map 
                   
       The goal is to enable 'TemplateState' to act as a normal state
       responding to the member function .transitions().
    """
    def __init__(self, TemplateIndex, TriggerMap, UniformStateEntriesF):
        self.__trigger_map          = []
        self.__target_state_list_db = []
        i = 0
        for interval, target in TriggerMap:

            if target == templates.TARGET_RECURSIVE:
                # Normal Recursion: 
                #   Return to the entry of the template
                # Dedicated Recursion: 
                #   This holds if one or more involved states require things to be set
                #   at state entry (e.g. last_acceptance = ..). Then, the recursion 
                #   needs to happen to the state entries.
                target = TemplateTarget(TemplateIndex,  
                                        TargetIndex          = None, # says recursion!
                                        UniformStateEntriesF = UniformStateEntriesF) 

            elif type(target) == list:
                if target not in self.__target_state_list_db: 
                    # Register a new target state combination
                    self.__target_state_list_db.append(target)
                    target_index = i
                    i += 1

                else:
                    # Target state combination has been registered before => get the index.
                    target_index = self.__target_state_list_db.index(target)

                target = TemplateTarget(TemplateIndex, target_index)

            self.__trigger_map.append([interval, target])

    def get_trigger_map(self):
        return self.__trigger_map

    def get_epsilon_target_state_index_list(self):
        return []

    def get_target_state_index_list(self):
        """Return list of all target states that are possibly entered from 
           the templated states.
        """
        result = set([])
        for target_state_list in self.__target_state_list_db:
            result.update(target_state_list)
        return result

    def get_map(self):
        """We need to return something that is not empty, so that the reload
           procedure will be implemented. See module 'state_coder.acceptance_info'.
        """
        return { -1: None }

    def target_state_list_db(self):
        return self.__target_state_list_db

class TemplateState(state_machine.State):
    """Implementation of a Template that is able to play the role of a
       state machine state. It is constructed on the basis of a 
       TemplateCombination object that is create by module
       
                state_machine.compression.templates

       Goal of this definition is to have a state that is able to 
       comply the requirements of 'state_coder.core'. Thus, the
       template can be generated through the same procedure as 
       all state machine states.
    """
    def __init__(self, Combi, StateMachineID, StateIndex, RepresentiveState):
        """Combi contains all information about the states of a template
                 and the template itself.
           
           StateIndex is the state index that is assigned to the template.

           RepresentiveState is a state that can represent all states in
                             the template. All states of a template must
                             be equivalent, so any of them can do.

                             If == None, then it means that state entries
                             differ and there is no representive state.
        """
        assert isinstance(Combi, templates.TemplateCombination)
        assert isinstance(RepresentiveState, state_machine.State) or RepresentiveState == None
        assert type(StateIndex) == long

        # (0) Components required to be a 'State'
        if RepresentiveState != None:
            self.__uniform_state_entries_f = True
            core        = deepcopy(RepresentiveState.core())
            origin_list = deepcopy(RepresentiveState.origins())
        else:
            self.__uniform_state_entries_f = False
            # Empty core and origins, since the particularities are handled at individual 
            # state entries.
            core        = state_machine.StateCoreInfo(StateMachineID, StateIndex, 
                                                      AcceptanceF=False)   
            origin_list = state_machine.StateOriginList()          

        state_machine.State._set(self, core, origin_list,
                # Internally, we adapt the trigger map from:  Interval -> Target State List
                # to:                                         Interval -> Index
                # where 'Index' represents the Target State List
                TransitionMapMimiker(StateIndex, Combi.get_trigger_map(), self.__uniform_state_entries_f))

        state_machine.State.core(self).state_index = StateIndex

        # (1) Template related information
        self.__template_combination    = Combi

    def uniform_state_entries_f(self):
        return self.__uniform_state_entries_f

    def template_combination(self):
        return self.__template_combination

def __transition_target_data_structures(txt, TheTemplate):
    """Defines the transition targets for each involved state.
    """
    involved_state_list = TheTemplate.template_combination().involved_state_list()
    involved_state_n    = len(involved_state_list)
    template_index      = TheTemplate.core().state_index
    for target_index, target_state_index_list in enumerate(TheTemplate.transitions().target_state_list_db()):
        assert len(target_state_index_list) == involved_state_n

        txt.append("QUEX_TYPE_GOTO_LABEL  template_%i_target_%i[%i] = {" \
                   % (template_index, target_index, involved_state_n))
        for index in target_state_index_list:
            if index != None: txt.append("%i, " % index)
            else:             txt.append("-%i," % template_index)
        txt.append("};\n")

    # If the template does not have uniform state entries, the entries
    # need to be routed on recursion, for example. Thus we need to map 
    # from state-key to state.
    if not TheTemplate.uniform_state_entries_f():
        txt.append("QUEX_TYPE_GOTO_LABEL  template_%i_map_state_key_to_state_index[%i] = {" \
                   % (template_index, involved_state_n))
        for state_index in involved_state_list:
            assert isinstance(state_index, (int, long))
            txt.append("%i, " % state_index)
        txt.append("};\n")

def __templated_state_entries(txt, TheTemplate, SMD):
    """Defines the entries of templated states, so that the state key
       for the template is set, before the jump into the template. E.g.

            STATE_4711: 
               key = 0; goto TEMPLATE_STATE_111;
            STATE_3123: 
               key = 1; goto TEMPLATE_STATE_111;
            STATE_8912: 
               key = 2; goto TEMPLATE_STATE_111;
    """
    for key, state_index in enumerate(TheTemplate.template_combination().involved_state_list()):
        txt.append(LanguageDB["$label-def"]("$entry", state_index))
        state = SMD.sm().states[state_index]
        # If all state entries are uniform, the entry handling happens uniformly at
        # the entrance of the template, not each state.
        if not TheTemplate.uniform_state_entries_f():
            txt.extend(input_block.do(state_index, False, SMD.backward_lexing_f()))
            txt.extend(acceptance_info.do(state, state_index, SMD, ForceSaveLastAcceptanceF=True))
        txt.append("    ")
        txt.append(LanguageDB["$assignment"]("template_state_key", "%i" % key).replace("\n", "\n    "))
        txt.append(LanguageDB["$goto"]("$template", TheTemplate.core().state_index))
        txt.append("\n\n")

def __template_state(txt, TheTemplate, SMD):
    """Generate the template state that 'hosts' the templated states.
    """
    state       = TheTemplate
    state_index = TheTemplate.core().state_index
    TriggerMap  = state.transitions().get_trigger_map()

    txt.extend(LanguageDB["$label-def"]("$template", state_index))
    if TheTemplate.uniform_state_entries_f():
        txt.extend(input_block.do(state_index, False, SMD.backward_lexing_f()))
        txt.extend(acceptance_info.do(state, state_index, SMD, ForceSaveLastAcceptanceF=True))
    txt.extend(transition_block.do(TriggerMap, state_index, False, SMD))
    txt.extend(drop_out.do(state, state_index, SMD, False))

def __state_router(StateIndexList, SMD):
    """Create code that allows to jump to a state based on an integer value.
    """

    txt = [
            "STATE_ROUTER:\n",
            "    switch( target_state_index ) {\n"
    ]
    for index in StateIndexList:
        txt.append("    case %i: " % index)
        if index >= 0:
            # Transition to state entry
            state_index = index
            code  = transition.do(state_index, None, None, SMD)
        else:
            # Transition to a templates 'drop-out'
            template_index = - index
            code = transition.do(None, template_index, None, SMD)
        txt.append(code)
        txt.append("\n")

    txt.append("    }\n")

    return txt

