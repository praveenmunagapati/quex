# MAIN CLASSES:
#
# (*) Command:
#
#     .id      -- identifies the command (from E_Cmd)
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
#     Maps from a command identifier (see E_Cmd) to a CommandInfo. The
#     CommandInfo is used to create a Command.
#
# (*) CommandList:
#
#     A class which represents a sequence of Command-s. 

#     'command.shared_tail.get(A, B)' find shared Command-s in 'A' and 'B'.
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
#     cmd = CommandFactory.do(E_Cmd.StoreInputPosition, 
#                             (PreContextID, PositionRegister, Offset))
#
# where, undoubtedly the first is much easier to read. 
#
# ADAPTATION:
#
# The list of commands is given by 'E_Cmd' and the CommandFactory's '.db' 
# member. That is, to add a new command requires an identifier in E_Cmd,
# and an entry in the CommandFactory's '.db' which associates the identifier
# with a CommandInfo. Additionally, the call to the CommandFactory may be 
# abbreviated by a dedicated function as in the example above.
#______________________________________________________________________________
#
# (C) Frank-Rene Schaefer
#______________________________________________________________________________
from   quex.engine.misc.enum import Enum
from   quex.engine.tools     import typed
from   quex.blackboard       import E_Cmd, \
                                    E_PreContextIDs, \
                                    E_TransitionN, \
                                    E_IncidenceIDs, \
                                    E_PostContextIDs

from   collections import namedtuple
from   operator    import attrgetter
from   copy        import deepcopy, copy
import types

E_R = Enum("AcceptanceRegister",
           "Buffer",
           "Indentation",
           "Column",
           "Input",
           "Indentation",
           "InputP",
           "LexemeStartP",
           "LexemeEnd",
           "CharacterBeginP",  # -> dynamic size codecs
           "Line",
           "PathIterator",
           "PreContextFlags",
           "ReferenceP",
           "PositionRegister",
           "Pointer",
           "TargetStateElseIndex",
           "TargetStateIndex",
           "TemplateStateKey",
           "ThreadOfControl")


class Command(namedtuple("Command_tuple", ("id", "content", "my_hash"))):
    """_________________________________________________________________________
    Information about an operation to be executed. It consists mainly of a 
    command identifier (from E_Cmd) and the content which specifies the command 
    further.
    ____________________________________________________________________________
    """
    # Commands which shall appear only once in a command list:
    unique_set = (E_Cmd.TemplateStateKeySet, E_Cmd.PathIteratorSet)

    def __new__(self, Id, *ParameterList):
        global _content_db
        # TODO: Consider 'Flyweight pattern'. Check wether object with same content exists, 
        #       then return pointer to object in database.
        content_type = _content_db[Id]
        if content_type is None:
            # No content
            content = None
        elif isinstance(content_type, types.ClassType):
            # Use 'real' constructor
            content = content_type() 
        else:
            # A tuple that describes the usage of the 'namedtuple' constructor.
            L = len(ParameterList)
            assert L != 0
            if   L == 1: content = content_type(ParameterList[0])
            elif L == 2: content = content_type(ParameterList[0], ParameterList[1])
            elif L == 3: content = content_type(ParameterList[0], ParameterList[1], ParameterList[2])
            elif L == 4: content = content_type(ParameterList[0], ParameterList[1], ParameterList[2], ParameterList[3])

        hash_value = hash(Id) ^ hash(content)
        return super(Command, self).__new__(self, Id, content, hash_value)

    def clone(self):         
        """Cloning should be unnecessary, since objects are constant!
        """
        if self.content is None:
            content = None
        elif hasattr(self.content, "clone"): 
            content = self.content.clone()
        else:
            content = deepcopy(self.content)
        return super(Command, self).__new__(self.__class__, self.id, content, self.my_hash)

    def __hash__(self):      
        return self.my_hash

    def __str__(self):
        name_str = str(self.id)
        if self.content is None:
            return "%s" % name_str

        elif self.id == E_Cmd.StoreInputPosition:
            x = self.content
            txt = ""
            if x.pre_context_id != E_PreContextIDs.NONE:
                txt = "if '%s': " % repr_pre_context_id(x.pre_context_id)
            pos_str = repr_position_register(x.position_register)
            if x.offset == 0:
                txt += "%s = input_p;" % pos_str
            else:
                txt += "%s = input_p - %i;" % (pos_str, x.offset)
            return txt

        elif self.id == E_Cmd.Accepter:
            return str(self.content)

        elif self.id == E_Cmd.PreContextOK:
            return "pre-context-fulfilled = %s;" % self.content.pre_context_id

        else:
            content_str = "".join("%s=%s, " % (member, value) for member, value in self.content._asdict().iteritems())
            return "%s: { %s }" % (name_str, content_str)   

AccepterContentElement = namedtuple("AccepterContentElement", ("pre_context_id", "acceptance_id"))

class AccepterContent:
    """_________________________________________________________________________

    AccepterContent: A list of conditional pattern acceptance actions. It 
          corresponds to a sequence of if-else statements such as 

          [0]  if   pre_condition_4711_f: acceptance = Pattern32
          [1]  elif pre_condition_512_f:  acceptance = Pattern21
          [2]  else:                      acceptance = Pattern56
    
    AccepterContentElement: An element in the sorted list of test/accept
    commands.  It contains the 'pre_context_id' of the condition to be checked
    and the 'acceptance_id' to be accepted if the condition is true.
    ___________________________________________________________________________
    """

    def __init__(self):
        Command.__init__(self)
        self.__list = []

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
        if   not isinstance(Other, AccepterContent):    return False
        elif len(self.__list) != len(Other.__list):     return False

        for x, y in zip(self.__list, Other.__list):
            if   x.pre_context_id != y.pre_context_id:  return False
            elif x.acceptance_id  != y.acceptance_id:   return False

        return True

    def __iter__(self):
        for x in self.__list:
            yield x

    def __str__(self):
        def to_string(X, FirstF):
            acc_str = "last_acceptance = %s" % repr_acceptance_id(X.acceptance_id)
            if X.pre_context_id == E_PreContextIDs.NONE:
                return acc_str

            cond_str = "%s" % repr_pre_context_id(X.pre_context_id)
            if FirstF:
                return "if %s:  %s" % (cond_str, acc_str)
            else:
                return "else if %s:  %s" % (cond_str, acc_str)

        last_i = len(self.__list) - 1
        return "".join("%s%s" % (to_string(element, i==0), "\n" if i != last_i else "") 
                       for i, element in enumerate(self.__list))

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

def __configure():
    """Configure the database for commands.
            
    cost_db:      CommandId --> computational cost.
    content_db:   CommandId --> related registers
    access_db:    CommandId --> access types of the command (read/write)
    brancher_set: set of commands which may cause jumps/gotos.
    """
    cost_db    = {}
    content_db = {}
    access_db  = {}    # map: register_id --> RegisterAccessRight
    #______________________________________________________________________________
    # 1        -> Read
    # 2        -> Write
    # 1+2 == 3 -> Read/Write
    r = 1                # READ
    w = 2                # WRITE
    RegisterAccessRight = namedtuple("AccessRight", ("write_f", "read_f"))

    class RegisterAccessDB(dict):
        def __init__(self, RegisterAccessInfoList):
            for info in RegisterAccessInfoList:
                register_id = info[0]
                rights      = info[1]
                if len(info) == 3: 
                    sub_id_reference = info[2]
                    register_id = (register_id, sub_id_reference)
                self[register_id] = RegisterAccessRight(rights & w, rights & r)

    #                    # 1 + 2 = READ/WRITE
    brancher_set = set() # set of ids of branching/goto-ing commands.

    def c(CmdId, ParameterList, *RegisterAccessInfoList):
        # -- access to related 'registers'
        access_db[CmdId] = RegisterAccessDB(RegisterAccessInfoList)

        # -- parameters that specify the command
        if type(ParameterList) != tuple: content_db[CmdId] = ParameterList # Constructor
        elif len(ParameterList) == 0:    content_db[CmdId] = None
        else:                            content_db[CmdId] = namedtuple("%s_content" % CmdId, ParameterList)
        
        # -- computational cost of the command
        cost_db[CmdId] = 1

        # -- determine whether command is subject to 'goto/branching'
        for register_id in (info[0] for info in RegisterAccessInfoList):
            if register_id == E_R.ThreadOfControl: brancher_set.add(CmdId)

    c(E_Cmd.Accepter,                         AccepterContent, 
                                              (E_R.PreContextFlags,r), (E_R.AcceptanceRegister,w))
    c(E_Cmd.Assign,                           ("target", "source"), 
                                              (0,w),     (1,r))
    c(E_Cmd.PreContextOK,                     ("pre_context_id",), 
                                              (E_R.PreContextFlags,w))
    #
    c(E_Cmd.GotoDoorId,                        ("door_id",), 
                                               (E_R.ThreadOfControl,r))
    c(E_Cmd.GotoDoorIdIfInputPNotEqualPointer, ("door_id",                              "pointer"),
                                               (E_R.ThreadOfControl,r), (E_R.InputP,r), (1,r))
    #
    c(E_Cmd.StoreInputPosition,               (               "pre_context_id",        "position_register",       "offset"),
                                              (E_R.InputP,r), (E_R.PreContextFlags,r), (E_R.PositionRegister,w,1)) # Argument '1' --> sub_id_reference
    c(E_Cmd.InputPDecrement,                  None, (E_R.InputP,r+w))
    c(E_Cmd.InputPIncrement,                  None, (E_R.InputP,r+w))
    c(E_Cmd.InputPDereference,                None, (E_R.InputP,r), (E_R.Input,w))
    #
    c(E_Cmd.LexemeResetTerminatingZero,       None, (E_R.LexemeStartP,r), (E_R.Buffer,w), (E_R.InputP,r), (E_R.Input,w))
    #
    c(E_Cmd.IndentationAdd,                   ("value",),
                                              (E_R.Indentation,r+w))
    c(E_Cmd.IndentationGridAdd,               ("grid_size",),
                                              (E_R.Indentation,r+w))
    c(E_Cmd.IndentationHandlerCall,           ("default_f", "mode_name"),
                                              (E_R.Indentation,r), (E_R.ReferenceP,r))
    c(E_Cmd.IndentationReferencePSet,         ("pointer_name", "offset"),
                                              (E_R.ReferenceP,w))
    c(E_Cmd.IndentationReferencePDeltaAdd,    ("pointer_name", "indentation_n_per_chunk"),
                                              (E_R.Indentation,r+w), (E_R.ReferenceP,r))
    c(E_Cmd.IndentationGridAddWithReferenceP, ("grid_size", "pointer_name", "indentation_n_per_chunk"),
                                              (E_R.Indentation,r+w), (E_R.ReferenceP,r+w))
    #
    c(E_Cmd.ColumnCountAdd,                   ("value",),
                                              (E_R.Column,r+w))
    c(E_Cmd.ColumnCountGridAdd,               ("grid_size",),
                                              (E_R.Column,r+w))
    c(E_Cmd.ColumnCountReferencePSet,         ("pointer", "offset"),
                                              (0,r), (E_R.ReferenceP,w))
    c(E_Cmd.ColumnCountReferencePDeltaAdd,    ("pointer", "column_n_per_chunk"),
                                              (E_R.Column,r+w), (0,r), (E_R.ReferenceP,r))
    c(E_Cmd.ColumnCountGridAddWithReferenceP, ("grid_size", "pointer", "column_n_per_chunk"),
                                              (E_R.Column,r+w), (1,r), (E_R.ReferenceP,r+w))
    c(E_Cmd.LineCountAdd,                     ("value",),
                                              (E_R.Line,r+w))
    c(E_Cmd.LineCountAddWithReferenceP,       ("value", "pointer", "column_n_per_chunk"),
                                              (E_R.Line,r+w), (1,r), (E_R.ReferenceP,r+w))
    #
    c(E_Cmd.PathIteratorSet,                  ("path_walker_id", "path_id", "offset"),
                                              (E_R.PathIterator,w))
    c(E_Cmd.TemplateStateKeySet,              ("state_key",),
                                              (E_R.TemplateStateKey,w))
    #
    c(E_Cmd.PrepareAfterReload,               ("on_success_door_id", "on_failure_door_id"),
                                              (E_R.TargetStateIndex,w), (E_R.TargetStateElseIndex,w))

    return access_db, content_db, brancher_set, cost_db

_access_db,    \
_content_db,   \
_brancher_set, \
_cost_db       = __configure()

def is_branching(CmdId):
    """RETURNS: True  -- if the command given by CmdId is 'branching' i.e. 
                         if it might cause jumps/gotos.
                False -- if the command does never cause a jump.
    """
    global _brancher_set
    assert CmdId in E_Cmd
    return CmdId in _brancher_set

def is_switchable(A, B):
    """Determines whether the command A and command B can be switched
    in a sequence of commands. This is NOT possible if:

       -- A and B read/write to the same register. 
          Two reads to the same register are no problem.

       -- One of the commands is goto-ing, i.e. branching.
    """
    global _brancher_set
    if A.id in _brancher_set or B.id in _brancher_set:
        return False

    a_access_iterable = get_register_access_iterable(A)
    b_access_db       = get_register_access_db(B)
    for register_id, access_a in a_access_iterable:
        access_b = b_access_db.get(register_id)
        if access_b is None:
            # Register from command A is not found in command B
            # => no restriction from this register.
            continue
        elif access_a.write_f or access_b.write_f:
            # => at least one writes.
            # Also:
            #   access_b not None => B accesses register_id (read, write, or both)
            #   access_a not None => A accesses register_id (read, write, or both)
            # 
            # => Possible cases here:
            #
            #     (A w,  B w), (A w,  B r), (A w,  B rw)
            #     (A r,  B w), (A r,  B r), (A r,  B rw)
            #     (A rw, B w), (A rw, B r), (A rw, B rw)
            #
            # In all those cases A and B depend on the order that they are executed.
            # => No switch possible
            return False
        else:
            continue

    return True

def get_register_access_iterable(Cmd):
    """For each command there are rights associated with registers. For example
    a command that writes into register 'X' associates 'write-access' with X.

    RETURNS: An iterable over pairs (register_id, access right) meaning that the
             command accesses the register with the given access type/right.
    """
    global _access_db

    for register_id, rights in _access_db[Cmd.id].iteritems():
        if isinstance(register_id, int):
            register_id = Cmd.content[register_id] # register_id == Argument number which contains E_R
        elif type(register_id) == tuple:
            main_id          = register_id[0]      # register_id[0] --> in E_R
            sub_reference_id = register_id[1]      # register_id[1] --> Argument number containing sub-id
            sub_id           = Cmd.content[sub_reference_id]
            register_id = "%s:%s" % (main_id, sub_id)
        yield register_id, rights

def get_register_access_db(Cmd):
    """RETURNS: map: register_id --> access right(s)
    """
    return dict( 
        (register_id, right)
        for register_id, right in get_register_access_iterable(Cmd)
    )

def StoreInputPosition(PreContextID, PositionRegister, Offset):
    return Command(E_Cmd.StoreInputPosition, PreContextID, PositionRegister, Offset)

def PreContextOK(PreContextID):
    return Command(E_Cmd.PreContextOK, PreContextID)

def TemplateStateKeySet(StateKey):
    return Command(E_Cmd.TemplateStateKeySet, StateKey)

def PathIteratorSet(PathWalkerID, PathID, Offset):
    return Command(E_Cmd.PathIteratorSet, PathWalkerID, PathID, Offset)

def PrepareAfterReload(OnSuccessDoorId, OnFailureDoorId):
    return Command(E_Cmd.PrepareAfterReload, OnSuccessDoorId, OnFailureDoorId)

def InputPIncrement():
    return Command(E_Cmd.InputPIncrement)

def InputPDecrement():
    return Command(E_Cmd.InputPDecrement)

def InputPDereference():
    return Command(E_Cmd.InputPDereference)

def LexemeResetTerminatingZero():
    return Command(E_Cmd.LexemeResetTerminatingZero)

def ColumnCountReferencePSet(Pointer, Offset=0):
    return Command(E_Cmd.ColumnCountReferencePSet, Pointer, Offset)

def ColumnCountReferencePDeltaAdd(Pointer, ColumnNPerChunk):
    return Command(E_Cmd.ColumnCountReferencePDeltaAdd, Pointer, ColumnNPerChunk)

def ColumnCountAdd(Value):
    return Command(E_Cmd.ColumnCountAdd, Value)

def IndentationHandlerCall(DefaultIhF, ModeName):
    return Command(E_Cmd.IndentationHandlerCall, DefaultIhF, ModeName)

def ColumnCountGridAdd(GridSize):
    return Command(E_Cmd.ColumnCountGridAdd, GridSize)

def ColumnCountGridAddWithReferenceP(Value, Pointer, ColumnNPerChunk):
    return Command(E_Cmd.ColumnCountGridAddWithReferenceP, Value, Pointer,ColumnNPerChunk)

def LineCountAdd(Value):
    return Command(E_Cmd.LineCountAdd, Value)

def LineCountAddWithReferenceP(Value, PointerName, ColumnNPerChunk):
    return Command(E_Cmd.LineCountAddWithReferenceP, Value, PointerName, ColumnNPerChunk)

def GotoDoorId(DoorId):
    return Command(E_Cmd.GotoDoorId, DoorId)

def GotoDoorIdIfInputPNotEqualPointer(DoorId, Pointer):
    return Command(E_Cmd.GotoDoorIdIfInputPNotEqualPointer, DoorId, Pointer)

def Assign(TargetRegister, SourceRegister):
    return Command(E_Cmd.Assign, TargetRegister, SourceRegister)

def Accepter():
    return Command(E_Cmd.Accepter)

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

    def is_empty(self):
        return super(CommandList, self).__len__() == 0

    def cost(self):
        global _cost_db
        return sum(_cost_db[cmd.id] for cmd in self)

    def has_command_id(self, CmdId):
        assert CmdId in E_Cmd
        for cmd in self:
            if cmd.id == CmdId: return True
        return False

    def access_accepter(self):
        """Gets the accepter from the command list. If there is no accepter
        yet, then it creates one and adds it to the list.
        """
        for cmd in self:
            if cmd.id == E_Cmd.Accepter: return cmd.content

        accepter = Accepter()
        self.append(accepter)
        return accepter.content

    def replace_position_registers(self, PositionRegisterMap):
        """Replace for any position register indices 'x' and 'y' given by
         
                      y = PositionRegisterMap[x]

        replace register index 'x' by 'y'.
        """
        if PositionRegisterMap is None or len(PositionRegisterMap) == 0: 
            return

        for i in xrange(len(self)):
            cmd = self[i]
            if cmd.id != E_Cmd.StoreInputPosition: continue

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
                if     cmd.id == E_Cmd.StoreInputPosition \
                   and cmd.content.pre_context_id == E_PreContextIDs.NONE
        )
        i = len(self) - 1
        while i >= 0:
            cmd = self[i]
            if cmd.id != E_Cmd.StoreInputPosition:
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
            if cmd.id == E_Cmd.StoreInputPosition: 
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

