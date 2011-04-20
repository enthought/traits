#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Demo to redefine legal values of one attribute based on another via GUI.

Code sample showing a simple implementation of the dynamic
redefining of a trait attribute's legal values on the basis of another
trait attribute's assigned value.

Demo class "Address" has a simple set of attributes: 'street_address',
'st' and 'city'.  The values of 'st' and 'city' are to be chosen
from enumerated lists; however, the user does not want to see every
city in the U.S. on the list, but only those for the chosen state.

Various implementations of the dynamic data retrieval are possible, but
should allow for run-time changes to the lists of permitted values.
We have chosen a dictionary for this simple example.

Note that 'city' is simply defined as a trait of type Str.  The values
that appear in the enumerated list of the GUI are determined by the
argument to the TraitEnum constructor.  (TraitEnum is a subclass of
TraitHandler, the class of objects that perform validation tasks for
trait attributes.)
"""

# Imports:
from traits.api \
    import HasTraits, Str, Enum, List

from traitsui.api \
    import View, Item, Handler, EnumEditor


# Dictionary of defined states and cities.
cities = {
    'GA': [ 'Athens', 'Atlanta', 'Macon', 'Marietta', 'Savannah' ],
    'TX': [ 'Austin', 'Amarillo', 'Dallas', 'Houston', 'San Antonio', 'Waco' ],
    'OR': [ 'Albany', 'Eugene', 'Portland' ]
}


class AddressHandler ( Handler ):
    """ Handler class to redefine the possible values of 'city' based on 'st'.
    """

    # Current list of cities that apply:
    cities = List( Str )

    def object_st_changed ( self, info ):
        # Change the selector options:
        #info.cityedit.factory.values = cities[ info.object.st ]
        self.cities = cities[ info.object.st ]

        # Assign the default value to the first element of the list:
        info.object.city = self.cities[0]


class Address ( HasTraits ):
    """ Demo class for demonstrating dynamic redefinition of valid trait values.
    """

    street_address = Str
    st             = Enum( cities.keys()[0], cities.keys() )
    city           = Str

    view = View(
        Item( name  = 'street_address' ),
        Item( name  = 'st', label = 'State' ),
        Item( name  = 'city',
              editor = EnumEditor( name = 'handler.cities' ),
              id     = 'cityedit' ),
        title     = 'Address Information',
        buttons   = [ 'OK' ],
        resizable = True,
        handler   = AddressHandler
    )


# Create the demo:
demo = Address(street_address="4743 Dudley Lane")

# Run the demo (if invoked from the command line):
if __name__== '__main__':
    demo.configure_traits()

