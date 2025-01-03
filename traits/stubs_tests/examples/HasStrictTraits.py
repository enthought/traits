# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Event, HasStrictTraits, observe


class Person(HasStrictTraits):
    conductor = Event()

    @observe("conductor")
    def talk(self, event):
        pass


def sing(event):
    pass


person = Person()
person.observe(sing, "conductor")
