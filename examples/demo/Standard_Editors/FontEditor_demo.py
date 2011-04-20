#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a FontEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the FontEditor
"""

# Imports:
from traits.api \
    import HasTraits, Font

from traitsui.api \
    import Item, Group, View

# Define the dmeo class:
class FontEditorDemo ( HasTraits ):
    """ Defines the main FontEditor demo class. """

    # Define a Font trait to view:
    font_trait = Font

    # Display specification (one Item per editor style):
    font_group = Group(
        Item( 'font_trait', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'font_trait', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'font_trait', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'font_trait', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        font_group,
        title     = 'FontEditor',
        buttons   = ['OK'],
        resizable = True
    )

# Create the demo:
demo = FontEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

