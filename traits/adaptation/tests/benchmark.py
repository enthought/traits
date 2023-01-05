# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Simple benchmarking of the adaptation manager.

This is not 'enforced' by any tests (i.e. we currently aren't bound to satisfy
any performance criteria - but in the future we might be ;^).

"""

# Imports are needed by the 'exec'd code.
import abc  # noqa: F401
import time

from traits.adaptation.adaptation_manager import AdaptationManager
from traits.api import Adapter, HasTraits, Interface, provides  # noqa: F401


N_SOURCES = 3
N_ITERATIONS = 100
N_PROTOCOLS = 50

# Create some classes to adapt.
create_classes_to_adapt = """
class IFoo{i}(Interface):
    pass

@provides(IFoo{i})
class Foo{i}(HasTraits):
    pass
"""
for i in range(N_SOURCES):
    exec(create_classes_to_adapt.format(i=i))

# The object that we will try to adapt!
foo = Foo1()  # noqa: F821

# Create a lot of other interfaces that we will adapt to.
for i in range(N_PROTOCOLS):
    exec("class I{i}(Interface): pass".format(i=i))

create_traits_adapter_class = """
@provides(I{target})
class IFoo{source}ToI{target}(Adapter):
    pass
"""

#  Create adapters from each 'IFooX' to all of the interfaces.
for source in range(N_SOURCES):
    for target in range(N_PROTOCOLS):
        exec(create_traits_adapter_class.format(source=source, target=target))


# traits.adaptation with Interfaces ###########################################

adaptation_manager = AdaptationManager()

register_ifoox_to_ix = """

adaptation_manager.register_factory(
    factory       = IFoo{source}ToI{target},
    from_protocol = IFoo{source},
    to_protocol   = I{target}
)

"""

# We register the adapters in reversed order, so that looking for the one
# with index 0 will need traversing the whole list.
# I.e., we're considering the worst case scenario.
for source in range(N_SOURCES):
    for target in reversed(range(N_PROTOCOLS)):
        exec(register_ifoox_to_ix.format(source=source, target=target))

start_time = time.time()
for _ in range(N_ITERATIONS):
    adaptation_manager.adapt(foo, I0)  # noqa: F821
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print("apptools using Interfaces: %.3f msec per iteration" % time_per_iter)


# traits.adaptation with ABCs #################################################

# Create some classes to adapt (using ABCs!).
for i in range(N_SOURCES):
    exec(
        """
class FooABC{i}(abc.ABC):
    pass
""".format(
            i=i
        )
    )
    exec("class Foo{i}(object): pass".format(i=i))
    exec("FooABC{i}.register(Foo{i})".format(i=i))

# The object that we will try to adapt!
foo = Foo0()  # noqa: F821

# Create a lot of other ABCs!
for i in range(N_PROTOCOLS):
    exec(
        """
class ABC{i}(abc.ABC):
    pass
""".format(
            i=i
        )
    )

# Create adapters from 'FooABC' to all of the ABCs.
create_abc_adapter_class = """
class FooABC{source}ToABC{target}(object):
    def __init__(self, adaptee):
        pass

ABC{target}.register(FooABC{source}ToABC{target})
"""

for source in range(N_SOURCES):
    for target in range(N_PROTOCOLS):
        exec(create_abc_adapter_class.format(source=source, target=target))

# Register all of the adapters.
adaptation_manager = AdaptationManager()

register_fooxabc_to_abcx = """
adaptation_manager.register_factory(
    factory       = FooABC{source}ToABC{target},
    from_protocol = FooABC{source},
    to_protocol   = ABC{target}
)
"""

# We register the adapters in reversed order, so that looking for the one
# with index 0 will need traversing the whole list.
# I.e., we're considering the worst case scenario.
for source in range(N_SOURCES):
    for target in reversed(range(N_PROTOCOLS)):
        exec(register_fooxabc_to_abcx.format(source=source, target=target))

start_time = time.time()
for _ in range(N_ITERATIONS):
    adaptation_manager.adapt(foo, ABC0)  # noqa: F821
time_per_iter = (time.time() - start_time) / float(N_ITERATIONS) * 1000.0
print("apptools using ABCs: %.3f msec per iteration" % time_per_iter)
