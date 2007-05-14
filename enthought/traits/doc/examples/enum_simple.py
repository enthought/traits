# enum_simple.py --- Example of using simple enums
from enthought.traits.api import HasTraits, Trait

class Flower(HasTraits):
    color = Trait(['white', 'yellow', 'red'])
    kind  = Trait('annual', 'perennial')
    
