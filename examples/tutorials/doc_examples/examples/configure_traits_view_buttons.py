#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.


# configure_traits_view_buttons.py -- Sample code to demonstrate 
#                                     configure_traits()

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Str, Int
from enthought.traits.ui.api import View, Item
from enthought.traits.ui.menu import OKButton, CancelButton

#--[Code]-----------------------------------------------------------------------

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str
    department = Str

    employee_number = Str
    salary = Int

view1 = View(Item(name = 'first_name'),
             Item(name = 'last_name'),
             Item(name = 'department'),
             buttons = [OKButton, CancelButton])

sam = SimpleEmployee()
sam.configure_traits(view=view1)    

