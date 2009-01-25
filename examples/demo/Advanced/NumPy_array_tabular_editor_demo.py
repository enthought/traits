#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
A demonstration of how the TabularEditor can be used to display (large) NumPy
arrays, in this case 100,000 random 3D points from a unit cube.

In addition to showing the coordinates of each point, it also displays the
index of each point in the array, as well as a red flag if the point lies within
0.25 of the center of the cube.
"""

#-- Imports --------------------------------------------------------------------

from os.path \
    import join, dirname
    
from numpy \
    import sqrt
    
from numpy.random \
    import random

from enthought.traits.api \
    import HasTraits, Property, Array
    
from enthought.traits.ui.api \
    import View, Item, TabularEditor
    
from enthought.traits.ui.tabular_adapter \
    import TabularAdapter

#-- Tabular Adapter Definition -------------------------------------------------

class ArrayAdapter ( TabularAdapter ):

    columns = [ ( 'i', 'index' ), ( 'x', 0 ), ( 'y', 1 ),  ( 'z', 2 ) ]
                
    font        = 'Courier 10'
    alignment   = 'right'
    format      = '%.4f'
    index_text  = Property
    index_image = Property
    
    def _get_index_text ( self ):
        return str( self.row )
        
    def _get_index_image ( self ):
        x, y, z = self.item
        if sqrt( (x - 0.5) ** 2 + (y - 0.5) ** 2 + (z - 0.5) ** 2 ) <= 0.25:
            return '@icons:red_ball'
            
        return None

#-- ShowArray Class Definition -------------------------------------------------

class ShowArray ( HasTraits ):

    data = Array
    
    view = View(
        Item( 'data', 
              show_label = False, 
              style      = 'readonly',
              editor     = TabularEditor( adapter = ArrayAdapter() )
        ),
        title     = 'Array Viewer',
        width     = 0.3,
        height    = 0.8,
        resizable = True
    )
    
# Create the demo:
demo = ShowArray( data = random( ( 100000, 3 ) ) )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
