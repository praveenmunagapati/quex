#! /usr/bin/env python
# vim: set fileencoding=utf8 :
import sys
import os
sys.path.insert(0, os.getcwd())
from helper import *
from quex.engine.interval_handling import NumberSet, Interval
from quex.engine.generator.TEST.generator_test   import __Setup_init_language_database
from quex.blackboard import setup as Setup

if "--hwut-info" in sys.argv:
    print "Skip-Characters: UTF8 Engine -- Varrying Buffer Size"
    print "CHOICES: 3, 4, 5, 6, 7, 8;"
    print "SAME;"
    sys.exit(0)

if len(sys.argv) < 2: 
    print "Argument not acceptable, use --hwut-info"
    sys.exit(0)

BS = int(sys.argv[1])

if BS not in [3, 4, 5, 6, 7, 8]:
    print "Argument not acceptable, use --hwut-info"
    sys.exit(0)

Language = "Cpp"
__Setup_init_language_database(Language)

trigger_set = NumberSet([Interval(0x600, 0x700)]) 
Setup.buffer_codec                     = "utf8"
Setup.buffer_codec_transformation_info = "utf8-state-split"

def make(TriggerSet, BufferSize):
    Language = "ANSI-C-from-file"
    code = create_character_set_skipper_code(Language, "", TriggerSet, QuexBufferSize=BufferSize, InitialSkipF=False)
    exe_name, tmp_file_name = compile(Language, code)
    return exe_name, tmp_file_name

def core(Executable, BufferSize, TestStr):
    fh = open("test.txt", "wb")
    fh.write(TestStr)
    fh.close()
    run_this("./%s test.txt %i" % (Executable, BufferSize))
    os.remove("test.txt")

exe_name, tmp_file = make(trigger_set, BS)

core(exe_name, BS, "س_")
core(exe_name, BS, "نض-")
core(exe_name, BS, "بحض'")
core(exe_name, BS, "ةنشر\n")
