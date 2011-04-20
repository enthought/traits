"""
Implementation of a FontEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the FontEditor.
"""

from traits.api import HasTraits, Font
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class FontEditorDemo ( HasTraits ):
    """ This class specifies the details of the FontEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    font_trait = Font

    # Display specification (one Item per editor style)
    font_group = Group( Item('font_trait', style = 'simple', label = 'Simple'),
                        Item('_'),
                        Item('font_trait', style = 'custom', label = 'Custom'),
                        Item('_'),
                        Item('font_trait', style = 'text', label = 'Text'),
                        Item('_'),
                        Item('font_trait',
                              style = 'readonly',
                              label = 'ReadOnly'))

    # Demo view
    view1 = View( font_group,
                  title = 'FontEditor',
                  buttons = ['OK'] )


# Create the demo:
popup = FontEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

