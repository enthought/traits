""" Simple benchmarking of the adaptation manager.

This is not 'enforced' by any tests (i.e. we currently aren't bound to satisfy
any performance criteria - but in the future we might be ;^).

"""


import abc
import time

from apptools.adaptation.api import HasTraitsAdapter
from apptools.adaptation.adaptation_manager import AdaptationManager
from traits.api import HasTraits, implements, Interface


N_ITERATIONS = 1 #10000
N_PROTOCOLS  = 1


# A class implementing a single Interface.
class IFoo(Interface):
    pass

class Foo(HasTraits):
    implements(IFoo)

# An interface with explcitly no relation to 'Foo' or 'IFoo'!
class IBar(Interface):
    pass

# The object that we will try to adapt!
foo = Foo()    


# Create a lot of other interfacs!
for i in range(N_PROTOCOLS):
    exec 'class I%d(Interface): pass' % i

#  Create adapters from 'IFoo' to all of the interfaces.
for i in range(N_PROTOCOLS):
    exec 'class IFooToI%d(HasTraitsAdapter): implements(I%d)' % (i, i)

#  Create adapters from 'IBar' to all of the interfaces.
for i in range(N_PROTOCOLS):
    exec 'class IBarToI%d(HasTraitsAdapter): implements(I%d)' % (i, i)

#### PyProtocols ###############################################################

from traits.api import adapts as traits_register

register_ifoo_to_ix = 'traits_register(IFooToI%d, IFoo, I%d)'
register_ibar_to_ix = 'traits_register(IBarToI%d, IBar, I%d)'

for i in range(N_PROTOCOLS):
    exec register_ifoo_to_ix % (i, i)
    exec register_ibar_to_ix % (i, i)

start_time = time.time()
for _ in range(N_ITERATIONS):
    I0(foo)
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print 'traits.protocol: %f msec per iteration' % time_per_iter

#### apptools.adaptation with Interfaces #######################################

adaptation_manager = AdaptationManager()

register_ifoo_to_ix = """

adaptation_manager.register_adapter_factory(
    factory       = IFooToI%d,
    from_protocol = IFoo,
    to_protocol   = I%d
)

"""

register_ibar_to_ix = """

adaptation_manager.register_adapter_factory(
    factory       = IBarToI%d,
    from_protocol = IBar,
    to_protocol   = I%d
)

"""

for i in range(N_PROTOCOLS):
    exec register_ifoo_to_ix % (i, i)
    exec register_ibar_to_ix % (i, i)
    
start_time = time.time()
for _ in range(N_ITERATIONS):
    adaptation_manager.adapt(foo, I0)
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print 'apptools using Interfaces: %.3f msec per iteration' % time_per_iter

#### apptools.adaptation with ABCs #############################################

# A class implementing a single ABC.
class FooABC(object):
    __metaclass__ = abc.ABCMeta

class Foo(object):
    pass

FooABC.register(Foo)

# An ABCe with explcitly no relation to 'Foo' or 'FooABC'!
class BarABC(object):
    __metaclass__ = abc.ABCMeta

# The object that we will try to adapt!
foo = Foo()


# Create a lot of other ABCs!
for i in range(N_PROTOCOLS):
    exec 'class ABC%d(object): __metaclass__ = abc.ABCMeta' % i

#  Create adapters from 'FooABC' to all of the ABCs.
for i in range(N_PROTOCOLS):
    exec """
class FooABCToABC%d(object):
    def __init__(self, adaptee):
        pass

""" % i
    exec 'ABC%d.register(FooABCToABC%d)' % (i, i)

    exec """
class BarABCToABC%d(object):
    def __init__(self, adaptee):
        pass

""" % i
    exec 'ABC%d.register(BarABCToABC%d)' % (i, i)

# Register all of the adapters.
adaptation_manager = AdaptationManager()

register_fooabc_to_abcx = """

adaptation_manager.register_adapter_factory(
    factory       = FooABCToABC%d,
    from_protocol = FooABC,
    to_protocol   = ABC%d
)

"""

register_barabc_to_abcx = """

adaptation_manager.register_adapter_factory(
    factory       = BarABCToABC%d,
    from_protocol = BarABC,
    to_protocol   = ABC%d
)

"""

for i in range(N_PROTOCOLS):
    exec register_fooabc_to_abcx % (i, i)
    exec register_barabc_to_abcx % (i, i)

start_time = time.time()
for _ in range(N_ITERATIONS):
    adaptation_manager.adapt(foo, ABC0)
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print 'apptools using ABCs: %.3f msec per iteration' % time_per_iter

#### EOF #######################################################################
