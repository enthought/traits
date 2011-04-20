#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This example demonstrates several different variations on using the
ScrubberEditor. A 'scrubber' is a type of widget often seen in certain types
of applications, such as video editing, image editing, 3D graphics and
animation.

These types of programs often have many parameters defined over various ranges
that the user can tweak to get varying effects or results. Because the number
of parameters is typically fairly large, and the amount of screen real estate is
fairly limited, these program often use 'scrubbers' to allow the user to adjust
the parameter values.

A scrubber often looks like a simple text field. The user can type in new
values, if they need a precise setting, or simply drag the mouse over the value
to set a new value, much like dragging a slider control. The visual feedback
often comes in the form of seeing both the text value of the parameter change
and the effect that the new parameter value has on the underlying model.

For example, in a 3D graphics program, there might be a scrubber for
controlling the rotation of the currently selected object around the Y-axis.
As the user scrubs the rotation parameter, they also see the model spin on
the screen as well. This visual feedback is what makes a scrubber more useful
than a simple text entry field. And the fact that the scrubber takes up no
more screen real estate that a text entry field is what makes it more useful
than a full-fledged slider in space limited applications.

The Traits UI ScrubberEditor works as follows:

  - When the mouse pointer moves over the scrubber, the cursor pointer changes
    shape to indicate that the field has some additional control behavior.

  - The control may optionally change color as well, to visually indicate that
    the control is 'live'.

  - If you simply click on the scrubber, an active text entry field is
    displayed, where you can type a new value for the trait, then press the
    Enter key.

  - If you click and drag while over the scrubber, the value of the trait is
    modified based on the direction you move the mouse. Right and/or up
    increases the value, left and/or down decreases the value. Holding the
    Shift key down while scrubbing causes the value to change by 10 times its
    normal amount. Holding the Control key down while scrubbing changes the
    value by 0.1 times its normal amount.

  - Scrubbing is not limited to the area of the scrubber control. You can drag
    as far as you want in any direction, subject to the maximum limits imposed
    by the trait or ScrubberEditor definition.

The ScrubberEditor also supports several different style and functional
variations:

  - The visual default is to display only the special scrubber pointer to
    indicate to the user that 'scrubber' functionality is available.

  - By specifying a 'hover_color' value, you can also have the editor change
    color when the mouse pointer is over it.

  - By specifying an 'active_color' value, you can have the editor change color
    while the user is scrubbing.

  - By specifying a 'border_color' value, you can display a solid border around
    the editor to mark it as something other than an ordinary text field.

  - By specifying an 'increment' value, you can tell the editor what the normal
    increment value for the scrubber should be. Otherwise, the editor will
    calculate the increment value itself. Explicitly specifying an increment
    can be very useful in cases where the underlying trait has an unbounded
    value, which makes it difficult for the editor to determine what a
    reasonable increment value might be.

  - The editor will also correctly handle traits with dynamic ranges (i.e.
    ranges whose high and low limits are defined by other traits). Besides
    correctly handling the range limits, the editor will also adjust the
    default tooltip to display the current range of the scrubber.

In this example, several of the variations described above are shown:

  - A simple integer range with default visual cues.

  - A float range with both 'hover_color' and 'active_color' values specified.

  - An unbounded range with a 'border_color' value specified.

  - A dynamic range using an Item theme. This consists of three scrubbers: one
    to control the low end of the range, one to control the high end, and one
    that uses the high and low values to determine its range.

For comparison purposes, the example also shows the same traits displayed using
their default editors.
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasTraits, Range, Float

from traitsui.api \
    import View, VGroup, HGroup, Item, ScrubberEditor, spring

from traitsui.ui_traits \
    import ATheme

#-- Shared Themed Item Definition ----------------------------------------------

class TItem ( Item ):
    editor     = ScrubberEditor()
    item_theme = ATheme( '@std:LG' )

#-- ScrubberDemo Class ---------------------------------------------------------

class ScrubberDemo ( HasTraits ):

    # Define some sample ranges and values:
    simple_integer       = Range( 0, 100 )
    rollover_float       = Range( -10.0, 10.0 )
    bordered_unbounded   = Float
    themed_dynamic_low   = Range( high = -0.01, value = -10.0 )
    themed_dynamic_high  = Range( low  =  0.01, value =  10.0 )
    themed_dynamic_value = Range( 'themed_dynamic_low', 'themed_dynamic_high',
                                  0.0 )

    # Define the demo view:
    view = View(
        HGroup(
            VGroup(
                Item( 'simple_integer',
                      editor = ScrubberEditor() ),
                Item( 'rollover_float',
                      editor = ScrubberEditor( hover_color  = 0xFFFFFF,
                                               active_color = 0xA0CD9E ) ),
                Item( 'bordered_unbounded',
                      editor = ScrubberEditor( hover_color  = 0xFFFFFF,
                                               active_color = 0xA0CD9E,
                                               border_color = 0x808080 ) ),
                TItem( 'themed_dynamic_low' ),
                TItem( 'themed_dynamic_high' ),
                TItem( 'themed_dynamic_value' ),
                show_border = True,
                label       = 'Scrubber Editors'
            ),
            VGroup(
                Item( 'simple_integer' ),
                Item( 'rollover_float' ),
                Item( 'bordered_unbounded' ),
                Item( 'themed_dynamic_low' ),
                Item( 'themed_dynamic_high' ),
                Item( 'themed_dynamic_value' ),
                show_border = True,
                label       = 'Default Editors'
            ),
            spring
        ),
        title = 'Scrubber Editor Demo'
    )

#-- Create and run the demo ----------------------------------------------------

# Create the demo:
demo = ScrubberDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
