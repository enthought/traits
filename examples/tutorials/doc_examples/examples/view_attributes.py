#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# view_attributes.py --- Example of a view as an 
#                        attribute of a class
from enthought.traits.api import HasTraits, Int, Str, Trait
from enthought.traits.ui.api import View
import enthought.traits.ui

class Person(HasTraits):
    first_name = Str
    last_name = Str
    age = Int
    gender = Trait(None, 'M', 'F')
    name_view = View('first_name', 'last_name')

bill = Person()
bill.configure_traits()
