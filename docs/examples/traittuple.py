# traittuple.py --- Example of using the TraitTuple class
from enthought.traits.api import HasTraits, Range, Trait, TraitTuple
from enthought.traits.ui.api import Item, View

rank = Range(1, 13)
suit = Trait('Hearts', 'Diamonds', 'Spades', 'Clubs')

class Card(HasTraits): 
    value = Trait(TraitTuple(rank, suit))
    view = View( Item('value'))
    
