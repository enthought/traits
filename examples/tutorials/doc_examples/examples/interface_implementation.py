# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# interface_implementation.py - Example of implementing an interface

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Instance, provides, Str
from interface_definition import IName


# --[Code]---------------------------------------------------------------------
@provides(IName)
class Person(HasTraits):
    first_name = Str("John")
    last_name = Str("Doe")

    # Implementation of the 'IName' interface:
    def get_name(self):
        """ Returns the name of an object. """
        return "%s %s" % (self.first_name, self.last_name)


# --[Example*]-----------------------------------------------------------------
class Apartment(HasTraits):
    renter = Instance(IName)


william = Person(first_name="William", last_name="Adams")
apt1 = Apartment(renter=william)
print("Renter is: ", apt1.renter.get_name())
# Result: Renter is: William Adams
