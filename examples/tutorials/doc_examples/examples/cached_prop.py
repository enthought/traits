# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
This example demonstrates the use of Property, with caching and notifcation
support.

"""

from traits.api import (
    cached_property, HasStrictTraits, Str, observe, Property,
)


class Person(HasStrictTraits):

    full_name = Str()
    last_name = Property(observe="full_name")

    @cached_property
    def _get_last_name(self):
        return self.full_name.split(" ")[-1]

    @observe("last_name")
    def _last_name_updated(self, event):
        print("last_name is changed.")


obj = Person()
obj.full_name = "John Doe"   # print: last_name is changed.
