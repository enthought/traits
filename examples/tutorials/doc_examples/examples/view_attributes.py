#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# view_attributes.py --- Example of a view as an
#                        attribute of a class
from traits.api import HasTraits, Int, Str, Trait
from traitsui.api import View
import traitsui

class Person(HasTraits):
    first_name = Str
    last_name = Str
    age = Int
    gender = Trait(None, 'M', 'F')
    name_view = View('first_name', 'last_name')

bill = Person()
bill.configure_traits()
