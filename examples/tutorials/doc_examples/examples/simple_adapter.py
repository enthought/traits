# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# simple_adapter.py - Example of adaptation using Adapter

# --[Imports]------------------------------------------------------------------
from traits.api import Adapter, Instance, provides

from interface_definition import IName
from interface_implementation import Person


# --[Code]---------------------------------------------------------------------
@provides(IName)
class PersonINameAdapter(Adapter):

    # Declare the type of client it supports:
    adaptee = Instance(Person)

    # Implement the 'IName' interface on behalf of its client:
    def get_name(self):
        return "%s %s" % (self.adaptee.first_name, self.adaptee.last_name)
