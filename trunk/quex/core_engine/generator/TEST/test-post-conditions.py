#! /usr/bin/env python
import sys
sys.path.append("../../../../")
import generator_test
from generator_test import action
import quex.core_engine.regular_expression.core as regex

if "--hwut-info" in sys.argv:
    print "Post Conditions: Part 1"
    print "CHOICES: PlainMemory, QuexBuffer"
    sys.exit(0)

if len(sys.argv) < 2:
    print "Choice argument requested. Run --hwut-info"
    sys.exit(0)

choice = sys.argv[1]
if not (choice == "PlainMemory" or choice == "QuexBuffer"): 
    print "choice argument not acceptable"
    sys.exit(0)

pattern_action_pair_list = [
    # -- pre-conditioned expressions need to preceed same (non-preoconditioned) expressions,
    #    otherwise, the un-conditional expressions gain precedence and the un-conditional
    #    pattern is never matched.
    #
    # -- post-conditioned patterns do not need to appear before the same non-postconditioned
    #    patterns, since they are always longer.
    #
    # normal repetition (one or more) of 'x'
    ('"x"+',           "X+"),
    # repetition of 'x' (one or more) **followed** by 'anonymous' whitespace
    ('"x"+/([ \\t]+)', "X+ / WS"),
    # whitespace
    ('[ \\t\\n]+',     "WHITESPACE")
]
test_str = "x   xxxxx xxx x"

generator_test.do(pattern_action_pair_list, test_str, {}, choice)    
