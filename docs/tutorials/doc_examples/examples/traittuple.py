#--[Imports]--------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Range, Enum, Tuple
    
from enthought.traits.ui.api \
    import View, Item

#--[Code]-----------------------------------------------------------------------

# Example of using the Tuple class:

rank = Range( 1, 13 )
suit = Enum( 'Hearts', 'Diamonds', 'Spades', 'Clubs' )

class Card ( HasTraits ):
    
    value = Tuple( rank, suit )
    
    view  = View( Item( 'value' ) )
    
#--[Example*]-------------------------------------------------------------------

demo = Card( value = ( 3, 'Diamonds' ) ) 
