"""
This program demonstrates hows how to add an event handler which performs an
action when the 'Apply' or 'Revert' buttons are pressed.
"""

# Imports:
from enthought.traits.api \
    import HasTraits, Str, List
    
from enthought.traits.ui.api \
    import Item, View, Handler, Group
    
from enthought.traits.ui.menu \
    import ApplyButton, RevertButton

# 'ApplyRevert_Handler' class:
class ApplyRevert_Handler ( Handler ):
        
    def apply ( self, info ):
        object = info.ui.context[ 'object' ]
        object.stack.insert( 0, object.input )
        object.queue.append( object.input )
        
    def revert ( self, info ):
        # Do something exciting here...
        print 'revert called...'
        
# 'ApplyRevertDemo' class:
class ApplyRevertDemo(HasTraits):
    
    # Trait definitions:  
    input = Str
    stack = List
    queue = List

    # Traits view definitions:  
    traits_view = View(
        Item( name = 'input' ),
        Group(
            Item( name = 'stack', height = 50, style = 'readonly' ),
            Item( name = 'queue', height = 50, style = 'readonly' ),
            orientation = 'horizontal'
        ),
        title   = 'Apply/Revert example',
        buttons = [ ApplyButton, RevertButton ],
        kind    = 'modal',
        handler = ApplyRevert_Handler
    )
    
popup = ApplyRevertDemo()

if __name__ == "__main__":
    popup.configure_traits()        
