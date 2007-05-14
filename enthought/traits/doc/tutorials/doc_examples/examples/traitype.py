# traittype.py --- Example of using TraitCoerceType
from enthought.traits.api import HasTraits, Trait, TraitCoerceType

class Person(HasTraits):
    name = Trait('', TraitCoerceType(''))
    weight = Trait(0.0, TraitCoerceType(float))
    
