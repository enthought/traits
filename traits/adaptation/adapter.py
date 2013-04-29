""" Base classes for adapters.

Adapters do not have to inherit from these classes, as long as their
constructor takes the object to be adapted as the first and only
*positional* argument.

"""


from traits.api import Any, HasTraits


class Adapter(object):
    """ Base class for pure Python adapters. """

    def __init__(self, adaptee):
        """ Constructor. """

        self.adaptee = adaptee

        return


class HasTraitsAdapter(HasTraits):
    """ Base class for adapters with traits. """

    def __init__(self, adaptee, **traits):
        """ Constructor. """

        super(HasTraitsAdapter, self).__init__(**traits)
        self.adaptee = adaptee

        return

    adaptee = Any

#### EOF ######################################################################
