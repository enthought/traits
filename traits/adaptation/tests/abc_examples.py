""" Test data for testing the protocol manager with ABCs. """


from abc import ABCMeta

from traits.adaptation.api import PurePythonAdapter as Adapter


#### 'Power plugs' metaphor ###################################################

#### Protocols ################################################################

class UKStandard(object):
    __metaclass__ = ABCMeta

class EUStandard(object):
    __metaclass__ = ABCMeta

class JapanStandard(object):
    __metaclass__ = ABCMeta

class IraqStandard(object):
    __metaclass__ = ABCMeta

#### Implementations ##########################################################

class UKPlug(object):
    pass

UKStandard.register(UKPlug)

class EUPlug(object):
    pass

EUStandard.register(EUPlug)

class JapanPlug(object):
    pass

JapanStandard.register(JapanPlug)

class IraqPlug(object):
    pass

IraqStandard.register(IraqPlug)

class TravelPlug(object):

    def __init__(self, mode):
        self.mode = mode

#### Adapters #################################################################

# UK->EU
class UKStandardToEUStandard(Adapter):
    pass

EUStandard.register(UKStandardToEUStandard)

# EU->Japan
class EUStandardToJapanStandard(Adapter):
    pass

JapanStandard.register(EUStandardToJapanStandard)

# Japan->Iraq
class JapanStandardToIraqStandard(Adapter):
    pass

IraqStandard.register(JapanStandardToIraqStandard)

# EU->Iraq
class EUStandardToIraqStandard(Adapter):
    pass

IraqStandard.register(EUStandardToIraqStandard)

# UK->Japan
class UKStandardToJapanStandard(Adapter):
    pass

JapanStandard.register(UKStandardToJapanStandard)

# Travel->Japan
class TravelPlugToJapanStandard(Adapter):
    pass

JapanStandard.register(TravelPlugToJapanStandard)

# Travel->EU
class TravelPlugToEUStandard(Adapter):
    pass

EUStandard.register(TravelPlugToEUStandard)


#### 'Editor, Scriptable, Undoable' metaphor ##################################

class FileType(object):
    pass

class IEditor(object):
    __metaclass__ = ABCMeta

class IScriptable(object):
    __metaclass__ = ABCMeta

class IUndoable(object):
    __metaclass__ = ABCMeta


class FileTypeToIEditor(Adapter):
    pass

IEditor.register(FileTypeToIEditor)
IScriptable.register(FileTypeToIEditor)

class IScriptableToIUndoable(Adapter):
    pass

IUndoable.register(IScriptableToIUndoable)


#### Hierarchy example ########################################################

class IPrintable(object):
    __metaclass__ = ABCMeta

class Editor(object):
    pass

class TextEditor(Editor):
    pass

class EditorToIPrintable(Adapter):
    pass

IPrintable.register(EditorToIPrintable)

class TextEditorToIPrintable(Adapter):
    pass

IPrintable.register(TextEditorToIPrintable)


#### Interface hierarchy example ##############################################

class IPrimate(object):
    __metaclass__ = ABCMeta

class IHuman(IPrimate):
    pass

class IChild(IHuman):
    pass

class IIntermediate(object):
    __metaclass__ = ABCMeta

class ITarget(object):
    __metaclass__ = ABCMeta

class Source(object):
    pass

IChild.register(Source)

class IChildToIIntermediate(Adapter):
    pass

IIntermediate.register(IChildToIIntermediate)

class IHumanToIIntermediate(Adapter):
    pass

IIntermediate.register(IHumanToIIntermediate)

class IPrimateToIIntermediate(Adapter):
    pass

IIntermediate.register(IPrimateToIIntermediate)

class IIntermediateToITarget(Adapter):
    pass

ITarget.register(IIntermediateToITarget)


#### Non-trivial chaining example #############################################

class IStart(object):
    __metaclass__ = ABCMeta

class IGeneric(object):
    __metaclass__ = ABCMeta

class ISpecific(IGeneric):
    pass

class IEnd(object):
    __metaclass__ = ABCMeta

class Start(object):
    pass

IStart.register(Start)

class IStartToISpecific(Adapter):
    pass

ISpecific.register(IStartToISpecific)

class IGenericToIEnd(Adapter):
    pass

IEnd.register(IGenericToIEnd)

#### EOF ######################################################################
