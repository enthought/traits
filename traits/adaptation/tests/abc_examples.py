""" Test data for testing the protocol manager with ABCs. """


from abc import ABCMeta


#### Protocols #################################################################

class FooABC(object):
    __metaclass__ = ABCMeta

class BarABC(object):
    __metaclass__ = ABCMeta

class BazABC(object):
    __metaclass__ = ABCMeta

#### Implementations ###########################################################

class Foo(object):
    pass

FooABC.register(Foo)

class Bar(object):
    pass

BarABC.register(Bar)

class Baz(object):
    pass

BazABC.register(Baz)

#### Adapters ##################################################################

class Adapter(object):
    def __init__(self, adaptee):
        self.adaptee = adaptee
    
class FooABCToBarABCAdapter(Adapter):
    pass

BarABC.register(FooABCToBarABCAdapter)

class BarABCToBazABCAdapter(Adapter):
    pass

BazABC.register(BarABCToBazABCAdapter)

#### EOF ######################################################################
