#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Demonstrates using a popup view within another view.

Try changing the gender of the person from 'Male' to 'Female' using the
drop-down list. When the person's gender is changed, a pop-up dialog is
displayed immediately below the gender field providing you with the
opportunity to cancel the gender change.

If you click the Cancel button, the person's gender will return to its previous
value. If you click anywhere else outside of the pop-up dialog, the pop-up
dialog will simply disappear, leaving the person's new gender value as is.

The main items of interest in this demo are:
 - The: kind = 'popup' trait set in the PersonHandler View which marks the view
   as being a popup view.
 - The parent = info.gender.control value passed to the edit_traits method
   when the popup dialog is created in the object_gender_changed method. This
   value specifies the control that the popup dialog should be positioned near.

Notes:
 - Traits UI will automatically position the popup dialog near the specified
   control in such a way that the pop-up dialog will not overlay the control
   and will be entirely on the screen (as long as these two conditions do not
   conflict).
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Str, Int, Enum, Instance, Button

from traitsui.api \
    import View, HGroup, Item, Handler, UIInfo, spring

#-- The PersonHandler class ----------------------------------------------------

class PersonHandler ( Handler ):

    # The UIInfo object associated with the view:
    info = Instance( UIInfo )

    # The cancel button used to revert an unintentional gender change:
    cancel = Button( 'Cancel' )

    # The pop-up customization view:
    view = View(
        HGroup(
            spring,
            Item( 'cancel', show_label = False ),
        ),
        kind = 'popup'
    )

    # Event handlers:
    def object_gender_changed ( self, info ):
        if info.initialized:
            self.info = info
            self._ui  = self.edit_traits( parent = info.gender.control )

    def _cancel_changed ( self ):
        object = self.info.object
        object.gender = [ 'Male', 'Female' ][ object.gender == 'Male' ]
        self._ui.dispose()

#-- The Person class -----------------------------------------------------------

class Person ( HasPrivateTraits ):

    # The person's name, age and gender:
    name   = Str
    age    = Int
    gender = Enum( 'Male', 'Female' )

    # The traits UI view:
    traits_view = View(
        Item( 'name' ),
        Item( 'age' ),
        Item( 'gender' ),
        title   = 'Button Popup Demo',
        handler = PersonHandler
    )

#-- Create and run the demo ----------------------------------------------------

# Create the demo:
demo = Person( name = 'Mike Thomas', age  = 32 )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

