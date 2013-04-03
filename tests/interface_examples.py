""" Test data for testing the protocol manager with interfaces. """


from traits.api import Any, HasTraits, implements, Interface


#### Protocols ################################################################

class UKStandard(Interface):
    pass

class EUStandard(Interface):
    pass

class JapanStandard(Interface):
    pass

#### Implementations ##########################################################

class UKPlug(HasTraits):
    implements(UKStandard)

class EUPlug(HasTraits):
    implements(EUStandard)

class JapanPlug(HasTraits):
    implements(JapanStandard)

#### Adapters #################################################################

class Adapter(HasTraits):
    adaptee = Any
    
class UKStandardToEUStandard(HasTraits):
    implements(EUStandard)

class EUStandardToJapanStandard(HasTraits):
    implements(JapanStandard)

#### EOF #####################################################################
