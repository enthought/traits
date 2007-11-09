#--[Imports]--------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Range

#--[Code]-----------------------------------------------------------------------

# Example of using the Range trait:

class GuiSplitter ( HasTraits ):
    
    bar_size = Range( 1, 15, value = 4 )
    
#--[Example*]-------------------------------------------------------------------    

# Create a sample GUISplitter object:
gs = GUISplitter()

# Display its initial contents:
gs.print_traits()

# Now change the bar size:
gs.bar_size = 14

# Display its value again:
gs.print_traits()

# Now try to set bar size to a value outside its range:
gs.bar_size = 0
