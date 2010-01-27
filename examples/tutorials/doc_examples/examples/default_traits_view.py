#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# default_traits_view.py -- Sample code to demonstrate the use of 'traits_view'

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Str, Int
from enthought.traits.ui.api import View, Item, Group
import enthought.traits.ui

#--[Code]-----------------------------------------------------------------------

class SimpleEmployee2(HasTraits):
    first_name = Str
    last_name = Str
    department = Str

    employee_number = Str
    salary = Int

    traits_view = View(Group(Item(name = 'first_name'),
                             Item(name = 'last_name'),
                             Item(name = 'department'),
                             label = 'Personnel profile',
                             show_border = True))

sam = SimpleEmployee2()
sam.configure_traits()

