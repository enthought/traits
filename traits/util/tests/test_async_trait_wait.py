# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import random
import threading
import time
import unittest

from traits.api import Enum, HasStrictTraits

from traits.util.async_trait_wait import wait_for_condition


class TrafficLights(HasStrictTraits):
    colour = Enum("Green", "Amber", "Red", "RedAndAmber")

    _next_colour = {
        "Green": "Amber",
        "Amber": "Red",
        "Red": "RedAndAmber",
        "RedAndAmber": "Green",
    }

    def make_random_changes(self, change_count):
        for _ in range(change_count):
            time.sleep(random.uniform(0.1, 0.3))
            self.colour = self._next_colour[self.colour]


class TestAsyncTraitWait(unittest.TestCase):
    def test_wait_for_condition_success(self):
        lights = TrafficLights(colour="Green")
        t = threading.Thread(target=lights.make_random_changes, args=(2,))
        t.start()

        wait_for_condition(
            condition=lambda l: l.colour == "Red", obj=lights, trait="colour"
        )

        self.assertEqual(lights.colour, "Red")
        t.join()

    def test_wait_for_condition_failure(self):
        lights = TrafficLights(colour="Green")
        t = threading.Thread(target=lights.make_random_changes, args=(2,))
        t.start()

        self.assertRaises(
            RuntimeError,
            wait_for_condition,
            condition=lambda l: l.colour == "RedAndAmber",
            obj=lights,
            trait="colour",
            timeout=5.0,
        )
        t.join()

    def test_traits_handler_cleaned_up(self):
        # An older version of wait_for_condition failed to clean up
        # the trait handler, leading to possibly evaluation of the
        # condition after the 'wait_for_condition' call had returned.

        self.lights = TrafficLights(colour="Green")
        t = threading.Thread(target=self.lights.make_random_changes, args=(3,))
        t.start()
        wait_for_condition(
            condition=lambda l: self.lights.colour == "Red",
            obj=self.lights,
            trait="colour",
        )
        del self.lights

        # If the condition gets evaluated again past this point, we'll
        # see an AttributeError from the failed self.lights lookup.

        # assertSucceeds!
        t.join()
