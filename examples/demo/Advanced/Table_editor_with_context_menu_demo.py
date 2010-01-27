#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This shows a table editor which has column-specific context menus.

The demo is a simple baseball scoring system, which lists each player and
their current batting statistics. After a given player has an at bat, you
right-click on the table cell corresponding to the player and the result of 
the at-bat (e.g. 'S' = single) and select the 'Add' menu option to register
that the player hit a single and update the player's overall statistics.

This demo also illustrates the use of Property traits, and how using 'event'
meta-data can simplify event handling by collapsing an event that can
occur on a number of traits into a category of event, which can be handled by
a single event handler defined for the category (in this case, the category
is 'affects_average').
"""

# Imports: 
from random \
    import randint
    
from enthought.traits.api \
    import HasStrictTraits, Str, Int, Float, List, Property
    
from enthought.traits.ui.api \
    import View, Item, TableEditor
    
from enthought.traits.ui.menu \
    import Menu, Action
    
from enthought.traits.ui.table_column \
    import ObjectColumn

    
# Define a custom table column for handling items which affect the player's
# batting average:
class AffectsAverageColumn ( ObjectColumn ):
    
    # The context menu for the column:
    menu = Menu( Action( name = 'Add', action = 'column.add( object )' ),
                 Action( name = 'Sub', action = 'column.sub( object )' ) )
    
    # Right-align numeric values (override):
    horizontal_alignment = 'center'
    
    # Column width (override):
    width = 0.09
    
    # Don't allow the data to be edited directly:
    editable = False
    
    def add ( self, object ):
        """ Increment the affected player statistic.
        """
        setattr( object, self.name, getattr( object, self.name ) + 1 ) 
    
    def sub ( self, object ):
        """ Decrement the affected player statistic.
        """
        setattr( object, self.name, getattr( object, self.name ) - 1 )

        
# The 'players' trait table editor:
player_editor = TableEditor(
    editable  = True,
    sortable  = True,
    auto_size = False,
    columns   = [ ObjectColumn( name     = 'name', 
                                editable = False, width = 0.28 ),
                  AffectsAverageColumn( name  = 'at_bats', 
                                        label = 'AB' ), 
                  AffectsAverageColumn( name  = 'strike_outs', 
                                        label = 'SO' ), 
                  AffectsAverageColumn( name  = 'singles', 
                                        label = 'S' ), 
                  AffectsAverageColumn( name  = 'doubles', 
                                        label = 'D' ), 
                  AffectsAverageColumn( name  = 'triples', 
                                        label = 'T' ), 
                  AffectsAverageColumn( name  = 'home_runs', 
                                        label = 'HR' ), 
                  AffectsAverageColumn( name  = 'walks', 
                                        label = 'W' ), 
                  ObjectColumn( name     = 'average', 
                                label    = 'Ave', 
                                editable = False,
                                width    = 0.09,
                                horizontal_alignment = 'center',
                                format   = '%0.3f' ) ]
)
        

# 'Player' class:  
class Player ( HasStrictTraits ):
    
    # Trait definitions:  
    name        = Str
    at_bats     = Int
    strike_outs = Int( event = 'affects_average' )
    singles     = Int( event = 'affects_average' )
    doubles     = Int( event = 'affects_average' )
    triples     = Int( event = 'affects_average' )
    home_runs   = Int( event = 'affects_average' )
    walks       = Int
    average     = Property( Float )
    
    def _get_average ( self ):
        """ Computes the player's batting average from the current statistics.
        """
        if self.at_bats == 0:
            return 0.0
            
        return float( self.singles + self.doubles + 
                      self.triples + self.home_runs ) / self.at_bats
                      
    def _affects_average_changed ( self ):
        """ Handles an event that affects the player's batting average.
        """
        self.at_bats += 1

        
class Team ( HasStrictTraits ):
    
    # Trait definitions:
    players = List( Player )
    
    # Trait view definitions:
    traits_view = View(
        Item( 'players',
              show_label = False,
              editor     = player_editor
        ),
        title     = 'Baseball Scoring Demo',
        width     = 0.5,
        height    = 0.5,
        resizable = True
    )


def random_player ( name ):    
    """ Generates and returns a random player.
    """
    p = Player( name        = name, 
                strike_outs = randint( 0, 50 ), 
                singles     = randint( 0, 50 ), 
                doubles     = randint( 0, 20 ), 
                triples     = randint( 0,  5 ), 
                home_runs   = randint( 0, 30 ), 
                walks       = randint( 0, 50 ) ) 
    return p.set( at_bats = p.strike_outs + p.singles + p.doubles + p.triples +
                            p.home_runs + randint( 100, 200 ) )
    
# Create the demo:
demo = view = Team( players = [ random_player( name ) for name in [
    'Dave', 'Mike', 'Joe', 'Tom', 'Dick', 'Harry', 'Dirk', 'Fields', 'Stretch'
] ] )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()        
    
