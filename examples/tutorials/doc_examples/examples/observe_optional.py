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
This example shows how to set up notifications for a trait that is defined
after the instance is created.

The optional flag suppresses the error that would otherwise occur because the
trait is not found at the time ``observe`` is called. When the observed trait
is defined, the change handler will be aded to the new trait.
"""

from traits.api import HasTraits, Int, observe
from traits.observation.api import trait


class Person(HasTraits):

    @observe(trait("age", optional=True))
    def notify_age_change(self, event):
        print("age changed")


person = Person()
person.add_trait("age", Int())
person.age = 2    # print 'age changed'
