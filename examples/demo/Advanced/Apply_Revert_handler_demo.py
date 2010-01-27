#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This program demonstrates hows how to add an event handler which performs an
action when the 'Apply' or 'Revert' buttons are pressed.
"""

# Imports:
from enthought.traits.api \
    import HasTraits, Str, List
    
from enthought.traits.ui.api \
    import Item, View, Handler, HGroup, VGroup

# 'ApplyRevert_Handler' class:
class ApplyRevert_Handler ( Handler ):
        
    def apply ( self, info ):
        object = info.object
        object.stack.insert( 0, object.input )
        object.queue.append( object.input )
        
    def revert ( self, info ):
        # Do something exciting here...
        print 'revert called...'
        
# 'ApplyRevertDemo' class:
class ApplyRevertDemo ( HasTraits ):
    
    # Trait definitions:  
    input = Str
    stack = List
    queue = List

    # Traits view definitions:  
    traits_view = View(
        VGroup(
            VGroup(
                Item( 'input', 
                      show_label = False
                ),
                label       = 'Input',
                show_border = True
            ),
            HGroup(
                VGroup(
                    Item( 'stack', 
                          show_label = False,
                          height     = 50, 
                          width      = 100, 
                          style      = 'readonly'
                    ),
                    label       = 'Stack',
                    show_border = True
                ),
                VGroup(
                    Item( 'queue', 
                          show_label = False,
                          height     = 50, 
                          width      = 100, 
                          style      = 'readonly'
                    ),
                    label       = 'Queue',
                    show_border = True
                )
            )
        ),
        title   = 'Apply/Revert example',
        buttons = [ 'Apply', 'Revert' ],
        kind    = 'modal',
        handler = ApplyRevert_Handler
    )
    
# Create the demo:
modal_popup = ApplyRevertDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    modal_popup.configure_traits()        
