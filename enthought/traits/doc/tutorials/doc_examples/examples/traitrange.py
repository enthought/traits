# traitrange.py --- Example of using the TraitRange class
from enthought.traits.api import HasTraits, Trait, TraitRange

class Person(HasTraits):
    age    = Trait(0, TraitRange(0, 150))
    weight = Trait(0.0, TraitRange(0.0, None))
