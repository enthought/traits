#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.


# configure_traits_view_group.py -- Sample code to demonstrate configure_traits()

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Str, Int
from enthought.traits.ui.api import View, Item, Group
import enthought.traits.ui

#--[Code]-----------------------------------------------------------------------

class SimpleEmployee(HasTraits):
    first_name = Str
    last_name = Str
    department = Str

    employee_number = Str
    salary = Int

view1 = View(Group(Item(name = 'first_name'),
                   Item(name = 'last_name'),
                   Item(name = 'department'),
                   label = 'Personnel profile',
                   show_border = True))


sam = SimpleEmployee()
sam.configure_traits(view=view1)    

