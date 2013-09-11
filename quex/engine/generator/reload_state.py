import quex.engine.generator.state.entry as entry
from   quex.blackboard import setup as Setup, \
                              E_StateIndices

def do(TheReloadState):
    LanguageDB = Setup.language_db

    if TheReloadState.entry.action_db.size() == 0:
        return []

    txt = ["%s\n" % LanguageDB.UNREACHABLE]

    entry.do_core(txt, TheReloadState)

    txt.extend(LanguageDB.RELOAD_PROCEDURE(ForwardF=(TheReloadState.index == E_StateIndices.RELOAD_FORWARD)))

    return txt

