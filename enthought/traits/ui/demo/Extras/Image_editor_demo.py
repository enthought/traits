""" 
A simple demonstration of how to use the ImageEditor to add a graphic element
to a Traits UI View.
"""

# Imports:
from enthought.traits.api \
    import HasTraits, Str
    
from enthought.traits.ui.api \
    import View, VGroup, Item
    
from enthought.traits.ui.wx.extra.image_editor \
    import ImageEditor

from enthought.pyface.image_resource \
    import ImageResource

# Define the demo class:    
class Employee ( HasTraits ):
    
    # Define the traits:
    name  = Str
    dept  = Str
    email = Str
  
    # Define the view:
    view = View(
        VGroup(
            VGroup(
                Item( 'name',
                      show_label = False,
                      editor = ImageEditor( image = ImageResource( 'info' ) ) )
            ),
            VGroup( 
                Item( 'name' ),
                Item( 'dept' ),
                Item( 'email' )
            )
        )
    )
    
# Create the demo:    
demo = Employee( name  = 'William Murchison', 
                 dept  = 'Receiving',
                 email = 'wmurchison@acme.com' )
        
# Run the demo (if invoked form the command line):                 
if __name__ == '__main__':
    demo.configure_traits()    

