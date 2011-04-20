#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Demo of dynamic enabling and disabling of trait editors in an interface.

Code sample showing a simple implementation of the dynamic
enabling and disabling of trait attribute editor interfaces
on the basis of another trait attribute's assigned value.

Demo class "Person" has attributes that apply to all instances
('first_name', 'last_name', 'age') and attributes that are
specific to age group ('marital_status' and 'registered_voter'
for adults, 'legal_guardian' for children.)  The adult-specific
attributes are disabled if 'age' is less than 18; otherwise
'legal_guardian' is disabled.

(NOTE: The 'enabled_when' expression for a given attribute must
be a condition on some attribute, e.g. 'object.age >= 18' so
that the evaluation is triggered by its trait handler.)
"""

# Imports:
from traits.api \
    import HasTraits, Str, Range, Enum, Bool

from traitsui.api \
    import Item, Group, View


class Person( HasTraits ):
    """ Demo class for demonstrating enabling/disabling of trait editors
    """

    first_name       = Str
    last_name        = Str
    age              = Range( 0, 120 )
    marital_status   = Enum( 'single', 'married', 'divorced', 'widowed' )
    registered_voter = Bool
    legal_guardian   = Str

    # Interface for attributes that are always enabled:
    gen_group = Group(
        Item( name = 'first_name' ),
        Item( name = 'last_name' ),
        Item( name = 'age' ),
        label       = 'General Info',
        show_border = True
    )

    # Interface for adult-only attributes:
    adult_group = Group(
        Item( name = 'marital_status' ),
        Item( name = 'registered_voter' ),
        enabled_when = 'age >= 18',
        label        = 'Adults',
        show_border  = True
    )

    # Interface for child-only attribute:
    child_group = Group(
        Item( name         = 'legal_guardian',
              enabled_when = 'age < 18'),
        label        = 'Minors',
        show_border  = True
    )

    # The view specification is simple, as the group specs have done the work:
    view = View(
        Group(
            gen_group,
            adult_group,
            child_group
        ),
        resizable = True,
        buttons   = [ 'OK' ]
    )

# Create the demo:
demo = Person(
    first_name = 'Samuel',
    last_name  = 'Johnson',
    age        = 16
)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

