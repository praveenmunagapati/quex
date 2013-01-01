from   quex.engine.interval_handling import Interval
from   quex.blackboard import E_StateIndices
import sys
from   copy import deepcopy, copy
from   itertools import izip

def zipped_iterable(TransitionMapA, TransitionMapB):
    """Produces an iterable over two transition maps at once. The borders in the
    zipped transition map consist of a superset of all borders of transition
    map 'A' and 'B'. Whenever a border hits a new interval is notified. 

            YIELDS:  begin, end, a_target, b_target

    Interval [begin, end) is homogenous in the zipped transition map, i.e.
    inside this interval 'A' triggers to 'a_target' and 'B' to 'b_target'.  
    """
    assert len(TransitionMapA) != 0 
    assert TransitionMapA[0][0].begin == - sys.maxint
    assert TransitionMapA[-1][0].end  == sys.maxint
    assert len(TransitionMapB) != 0 
    assert TransitionMapB[0][0].begin == - sys.maxint
    assert TransitionMapB[-1][0].end  == sys.maxint

    LenA             = len(TransitionMapA)
    LenB             = len(TransitionMapB)
    i                = 0 # iterator over TransitionMapA
    k                = 0 # iterator over TransitionMapB
    i_itvl, i_target = TransitionMapA[i]
    k_itvl, k_target = TransitionMapB[k]
    prev_end         = - sys.maxint
    # Intervals in trigger map are always adjacent, so the '.begin' member is
    # not accessed.
    while not (i == LenA - 1 and k == LenB - 1):
        end    = min(i_itvl.end, k_itvl.end)

        yield prev_end, end, i_target, k_target

        prev_end  = end

        if   i_itvl.end == k_itvl.end: 
            i += 1; i_itvl, i_target = TransitionMapA[i]
            k += 1; k_itvl, k_target = TransitionMapB[k]
        elif i_itvl.end <  k_itvl.end: 
            i += 1; i_itvl, i_target = TransitionMapA[i]
        else:                          
            k += 1; k_itvl, k_target = TransitionMapB[k]

    # Treat the last trigger interval
    yield prev_end, sys.maxint, TransitionMapA[-1][1], TransitionMapB[-1][1]
    return

def clone(transition_map):
    return [ (interval.clone(), deepcopy(target)) for interval, target in transition_map ]

def relate_to_door_ids(transition_map, TheAnalyzer, StateIndex):
    """Creates a transition_map that triggers to DoorIDs instead of target states.
    """
    def adapt(Target):
        if Target == E_StateIndices.DROP_OUT:
            return Target
        else:
            result = TheAnalyzer.state_db[Target].entry.get_door_id(StateIndex=Target, FromStateIndex=StateIndex)
            return result

    return [(interval, adapt(target)) for interval, target in transition_map]

def get_string(transition_map, Option="utf8", IntervalF=True):
    assert Option in ("hex", "dec", "utf8")
    def get(X):
        if   X == sys.maxint:   return "+oo"
        elif X == - sys.maxint: return "-oo"
        return "%i" % X
    if len(transition_map) == 0:
        return "   <empty>"
    L = max(len(x[0].get_string(Option)) for x in transition_map)
    txt = []
    for interval, target in transition_map:
        if IntervalF: interval_str = interval.get_string(Option)
        else:         interval_str = "[%s:%s)" % (get(interval.begin), get(interval.end))
        txt.append("   %s%s %s\n" % (interval_str, " " * (L - len(interval_str)), target))
    return "".join(txt)

def bisect_begin(transition_map, Value, lower=0):
    """Find entry 'i' by bisectioning so that it holds:

          -- transition_map[i][0].begin <= Value
          -- transition_map[k][0].begin > Value for all k > i
    """
    upper = len(transition_map)
    delta = upper - lower
    while delta > 1:
        i       = lower + delta / 2
        current = transition_map[i][0].begin
        if   current > Value: upper = i 
        elif current < Value: lower = i
        else:                 return i
        delta   = upper - lower

    return lower if transition_map[lower][0].begin == Value else -1

def set(transition_map, Character, NewTarget):
    # (bisectioning would certainly be more elegant ...)
    for i, entry in enumerate(transition_map):
        interval, target = entry
        if interval.contains(Character):
            break
    else:
        print "TM: {\n%s}" % get_string(transition_map, "dec")
        print "Character:", Character
        assert False

    # Found the interval that contains the Character
    assert interval.size() > 0
    L = len(transition_map)

    # Check whether an adjacent interval has the same target, so that
    # the new interval can directly be docked to it.
    if target == NewTarget:
        return # Nothing to be done

    if interval.size() == 1:
        if i > 0 and interval.begin == Character and transition_map[i-1][1] == NewTarget:
            # Interval before fits
            if i < L-1 and interval.end == Character + 1 and transition_map[i+1][1] == NewTarget:
                # Interval before and after fits
                transition_map[i-1][0].end = transition_map[i+1][0].end
                del transition_map[i:i+2]
            else:
                # Only interval before fits
                transition_map[i-1][0].end = transition_map[i][0].end
                del transition_map[i]

        elif i < L-1 and interval.end == Character + 1 and transition_map[i+1][1] == NewTarget:
            # Only interval after fits, Interval before does not fit
            transition_map[i+1][0].begin = transition_map[i][0].begin
            del transition_map[i]

        else:
            transition_map[i] = (interval, NewTarget)

        assert_adjacency(transition_map, TotalRangeF=False)
        return

    if i > 0 and interval.begin == Character and transition_map[i-1][1] == NewTarget:
        # Interval before fits, Interval after cannot fit, because size() > 1
        transition_map[i-1][0].end = Character + 1
        transition_map[i][0].begin = Character + 1

    elif i < L-1 and interval.end == Character + 1 and transition_map[i+1][1] == NewTarget:
        # Interval after fits, Interval before cannot fit, because size() > 1
        transition_map[i+1][0].begin = Character 
        transition_map[i][0].end     = Character

    elif interval.begin == Character:
        transition_map[i][0].begin = Character + 1
        transition_map.insert(i, (Interval(Character), NewTarget))

    elif interval.end == Character + 1:
        transition_map.insert(i+1, (Interval(Character), NewTarget))
        transition_map[i][0].end = Character

    else:
        # Character lies in the middle of a non-fitting interval
        transition_map.insert(i+1, (Interval(Character), NewTarget))
        transition_map.insert(i+2, (Interval(Character+1, interval.end), target))
        transition_map[i][0].end = Character 

    assert_adjacency(transition_map, TotalRangeF=False)
    return

def assert_adjacency(transition_map, TotalRangeF=False, ChangeF=False):
    """Check that the trigger map consist of sorted adjacent intervals 
       This assumption is critical because it is assumed that for any isolated
       interval the bordering intervals have bracketed the remaining cases!
    """
    if len(transition_map) == 0: 
        assert not TotalRangeF
        return

    if TotalRangeF: 
        assert transition_map[0][0].begin == -sys.maxint
        assert transition_map[-1][0].end  == sys.maxint

    iterable    = transition_map.__iter__()
    info        = iterable.next()
    prev_end    = info[0].end
    prev_target = info[1]

    for interval, target in iterable:
        assert interval.begin == prev_end       # Intervals are adjacent!
        assert interval.end   > interval.begin  # Interval size > 0! 
        if ChangeF:
            assert target != prev_target

        prev_end    = interval.end
        prev_target = target

    # If we reach here, then everything is OK.
    return

def index(transition_map, Character):
    # TODO: Bisectioning
    for i, info in enumerate(transition_map):
        interval, target = info
        if   interval.end   <  Character + 1: continue
        elif interval.begin <= Character: return i
    return None

def smoothen(transition_map, Character):
    """Replaces a single character transition by a transition of its adjacent 
    intervals.
    """
    i = index(transition_map, Character)
    assert transition_map[i][0].size() == 1

    L = len(transition_map)
    if i > 0: 
        if i < L - 1 and transition_map[i+1][1] == transition_map[i-1][1]:
            transition_map[i-1][0].end = transition_map[i+1][0].end
            del transition_map[i:i+2]
        else:
            transition_map[i-1][0].end = Character
            del transition_map[i]

    elif i < L:
        transition_map[i+1][0].end = Character + 1
        del transition_map[i]
    else:
        assert False

def is_equal(One, Other):
    if len(One) != len(Other): return False
    for x, y in izip(One, Other):
        if   x[0] != y[0]: return False  # Interval
        elif x[1] != y[1]: return False  # Target
    return True

def fill_gaps(transition_map, Target):
    """Fill gaps in the transition map. 
    """
    size = len(transition_map)

    if size == 0:
        transition_map.append((Interval(-sys.maxint, sys.maxint), Target))
        return

    # If outer borders are lacking, then add them
    if transition_map[0][0].begin != -sys.maxint: 
        transition_map.insert(0, (Interval(-sys.maxint, transition_map[0][0].begin), Target))
        size += 1

    if transition_map[-1][0].end != sys.maxint: 
        transition_map.append((Interval(transition_map[-1][0].end, sys.maxint), Target))
        size += 1

    # Fill gaps between the intervals
    prev_end    = transition_map[0][0].end
    prev_target = transition_map[0][1]
    i           = 1
    while i < size:
        interval = transition_map[i][0]
        target   = transition_map[i][1]

        ##print 
        ##print "#i:", i
        ##print "#tm:", transition_map
        ##print "#int,target:", interval, target
        ##print "#prev_end, prev_target:", prev_end, prev_target

        assert interval.begin >= prev_end

        if prev_end == interval.begin: 
            ##print "#A"
            if prev_target == target:
                # (*) Combine two intervals which have the same target
                transition_map[i-1][0].end = interval.end
                del transition_map[i]
                size -= 1
            else:
                i += 1
            prev_end    = interval.end
            prev_target = target

        elif prev_target != Target:
            ##print "#B"
            # (*) Gap detected, targets differ => fill!
            transition_map.insert(i, (Interval(prev_end, interval.begin), Target))
            size += 1
            # prev_target = same;
            # prev_end    = same; 
            # NOT: i+=1, because need to check for combination with next interval.

        else:
            ##print "#C", prev_target, Target
            # (*) Gap detected, targets equal => extend!
            transition_map[i-1][0].end = interval.begin
            prev_target = Target
            prev_end    = interval.begin
            # NOT: i+=1, because need to check for combination with next interval.

def cut(transition_map, CharacterSet):
    result = []
    for interval, target in transition_map:
        diff = CharacterSet.intersection(interval)
        result.extend((x_interval, target) 
                      for x_interval in diff.get_intervals(PromiseToTreatWellF=True))
    return result

def get_target(transition_map, Character):
    # TODO: Bisectioning
    for interval, target in transition_map:
        if   interval.end   <  Character + 1: continue
        elif interval.begin <= Character: return target
    return None

def sort(transition_map):
    transition_map.sort(key=lambda x: x[0].begin)

def add_transition_actions(transition_map, TransitionActionMap):
    """'TransitionActionMap' describes actions to be taken upon the 
    occurence of a particular character. The actions are to be added
    to the 'transition_map'.
    """
    def extend(Target, ActionList):
        result = copy(Target)
        if len(Target) != 0 and len(Target[-1]) != 0:
            plain_target = Target[-1][-1].rstrip()
            if len(plain_target) and plain_target[-1] == "\n": result.append(0)
        result.extend(ActionList)
        return result

    result = []
    for begin, end, target, action_list in zipped_iterable(transition_map, TransitionActionMap):
        if action_list is None:
            result.append((Interval(begin, end), copy(target)))
        else:
            result.append((Interval(begin, end), extend(target, action_list)))
    return result

