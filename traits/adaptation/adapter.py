""" Base classes for adapters.

Adapters do not have to inherit from these classes, as long as their
constructor takes the object to be adapted as the first and only
*positional* argument.

"""


from traits.has_traits import HasTraits
from traits.trait_types import Any


class PurePythonAdapter(object):
    """ Base class for pure Python adapters. """

    def __init__(self, adaptee):
        """ Constructor. """

        self.adaptee = adaptee

        return


class Adapter(HasTraits):
    """ Base class for adapters with traits. """

    def __init__(self, adaptee, **traits):
        """ Constructor. """

        traits["adaptee"] = adaptee
        super(Adapter, self).__init__(**traits)

        return

    adaptee = Any
