#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This demo shows you how to space editors horizontally using 'springs'.

It illustrates several different combinations, including a normal, non-spring,
example.
"""

from enthought.traits.api \
    import HasTraits, Button

from enthought.traits.ui.api \
    import View, VGroup, HGroup, Item, spring 

button = Item( 'ignore', show_label = False )

class SpringDemo ( HasTraits ):
    
    ignore = Button( 'Ignore' )
    
    view = View( 
               VGroup(
                   HGroup( button, spring, button,
                           show_border = True,
                           label       = 'Left and right justified' ),
                   HGroup( button, button, spring, 
                           button, button, spring, 
                           button, button, 
                           show_border = True,
                           label       = 'Left, center and right justified' ),
                   HGroup( spring, button, button, 
                           show_border = True,
                           label       = 'Right justified' ),
                   HGroup( button, button,
                           show_border = True,
                           label       = 'Left justified (no springs)' ),
               ),
               title   = 'Spring Demo',
               buttons = [ 'OK' ]
           )
                         
demo = SpringDemo()

if __name__ == '__main__':
    demo.configure_traits()
