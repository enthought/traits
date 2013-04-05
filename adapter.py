""" Base classes for adapters.

Adapters do not have to inherit from these classes, as long as their
constructor takes the object to be adapted as first argument.

"""


from traits.api import Any, HasTraits


class Adapter(object):
    """ Base class for pure Python adapters. """

    def __init__(self, adaptee):
        self.adaptee = adaptee


class HasTraitsAdapter(HasTraits):
    """ Base class for pure traits adapters. """

    def __init__(self, adaptee, **traits):
        super(HasTraitsAdapter, self).__init__(**traits)
        self.adaptee = adaptee

    adaptee = Any

#### EOF ######################################################################
