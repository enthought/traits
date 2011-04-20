#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Demo of the dynamic restructuring of an interface using 'visible_when'.

This code sample shows a simple implementation of the dynamic
restructuring of a View on the basis of some trait attribute's
assigned value.

The demo class "Person" has a set of attributes that apply to all instances
('first_name', 'last_name', 'age'), a set of attributes that apply only
to children (Persons whose age is under 18), and a set of attributes that
apply only to adults.  The view for the Person object is defined in such
a way that the visible fields change accordingly when the 'age' attribute
crosses the boundary.
"""

# Imports:
from traits.api \
    import HasTraits, Str, Range, Bool, Enum

from traitsui.api \
    import Item, Group, View

class Person ( HasTraits ):

    # General traits:
    first_name = Str
    last_name  = Str
    age        = Range( 0, 120 )

    # Traits for children only:
    legal_guardian = Str
    school         = Str
    grade          = Range( 1, 12 )

    # Traits for adults only:
    marital_status   = Enum( 'single', 'married', 'divorced', 'widowed' )
    registered_voter = Bool( False )
    military_service = Bool( False )

    # Interface for attributes that are always visible in interface:
    gen_group = Group(
        Item( name = 'first_name' ),
        Item( name = 'last_name' ),
        Item( name = 'age' ),
        label       = 'General Info',
        show_border = True
    )

    # Interface for attributes of Persons under 18:
    child_group = Group(
        Item( name = 'legal_guardian' ),
        Item( name = 'school' ),
        Item( name = 'grade' ),
        label        = 'Additional Info',
        show_border  = True,
        visible_when = 'age < 18'
    )

    # Interface for attributes of Persons 18 and over:
    adult_group = Group(
        Item( name = 'marital_status' ),
        Item( name = 'registered_voter' ),
        Item( name = 'military_service' ),
        label        = 'Additional Info',
        show_border  = True,
        visible_when = 'age >= 18'
    )

    # A simple View is sufficient, since the Group definitions do all the work:
    view = View(
        Group(
            gen_group,
            child_group,
            adult_group
        ),
        title     = 'Personal Information',
        resizable = True,
        buttons   = [ 'OK' ]
    )

# Create the demo:
demo = Person(
    first_name = "Samuel",
    last_name  = "Johnson",
    age        = 16
)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

