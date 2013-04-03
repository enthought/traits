""" Test data for testing the protocol manager with interfaces. """


from traits.api import Any, HasTraits, implements, Interface


#### Protocols #################################################################

class IFoo(Interface):
    pass

class IBar(Interface):
    pass

class IBaz(Interface):
    pass

#### Implementations ###########################################################

class Foo(HasTraits):
    implements(IFoo)

class Bar(HasTraits):
    implements(IBar)

class Baz(HasTraits):
    implements(IBaz)

#### Adapters ##################################################################

class Adapter(HasTraits):
    adaptee = Any
    
class IFooToIBarAdapter(HasTraits):
    implements(IBar)

class IBarToIBazAdapter(HasTraits):
    implements(IBaz)

#### EOF ######################################################################
