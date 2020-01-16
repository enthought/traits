# wildcard_all.py --- Example of using a wildcard with all trait
#                     attribute names
from traits.api import HasTraits, Any


class Person(HasTraits):
    _ = Any
