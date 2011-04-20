#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Simple demonstration of the ListStrEditor, which can be used for editing and
displaying lists of strings, or other data that can be logically mapped to a
list of strings.
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasTraits, List, Str

from traitsui.api \
    import View, Item, ListStrEditor

#-- ShoppingListDemo Class -----------------------------------------------------

class ShoppingListDemo ( HasTraits ):

    # The list of things to buy at the store:
    shopping_list = List( Str )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'shopping_list',
              show_label = False,
              editor = ListStrEditor( title = 'Shopping List', auto_add = True )
        ),
        title     = 'Shopping List',
        width     = 0.2,
        height    = 0.5,
        resizable = True
    )

#-- Set up the Demo ------------------------------------------------------------

demo = ShoppingListDemo( shopping_list = [
    'Carrots',
    'Potatoes (5 lb. bag)',
    'Cocoa Puffs',
    'Ice Cream (French Vanilla)',
    'Peanut Butter',
    'Whole wheat bread',
    'Ground beef (2 lbs.)',
    'Paper towels',
    'Soup (3 cans)',
    'Laundry detergent'
] )

# Run the demo (in invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

