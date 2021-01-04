# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# post_init_notification.py --- Example of static notification
from traits.api import Float, HasTraits, on_trait_change, Str


class Part(HasTraits):
    cost = Float(0.0)

    name = Str("Part")

    @on_trait_change("cost")
    def cost_updated(self, object, name, old, new):
        print("{} is changed from {} to {}".format(name, old, new))

    @on_trait_change("name", post_init=True)
    def name_updated(self, object, name, old, new):
        print("{} is changed from {} to {}".format(name, old, new))


part = Part(cost=2.0, name="Nail")
# Result: cost is changed from 0.0 to 2.0
