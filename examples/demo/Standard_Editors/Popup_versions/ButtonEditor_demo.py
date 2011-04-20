"""
Implementation of a ButtonEditor demo plugin for Traits UI demo program.

This demo shows each of the two styles of the ButtonEditor.
(As of this writing, they are identical.)
"""

from traits.api import HasTraits, Button
from traitsui.api import Item, View, Group
from traitsui.message import message


#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class ButtonEditorDemo ( HasTraits ):
    """ This class specifies the details of the ButtonEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    fire_event = Button('Click Me')


    def _fire_event_fired():
        message("Button clicked!")



    # ButtonEditor display
    # (Note that Text and ReadOnly versions are not applicable)
    event_group = Group( Item('fire_event', style='simple', label='Simple'),
                         Item('_'),
                         Item('fire_event', style='custom', label='Custom'),
                         Item('_'),
                         Item(label='[text style unavailable]'),
                         Item('_'),
                         Item(label='[read only style unavailable]'))

    # Demo view
    view1 = View( event_group,
                  title = 'ButtonEditor',
                  buttons = ['OK'],
                  width = 250 )


# Create the demo:
popup = ButtonEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

