"""
Implementation of an EnableRGBAColorEditor demo plugin for Traits UI demo 
program.

This demo shows each of the four styles of the EnableRGBAColorEditor
"""

# Imports:
from enthought.traits.api \
    import HasTraits, RGBAColor
    
from enthought.traits.ui.api \
    import Item, Group, View, EnableRGBAColorEditor

# Define the main demo class:
class EnableRGBAColorEditorDemo ( HasTraits ): 
    """ Defines the EnableRGBAColorEditor demo class.
    """

    # Define a trait to view:
    RGBAcolor_trait = RGBAColor

    # Items are used to define the demo display, one Item per editor style:
    RGBAcolor_group = Group( 
        Item( 'RGBAcolor_trait', 
              editor = EnableRGBAColorEditor(),
              style  = 'simple', 
              label  = 'Simple' ), 
        Item( '_' ),

        # Custom editor has to be enclosed in a 'horizontal' Group to work
        # around painting bug:
        Group(
            Item( 'RGBAcolor_trait', 
                  editor = EnableRGBAColorEditor(),
                  style  = 'custom', 
                  label  = 'Custom' ),
            orientation='horizontal'
        ),
        
        Item( '_' ),
        Item( 'RGBAcolor_trait', 
              editor = EnableRGBAColorEditor(),
              style  = 'text', 
              label  = 'Text'), 
        Item( '_' ),
        Item( 'RGBAcolor_trait', 
               editor = EnableRGBAColorEditor(),
               style  = 'readonly', 
               label  = 'ReadOnly' )
    ) 

    # Demo view:
    view = View(
        RGBAcolor_group,
        title     = 'EnableRGBAColorEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

# Create the demo:
demo = EnableRGBAColorEditorDemo()

# Run the demo (if not invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
