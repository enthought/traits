"""
Implementation of a TupleEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the TupleEditor.
"""

from traits.api import HasTraits, Tuple, Color, Range, Str
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class TupleEditorDemo ( HasTraits ):
    """ This class specifies the details of the TupleEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    tuple = Tuple( Color, Range( 1, 4 ), Str )


    # Display specification (one Item per editor style)
    tuple_group = Group( Item('tuple', style = 'simple', label = 'Simple'),
                         Item('_'),
                         Item('tuple', style = 'custom', label = 'Custom'),
                         Item('_'),
                         Item('tuple', style = 'text', label = 'Text'),
                         Item('_'),
                         Item('tuple', style = 'readonly', label = 'ReadOnly'))

    # Demo view
    view1 = View( tuple_group,
                  title = 'TupleEditor',
                  buttons = ['OK'] )


# Create the demo:
popup = TupleEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

