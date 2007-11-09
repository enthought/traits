# type_simple.py --- Example of using simple types
from enthought.traits.api import HasTraits, Trait

class Person(HasTraits):
    name = Trait('')
    weight = Trait(0.0)
