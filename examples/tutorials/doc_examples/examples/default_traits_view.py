#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# default_traits_view.py -- Sample code to demonstrate the use of 'traits_view'

#--[Imports]--------------------------------------------------------------------
from traits.api import HasTraits, Str, Int
from traitsui.api import View, Item, Group
import traitsui

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

