# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# external_adapter.py - Example of declaring a class as an adapter
#                       externally to the class

# --[Imports]-------------------------------------------------------------------
from traits.api import adapts
from interface_definition import IName
from interface_implementation import Person


# --[Code]----------------------------------------------------------------------
class AnotherPersonAdapter(object):

    # Implement the adapter's constructor:
    def __init__(self, person):
        self.person = person

    # Implement the 'IName' interface on behalf of its client:
    def get_name(self):
        return "%s %s" % (self.person.first_name, self.person.last_name)


adapts(AnotherPersonAdapter, Person, IName)
