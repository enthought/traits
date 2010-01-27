#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This shows a table editor which has a checkbox column in addition to normal
data columns.
"""

# Imports: 
from random \
    import randint
    
from enthought.traits.api \
    import HasStrictTraits, Str, Int, Float, List, Bool, Property
    
from enthought.traits.ui.api \
    import View, Item, TableEditor
    
from enthought.traits.ui.table_column \
    import ObjectColumn
    
from enthought.traits.ui.extras.checkbox_column \
    import CheckboxColumn

    
# Create a specialized column to set the text color differently based upon
# whether or not the player is in the lineup:
class PlayerColumn ( ObjectColumn ):
    
    # Override some default settings for the column:
    width                = 0.08
    horizontal_alignment = 'center'

    def get_text_color ( self, object ):
        return [ 'light grey', 'black' ][ object.in_lineup ]
   
        
# The 'players' trait table editor:
player_editor = TableEditor(
    sortable     = False,
    configurable = False,
    auto_size    = False,
    columns  = [ CheckboxColumn( name  = 'in_lineup',  label = 'In Lineup',
                                 width = 0.12 ),
                 PlayerColumn( name = 'name', editable = False, width  = 0.24, 
                               horizontal_alignment = 'left' ),
                 PlayerColumn( name   = 'at_bats',     label  = 'AB' ), 
                 PlayerColumn( name   = 'strike_outs', label  = 'SO' ), 
                 PlayerColumn( name   = 'singles',     label  = 'S' ), 
                 PlayerColumn( name   = 'doubles',     label  = 'D' ), 
                 PlayerColumn( name   = 'triples',     label  = 'T' ), 
                 PlayerColumn( name   = 'home_runs',   label  = 'HR' ), 
                 PlayerColumn( name   = 'walks',       label  = 'W' ), 
                 PlayerColumn( name   =  'average',    label  = 'Ave', 
                               editable = False,       format = '%0.3f' ) ] )

# 'Player' class:  
class Player ( HasStrictTraits ):
    
    # Trait definitions:  
    in_lineup   = Bool( True )
    name        = Str
    at_bats     = Int
    strike_outs = Int
    singles     = Int
    doubles     = Int
    triples     = Int
    home_runs   = Int
    walks       = Int
    average     = Property( Float )
    
    def _get_average ( self ):
        """ Computes the player's batting average from the current statistics.
        """
        if self.at_bats == 0:
            return 0.0
            
        return float( self.singles + self.doubles + 
                      self.triples + self.home_runs ) / self.at_bats

                      
class Team ( HasStrictTraits ):
    
    # Trait definitions:
    players = List( Player )
    
    # Trait view definitions:
    traits_view = View(
        Item( 'players',
              show_label = False,
              editor     = player_editor
        ),
        title     = 'Baseball Team Roster Demo',
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
    
