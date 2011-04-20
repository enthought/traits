#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implemention of a ListEditor demo plugin for Traits UI demo program

This demo shows each of the four styles of ListEditor
"""

# Imports:
from traits.api \
    import HasTraits, List, Str

from traitsui.api \
    import Item, Group, View

# Define the demo class:
class ListEditorDemo ( HasTraits ):
    """ Defines the main ListEditor demo class. """

    # Define a List trait to display:
    play_list = List( Str, [ "The Merchant of Venice", "Hamlet", "MacBeth" ] )

    # Items are used to define display, one per editor style:
    list_group = Group(
        Item( 'play_list', style = 'simple',   label = 'Simple', height = 75 ),
        Item( '_' ),
        Item( 'play_list', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'play_list', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'play_list', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        list_group,
        title     = 'ListEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

# Create the demo:
demo = ListEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
