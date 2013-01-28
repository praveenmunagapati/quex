import quex.engine.state_machine.algorithm.beautifier as     beautifier
import quex.engine.state_machine.check.special        as     special
import quex.engine.state_machine.algebra.complement   as     complement
import quex.engine.state_machine.repeat               as     repeat
import quex.engine.state_machine.index                as     index
from   quex.engine.state_machine.core                 import State, StateMachine
from   quex.engine.misc.tree_walker                   import TreeWalker
from   quex.engine.tools                              import r_enumerate
from   quex.blackboard import E_StateIndices

from   copy      import deepcopy
from   itertools import islice
import sys

def do(SM_A, SM_B):
    """Cut Begin:

    Let SM_A match the set of lexemes LA and SM_B match the set of lexemes LB.
    Then, the cut begin operation 'CutBegin'

                           SM_C = CutBegin(SM_A, SM_B)

    results in a state machine SM_C. The set of lexemes which it matches is
    given by 
                             .-
                             |   c(La) for all La in L(SM_A) where La
                             |         starts with one of L(SM_B).
                L(SM_C)  =  <          
                             |   La    for all other La from L(SM_A)
                             '-

    The cut operation 'c(La)' takes the elements Lb out of La that match SM_B.
    That is if La = [x0, x1, ... xi, xj, ... xN] and there is a Lb in L(SM_B)
    with Lb = [x0, x1, ... xi], then

                    c(La) = [xj, ... XN]
                           
    EXAMPLE 1: 

          NotBegin([0-9]+, [0-9]) = [0-9]{2,}

    That is where '[0-9]+' required at least one character in [0-9], the 
    cut version does not allow lexemes with one [0-9]. The result is a
    repetition of at least two characters in [0-9].

    EXAMPLE 2: 

          NotBegin(1(2?), 12) = 1

    Because the lexeme "12" is not to be matched by the result. The lexeme
    "1", though, does not start with "12". Thus, it remains.

    EXAMPLE 2: 

          NotBegin([a-z]+, print) = all identifiers except 'print'

    (C) 2013 Frank-Rene Schaefer
    """
    tmp = beautifier.do(repeat.do(SM_B, min_repetition_n=1))
    cutter = WalkAlong(SM_A, tmp)
    print "#SM_A:", SM_A.get_string(NormalizeF=False)
    print "#SM_B:", tmp.get_string(NormalizeF=False)
    cutter.do((SM_A.init_state_index, tmp.init_state_index, None))

    # Delete orphaned and hopeless states in result
    cutter.result.clean_up()

    # Get propper state indices for result
    return beautifier.do(cutter.result)

class WalkAlong(TreeWalker):
    def __init__(self, SM_A, SM_B):
        self.original    = SM_A
        self.admissible  = SM_B

        init_state_index = index.map_state_combination_to_index((SM_A.init_state_index, 
                                                                 SM_B.init_state_index))
        state            = self.get_state_core(SM_A.init_state_index, 
                                               SM_B.init_state_index)
        self.result      = StateMachine(InitStateIndex = init_state_index,
                                        InitState      = state)
        self.state_db    = {}
        self.path        = []
        TreeWalker.__init__(self)

    def on_enter(self, Args):
        if self.is_on_path(Args): 
            return None

        a_state_index, b_state_index, trigger_set = Args
        self.path.append((a_state_index, b_state_index, trigger_set))

        sub_node_list = []

        a_tm = self.original.states[a_state_index].transitions().get_map()
        if b_state_index == E_StateIndices.NONE:
            dummy, state = self.get_state(a_state_index, b_state_index)

            # Everything 'A' does is admissible. 'B' is not involved.
            for a_ti, a_trigger_set in a_tm.iteritems():
                target_index = index.map_state_combination_to_index((a_ti, E_StateIndices.NONE))
                state.add_transition(a_trigger_set, target_index)
                sub_node_list.append((a_ti, E_StateIndices.NONE, None))
            return sub_node_list

        b_tm = self.admissible.states[b_state_index].transitions().get_map()
        for a_ti, a_trigger_set in a_tm.iteritems():
            remainder = a_trigger_set.clone()
            for b_ti, b_trigger_set in b_tm.iteritems():
                intersection = a_trigger_set.intersection(b_trigger_set)
                if intersection.is_empty(): 
                    continue

                sub_node_list.append((a_ti, b_ti, intersection))
                remainder.subtract(intersection)

            if not remainder.is_empty():
                # If we quit 'B', then all transitions are not and the path can 
                # be overtaken into the result.
                self.integrate_path_in_result(a_ti, remainder)
                sub_node_list.append((a_ti, E_StateIndices.NONE, None))


        ## print "#1-sub_node_list:", sub_node_list
        return sub_node_list

    def on_finished(self, Node):
        self.path.pop()

    def is_on_path(self, Args):
        a_state_index, b_state_index, dummy = Args
        for ai, bi, dummy in self.path:
            if ai == a_state_index and bi == b_state_index:
                return True
        return False

    def integrate_path_in_result(self, TargetIndexA, Remainder):
        print "#integrate_path_in_result:", TargetIndexA, Remainder.get_utf8_string()
        for x in self.path:
            print "#", x

        for k, info in r_enumerate(self.path):
            dummy, bi, dummy = info
            if self.admissible.states[bi].is_acceptance():
                first_remainder_k = k
                break
        else:
            first_remainder_k = 0

        ai, bi, trigger_set = self.path[first_remainder_k]
        state_index, state  = self.get_state(ai, bi)
        if state_index != self.result.init_state_index:
            print "#(%s, %s) %s -- epsilon --> %s" % (ai, bi, self.result.init_state_index, state_index)
            self.result.get_init_state().transitions().add_epsilon_target_state(state_index)

        for ai, bi, trigger_set in islice(self.path, first_remainder_k+1, None):
            target_index, target_state = self.get_state(ai, bi)
            state.add_transition(trigger_set, target_index)
            print "# (%s, %s) -- %s --> %s" % (ai, bi, trigger_set.get_utf8_string(), target_index)
            state = target_state

        target_index, target_state = self.get_state(ai, E_StateIndices.NONE)
        state.add_transition(Remainder, target_index)
            
    def get_state_core(self, AStateIndex, BStateIndex):
        acceptance_f = self.original.states[AStateIndex].is_acceptance() 
        return State(AcceptanceF=acceptance_f)

    def get_state(self, a_state_index, b_state_index):
        state_index = index.map_state_combination_to_index((a_state_index, b_state_index))
        state       = self.state_db.get(state_index)
        if state is None:
            state = self.get_state_core(a_state_index, b_state_index)
            self.result.states[state_index] = state
        return state_index, state



