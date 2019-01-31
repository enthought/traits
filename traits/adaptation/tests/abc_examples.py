""" Test data for testing the protocol manager with ABCs. """


from abc import ABCMeta

import six

from traits.adaptation.api import PurePythonAdapter as Adapter


#### 'Power plugs' metaphor ###################################################

#### Protocols ################################################################


@six.add_metaclass(ABCMeta)
class UKStandard(object):
    pass


@six.add_metaclass(ABCMeta)
class EUStandard(object):
    pass


@six.add_metaclass(ABCMeta)
class JapanStandard(object):
    pass


@six.add_metaclass(ABCMeta)
class IraqStandard(object):
    pass


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


@six.add_metaclass(ABCMeta)
class IEditor(object):
    pass


@six.add_metaclass(ABCMeta)
class IScriptable(object):
    pass


@six.add_metaclass(ABCMeta)
class IUndoable(object):
    pass


class FileTypeToIEditor(Adapter):
    pass


IEditor.register(FileTypeToIEditor)
IScriptable.register(FileTypeToIEditor)


class IScriptableToIUndoable(Adapter):
    pass


IUndoable.register(IScriptableToIUndoable)


#### Hierarchy example ########################################################


@six.add_metaclass(ABCMeta)
class IPrintable(object):
    pass


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


@six.add_metaclass(ABCMeta)
class IPrimate(object):
    pass


class IHuman(IPrimate):
    pass


class IChild(IHuman):
    pass


@six.add_metaclass(ABCMeta)
class IIntermediate(object):
    pass


@six.add_metaclass(ABCMeta)
class ITarget(object):
    pass


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


@six.add_metaclass(ABCMeta)
class IStart(object):
    pass


@six.add_metaclass(ABCMeta)
class IGeneric(object):
    pass


class ISpecific(IGeneric):
    pass


@six.add_metaclass(ABCMeta)
class IEnd(object):
    pass


class Start(object):
    pass


IStart.register(Start)


class IStartToISpecific(Adapter):
    pass


ISpecific.register(IStartToISpecific)


class IGenericToIEnd(Adapter):
    pass


IEnd.register(IGenericToIEnd)
