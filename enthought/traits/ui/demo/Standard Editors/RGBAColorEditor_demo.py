"""
Implementation of an RGBAColorEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the RGBAColorEditor.
"""

# Imports:
from enthought.traits.api \
    import HasTraits, RGBAColor
    
from enthought.traits.ui.api \
    import Item, Group, View

# The main demo class:
class RGBAColorEditorDemo ( HasTraits ): 
    """ Defines the RGBAColorEditor demo class.
    """

    # Define a trait to view:
    RGBAcolor_trait = RGBAColor

    # Items are used to define the demo display, one item per editor style:
    RGBAcolor_group = Group(
        Item( 'RGBAcolor_trait', style = 'simple',   label = 'Simple' ), 
        Item( '_' ),
        Item( 'RGBAcolor_trait', style = 'custom',   label = 'Custom' ), 
        Item( '_' ),
        Item( 'RGBAcolor_trait', style = 'text',     label = 'Text' ), 
        Item( '_' ),
        Item( 'RGBAcolor_trait', style = 'readonly', label = 'ReadOnly' )
    ) 

    # Demo view:
    view = View(
        RGBAcolor_group,
        title     = 'RGBAColorEditor',
        buttons   = ['OK'],
        resizable = True
    )

# Create the demo:
demo = RGBAColorEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
