"""
This example demonstrates how to create a user interface with fields that when
you click on them pop up an editor that allows you to modify the associated
trait value.

This can be a useful technique when you need to create a user interface which
contains many potentially editable values, but you also need to conserve screen 
real estate as well.

In this demo, simply click on the value of any of the three traits. A popup
slider will be displayed which allows you to drag or type a new value for the 
trait. You can dismiss the popup simply by moving the mouse away from the 
slider.

This particular example uses the default 'popover' kind, which displays the
popup directly over the value it is associated with. You can also specify 'kind'
as:

  - 'popup': The popup will be displayed adjacent to (usually below) the value 
    it is associated with.
    
  - 'info': The popup is displayed over the the value it is associated with.
    This is similar to 'popover', but the popup will be dismissed when the mouse
    pointer moves out of the original area occupied by the value (not the
    popup). This area is usually smaller than the popup and allows the popup to
    be dismissed more easily. However it should only be used with popups that
    contain read-only information, since the user may not be able to select all
    editable fields present.
    
Besides 'kind', the PopupEditor also allows specifying:

  - editor: The editor to use for the popup. If specified (or left) as None,
    the default editor associated with the associated trait will be used.
    Otherwise, the value should be either an EditorFactory subclass instance,
    or a callable which returns an EditorFactory subclass instance.
  - style: The style of editor to popup (same as Item.style)
  - width: The width of the editor to popup (same as Item.width)
  - height: The height of the editor to popup (same as Item.height)
"""

#-- Imports --------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Range, Font
    
from enthought.traits.ui.api \
    import View, HGroup, VGroup, Item, PopupEditor
    
from enthought.traits.ui.wx.themed_slider_editor \
    import ThemedSliderEditor

#-- Create a custom view Item for editing using a popup slider -----------------

class PopupSlider ( Item ):
    
    # Make sure each field is wide enough to hold its maximum value:
    width = -40
    
    # Define the editor to use:
    editor = PopupEditor( editor = ThemedSliderEditor, width = -150 )

#-- Create a simple demonstration model to edit --------------------------------

class Popups ( HasTraits ):

    speed    = Range( 0.0, 150.00 )
    distance = Range( 0.0, 1000.0 )
    fuel     = Range( 0.0, 20.0 )
    
    # Define a group (so we can re-use it more easily):
    group = VGroup(
        PopupSlider( 'speed' ),
        PopupSlider( 'distance' ),
        PopupSlider( 'fuel' ),
        show_border = True
    )
    
    # Define the demo view:
    traits_view = View(
        HGroup( group, group, group ) 
    )

#-- Create and run the demo ----------------------------------------------------

# Create the demo:
demo = Popups()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
