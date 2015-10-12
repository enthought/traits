#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# scratch_adapter.py - Example of writing an adapter from scratch

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Instance, adapts
from interface_definition import IName
from interface_implementation import Person


#--[Code]----------------------------------------------------------------------
class PersonINameAdapter(HasTraits):

    # Declare what interfaces this adapter implements,
    # and for what class:
    adapts(Person, IName)

    # Declare the type of client it supports:
    client = Instance(Person)

    # Implement the adapter's constructor:
    def __init__(self, client):
        self.client = client

    # Implement the 'IName' interface on behalf of its client:
    def get_name(self):
        return ('%s %s' % (self.client.first_name,
                self.client.last_name))
