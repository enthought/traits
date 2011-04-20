"""
Implemention of a ListEditor demo plugin for Traits UI demo program

This demo shows each of the four styles of ListEditor.
"""

from traits.api import HasTraits, List, Str
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class ListEditorDemo ( HasTraits ):
    """ This class specifies the details of the BooleanEditor demo.
    """

    # The Trait to be displayed in the editor
    play_list = List( Str, ["The Merchant of Venice", "Hamlet", "MacBeth"])


    # Items are used to define display; one per editor style.
    list_group = Group( Item('play_list', style='simple', label='Simple'),
                        Item('_'),
                        Item('play_list', style='custom', label='Custom'),
                        Item('_'),
                        Item('play_list', style='text', label='Text'),
                        Item('_'),
                        Item('play_list',
                              style='readonly',
                              label='ReadOnly'))

    # Demo view
    view1 = View( list_group,
                  title = 'ListEditor',
                  buttons = ['OK'],
                  height=400,
                  width=400 )


# Create the demo:
popup = ListEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

