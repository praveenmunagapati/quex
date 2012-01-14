#! /usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
sys.path.insert(0, os.environ["QUEX_PATH"])

from   quex.engine.analyzer.state_entry        import *
from   quex.engine.analyzer.state_entry_action import categorize_command_lists
import help

from   collections import namedtuple
from   copy import copy

if "--hwut-info" in sys.argv:
    print "Categorize Entry Door Actions"
    print "CHOICES: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11;"
    sys.exit()

choice = sys.argv[1]

AcceptInfo = namedtuple("AcceptInfo", ("pre_context_id", "pattern_id"))
StoreInfo  = namedtuple("StoreInfo",  ("pre_context_id", "position_register", "offset"))

A1   = [AcceptInfo(x, y) for x, y in [(1, 10), (2, 20)]]
A2   = [AcceptInfo(x, y) for x, y in [(2, 20), (1, 10)]]
S000 = StoreInfo(0, 0, 0) # 1
S001 = StoreInfo(0, 0, 1) # 2
S002 = StoreInfo(0, 0, 2) # 3
S100 = StoreInfo(1, 0, 0) # 4
S101 = StoreInfo(1, 0, 1) # 5
S102 = StoreInfo(1, 0, 2) # 6
S010 = StoreInfo(0, 1, 0) # 7
S011 = StoreInfo(0, 1, 1) # 8
S012 = StoreInfo(0, 1, 2) # 9

def test(ActionDB):
    entry = Entry(ActionDB.keys())
    for from_state_index, action_list in ActionDB.iteritems():
        for element in action_list:
            if isinstance(element, list):
                entry.doors_accept(from_state_index, element)
            else:
                entry.doors_store(from_state_index, 
                                  element.pre_context_id, 
                                  element.position_register, 
                                  element.offset)
    node_db, door_tree_root = categorize_command_lists(entry.action_db.values())
    print door_tree_root

if "1" in sys.argv:
    # All three states have exactly the same entry actions
    action_db = {
        0: [ A1 ],
        1: [ A1 ],
        2: [ A1 ],
    }
elif "2" in sys.argv:
    # Two different entry actions
    action_db = { 
        0: [ A2 ],
        1: [ A1 ],
    }
elif "3" in sys.argv:
    # One entry action is shared. 
    # Each door has a special action.
    action_db = {
        0: [ A1, S000 ],
        1: [ A1, S001 ],
        2: [ A1, S002 ],
    }
elif "4" in sys.argv:
    # One entry action is shared. 
    # Each two doors share an action.
    action_db = {
        0: [ A1, S000 ],
        1: [ A1, S000 ],
        2: [ A1, S001 ],
        3: [ A1, S001 ],
        4: [ A1, S002 ],
        5: [ A1, S002 ],
    }
elif "5" in sys.argv:
    # One entry action is shared. 
    # Each two doors share an action.
    # Each door has a special action.
    action_db = {
        0: [ A1, S000, S100 ],
        1: [ A1, S000, S101 ],
        2: [ A1, S001, S102 ],
        3: [ A1, S001, S010 ],
    }
elif "6" in sys.argv:
    # One entry action is shared. 
    # Each two doors share an action.
    # Each door has a special action.
    action_db = {
        0: [ A1, S000, S100 ],
        1: [ A1, S000, S101 ],
        2: [ A2, S001, S102 ],
        3: [ A2, S001, S010 ],
    }
elif "7" in sys.argv:
    actions   = [A1, A2, S000, S001, S002, S100, S101, S102, S010, S011, S012]
    action_db = dict((i, [x]) for i, x in enumerate(actions))

elif "8" in sys.argv:
    actions   = [A1, S000, S001, S002, S100, S101, S102, S010, S011, S012]
    action_db = dict((i, actions) for i in xrange(100))

elif "9" in sys.argv:
    action_db = dict((i, []) for i in xrange(1000))

elif "10" in sys.argv:
    actions   = [A1, S000, S001, S002, S100, S101, S102, S010, S011, S012]
    L         = len(actions)
    def get_actions(Index):
        result = copy(actions)
        del result[Index % L]
        return result
    action_db = dict((i, get_actions(i)) for i in xrange(10))

elif "11" in sys.argv:
    from quex.blackboard import setup as Setup
    Setup.state_entry_analysis_complexity_limit = 5
    action_db = dict((i, [StoreInfo(0, 0, i)]) for i in xrange(10))

elif "X" in sys.argv:
    actions   = [A1, S000, S001, S002, S100, S101, S102, S010, S011, S012]
    L         = len(actions)
    def get_actions(Index):
        result = copy(actions)
        del result[Index % L]
        return result
    action_db = dict((i, get_actions(i)) for i in xrange(1000))

test(action_db)


