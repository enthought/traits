#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a BooleanEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the BooleanEditor
"""

# Imports:
from traits.api \
    import HasTraits, Bool

from traitsui.api \
    import Item, Group, View

# Define the demo class:
class BooleanEditorDemo ( HasTraits ):
    """ Defines the main BooleanEditor demo class. """

    # Define a boolean trait to view:
    boolean_trait = Bool

    # Items are used to define the demo display, one Item per editor style:
    bool_group = Group(
        Item( 'boolean_trait', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'boolean_trait', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'boolean_trait', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'boolean_trait', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view
    view = View(
        bool_group,
        title     = 'BooleanEditor',
        buttons   = ['OK'],
        resizable = True
    )

# Create the demo:
demo = BooleanEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

