#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Demonstrates how to set up an EnumEditor that is updated dynamically.

The scenario is a restaurant that at the beginning of the day has a menu list
of entrees based upon a fully stocked kitchen. However, as the day progresses,
the kitchen's larder gets depleted, and the kitchen may no longer be able to
prepare certain entrees, which must then be deleted from the menu. Similarly,
deliveries may allow certain entrees to be added back onto the menu.

The demo is divided into two tabs: Order and Kitchen.

The Order tab represents a customer's order and consists of a single Entree
field, which represents the customer's selection from the drop-down list of
entrees that the kitchen can currently prepare.

The Kitchen tab represents the current set of entrees that the kitchen can
prepare, based upon the current contents of its larder.

As entrees are checked on or off from the Kitchen tab, the customer's Entree
drop-down is dynamically updated with the current list of available entrees.

Notes:
 - The key point of the demo is the use of the 'name' trait in the EnumEditor
   definition, which links the list of available entrees from the
   KitchenCapabilities object to the OrderMenu object's entree EnumEditor.

 - The design will work with any number of active OrderMenu objects, since they
   all share a common KitchenCapabilities object. As the KitchenCapabilities
   object is updated, all OrderMenu UI's will automatically update their
   associated Entree's drop-down list.

 - A careful reader will also observe that this example contains only
   declarative code. No imperative code is required to handle the automatic
   updating of the Entree list.
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Str, List, Constant

from traitsui.api \
    import View, Item, VGroup, HSplit, EnumEditor, CheckListEditor

#-- The list of possible entrees -----------------------------------------------

possible_entrees = [
    'Chicken Fried Steak',
    'Chicken Fingers',
    'Chicken Enchiladas',
    'Cheeseburger',
    'Pepper Steak',
    'Beef Tacos',
    'Club Sandwich',
    'Ceasar Salad',
    'Cobb Salad'
]

#-- The KitchenCapabilities class ----------------------------------------------

class KitchenCapabilities ( HasPrivateTraits ):

    # The current set of entrees the kitchen can make (based on its larder):
    available = List( possible_entrees )

# The KitchenCapabilities are shared by all waitstaff taking orders:
kitchen_capabilities = KitchenCapabilities()

#-- The OrderMenu class --------------------------------------------------------

class OrderMenu ( HasPrivateTraits ):

    # The person's entree order:
    entree = Str

    # Reference to the restaurant's current entree capabilities:
    capabilities = Constant( kitchen_capabilities )

    # The user interface view:
    view = View(
        HSplit(
            VGroup(
                Item( 'entree',
                      editor = EnumEditor(
                                   name = 'object.capabilities.available' )
                ),
                label       = 'Order',
                show_border = True,
                dock        = 'tab'
            ),
            VGroup(
                Item( 'object.capabilities.available',
                      show_label = False,
                      style      = 'custom',
                      editor     = CheckListEditor( values = possible_entrees )
                ),
                label       = 'Kitchen',
                show_border = True,
                dock        = 'tab'
            )
        ),
        title = 'Dynamic EnumEditor Demo',
    )

#-------------------------------------------------------------------------------

# Create the demo:
demo = OrderMenu()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

