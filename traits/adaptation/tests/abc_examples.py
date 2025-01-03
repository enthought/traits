# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test data for testing the protocol manager with ABCs. """


from abc import ABC

from traits.adaptation.api import PurePythonAdapter as Adapter


#### 'Power plugs' metaphor ###################################################

#### Protocols ################################################################


class UKStandard(ABC):
    pass


class EUStandard(ABC):
    pass


class JapanStandard(ABC):
    pass


class IraqStandard(ABC):
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


class IEditor(ABC):
    pass


class IScriptable(ABC):
    pass


class IUndoable(ABC):
    pass


class FileTypeToIEditor(Adapter):
    pass


IEditor.register(FileTypeToIEditor)
IScriptable.register(FileTypeToIEditor)


class IScriptableToIUndoable(Adapter):
    pass


IUndoable.register(IScriptableToIUndoable)


#### Hierarchy example ########################################################


class IPrintable(ABC):
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


class IPrimate(ABC):
    pass


class IHuman(IPrimate):
    pass


class IChild(IHuman):
    pass


class IIntermediate(ABC):
    pass


class ITarget(ABC):
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


class IStart(ABC):
    pass


class IGeneric(ABC):
    pass


class ISpecific(IGeneric):
    pass


class IEnd(ABC):
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
