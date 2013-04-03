""" Test data for testing the protocol manager with ABCs. """


from abc import ABCMeta


#### Protocols #################################################################

class UKStandard(object):
    __metaclass__ = ABCMeta

class EUStandard(object):
    __metaclass__ = ABCMeta

class JapanStandard(object):
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

#### Adapters ##################################################################

class Adapter(object):
    def __init__(self, adaptee):
        self.adaptee = adaptee
    
class UKStandardToEUStandard(Adapter):
    pass

EUStandard.register(UKStandardToEUStandard)

class EUStandardToJapanStandard(Adapter):
    pass

JapanStandard.register(EUStandardToJapanStandard)

#### EOF ######################################################################
