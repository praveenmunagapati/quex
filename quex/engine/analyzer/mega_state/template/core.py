from   quex.engine.analyzer.mega_state.core               import PseudoMegaState
from   quex.engine.analyzer.mega_state.template.state     import TemplateState
from   quex.engine.analyzer.mega_state.template.candidate import TemplateStateCandidate
from   quex.blackboard import E_Compression
from   itertools       import ifilter, islice
from   collections     import defaultdict

# (C) 2010 Frank-Rene Schaefer
"""
   Template Compression _______________________________________________________

   The idea behind 'template compression' is to combine the transition maps of
   multiple similar states into a single transition map. The difference in the
   transition maps is dealt with by an adaption table. For example the three
   states

         .---- 'a' --> 2        .---- 'a' --> 2        .---- 'a' --> 2
         |                      |                      |
       ( A )-- 'e' --> 0      ( B )-- 'e' --> 1      ( C )-- 'e' --> 2
         |                      |                      |
         `---- 'x' --> 5        `---- 'x' --> 5        `---- 'y' --> 5

   can be combined into a single template state

                         .----- 'a' --> 2 
                         |               
                      ( T1 )--- 'e' --> Target0 
                         |\               
                         \  `-- 'x' --> Target1
                          \
                           `--- 'y' --> Target2

   where the targets Target0, Target1, and Target2 are adapted. If the template
   has to mimik state A then Target0 needs to be 1, Target1 is 5, and Target2
   is 'drop-out'. The adaptions can be stored in a table:

                                A     B     C
                       Target0  0     1     2
                       Target1  5     5     drop
                       Target2  drop  drop  5

   The columns in the table tell how the template behaves if it operates on
   behalf of a certain state--here A, B, and C. Practically, a state_key is
   associated with each state, e.g. 0 for state A, 1 for state B, and 2 for
   state C.  Thus, a state that is implemented in a template is identified by
   'template index' and 'state key', i.e.

            templated state <--> (template index, state_key)

   The combination of multiple states reduces memory consumption. The
   efficiency increases with the similarity of the transition maps involved.
   The less differences there are in the trigger intervals, the less additional
   intervals need to be added. The less differences there are in target states,
   the less information needs to be stored in adaption tables.

   Result ______________________________________________________________________


   The result of analyzis of template state compression is:
    
              A list of 'TemplateState' objects. 

   A TemplateState carries:
   
     -- A trigger map, i.e. a list of intervals together with target state
        lists to which they trigger. If there is only one associated target
        state, this means that all involved states trigger to the same target
        state.

     -- A list of involved states. A state at position 'i' in the list has
        the state key 'i'. It is the key into the adaption table mentioned
        above.

   Algorithm __________________________________________________________________

   Not necessarily all states can be combined efficiently with each other. The
   following algorithm finds successively best combinations and stops when no
   further useful combinations can be found. 

   Each state has a transition map, i.e. an object that tells on what character
   code the analyzer jump to what states:

             transition map:  interval  --> target state

   The algorithm works as follows:

      (1) Compute for each possible pair of states a TemplateStateCandidate. 

          (1.1) Compute the 'gain of combination' for candidate.

          (1.2) Do not consider to combine states where the 'gain' is 
                below MinGain.

          (1.3) Register the candidate in 'gain_matrix'.

      (4) Pop best candidate from gain_matrix. If no more reasonable
          candidates present, then stop.
            
      (5) With given candidate goto (1.1)

   The above algorithm is supported by TemplateStateCandidate being derived
   from TemplateState.

   Measurement of the 'Gain Value' ____________________________________________

   The measurement of the gain value happens inside a TemplateStateCandidate. 
   It is a function of the similarity of the states. In particular the entries, 
   the drop_outs and the transition map is considered. 

   Transition Map of a TemplateState __________________________________________

   The transition map of a template state is a list of (interval, target)
   tuples as it is in a normal AnalyzerState. In an AnalyzerState the target
   can only be a scalar value indicating the target state. The target object of
   a TemplateState, though, can be one of the following:

        E_StateIndices.RECURSIVE -- which means that the template recurses
                                    to itself.

        Scalar Value X           -- All states that are involved in the template
                                    trigger for the given interval to the same
                                    state given by 'X'.

        MegaState_Target T       -- which means that the target state depends 
                                    on the state_key. 'T[state_key]' tells the
                                    target state when the templates operates
                                    for a state given by 'state_key'.

"""

def do(TheAnalyzer, MinGain, CompressionType, 
       AvailableStateIndexList, MegaStateList):
    """RETURNS: List of TemplateState-s that were identified from states in
                TheAnalyzer.

       ALGORITHM: 

       The CombinationDB computes for all possible combinations of states A and
       B an object of class TemplateStateCandidate. That is a template state that
       represents the combination of A and B. By means of a call to '.combine_best()'
       the candidate with the highest expected gain replaces the two states that 
       it represents. This candidate enters the CombinationDB as any other state
       and candidates of combinations with other states are computed. In this sense
       the iteration of calls to '.combine_next()' happen until no meaningful
       combination of states can be identified.
    """
    assert CompressionType in (E_Compression.TEMPLATE, E_Compression.TEMPLATE_UNIFORM)
    assert isinstance(MinGain, (int, long, float))

    # (*) The Combination Process
    #
    # CombinationDB: -- Keep track of possible combinations between states.
    #                -- Can determine best matching state candidates for combination.
    #                -- Replaces two combined states by TemplateState.
    #
    # (A 'state' in the above sense can also be a TemplateState)
    combiner = CombinationDB(TheAnalyzer, MinGain, CompressionType, AvailableStateIndexList)

    # Combine states until there is nothing that can be reasonably be combined.
    while combiner.combine_best():
        pass

    done_state_index_set, template_state_list = combiner.result()

    print "##RESULT:", done_state_index_set
    print "         ", len(template_state_list), [x.index for x in template_state_list]
    return done_state_index_set, template_state_list

class CombinationDB:
    """Contains the 'Gain' for each possible combination of states. This includes
       TemplateStates which are already combined. States are referred by state
       index. Internally, a list is maintained that stores for each possible 
       combination the gain. This list is sorted, so that a simple '.pop()' returns
       the best gain, and the two state indices that would need to be combined. 

       The 'matrix' is not actually a matrix. But, the name shall indicate that 
       the gain is computed for each possible pair as it could be nicely displayed
       in a matrix, e.g.

                       0     1    2     4
                  0    0   -4.0  2.1   7.1      The matrix is, of course, 
                  1          0  -0.8   2.1      symmetric.
                  2               0    1.2
                  4                     0

       (1) .__base(): The 'matrix' is first computed for all states.

       (2) .pop_best(): When the best pair is popped, the correspondent 
                        entries are deleted from the 'matrix'.
       (3) .enter(): The combined states is then entered. The gains for
                     combination with the other states in the 'matrix' 
                     is computed.
    """
    def __init__(self, TheAnalyzer, MinGain, CompressionType, AvailableStateIndexList):
        assert CompressionType in (E_Compression.TEMPLATE, E_Compression.TEMPLATE_UNIFORM)
        assert MinGain >= 0
        self.__uniformity_required_f = (CompressionType == E_Compression.TEMPLATE_UNIFORM)

        # (*) Database of states that are subject to combination tries.
        #
        # Do not consider: -- tates with empty transition maps
        #                  -- states which are no more availabe for combination
        #                  -- the init state.
        # x[0] = state_index, x[1] = state
        condition = lambda x:     len(x[1].transition_map) != 0 \
                              and x[0] in AvailableStateIndexList \
                              and x[1].init_state_f == False

        # Represent each state by a PseudoMegaState that behaves uniformly with the 
        # resulting TemplateStates.
        self.__db = dict( (state_index, PseudoMegaState(state, TheAnalyzer)) \
                          for state_index, state in ifilter(condition, TheAnalyzer.state_db.iteritems()) )

        self.__analyzer    = TheAnalyzer
        self.__min_gain    = float(MinGain)
        self.__gain_matrix = self.__base()
        self.__door_id_replacement_db = None

    def combine_best(self):
        """Finds the two best matching states and combines them into one.
           If no adequate state pair can be found 'False' is returned.
           Else, 'True'.
        """
        elect = self.pop_best()
        if elect is None: return False

        # The 'candidate' is a TemplateStateCandidate which is derived from 
        # TemplateState. Thus, it can play the TemplateState role without
        # modification. Only, a meaningful index has to be assigned to it.
        self.enter(elect)
        return True

    def result_iterable(self):
        """RETURNS: List of TemplateStates. Those are the states that have been 
                    generated from combinations of analyzer states.
        """
        return ifilter(lambda x: isinstance(x, TemplateState), self.__db.itervalues())

    def result(self):
        """RETURNS: List of TemplateStates. Those are the states that have been 
                    generated from combinations of analyzer states.
        """
        template_state_list = [ x for x in self.__db.itervalues() if isinstance(x, TemplateState) ]
        done_state_index_set = set()
        for state in template_state_list:
            done_state_index_set.update(state.state_index_list)
        return done_state_index_set, template_state_list

    @property
    def gain_matrix(self):
        return self.__gain_matrix

    def __base(self):
        """Compute TemplateStateCandidate-s for each possible combination of 
           two states in the StateDB. If the gain of a combination is less 
           that 'self.__min_gain' then it is not considered.
        """
        state_list = self.__db.values()
        L          = len(state_list)

        # Pre-allocate the result array to avoid frequent allocations
        #
        # NOTE: L * (L - 1) is always even, i.e. dividable by 2.
        #       Proof:
        #       (a) L even = k * 2:     -> k * 2 ( k * 2 - 1 )            = k * k * 4 - k * 2
        #                                = even - even = even
        #       (b) L odd  = k * 2 + 1: -> (k * 2 + 1) * ( k * 2 + 1 - 1) = k * k * 4 + k * 2
        #                                = even + even = even
        # 
        #       => division by two without remainder 
        MaxSize = (L * (L - 1)) / 2
        result  = [None] * MaxSize
        n       = 0
        for i, i_state in enumerate(state_list):
            for k_state in islice(state_list, i + 1, None):

                if self.__uniformity_required_f:
                    # Rely on __eq__ operator (used '=='). '!=' uses __neq__ 
                    if   not (i_state.drop_out == k_state.drop_out):    continue
                    elif not (i_state.entry.is_uniform(k_state.entry)): continue

                candidate = TemplateStateCandidate(i_state, k_state, self.__analyzer)

                if candidate.gain >= self.__min_gain:
                    result[n] = (i_state.index, k_state.index, candidate)
                    n += 1

        if n != MaxSize:
            del result[n:]

        # Sort according to delta cost
        result.sort(key=lambda x: x[2].gain)
        return result

    def enter(self, NewState):
        """Adapt the __gain_matrix to include candidates of combinations with
           the NewState.
        """
        assert isinstance(NewState, TemplateState)
        # The new state index must be known. It is used in the gain matrix.
        # But, the new state does not need to be entered into the db, yet.

        # Avoid extensive 'appends' by single allocation (see initial computation)
        MaxIncrease = len(self.__db) 
        n           = len(self.__gain_matrix)
        MaxSize     = len(self.__gain_matrix) + MaxIncrease
        self.__gain_matrix.extend([None] * MaxIncrease)

        for state in self.__db.itervalues():
            if self.__uniformity_required_f:
                # Rely on __eq__ operator (used '=='). '!=' uses __neq__ 
                if   not (state.drop_out == NewState.drop_out):    continue
                elif not (state.entry.is_uniform(NewState.entry)): continue

            candidate = TemplateStateCandidate(NewState, state, self.__analyzer)

            if candidate.gain >= self.__min_gain:
                self.__gain_matrix[n] = (state.index, NewState.index, candidate)
                n += 1

        if n != MaxSize:
            del self.__gain_matrix[n:]

        self.__gain_matrix.sort(key=lambda x: x[2].gain)

        self.__db[NewState.index] = NewState

    def pop_best(self):
        """Determines the two states that result in the greatest gain if they are 
           combined into a TemplateState. 

           If no combination has a "gain >= self.__min_gain", then None
           is returned. This is ensured, by not letting any entry enter the
           __gain_matrix, where 'gain < self.__min_gain'.

           RETURNS: TemplateStateCandidate of combination of states with the 
                    greatest gain. 
                    None, if there is no more.
        """

        if len(self.__gain_matrix) == 0: return None

        # (*) The entry with the highest gain is at the tail of the list.
        i, k, elect = self.__gain_matrix.pop()

        # (*) Delete related entries in __gain_matrix and database. 
        # 
        # If 'i' or 'k' referes to a 'normal' state, then any combination with each 
        # of those is removed from the list of candidates. This candidate, let it 
        # have state index 'p', is the only state that contains now 'i' and 'k'. Any
        # state, with index 'q', that combines with it does not contain 'i' and 
        # 'k'. And, on the event of combining 'p' and 'q' all other combinations
        # related to 'p' are deleted, thus all other combinations that contain
        # 'i' and 'k'.
        # => The consideration of 'implemented_state_index_list' is not necessary.
        self.__gain_matrix_delete(i)
        self.__gain_matrix_delete(k)

        # (*) If the following fails, it means that states have been combined twice
        del self.__db[i]
        del self.__db[k]

        # (*) Adapt all transition maps with their door_ids
        replacement_db = elect.entry.door_id_replacement_db
        replacement_db.update(elect.local_door_id_replacement_db)
        for state in self.__db.itervalues():
            state.replace_door_ids_in_transition_map(replacement_db)
            t_db = defaultdict(list)
            for door_id, transition_id_list in elect.entry.transition_db.iteritems():
                if door_id.door_index == 0:
                    # The root door
                    t_db[door_id] = []
                else:
                    for transition_id in transition_id_list:
                        if not state.entry.door_db.has_key(transition_id): continue
                        t_db[door_db].append(transition_id)
            state.entry.set_transition_db(t_db)

        # Double Check: No state shall refer to a Door of the combined states.
        for state in self.__db.itervalues():
            for door_id in state.entry.door_db.itervalues():
                assert door_id.state_index != i 
                assert door_id.state_index != k 
                assert self.__db.has_key(door_id.state_index), \
                       "%s--\n%s\n" % (state.entry.transition_db, door_id)
            for door_id in state.entry.transition_db.iterkeys():
                assert door_id.state_index != i 
                assert door_id.state_index != k 
                assert self.__db.has_key(door_id.state_index), \
                       "%s--\n%s\n" % (state.entry.transition_db, door_id)
            for interval, target in state.transition_map:
                if target.drop_out_f: 
                    continue
                elif target.door_id is not None:
                    assert door_id.state_index != i 
                    assert door_id.state_index != k 
                    assert self.__db.has_key(door_id.state_index), \
                           "%s--\n%s\n" % (state.entry.transition_db, door_id)
                    target_state = self.__db[door_id.state_index]
                    assert target_state.entry.transition_db.has_key(door_id), \
                           "%s--\n%s\n" % (state.entry.transition_db, door_id)
                else:
                    for door_id in target.scheme:
                        assert door_id.state_index != i 
                        assert door_id.state_index != k 
                        assert self.__db.has_key(door_id.state_index), \
                               "%s--\n%s\n" % (state.entry.transition_db, door_id)
                        target_state = self.__db[door_id.state_index]
                        assert target_state.entry.transition_db.has_key(door_id), \
                               "%s--\n%s\n" % (state.entry.transition_db, door_id)

        print "##ELECT:", elect.index,  elect._DEBUG_combined_state_indices()
        print "##     :", replacement_db
        return elect

    def __gain_matrix_delete(self, StateIndex):
        """Delete all related entries in the '__gain_matrix' that relate to states
           I and K. This function is used after the decision has been made that 
           I and K are combined into a TemplateState. None of them can be combined
           with another state anymore.
        """
        size = len(self.__gain_matrix)
        i    = 0
        while i < size:
            entry = self.__gain_matrix[i]
            if entry[0] == StateIndex or entry[1] == StateIndex:
                del self.__gain_matrix[i]
                size -= 1
            else:
                i += 1

        return 

    def __len__(self):
        return len(self.__db)

    def __getitem__(self, Key):
        assert False # This function should not be used, actually
        assert type(Key) == long
        return self.__db[Key]

    def iteritems(self):
        for x in self.__db.iteritems():
            yield x


