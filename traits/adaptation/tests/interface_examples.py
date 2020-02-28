# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test data for testing the protocol manager with interfaces. """


from traits.api import Adapter, Enum, HasTraits, Interface, provides


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


@provides(UKStandard)
class UKPlug(HasTraits):
    pass


@provides(EUStandard)
class EUPlug(HasTraits):
    pass


@provides(JapanStandard)
class JapanPlug(HasTraits):
    pass


@provides(IraqStandard)
class IraqPlug(HasTraits):
    pass


class TravelPlug(HasTraits):

    mode = Enum(["Europe", "Asia"])


#### Adapters #################################################################


@provides(EUStandard)
class UKStandardToEUStandard(Adapter):
    pass


@provides(JapanStandard)
class EUStandardToJapanStandard(Adapter):
    pass


@provides(IraqStandard)
class JapanStandardToIraqStandard(Adapter):
    pass


@provides(IraqStandard)
class EUStandardToIraqStandard(Adapter):
    pass


@provides(JapanStandard)
class UKStandardToJapanStandard(Adapter):
    pass


@provides(JapanStandard)
class TravelPlugToJapanStandard(Adapter):
    pass


@provides(EUStandard)
class TravelPlugToEUStandard(Adapter):
    pass


#### 'Editor, Scriptable, Undoable' metaphor ##################################


class FileType(HasTraits):
    pass


class IEditor(Interface):
    pass


class IScriptable(Interface):
    pass


class IUndoable(Interface):
    pass


@provides(IEditor, IScriptable)
class FileTypeToIEditor(Adapter):
    pass


@provides(IUndoable)
class IScriptableToIUndoable(Adapter):
    pass


#### Hierarchy example ########################################################


class IPrintable(Interface):
    pass


class Editor(HasTraits):
    pass


class TextEditor(Editor):
    pass


@provides(IPrintable)
class EditorToIPrintable(Adapter):
    pass


@provides(IPrintable)
class TextEditorToIPrintable(Adapter):
    pass


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


@provides(IChild)
class Source(HasTraits):
    pass


@provides(IIntermediate)
class IChildToIIntermediate(Adapter):
    pass


@provides(IIntermediate)
class IHumanToIIntermediate(Adapter):
    pass


@provides(IIntermediate)
class IPrimateToIIntermediate(Adapter):
    pass


@provides(ITarget)
class IIntermediateToITarget(Adapter):
    pass


#### Non-trivial chaining example #############################################


class IStart(Interface):
    pass


class IGeneric(Interface):
    pass


class ISpecific(IGeneric):
    pass


class IEnd(Interface):
    pass


@provides(IStart)
class Start(HasTraits):
    pass


@provides(ISpecific)
class IStartToISpecific(Adapter):
    pass


@provides(IEnd)
class IGenericToIEnd(Adapter):
    pass
