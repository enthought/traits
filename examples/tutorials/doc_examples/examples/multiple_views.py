#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# multiple_views.py -- Sample code to demonstrate the use of multiple views

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Str, Int
from enthought.traits.ui.api import View, Item, Group
import enthought.traits.ui

#--[Code]-----------------------------------------------------------------------

class SimpleEmployee3(HasTraits):
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

    all_view = View(Group(Item(name = 'first_name'),
                          Item(name = 'last_name'),
                          Item(name = 'department'),
                          Item(name = 'employee_number'),
                          Item(name = 'salary'),
                          label = 'Personnel database ' + 
                                  'entry',
                          show_border = True))

sam = SimpleEmployee3()
sam.configure_traits()
sam.configure_traits(view='all_view')
                          
