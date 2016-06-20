#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# configure_traits.py -- Sample code to demonstrate configure_traits()

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Str, Int


#--[Code]----------------------------------------------------------------------
class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str
    department = Str

    employee_number = Str
    salary = Int

sam = SimpleEmployee()
sam.configure_traits()
