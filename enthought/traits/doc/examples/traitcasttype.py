# traitcasttype.py --- Example of using TraitCastType
from enthought.traits.api import HasTraits, Trait, TraitCastType

class Person(HasTraits):
    name = Trait('', TraitCastType(''))
    weight = Trait(0.0, TraitCastType(float))
    
