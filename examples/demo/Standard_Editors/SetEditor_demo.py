#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a SetEditor demo plugin for the Traits UI demo program.

The four tabs of this demo show variations on the interface as follows:

   Unord I:  Creates an alphabetized subset, has no "move all" options
   Unord II: Creates an alphabetized subset, has "move all" options
   Ord I:    Creates a set whose order is specified by the user, no "move all"
   Ord II:   Creates a set whose order is specifed by the user, has "move all"
"""

# Imports:
from traits.api \
    import HasTraits, List

from traitsui.api \
    import Item, Group, View, SetEditor

# Define the main demo class:
class SetEditorDemo ( HasTraits ):
    """ Defines the SetEditor demo class.
    """

    # Define a trait each for four SetEditor variants:
    unord_nma_set = List( editor = SetEditor(
                              values = [ 'kumquats', 'pomegranates', 'kiwi' ],
                              can_move_all       = False,
                              left_column_title  = 'Available Fruit',
                              right_column_title = 'Exotic Fruit Bowl' ) )

    unord_ma_set = List( editor = SetEditor(
                              values = [ 'kumquats', 'pomegranates', 'kiwi' ],
                              left_column_title  = 'Available Fruit',
                              right_column_title = 'Exotic Fruit Bowl' ) )

    ord_nma_set = List( editor = SetEditor(
                            values  = ['apples', 'berries', 'cantaloupe' ],
                            ordered            = True,
                            can_move_all       = False,
                            left_column_title  = 'Available Fruit',
                            right_column_title = 'Fruit Bowl' ) )

    ord_ma_set = List( editor = SetEditor(
                       values  = ['apples', 'berries', 'cantaloupe' ],
                       ordered            = True,
                       left_column_title  = 'Available Fruit',
                       right_column_title = 'Fruit Bowl' ) )

    # SetEditor display, unordered, no move-all buttons:
    no_nma_group = Group(
        Item( 'unord_nma_set', style = 'simple' ),
        label       = 'Unord I',
        show_labels = False
    )

    # SetEditor display, unordered, move-all buttons:
    no_ma_group = Group(
        Item( 'unord_ma_set', style = 'simple' ),
        label       = 'Unord II',
        show_labels = False
    )

    # SetEditor display, ordered, no move-all buttons:
    o_nma_group = Group(
        Item( 'ord_nma_set', style = 'simple' ),
        label       = 'Ord I',
        show_labels = False
    )

    # SetEditor display, ordered, move-all buttons:
    o_ma_group = Group(
        Item( 'ord_ma_set', style = 'simple' ),
        label       = 'Ord II',
        show_labels = False
    )

    # The view includes one group per data type. These will be displayed
    # on separate tabbed panels:
    view = View(
        no_nma_group,
        no_ma_group,
        o_nma_group,
        o_ma_group,
        title   = 'SetEditor',
        buttons = ['OK']
    )

# Create the demo:
demo = SetEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

