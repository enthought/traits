#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# simple_adapter.py - Example of adaptation using Adapter

#--[Imports]-------------------------------------------------------------------
from traits.api import Adapter, Instance, implements
from interface_definition import IName
from interface_implementation import Person


#--[Code]----------------------------------------------------------------------
class PersonINameAdapter(Adapter):

    # Declare what interfaces this adapter implements for its
    # client:
    implements(IName)

    # Declare the type of client it supports:
    adaptee = Instance(Person)

    # Implement the 'IName' interface on behalf of its client:
    def get_name(self):
        return ('%s %s' % (self.adaptee.first_name,
                           self.adaptee.last_name))
