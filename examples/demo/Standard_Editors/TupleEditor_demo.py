#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a TupleEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the TupleEditor
"""

# Imports:
from traits.api \
    import HasTraits, Tuple, Color, Range, Str

from traitsui.api \
    import Item, Group, View

# The main demo class:
class TupleEditorDemo ( HasTraits ):
    """ Defines the TupleEditor demo class.
    """

    # Define a trait to view:
    tuple = Tuple( Color, Range( 1, 4 ), Str )


    # Display specification (one Item per editor style):
    tuple_group = Group(
        Item( 'tuple', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'tuple', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'tuple', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'tuple', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view
    view = View(
        tuple_group,
        title     = 'TupleEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )


# Create the demo:
demo = TupleEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

