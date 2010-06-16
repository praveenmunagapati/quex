#! /usr/bin/env python
import sys
import os
sys.path.insert(0, os.environ["QUEX_PATH"])

from   quex.core_engine.interval_handling import *
import quex.core_engine.state_machine.core                  as core
import quex.core_engine.state_machine.nfa_to_dfa            as nfa_to_dfa
import quex.core_engine.state_machine.hopcroft_minimization as hopcroft
import quex.core_engine.state_machine.compression.paths     as paths 

if "--hwut-info" in sys.argv:
    print "Paths: find_path (mean tests);"
    print "CHOICES: 1, 2, 3;"
    sys.exit(0)


def construct_path(sm, StartStateIdx, String, Skeleton):
    state_idx = StartStateIdx
    i = 0
    for letter in String:
        i += 1
        char = int(ord(letter))
        for target_idx, trigger_set in Skeleton.items():
            adapted_trigger_set = trigger_set.difference(NumberSet(char))
            end = sm.add_transition(state_idx, trigger_set, target_idx, True)
            sm.states[end].mark_self_as_origin(target_idx + 1000, end)
        
        state_idx = sm.add_transition(state_idx, char, None, True)
        sm.states[state_idx].mark_self_as_origin(i + 10000, end)

    return state_idx # Return end of the string path

def number_set(IntervalList):
    result = NumberSet(map(lambda x: Interval(x[0], x[1]), IntervalList))
    return result

def test(Skeleton, AddTransitionList, *StringPaths):
    sm = core.StateMachine()

    # def construct_path(sm, StartStateIdx, String, Skeleton):
    idx0 = sm.init_state_index
    for character_sequence in StringPaths:
        idx = construct_path(sm, idx0, character_sequence, Skeleton)

    sm = nfa_to_dfa.do(sm)
    sm = hopcroft.do(sm)

    for start_idx, end_idx, trigger_set in AddTransitionList:
        sm.add_transition(long(start_idx), trigger_set, long(end_idx))

    # Path analyzis may not consider the init state, so mount 
    # an init state before everything.
    sm.add_transition(7777L, ord('0'), sm.init_state_index)
    sm.init_state_index = 7777L

    # print Skeleton
    print sm.get_graphviz_string(NormalizeF=False)
    print
    result = paths.find_paths(sm)
    for path in result:
        print "# " + repr(path).replace("\n", "\n# ")

    print "## String paths were = " + repr(StringPaths)

skeleton_0 = { 
   66L: NumberSet(Interval(ord('a'))),
}
skeleton_1 = { 
   6666L: NumberSet(Interval(ord('a'), ord('z')+1)),
}

skeleton_2 = {} 
for char in "abc":
    letter = ord(char)
    random = (letter % 15) + 1000
    trigger = NumberSet(Interval(letter))
    skeleton_2.setdefault(long(random), NumberSet()).unite_with(NumberSet(int(letter)))

skeleton_3 = {} 
for char in "bc":
    letter = ord(char)
    random = (letter % 15) + 1000
    trigger = NumberSet(Interval(letter))
    skeleton_3.setdefault(long(random), NumberSet()).unite_with(NumberSet(int(letter)))

skeleton_4 = {} 
for char in "cd":
    letter = ord(char)
    random = (letter % 15) + 1000
    # Add intervals that have an extend of '2' so that they do not
    # add possible single paths.
    trigger = NumberSet(Interval((letter % 2) * 2, (letter % 2) * 2 + 2))
    skeleton_4.setdefault(long(random), NumberSet()).unite_with(NumberSet(int(letter)))

add_transition_list_0 = [
        (18, 18, ord('b')),
        (18, 19, ord('c')),
        (18, 16, ord('a')),
        ]

# Hint: Use 'dot' (graphviz utility) to print the graphs.
# EXAMPLE:
#          > ./paths-find_paths.py 2 > tmp.dot
#          > dot tmp.dot -Tfig -o tmp.fig       # produce .fig graph file 
#          > xfig tmp.fig                       # use xfig to view
if len(sys.argv) < 2:
    print "Call this with: --hwut-info"
    sys.exit(0)

if "1" in sys.argv: 
    test(skeleton_0, [(8, 8, ord('b')), (8, 9, ord('a'))], "b")

elif "2" in sys.argv: 
    test(skeleton_2, add_transition_list_0, "cb")

elif "3" in sys.argv: 
    test(skeleton_0, 
         [(11, 11, ord('c'))], #[(8, 8, ord('b')), (8, 9, ord('a'))], 
         "bb")
print "#"
print "# Some recursions are possible, if the skeleton contains them."
print "# In this case, the path cannot contain but the 'iterative' char"
print "# plus some exit character."
