# MAIN CLASSES:
#
# (*) Command:
#
#     .id      -- identifies the command (from E_Commands)
#     .content -- 'Arguments' and/or additional information
#                 (Normally a tuple, 'AccepterContent' is a real class).
#  
# (*) CommandFactory:
#
#     Contains the database of all available commands. The '.do()' member
#     function can generate a command based on a set of arguments and 
#     the command's identifier.
#
#     CommandInfo:
#
#     Tells about the attributes of each command, i.e. its 'cost', its access
#     type (read/write/none) a constructor for the class of the '.content'
#     member.
#
#     CommandFactory.db:
#
#               Command identifier ----> CommandInfo
#
#     Maps from a command identifier (see E_Commands) to a CommandInfo. The
#     CommandInfo is used to create a Command.
#
# (*) CommandList:
#
#     A class which represents a sequence of Command-s. There is one special
#     function in this class '.get_shared_tail(Other)' which allows to find
#     find shared Command-s in 'self' and 'Other' so that each CommandList
#     can do its own Command-s followed by the shared tail. 
#
#     This 'shared tail' is used for the 'door tree construction'. That is, 
#     upon entry into a state the CommandList-s may different dependent on
#     the source state, but some shared commands may be the same. Those
#     shared commands are then only implemented once and not for each source
#     state separately.
#______________________________________________________________________________
#
# EXPLANATION:
#
# Command-s represent operations such as 'Accept X if Pre-Context Y fulfilled'
# or 'Store Input Position in Position Register X'. They are used to control
# basic operations of the pattern matching state machine.
#
# A command is generated by the CommandFactory's '.do(id, parameters)'
# function. For clarity, dedicated functions may be used, do provide a more
# beautiful call to the factory, for example:
#
#     cmd = StoreInputPosition(PreContextID, PositionRegister, Offset)
#
# is equivalent to
#
#     cmd = CommandFactory.do(E_Commands.StoreInputPosition, 
#                             (PreContextID, PositionRegister, Offset))
#
# where, undoubtedly the first is much easier to read. 
#
# ADAPTATION:
#
# The list of commands is given by 'E_Commands' and the CommandFactory's '.db' 
# member. That is, to add a new command requires an identifier in E_Commands,
# and an entry in the CommandFactory's '.db' which associates the identifier
# with a CommandInfo. Additionally, the call to the CommandFactory may be 
# abbreviated by a dedicated function as in the example above.
#______________________________________________________________________________
#
# (C) Frank-Rene Schaefer
#______________________________________________________________________________
from   quex.engine.misc.enum import Enum
from   quex.blackboard       import E_Commands, \
                                    E_PreContextIDs, \
                                    E_TransitionN, \
                                    E_IncidenceIDs, \
                                    E_PostContextIDs

from   collections import namedtuple
from   operator    import attrgetter
from   copy        import deepcopy, copy

#______________________________________________________________________________
# Command: Information about an operation to be executed. It consists mainly
#     of a command identifier (from E_Commands) and the content which specifies
#     the command further.
#______________________________________________________________________________
class Command(namedtuple("Command_tuple", ("id", "content", "my_hash"))):
    def __new__(self, Id, Content, Hash=None):
        if Hash is None: Hash = hash(Id) ^ hash(Content)
        return super(Command, self).__new__(self, Id, Content, Hash)

    def clone(self):         
        if self.content is None:
            content = None
        elif hasattr(self.content, "clone"): 
            content = self.content.clone()
        else:
            content = deepcopy(self.content)
        return Command(self.id, content, self.my_hash)

    def get_pretty_string(self):
        assert False, "Use self.__str__() instead!"

    def __hash__(self):      
        return self.my_hash

    def __str__(self):
        name_str = str(self.id)
        if self.content is None:
            return "%s" % name_str
        elif self.id == E_Commands.StoreInputPosition:
            x = self.content
            txt = ""
            if x.pre_context_id != E_PreContextIDs.NONE:
                txt = "if '%s': " % repr_pre_context_id(x.pre_context_id)
            if x.offset == 0:
                txt += "%s = input_p;\n" % repr_position_register(x.position_register)
            else:
                txt += "%s = input_p - %i;\n" % (repr_position_register(x.position_register), x.offset)
            return txt
        elif self.id == E_Commands.Accepter:
            return str(self.content)
        elif self.id == E_Commands.PreContextOK:
            return "pre-context-fulfilled = %s;\n" % self.content.pre_context_id
        else:
            content_str = "".join("%s=%s, " % (member, value) for member, value in self.content._asdict().iteritems())
            return "%s: { %s }" % (name_str, content_str)

#______________________________________________________________________________
#
# AccepterContent(virtually Command): A list of conditional pattern acceptance 
#     actions. It corresponds to a sequence of if-else statements such as 
#
#       [0]  if   pre_condition_4711_f: acceptance = Pattern32
#       [1]  elif pre_condition_512_f:  acceptance = Pattern21
#       [2]  else:                      acceptance = Pattern56
# 
# AccepterContentElement: An element in the sorted list of test/accept commands. 
#     It contains the 'pre_context_id' of the condition to be checked and the 
#     'acceptance_id' to be accepted if the condition is true.
#______________________________________________________________________________
AccepterContentElement = namedtuple("AccepterContentElement", ("pre_context_id", "acceptance_id"))
class AccepterContent:
    def __init__(self, PathTraceList=None):
        Command.__init__(self)
        if PathTraceList is None: 
            self.__list = []
        else:
            self.__list = [ AccepterContentElement(x.pre_context_id, x.acceptance_id) for x in PathTraceList ]

    def clone(self):
        result = AccepterContent()
        result.__list = [ deepcopy(x) for x in self.__list ]
        return result
    
    def add(self, PreContextID, AcceptanceID):
        self.__list.append(AccepterContentElement(PreContextID, AcceptanceID))

    def clean_up(self):
        """Ensure that nothing follows and unconditional acceptance."""
        self.__list.sort(key=attrgetter("acceptance_id"))
        for i, x in enumerate(self.__list):
            if x.pre_context_id == E_PreContextIDs.NONE:
                break
        if i != len(self.__list) - 1:
            del self.__list[i+1:]

    def get_pretty_string(self):
        txt    = []
        if_str = "if     "
        for x in self.__list:
            if x.pre_context_id != E_PreContextIDs.NONE:
                txt.append("%s %s: " % (if_str, repr_pre_context_id(x.pre_context_id)))
            else:
                if if_str == "else if": txt.append("else: ")
            txt.append("last_acceptance = %s\n" % repr_acceptance_id(x.acceptance_id))
            if_str = "else if"
        return txt

    # Require '__hash__' and '__eq__' to be element of a set.
    def __hash__(self): 
        xor_sum = 0
        for x in self.__list:
            if isinstance(x.acceptance_id, (int, long)): xor_sum ^= x.acceptance_id
        return xor_sum

    def __eq__(self, Other):
        if not isinstance(Other, AccepterContent):             return False
        if len(self.__list) != len(Other.__list):       return False
        for x, y in zip(self.__list, Other.__list):
            if   x.pre_context_id != y.pre_context_id:  return False
            elif x.acceptance_id     != y.acceptance_id:      return False
        return True

    def __iter__(self):
        for x in self.__list:
            yield x

    def __str__(self):
        def to_string(X, FirstF):
            if X.pre_context_id == E_PreContextIDs.NONE:
                return "last_acceptance = %s" % repr_acceptance_id(X.acceptance_id)
            elif FirstF:
                return "if %s:  last_acceptance = %s" % (repr_pre_context_id(element.pre_context_id), repr_acceptance_id(element.acceptance_id))
            else:
                return "else if %s:  last_acceptance = %s" % (repr_pre_context_id(element.pre_context_id), repr_acceptance_id(element.acceptance_id))

        return "".join(["%s\n" % to_string(element, i==0) for i, element in enumerate(self.__list)])

E_InputPAccess = Enum("WRITE",     # writes value to 'x'
                      "READ",      # reads value of 'x'
                      "NONE",      # does nothing to 'x'
                      "BRANCH",    # commands cannot be moved before or after this command
                      "E_InputAccess_DEBUG")

#______________________________________________________________________________
# CommandInfo: Information about a command. CommandInfo-s provide information
#     about commands based on the command identifier. That is:
#
#     .cost         -- The computational cost of the operation.
#     .access       -- What it access and whether it is read or write.
#     .content_type -- Information so that the 'CommandFactory' can generate
#                      a command based on the command identifier.
#______________________________________________________________________________
class CommandInfo(namedtuple("CommandInfo_tuple", ("cost", "access", "content_type"))):
    def __new__(self, Cost, Access, ContentType=None):
        if type(ContentType) == tuple: content_type = namedtuple("Command_tuple", ContentType)
        else:                          content_type = ContentType
        return super(CommandInfo, self).__new__(self, Cost, Access, content_type)

    @property
    def read_f(self):  return self.access == E_InputPAccess.READ

    @property
    def write_f(self): return self.access == E_InputPAccess.WRITE


#______________________________________________________________________________
# CommandFactory: Produces Command-s. It contains a database which maps from 
#     command identifiers to CommandInfo-s. And, it contains the '.do()' 
#     function which produces Command-s.
#
# For a sleeker look, dedicated function are provided below which all implement
# a call to 'CommandFactory.do()' in a briefer way.
#______________________________________________________________________________
class CommandFactory:
    db = {
        E_Commands.Accepter:                         CommandInfo(1, E_InputPAccess.NONE,   AccepterContent),
        E_Commands.GotoDoorId:                       CommandInfo(1, E_InputPAccess.BRANCH, ("door_id",)),
        E_Commands.GotoDoorIdIfInputPLexemeEnd:      CommandInfo(1, E_InputPAccess.BRANCH, ("door_id",)),
        E_Commands.InputPToLexemeStartP:             CommandInfo(1, E_InputPAccess.WRITE),
        E_Commands.InputPDecrement:                  CommandInfo(1, E_InputPAccess.WRITE),
        E_Commands.InputPDereference:                CommandInfo(1, E_InputPAccess.READ),
        E_Commands.InputPIncrement:                  CommandInfo(1, E_InputPAccess.WRITE),
        E_Commands.LexemeResetTerminatingZero:       CommandInfo(1, E_InputPAccess.WRITE),
        E_Commands.LexemeStartToReferenceP:          CommandInfo(1, E_InputPAccess.READ,   ("pointer_name",)),
        E_Commands.ColumnCountReferencePSet:         CommandInfo(1, E_InputPAccess.NONE,   ("pointer_name", "offset")),
        E_Commands.ColumnCountReferencePDeltaAdd:    CommandInfo(1, E_InputPAccess.NONE,   ("pointer_name", "column_n_per_chunk")),
        E_Commands.ColumnCountGridAdd:               CommandInfo(1, E_InputPAccess.NONE,   ("grid_size",)),
        E_Commands.ColumnCountGridAddWithReferenceP: CommandInfo(1, E_InputPAccess.NONE,   ("grid_size", "pointer_name", "column_n_per_chunk")),
        E_Commands.ColumnCountAdd:                   CommandInfo(1, E_InputPAccess.NONE,   ("value",)),
        E_Commands.LineCountAdd:                     CommandInfo(1, E_InputPAccess.NONE,   ("value",)),
        E_Commands.LineCountAddWithReferenceP:       CommandInfo(1, E_InputPAccess.NONE,   ("value", "pointer_name", "column_n_per_chunk")),
        E_Commands.PathIteratorSet:                  CommandInfo(1, E_InputPAccess.NONE,   ("path_walker_id", "path_id", "offset")),
        E_Commands.PreContextOK:                     CommandInfo(1, E_InputPAccess.NONE,   ("pre_context_id",)),
        E_Commands.PrepareAfterReload:               CommandInfo(1, E_InputPAccess.NONE,   ("on_success_door_id", "on_failure_door_id")),
        E_Commands.StoreInputPosition:               CommandInfo(1, E_InputPAccess.READ,   ("pre_context_id", "position_register", "offset")),
        E_Commands.TemplateStateKeySet:              CommandInfo(1, E_InputPAccess.NONE,   ("state_key",)),
        # CountColumnN_ReferenceSet
        # CountColumnN_ReferenceAdd
        # CountColumnN_Add
        # CountColumnN_Grid
        # CountLineN_Add
    }

    @staticmethod
    def do(Id, ParameterList=None):
        # TODO: Consider 'Flyweight pattern'. Check wether object with same content exists, 
        #       then return pointer to object in database.
        assert ParameterList is None or type(ParameterList) == tuple, "ParameterList: '%s'" % str(ParameterList)
        content_type = CommandFactory.db[Id].content_type
        if ParameterList is None:
            if content_type is None: content = None
            else:                    content = content_type()
        else:
            L        = len(ParameterList)
            if   L == 0: content = None
            elif L == 1: content = content_type(ParameterList[0])
            elif L == 2: content = content_type(ParameterList[0], ParameterList[1])
            elif L == 3: content = content_type(ParameterList[0], ParameterList[1], ParameterList[2])

        return Command(Id, content)

def StoreInputPosition(PreContextID, PositionRegister, Offset):
    return CommandFactory.do(E_Commands.StoreInputPosition, (PreContextID, PositionRegister, Offset,))

def PreContextOK(PreContextID):
    return CommandFactory.do(E_Commands.PreContextOK, (PreContextID,))

def TemplateStateKeySet(StateKey):
    return CommandFactory.do(E_Commands.TemplateStateKeySet, (StateKey,))

def PathIteratorSet(PathWalkerID, PathID, Offset):
    return CommandFactory.do(E_Commands.PathIteratorSet, (PathWalkerID, PathID, Offset,))

def PathIteratorIncrement():
    return CommandFactory.do(E_Commands.PathIteratorIncrement)

def PrepareAfterReload(OnSuccessDoorId, OnFailureDoorId):
    return CommandFactory.do(E_Commands.PrepareAfterReload, (OnSuccessDoorId, OnFailureDoorId,))

def InputPIncrement():
    return CommandFactory.do(E_Commands.InputPIncrement)

def InputPDecrement():
    return CommandFactory.do(E_Commands.InputPDecrement)

def InputPDereference():
    return CommandFactory.do(E_Commands.InputPDereference)

def InputPToLexemeStartP():
    return CommandFactory.do(E_Commands.InputPToLexemeStartP)

def LexemeStartToReferenceP(PointerName):
    return CommandFactory.do(E_Commands.LexemeStartToReferenceP, (PointerName,))

def LexemeResetTerminatingZero():
    return CommandFactory.do(E_Commands.LexemeResetTerminatingZero)

def ColumnCountReferencePSet(PointerName, Offset=0):
    return CommandFactory.do(E_Commands.ColumnCountReferencePSet, (PointerName, Offset,))

def ColumnCountReferencePDeltaAdd(PointerName, ColumnNPerChunk):
    return CommandFactory.do(E_Commands.ColumnCountReferencePDeltaAdd, (PointerName, ColumnNPerChunk,))

def ColumnCountAdd(Value):
    return CommandFactory.do(E_Commands.ColumnCountAdd, (Value,))

def ColumnCountGridAdd(GridSize):
    return CommandFactory.do(E_Commands.ColumnCountGridAdd, (GridSize,))

def ColumnCountGridAddWithReferenceP(Value, PointerName, ColumnNPerChunk):
    return CommandFactory.do(E_Commands.ColumnCountGridAddWithReferenceP, (Value, PointerName,ColumnNPerChunk))

def LineCountAdd(Value):
    return CommandFactory.do(E_Commands.LineCountAdd, (Value,))

def LineCountAddWithReferenceP(Value, PointerName, ColumnNPerChunk):
    return CommandFactory.do(E_Commands.LineCountAddWithReferenceP, (Value, PointerName, ColumnNPerChunk))

def GotoDoorId(DoorId):
    return CommandFactory.do(E_Commands.GotoDoorId, (DoorId,))

def GotoDoorIdIfInputPLexemeEnd(DoorId):
    return CommandFactory.do(E_Commands.GotoDoorIdIfInputPLexemeEnd, (DoorId,))

def Accepter():
    return CommandFactory.do(E_Commands.Accepter)

class CommandList(list):
    """CommandList -- a list of commands -- Intend: 'tuple' => immutable.
    """
    def __init__(self, *CL):
        self.__enter_list(CL)

    def __enter_list(self, CmdList):
        for cmd in CmdList:
            assert isinstance(cmd, Command), "%s: %s" % (cmd.__class__, cmd)
        super(CommandList, self).__init__(CmdList)

    @classmethod
    def from_iterable(cls, Iterable):
        result = CommandList()
        result.__enter_list(list(Iterable))
        return result

    def concatinate(self, Second):
        result = CommandList()
        # As soon as CommandList and Commands are 100% is immutable, 
        # 'clone' will not be necessary.
        result.__enter_list([ x.clone() for x in self ] + [ x.clone() for x in Second ])
        return result

    def cut(self, NoneOfThis):
        """Delete all commands of SharedTail from this command list.
        """
        cmd_list = list(self)
        i        = len(cmd_list) - 1
        while i >= 0:
            if cmd_list[i] in NoneOfThis:
                del cmd_list[i]
            i -= 1

        return CommandList.from_iterable(cmd_list)

    def clone(self):
        return CommandList.from_iterable(self)

    @staticmethod
    def get_shared_tail(This, That):
        """DEFINITION 'shared tail':
        
        ! A 'shared tail' is a list of commands. For each command of a        !
        ! shared tail, it holds that:                                         !
        !                                                                     !
        !  -- it appears in 'This' and 'That'.                                !
        !  -- if it is a 'WRITE', there is no related 'READ' or 'WRITE'       !
        !     command in This or That coming after the shared command.        !
        !  -- if it is a 'READ', there no related 'WRITE' command in          !
        !     This or That coming after the shared command.                   !

        The second and third condition is essential, so that the shared tail
        can be implemented from a joining point between 'This' and 'That'.
        Consider

            This:                               That:
            * position = input_p # READ         * position = input_p;
            * ++input_p          # WRITE        * input = *input_p;
            * input = *input_p;                      

        The 'position = input_p' cannot appear after '++input_p'. Let input_p
        be 'x' at the entry of This and That. This and That, both result in
        'position = x'. Then a combination, however, without second and third 
        condition results in

            This:                           That:
            * ++input_p;         # READ     * input = *input_p;
            * input = *input_p;                /
                          \                   /
                           \                 /
                          * position = input_p;   # WRITE (Error for This)

        which in the case of 'This' results in 'position = x + 1' (ERROR).
        """
        def is_related_to_unshared_write(CmdI, CmdList, SharedISet):
            for i in xrange(CmdI+1, len(CmdList)):
                cmd = CmdList[i]
                if CommandFactory.db[cmd.id].write_f and i not in SharedISet: 
                    return True
            return False

        def is_related_to_unshared_read_write(CmdI, CmdList, SharedISet):
            for i in xrange(CmdI+1, len(CmdList)):
                cmd = CmdList[i]
                if (CommandFactory.db[cmd.id].write_f or CommandFactory.db[cmd.id].read_f) and i not in SharedISet: 
                    return True
            return False

        shared_list = []
        done_k      = set() # The same command cannot be shared twice
        for i, cmd_a in enumerate(This):
            for k, cmd_b in enumerate(That):
                if   k in done_k:    continue
                elif cmd_a != cmd_b: continue
                shared_list.append((cmd_a, i, k))
                done_k.add(k) # Command 'k' has been shared. Prevent sharing twice.
                break         # Command 'i' hass been shared, continue with next 'i'.

        change_f = True
        while change_f:
            change_f     = False
            shared_i_set = set(x[1] for x in shared_list)
            shared_k_set = set(x[2] for x in shared_list)
            i            = len(shared_list) - 1
            while i >= 0:
                candidate, this_i, that_k = shared_list[i]
                if     CommandFactory.db[candidate.id].write_f \
                   and (   is_related_to_unshared_read_write(this_i, This, shared_i_set) \
                        or is_related_to_unshared_read_write(that_k, That, shared_k_set)):
                    del shared_list[i]
                    change_f = True
                if     CommandFactory.db[candidate.id].read_f \
                   and (   is_related_to_unshared_write(this_i, This, shared_i_set) \
                        or is_related_to_unshared_write(that_k, That, shared_k_set)):
                    del shared_list[i]
                    change_f = True
                else:
                    pass
                i -= 1

        return CommandList.from_iterable(cmd for cmd, i, k in shared_list) 

    def is_empty(self):
        return super(CommandList, self).__len__() == 0

    def cost(self):
        return sum(CommandFactory.db[cmd.id].cost for cmd in self)

    def has_command_id(self, CmdId):
        assert CmdId in E_Commands
        for cmd in self:
            if cmd.id == CmdId: return True
        return False

    def access_accepter(self):
        """Gets the accepter from the command list. If there is no accepter
        yet, then it creates one and adds it to the list.
        """
        accepter = None
        for cmd in self:
            if cmd.id == E_Commands.Accepter:
                accepter = cmd
                break

        if accepter is None:
            accepter = Accepter()
            self.append(accepter)

        return accepter

    def replace_position_registers(self, PositionRegisterMap):
        """Replace for any position register indices 'x' and 'y' given by
         
                      y = PositionRegisterMap[x]

        replace register index 'x' by 'y'.
        """
        if PositionRegisterMap is None or len(PositionRegisterMap) == 0: 
            return

        for i in xrange(len(self)):
            cmd = self[i]
            if cmd.id != E_Commands.StoreInputPosition: continue

            # Commands are immutable, so create a new one.
            new_command = StoreInputPosition(cmd.content.pre_context_id, 
                                             PositionRegisterMap[cmd.content.position_register],
                                             cmd.content.offset)
            self[i] = new_command

    def delete_superfluous_commands(self):
        """
        (1) A position storage which is unconditional makes any conditional
            storage superfluous. Those may be deleted without loss.
        (2) A position storage does not have to appear twice, leave the first!
            (This may occur due to register set optimization!)
        """
        for cmd in self:
            assert isinstance(cmd, Command), "%s" % cmd

        # (1) Unconditional rules out conditional
        unconditional_position_register_set = set(
            cmd.content.position_register
            for cmd in self \
                if     cmd.id == E_Commands.StoreInputPosition \
                   and cmd.content.pre_context_id == E_PreContextIDs.NONE
        )
        i = len(self) - 1
        while i >= 0:
            cmd = self[i]
            if cmd.id != E_Commands.StoreInputPosition:
                pass
            elif    cmd.content.position_register in unconditional_position_register_set \
                and cmd.content.pre_context_id != E_PreContextIDs.NONE:
                del self[i]
            i -= 1

        # (2) Storage command does not appear twice. Keep first.
        #     (May occur due to optimizations!)
        occured_set = set()
        size        = len(self)
        i           = 0
        while i < size:
            cmd = self[i]
            if cmd.id == E_Commands.StoreInputPosition: 
                if cmd not in occured_set: 
                    occured_set.add(cmd)
                else:
                    del self[i]
                    size -= 1
                    continue
            i += 1
        return

    def __hash__(self):
        xor_sum = 0
        for cmd in self:
            xor_sum ^= hash(cmd)
        return xor_sum

    def __eq__(self, Other):
        if isinstance(Other, CommandList) == False: return False
        return super(CommandList, self).__eq__(Other)

    def __ne__(self, Other):
        return not self.__eq__(Other)

    def __str__(self):
        return "".join("%s\n" % str(cmd) for cmd in self)

def repr_acceptance_id(Value, PatternStrF=True):
    if   Value == E_IncidenceIDs.VOID:                       return "last_acceptance"
    elif Value == E_IncidenceIDs.MATCH_FAILURE:                    return "Failure"
    elif Value >= 0:                                    
        if PatternStrF: return "Pattern%i" % Value
        else:           return "%i" % Value
    else:                                               assert False

def repr_position_register(Register):
    if Register == E_PostContextIDs.NONE: return "position[Acceptance]"
    else:                                 return "position[PostContext_%i] " % Register

def repr_pre_context_id(Value):
    if   Value == E_PreContextIDs.NONE:          return "Always"
    elif Value == E_PreContextIDs.BEGIN_OF_LINE: return "BeginOfLine"
    elif Value >= 0:                             return "PreContext_%i" % Value
    else:                                        assert False

def repr_positioning(Positioning, PositionRegisterID):
    if   Positioning == E_TransitionN.VOID: 
        return "pos = %s;" % repr_position_register(PositionRegisterID)
    elif Positioning == E_TransitionN.LEXEME_START_PLUS_ONE: 
        return "pos = lexeme_start_p + 1; "
    elif Positioning > 0:   
        return "pos -= %i; " % Positioning
    elif Positioning == 0:  
        return ""
    else: 
        assert False

