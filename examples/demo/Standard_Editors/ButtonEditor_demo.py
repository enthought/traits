#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a ButtonEditor demo plugin for Traits UI demo program.

This demo shows each of the two styles of the ButtonEditor
(As of this writing, they are identical.)
"""

# Imports:
from traits.api \
    import HasTraits, Button

from traitsui.api \
    import Item, View, Group

# Define the demo class:
class ButtonEditorDemo ( HasTraits ):
    """ Defines the main ButtonEditor demo class. """

    # Define a Button trait:
    fire_event = Button( 'Click Me' )

    def _fire_event_fired ( self ):
        print 'Button clicked!'

    # ButtonEditor display:
    # (Note that Text and ReadOnly versions are not applicable)
    event_group = Group(
        Item( 'fire_event', style = 'simple', label = 'Simple' ),
        Item( '_' ),
        Item( 'fire_event', style = 'custom', label = 'Custom' ),
        Item( '_' ),
        Item( label = '[text style unavailable]' ),
        Item( '_' ),
        Item( label = '[read only style unavailable]' )
    )

    # Demo view:
    view = View(
        event_group,
        title     = 'ButtonEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

# Create the demo:
demo = ButtonEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
