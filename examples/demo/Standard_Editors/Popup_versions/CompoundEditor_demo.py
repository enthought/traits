"""
Implementation of a CompoundEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the CompoundEditor.
"""

from traits.api import HasTraits, Trait, Range
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class CompoundEditorDemo ( HasTraits ):
    """ This class specifies the details of the CompoundEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    compound_trait = Trait( 1, Range( 1, 6 ), 'a', 'b', 'c', 'd', 'e', 'f' )


    # Display specification (one Item per editor style)
    comp_group = Group( Item('compound_trait', style = 'simple', label = 'Simple'),
                        Item('_'),
                        Item('compound_trait', style = 'custom', label = 'Custom'),
                        Item('_'),
                        Item('compound_trait', style = 'text', label = 'Text'),
                        Item('_'),
                        Item('compound_trait',
                             style = 'readonly',
                             label = 'ReadOnly'))

    # Demo view
    view1 = View( comp_group,
                  title = 'CompoundEditor',
                  buttons = ['OK'] )


# Create the demo:
popup = CompoundEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

