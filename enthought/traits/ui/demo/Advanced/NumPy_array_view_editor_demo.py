"""
A demonstration of how the ArrayViewEditor can be used to display (large) NumPy
arrays, in this case 100,000 random 3D points from a unit cube.
"""

#-- Imports --------------------------------------------------------------------

from numpy.random \
    import random

from enthought.traits.api \
    import HasTraits, Array
    
from enthought.traits.ui.api \
    import View, Item

from enthought.traits.ui.wx.extra.array_view_editor \
    import ArrayViewEditor

#-- ShowArray demo class -------------------------------------------------------

class ShowArray ( HasTraits ):

    data = Array
    
    view = View(
        Item( 'data',
              show_label = False,
              editor     = ArrayViewEditor( titles = [ 'x', 'y', 'z' ],
                                            format = '%.4f' )
        ),
        title     = 'Array Viewer',
        width     = 0.3,
        height    = 0.8,
        resizable = True
    )

#-- Run the demo ---------------------------------------------------------------

# Create the demo:
demo = ShowArray( data = random( ( 100000, 3 ) ) )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
