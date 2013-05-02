""" Test data for testing the protocol manager with interfaces. """


from traits.api import Adapter, Enum, HasTraits, implements, Interface


#### 'Power plugs' metaphor ###################################################

#### Protocols ################################################################

class UKStandard(Interface):
    pass

class EUStandard(Interface):
    pass

class JapanStandard(Interface):
    pass

class IraqStandard(Interface):
    pass

#### Implementations ##########################################################

class UKPlug(HasTraits):
    implements(UKStandard)

class EUPlug(HasTraits):
    implements(EUStandard)

class JapanPlug(HasTraits):
    implements(JapanStandard)

class IraqPlug(HasTraits):
    implements(IraqStandard)

class TravelPlug(HasTraits):

    mode = Enum(['Europe', 'Asia'])

#### Adapters #################################################################

class UKStandardToEUStandard(Adapter):
    implements(EUStandard)

class EUStandardToJapanStandard(Adapter):
    implements(JapanStandard)

class JapanStandardToIraqStandard(Adapter):
    implements(IraqStandard)

class EUStandardToIraqStandard(Adapter):
    implements(IraqStandard)

class UKStandardToJapanStandard(Adapter):
    implements(JapanStandard)

class TravelPlugToJapanStandard(Adapter):
    implements(JapanStandard)

class TravelPlugToEUStandard(Adapter):
    implements(EUStandard)


#### 'Editor, Scriptable, Undoable' metaphor ##################################

class FileType(HasTraits):
    pass

class IEditor(Interface):
    pass

class IScriptable(Interface):
    pass

class IUndoable(Interface):
    pass

class FileTypeToIEditor(Adapter):
    implements(IEditor)
    implements(IScriptable)

class IScriptableToIUndoable(Adapter):
    implements(IUndoable)


#### Hierarchy example ########################################################

class IPrintable(Interface):
    pass

class Editor(HasTraits):
    pass

class TextEditor(Editor):
    pass

class EditorToIPrintable(Adapter):
    implements(IPrintable)

class TextEditorToIPrintable(Adapter):
    implements(IPrintable)


#### Interface hierarchy example ##############################################

class IPrimate(Interface):
    pass

class IHuman(IPrimate):
    pass

class IChild(IHuman):
    pass

class IIntermediate(Interface):
    pass

class ITarget(Interface):
    pass

class Source(HasTraits):
    implements(IChild)

class IChildToIIntermediate(Adapter):
    implements(IIntermediate)

class IHumanToIIntermediate(Adapter):
    implements(IIntermediate)

class IPrimateToIIntermediate(Adapter):
    implements(IIntermediate)

class IIntermediateToITarget(Adapter):
    implements(ITarget)


#### Non-trivial chaining example #############################################

class IStart(Interface):
    pass

class IGeneric(Interface):
    pass

class ISpecific(IGeneric):
    pass

class IEnd(Interface):
    pass

class Start(HasTraits):
    implements(IStart)

class IStartToISpecific(Adapter):
    implements(ISpecific)

class IGenericToIEnd(Adapter):
    implements(IEnd)

#### EOF ######################################################################
