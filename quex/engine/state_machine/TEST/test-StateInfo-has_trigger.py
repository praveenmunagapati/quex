#! /usr/bin/env python
import sys
import os
sys.path.insert(0, os.environ["QUEX_PATH"])

import quex.input.regular_expression.engine as core

if "--hwut-info" in sys.argv:
    print "Trigger Set Check: Has Trigger "
    sys.exit(0)
    
def test(TestString, StartCharacterList):
    print "____________________________________________________________________"
    print "expr.   = " + TestString.replace("\n", "\\n").replace("\t", "\\t")
    sm = core.do(TestString, {}).sm
    print "start   = ", map(lambda char: char.replace("\t", "\\t"), StartCharacterList)
    code_list = map(lambda char: ord(char), StartCharacterList)
    print "verdict = ", repr(sm.get_init_state().target_map.has_one_of_triggers(code_list))

test('[0-9]+', ['2', 'A'])
test('[0-9]+', ['2', '5'])
test('" 123"', [' '])
test('"\t123"', [' ', '\t'])

test('[0-9]+', ['C', 'A'])
test('[0-8]+', ['Q', '9'])
test('"\t123"', [' '])
test('"123"', [' ', '\t'])
