# traitmap.py --- Example of using the TraitMap class
from enthought.traits.api import Trait, TraitMap

true_boolean = Trait('yes', TraitMap({'yes': True, 'no': False}))
