#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Sometimes the inputs to a model are not correlated. That is, any valid model
input produces a corresponding valid model state. However, in other cases, some
or all of the model inputs are correlated. That is, there may exist one or more
combinations of individually valid model inputs which produce invalid model
states.

In cases where this can happen, it is very often desirable to warn the user if
a particular combination of input values will not produce a usable result. This
problem cannot be solved solely though the use of carefully chosen trait types
and editors, because each individual input may be valid, but it is the
combination of inputs which is invalid.

Solving this problem therefore typically requires providing a way of determining
whether or not the model is in a valid state, and then communicating that
information to the user via the user interface.

This demonstration provides an example of doing this using the TraitEditor's
'invalid' trait. Each trait editor has an 'invalid' trait which can be set
equal to the name of a trait in the user interface context which contains a
boolean value reflecting whether or not the user interface (and underlying
model) are in a invalid state or not. A True value for the trait indicates that
the editor's current value produces an invalid model state. By associating the
same 'invalid' trait with one or more editors in the user interface, the
resulting user interface can indicate to the user which combination of input
values is producing the invalid state.

In this example, we have a very simple model which allows the user to control
the mass and velocity of a system. The model also defines the kinetic energy
of the resulting system. For safety reasons, the kinetic energy of the system
should not exceed a certain threshold. If it does, the user should be warned
so that they can reduce either or both of the system mass and velocity back down
to a safe level.

In the model, an 'error' property is defined which is True whenever the
kinetic energy level of the system exceeds the safety threshold. This trait is
then synchronized with the user interface's 'mass', velocity' and 'status'
editors, turning them red whenever the model enters an invalid state.

The 'status' trait is another property, based on the 'error' trait, which
provides a human readable description of the current system state.

Note that in this example, we synchronize the 'error' trait with the user
interface using 'sync_to_view' metadata, whose value is a list of user
interface editor traits the trait should be synchronized 'to' (i.e. changes to
the 'error' trait will be copied to the corresponding trait in the editor, but
not vice versa). We could also have explicitly set the 'invalid' trait of each
corresponding editor in the view definition to 'error' as well.

To use the demo, simply use the 'mass' and 'velocity' sliders and observe the
changes to the 'kinetic_energy' of the system. When the kinetic energy exceeds
50,000, notice how the 'mass', 'velocity' and 'status' fields turn red, and
that when the kinetic energy drops below 50,000, the fields return to their
normal color.
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasTraits, Range, Float, Bool, Str, Property, property_depends_on

from traitsui.api \
    import View, VGroup, Item

#-- System Class ---------------------------------------------------------------

class System ( HasTraits ):

    # The mass of the system:
    mass = Range( 0.0, 100.0 )

    # The velocity of the system:
    velocity = Range( 0.0, 100.0 )

    # The kinetic energy of the system:
    kinetic_energy = Property( Float )

    # The current error status of the system:
    error = Property( Bool,
               sync_to_view = 'mass.invalid, velocity.invalid, status.invalid' )

    # The current status of the system:
    status = Property( Str )

    view = View(
        VGroup(
            VGroup(
                Item( 'mass' ),
                Item( 'velocity' ),
                Item( 'kinetic_energy',
                      style      = 'readonly',
                      format_str = '%.0f'
                ),
                label       = 'System',
                show_border = True ),
            VGroup(
                Item( 'status',
                      style      = 'readonly',
                      show_label = False
                ),
                label       = 'Status',
                show_border = True
            ),
        )
    )

    @property_depends_on( 'mass, velocity' )
    def _get_kinetic_energy ( self ):
        return (self.mass * self.velocity * self.velocity) / 2.0

    @property_depends_on( 'kinetic_energy' )
    def _get_error ( self ):
        return (self.kinetic_energy > 50000.0)

    @property_depends_on( 'error' )
    def _get_status ( self ):
        if self.error:
            return 'The kinetic energy of the system is too high.'

        return ''

#-- Create and run the demo ----------------------------------------------------

# Create the demo:
demo = System()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
