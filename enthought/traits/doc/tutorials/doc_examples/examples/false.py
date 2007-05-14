#--[Imports]--------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, true, false

#--[Code]-----------------------------------------------------------------------

# Example of using the boolean 'true' and 'false' trait:

# Base class for GUI objects
class GUIControl ( HasTraits ):
    
    enabled  = true
    readonly = false 
    
    view = View(
        Item( 'enabled' ),
        Item( 'readonly' )
    )
    
#--[Example*]-------------------------------------------------------------------

demo = GUIControl()
