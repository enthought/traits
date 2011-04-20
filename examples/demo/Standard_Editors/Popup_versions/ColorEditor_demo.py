"""
Implementation of a ColorEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the ColorEditor.
"""

from traits.api import HasTraits, Color
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class ColorEditorDemo ( HasTraits ):
    """ This class specifies the details of the ColorEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    color_trait = Color

    # Items are used to define the demo display - one item per
    # editor style
    color_group = Group( Item('color_trait', style='simple', label='Simple'),
                         Item('_'),
                         Item('color_trait', style='custom', label='Custom'),
                         Item('_'),
                         Item('color_trait', style='text', label='Text'),
                         Item('_'),
                         Item('color_trait', style='readonly', label='ReadOnly'))


    # Demo view
    view1 = View( color_group,
                  title = 'ColorEditor',
                  buttons = ['OK'] )


# Create the demo:
popup = ColorEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

