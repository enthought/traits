# trait_reuse.py --- Example of reusing trait 
#                    definitions
from enthought.traits.api import HasTraits, Range, Trait, TraitRange

coefficient = Trait(0.0, TraitRange(-1.0, 1.0))

class quadratic(HasTraits):
    c2 = coefficient
    c1 = coefficient
    c0 = coefficient
    x  = Range(-100.0, 100.0, 0.0)
