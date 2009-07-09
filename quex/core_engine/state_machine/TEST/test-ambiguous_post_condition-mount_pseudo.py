#! /usr/bin/env python
import sys
import os
sys.path.insert(0, os.environ["QUEX_PATH"])

from StringIO import StringIO
from quex.exception import *

import quex.core_engine.state_machine.index as sm_index
import quex.core_engine.regular_expression.core as regex
import quex.core_engine.state_machine.ambiguous_post_context as ambiguous_post_context 
import quex.core_engine.state_machine.nfa_to_dfa as nfa_to_dfa
import quex.core_engine.state_machine.hopcroft_minimization as hopcroft

if "--hwut-info" in sys.argv:
    print "Pseudo Ambigous Post Condition: Mounting"
    sys.exit(0)
    
def test(RE_Core, RE_PostCondition):
    string_stream_Core          = StringIO(RE_Core)
    string_stream_PostCondition = StringIO(RE_PostCondition)

    # reset the index, so that things get a litter less 'historic'
    try:
        core_sm           = regex.do(string_stream_Core, {}, -1)
    except RegularExpressionException, x:
        print "Core Pattern:\n" + repr(x)
        return

    try:
        post_context_sm = regex.do(string_stream_PostCondition, {}, -1)
    except RegularExpressionException, x:
        print "Post Condition Pattern:\n" + repr(x)
        return

    print "---------------------------------------------------------"
    print "core pattern            =", RE_Core
    print "post condition pattern  =", RE_PostCondition

    ambiguous_post_context.mount(core_sm, post_context_sm)
    # .mount() does not transformation from NFA to DFA
    core_sm = nfa_to_dfa.do(core_sm)
    core_sm = hopcroft.do(core_sm)

    print "ambigous post condition =", core_sm

    print "backward detector =", core_sm.core().post_context_backward_input_position_detector_sm()


test('"xy"+', '((ab)+|xy)')
test('"xz"+', '[a-z]{2}')
test('"xyz"+', '"xyz"')
test("(a)+",   "ab")
test("(.)+a",   "(.)+")

# test('"xz"+', '"xz"+')
# test('"xyz"+', '("abc")|(("x"|"X")[a-z]{1}("z"|"Z"))')
# test('("abc"+|"xyz")+', '("abc")|(("x"|"X")[a-z]{1}("z"|"Z"))')
# test('(("xyz")+hello)+', '"xyz"hello')



