#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# external_adapter.py - Example of declaring a class as an adapter
#                       externally to the class

#--[Imports]-------------------------------------------------------------------
from traits.api import adapts
from interface_definition import IName
from interface_implementation import Person


#--[Code]----------------------------------------------------------------------
class AnotherPersonAdapter(object):

    # Implement the adapter's constructor:
    def __init__(self, person):
        self.person = person

    # Implement the 'IName' interface on behalf of its client:
    def get_name(self):
        return ('%s %s' % (self.person.first_name,
                           self.person.last_name))

adapts(AnotherPersonAdapter, Person, IName)
