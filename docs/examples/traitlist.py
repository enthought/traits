# traitlist.py --- Example of using the TraitList class
from enthought.traits.api import HasTraits, Trait, TraitList

class Card:
    pass

class Hand(HasTraits):
    cards = Trait([], TraitList(Trait(Card), maxlen=52))
    
    
