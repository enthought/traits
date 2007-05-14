# traitenum.py --- Example of using TraitEnum class
from enthought.traits.api import HasTraits, Trait, TraitEnum

class Flower(HasTraits):
    color = Trait('white', TraitEnum([ 
                  'white', 'yellow', 'red']))
    kind  = Trait('annual', TraitEnum( 
                  'annual', 'perennial'))
