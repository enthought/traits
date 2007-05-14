#--[Imports]--------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Enum, Range, List

#--[Code]-----------------------------------------------------------------------

# Example of using the List trait:

class Card ( HasTraits ):
    
    suit = Enum( 'Spades', 'Clubs', 'Hearts', 'Diamonds' )
    rank = Range( 1, 13 )

    
class PokerHand ( HasTraits ):
    
    cards = List( Card, maxlen = 5 )
    
#--[Example*]-------------------------------------------------------------------

# Create a sample poker hand:
hand = PokerHand()

# Now give it a valid set of cards:
hand.cards = [
    Card( suit = 'Clubs',    rank = 4 ),
    Card( suit = 'Diamonds', rank = 10 ),
    Card( suit = 'Hearts',   rank = 12 ),
    Card( suit = 'Spades',   rank = 1 ),
    Card( suit = 'Hearts',   rank = 7 ) ] )
    
# Now, try to give it an invalid hand (too many cards):
hand.cards.append( Card( suit = 'Diamonds', rank = '5' ) )
    
