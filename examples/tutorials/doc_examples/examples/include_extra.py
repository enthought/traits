#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# include_extra.py --- Example of Include object
#                      provided for subclasses
from traits.api import HasTraits, Int, Str, Trait
from traitsui.api import Group, Include, View
import traitsui

class Person(HasTraits):
    name = Str
    age = Int

    person_view = View('name', Include('extra'), 'age',
                       kind='livemodal')

Person().configure_traits()

class LocatedPerson(Person):
    street = Str
    city = Str
    state = Str
    zip = Str

    extra = Group('street', 'city', 'state', 'zip')

LocatedPerson().configure_traits()

