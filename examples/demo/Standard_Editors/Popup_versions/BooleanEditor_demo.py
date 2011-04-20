"""
Implementation of a BooleanEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the BooleanEditor
"""


#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

from traits.api import HasTraits, Bool
from traitsui.api import Item, Group, View


class BooleanEditorDemo ( HasTraits ):
    """ This class specifies the details of the BooleanEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    boolean_trait    = Bool

    # Items are used to define the demo display - one Item per
    # editor style
    bool_group = Group( Item('boolean_trait', style='simple', label='Simple'),
                        Item('_'),
                        Item('boolean_trait', style='custom', label='Custom'),
                        Item('_'),
                        Item('boolean_trait', style='text', label='Text'),
                        Item('_'),
                        Item('boolean_trait', style='readonly', label='ReadOnly'))

    # Demo view
    view1 = View( bool_group,
                  title = 'BooleanEditor',
                  buttons = ['OK'],
                  width = 300 )


# Hook for 'demo.py'
popup = BooleanEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

