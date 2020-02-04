# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# scratch_adapter.py - Example of writing an adapter from scratch

# --[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Instance, adapts
from interface_definition import IName
from interface_implementation import Person


# --[Code]----------------------------------------------------------------------
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
        return "%s %s" % (self.client.first_name, self.client.last_name)
