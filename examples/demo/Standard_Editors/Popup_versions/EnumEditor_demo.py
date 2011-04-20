"""
Implementation of an EnumEditor demo for Traits UI

This demo shows each of the four styles of the EnumEditor.

Fixme: This only shows the capabilities of the old-style EnumEditor
"""

from traits.api import HasTraits, Enum
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class EnumEditorDemo ( HasTraits ):
    """ This class specifies the details of the BooleanEditor demo.
    """

    # The Trait to be displayed in the editor
    name_list = Enum('A-495', 'A-498', 'R-1226', 'TS-17', 'TS-18')

    # Items are used to define the display; one Item per editor style.
    enum_group = Group( Item('name_list', style='simple', label='Simple'),
                        Item('_'),
                        Item('name_list', style='custom', label='Custom'),
                        Item('_'),
                        Item('name_list', style='text', label='Text'),
                        Item('_'),
                        Item('name_list', style='readonly', label='ReadOnly'))

    # Demo view
    view1 = View( enum_group,
                  title = 'EnumEditor',
                  buttons = ['OK'] )


# Create the demo:
popup = EnumEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

