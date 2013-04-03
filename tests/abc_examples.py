""" Test data for testing the protocol manager with ABCs. """


from abc import ABCMeta


#### 'Power plugs' metaphor ###################################################

#### Protocols #################################################################

class UKStandard(object):
    __metaclass__ = ABCMeta

class EUStandard(object):
    __metaclass__ = ABCMeta

class JapanStandard(object):
    __metaclass__ = ABCMeta

class IraqStandard(object):
    __metaclass__ = ABCMeta

#### Implementations ###########################################################

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

#### Adapters ##################################################################

class Adapter(object):
    def __init__(self, adaptee):
        self.adaptee = adaptee

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


#### 'File, Editor, Printable' metaphor #######################################

class FileType(object):
    pass

class IEditor(object):
    __metaclass__ = ABCMeta

class ITextEditor(object):
    __metaclass__ = ABCMeta

class IPrintable(object):
    __metaclass__ = ABCMeta


class TextEditor(object):
    pass

ITextEditor.register(TextEditor)


class FileTypeToIEditor(Adapter, TextEditor):
    pass

IEditor.register(FileTypeToIEditor)


class ITextEditorToIPrintable(Adapter):
    pass

IPrintable.register(ITextEditorToIPrintable)

#### EOF ######################################################################
