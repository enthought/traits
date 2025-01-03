# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import collections
import enum
import unittest

from traits.trait_base import safe_contains


class Lights(enum.Enum):
    red = "red"
    blue = "blue"
    green = "green"


class MoreLights(enum.Enum):
    amber = 1
    aquamarine = 2
    azure = 3


class RaisingContainer(collections.abc.Sequence):
    def __len__(self):
        return 15

    def __getitem__(self, index):
        if not 0 <= index < 15:
            raise IndexError("Index out of range")
        return 1729

    def __contains__(self, value):
        if value != 1729:
            raise TypeError("My contents are my own private business!")
        return True


class TestTraitBase(unittest.TestCase):
    def test_safe_contains(self):
        self.assertFalse(safe_contains(1, Lights))
        self.assertFalse(safe_contains(MoreLights.amber, Lights))
        self.assertTrue(safe_contains(Lights.red, Lights))

        lights_list = list(Lights)
        self.assertFalse(safe_contains(1, lights_list))
        self.assertFalse(safe_contains(MoreLights.amber, lights_list))
        self.assertTrue(safe_contains(Lights.red, lights_list))

        unfriendly_container = RaisingContainer()
        self.assertFalse(safe_contains(1, unfriendly_container))
        self.assertTrue(safe_contains(1729, unfriendly_container))
        self.assertFalse(safe_contains(Lights.green, unfriendly_container))
