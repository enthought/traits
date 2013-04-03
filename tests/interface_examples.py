""" Test data for testing the protocol manager with interfaces. """


from traits.api import Any, Enum, HasTraits, implements, Interface


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

class Adapter(HasTraits):
    adaptee = Any
    
class UKStandardToEUStandard(HasTraits):
    implements(EUStandard)

class EUStandardToJapanStandard(HasTraits):
    implements(JapanStandard)

class JapanStandardToIraqStandard(HasTraits):
    implements(IraqStandard)

class EUStandardToIraqStandard(HasTraits):
    implements(IraqStandard)

class UKStandardToJapanStandard(HasTraits):
    implements(JapanStandard)

class TravelPlugToJapanStandard(HasTraits):
    implements(JapanStandard)

class TravelPlugToEUStandard(HasTraits):
    implements(EUStandard)

#### EOF #####################################################################
