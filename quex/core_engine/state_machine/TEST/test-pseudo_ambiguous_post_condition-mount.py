#! /usr/bin/env python
import sys
import os
sys.path.insert(0, os.environ["QUEX_PATH"])

from StringIO import StringIO
from quex.exception import *

import quex.core_engine.state_machine.index as sm_index
import quex.core_engine.regular_expression.core as regex
import quex.core_engine.state_machine.pseudo_ambiguous_post_condition as pa_post_condition 

if "--hwut-info" in sys.argv:
    print "Pseudo Ambigous Post Condition: Mounting"
    sys.exit(0)
    
def test(RE_Core, RE_PostCondition):
    string_stream_Core          = StringIO(RE_Core)
    string_stream_PostCondition = StringIO(RE_PostCondition)

    # reset the index, so that things get a litter less 'historic'
    sm_index.__internal_state_index_counter = long(-1)
    try:
        core_sm           = regex.do(string_stream_Core)
    except RegularExpressionException, x:
        print "Core Pattern:\n" + repr(x)
        return

    try:
        post_condition_sm = regex.do(string_stream_PostCondition)
    except RegularExpressionException, x:
        print "Post Condition Pattern:\n" + repr(x)
        return

    print "---------------------------------------------------------"
    print "core pattern            =", RE_Core
    print "post condition pattern  =", RE_PostCondition

    pa_post_condition.mount(core_sm, post_condition_sm)
    # .mount() does not transformation from NFA to DFA
    core_sm = core_sm.get_DFA()
    core_sm = core_sm.get_hopcroft_optimization()

    print "ambigous post condition =", core_sm

    acceptance_state_list = core_sm.get_acceptance_state_list()[0]
    one_acceptance_state = core_sm.states[acceptance_state_list[0]]
    origin_list = one_acceptance_state.get_origin_list()

    backward_detector_id = None
    for origin in origin_list:
        if origin.pseudo_ambiguous_post_condition_id() != -1L:
            backward_detector_id = origin.pseudo_ambiguous_post_condition_id()
            break

    print "backward detector =", sm_index.get_state_machine_by_id(backward_detector_id)


test('"xy"+', '("ab"|"xy")')
sys.exit()
test('"xz"+', '[a-z]{2}')
test('"xz"+', '"xz"+')
test('"xyz"+', '"xyz"')
test("(a)+", "ab")

test('"xyz"+', '("abc")|(("x"|"X")[a-z]{1}("z"|"Z"))')
test('("abc"+|"xyz")+', '("abc")|(("x"|"X")[a-z]{1}("z"|"Z"))')
test('(("xyz")+hello)+', '"xyz"hello')



