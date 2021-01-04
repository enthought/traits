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
This example shows how to set up notifications for changes on a single trait,
for all instances of this class.

Note that a change notification is also fired when the instance is created.
This is because the value provided in the instance constructor is different
from the default value.
"""

from traits.api import HasTraits, Int, observe


class Person(HasTraits):
    age = Int(0)

    @observe("age")
    def notify_age_change(self, event):
        print("age changed from {} to {}".format(event.old, event.new))


person = Person(age=1)  # print 'age changed from 0 to 1'
person.age = 2    # print 'age changed from 1 to 2'
