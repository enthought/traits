#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This program converts length measurements from one unit system to another.

<p>Select the input and output units using the drop down combo-boxes in the
<b>Input:</b> and <b>Output:</b> sections respectively. Type the input quantity
to convert into the left most text box. The output value corresponding to the
current input value will automatically be updated in the <b>Output:</b>
section.</p>

<p>Use the <b>Undo</b> and <b>ReDo</b> buttons to undo and redo changes you
have made to any of the input fields.</p>

<p>Note that other than the 'output_amount' property implementation, the rest
of the code is simply declarative.</p>
"""

# Imports:
from traits.api \
    import HasStrictTraits, Trait, CFloat, Property

from traitsui.api \
    import View, VGroup, HGroup, Item

# Help text:
ViewHelp = """
This program converts length measurements from one unit system to another.

<p>Select the input and output units using the drop down combo-boxes in the
<b>Input:</b> and <b>Output:</b> sections respectively. Type the input quantity
to convert into the left most text box. The output value corresponding to the
current input value will automatically be updated in the <b>Output:</b>
section.</p>

<p>Use the <b>Undo</b> and <b>ReDo</b> buttons to undo and redo changes you
have made to any of the input fields.</p>
"""

# Units trait maps all units to centimeters:
Units = Trait( 'inches', { 'inches':      2.54,
                           'feet':        (12 * 2.54),
                           'yards':       (36 * 2.54),
                           'miles':       (5280 * 12 * 2.54),
                           'millimeters': 0.1,
                           'centimeters': 1.0,
                           'meters':      100.0,
                           'kilometers':  100000.0 } )

# Converter Class:
class Converter ( HasStrictTraits ):

    # Trait definitions:
    input_amount  = CFloat( 12.0,    desc = "the input quantity" )
    input_units   = Units( 'inches', desc = "the input quantity's units" )
    output_amount = Property( depends_on = [ 'input_amount', 'input_units',
                                             'output_units' ],
                              desc = "the output quantity" )
    output_units  = Units( 'feet',   desc = "the output quantity's units" )

    # User interface views:
    traits_view = View(
        VGroup(
            HGroup(
                Item( 'input_amount', springy = True ),
                Item( 'input_units', show_label = False ),
                label       = 'Input',
                show_border = True
            ),
            HGroup(
                Item( 'output_amount', style = 'readonly', springy = True ),
                Item( 'output_units',  show_label = False ),
                label       = 'Output',
                show_border = True
            ),
            help = ViewHelp
        ),
        title   = 'Units Converter',
        buttons = [ 'Undo', 'OK', 'Help' ]
    )

    # Property implementations
    def _get_output_amount ( self ):
        return ((self.input_amount * self.input_units_) / self.output_units_)

# Create the demo:
popup = Converter()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

