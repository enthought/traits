""" Simple benchmarking code. """


import abc
import time

from apptools.adaptation.api import HasTraitsAdapter
from apptools.adaptation.adaptation_manager import AdaptationManager
from traits.api import HasTraits, implements, Interface


N_ITERATIONS = 100000


class IFoo(Interface):
    pass

class IBar(Interface):
    pass

class IFooToIBar(HasTraitsAdapter):
    implements(IBar)

class Foo(HasTraits):
    implements(IFoo)

foo = Foo()

# PyProtocols
from traits.api import adapts as traits_register
traits_register(IFooToIBar, IFoo, IBar)

start_time = time.time()
for _ in range(N_ITERATIONS):
    IBar(foo)
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print 'traits.protocol: %f msec per iteration' % time_per_iter

# apptools with Interfaces
adaptation_manager = AdaptationManager()
adaptation_manager.register_adapter_factory(
    factory       = IFooToIBar,
    from_protocol = IFoo,
    to_protocol   = IBar
)

start_time = time.time()
for _ in range(N_ITERATIONS):
    adaptation_manager.adapt(foo, IBar)
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print 'apptools using Interfaces: %.3f msec per iteration' % time_per_iter

# apptools with ABCs
class FooABC(object):
    __metaclass__ = abc.ABCMeta

class BarABC(object):
    __metaclass__ = abc.ABCMeta

class FooABCToBarABC(object):
    def __init__(self, adaptee):
        pass

BarABC.register(FooABCToBarABC)

class ConcreteFoo(object):
    pass

FooABC.register(ConcreteFoo)

concrete_foo = ConcreteFoo()

adaptation_manager = AdaptationManager()
adaptation_manager.register_adapter_factory(
    factory       = FooABCToBarABC,
    from_protocol = FooABC,
    to_protocol   = BarABC
)

start_time = time.time()
for _ in range(N_ITERATIONS):
    adaptation_manager.adapt(concrete_foo, BarABC)
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print 'apptools using ABCs: %.3f msec per iteration' % time_per_iter
