# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# observe_optional.py --- Example of using observe with post_init
from traits.api import HasTraits, Int, observe
from traits.observation.api import trait

class Person(HasTraits):

    @observe(trait("age", optional=True))
    def notify_age_change(self, event):
        print("age changed")

person = Person()
person.add_trait("age", Int())
person.age = 2    # print 'age changed'
