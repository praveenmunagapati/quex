import quex.engine.state_machine.compression.templates as templates 

def get_combination(TriggerMap, StateList):
    """Creates A Template Combination Object for the given Trigger Map
       and States. The trigger map is a list of objects

            [ interval, State Index to which interval triggers ] 

       The generated object of type 'TemplateCombination' will contain
       the 'StateList' as '__involved_state_list' and the trigger map
       as '__trigger_map'.
    """

    result = templates.TemplateCombination(map(long, StateList), [])

    for info in TriggerMap: 
        result.append(info[0].begin, info[0].end, info[1])

    return result

def print_tm(TM):
    """Prints a trigger map. That is, character ranges are aligned horizontally, 
       and target states, or respectively involved state lists are printed 
       inside the cells. E.g.

       |         |         |         |        |    [1L, 2L, 3L], 1, [7L, 4L, 3L], 7;

       Means, that there are four intervals. The first is a TemplateCombination
       and triggers to '[1, 2, 3]', the second is a pure state and triggers to 
       state '1', the third is a TemplateCombination and triggers to '[7, 4, 3]'
       and the forth interval triggers to '7'.

       NOTE: The first state in an involved state list is always state index of 
             the TemplateCombination. 
    """
    cursor = 0
    txt    = [" "] * 40
    for info in TM[1:]:
        x = max(0, min(40, info[0].begin))
        txt[x] = "|"

    txt[0]  = "|"
    txt[39] = "|"
    print "".join(txt),

    txt = ""
    for info in TM:
        if type(info[1]) != list: txt += "%i, " % info[1]
        else:                     txt += "%s, " % repr(info[1])
    txt = txt[:-2] + ";"
    print "   " + txt

def print_metric(M):
    print "BorderN     = %i" % M[0]
    print "TargetCombN = %s" % repr(M[1])[1:-1].replace("[", "(").replace("]", ")")
