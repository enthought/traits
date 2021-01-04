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
for a specific instance of HasTraits.

The change handler can be removed using the 'remove' argument on ``observe``.
"""

from traits.api import HasTraits, Int


class Person(HasTraits):
    age = Int(0)


def print_change(event):
    print("{} changed: {} -> {}".format(event.name, event.old, event.new))


person = Person(age=1)
person.observe(print_change, "age")
person.age = 2    # print 'age changed: 1 -> 2'

person.observe(print_change, "age", remove=True)
person.age = 3    # nothing is printed.
