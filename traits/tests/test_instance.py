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
Tests for the Instance and BaseInstance trait types.
"""

import unittest

from traits.api import BaseInstance, HasStrictTraits, Instance, TraitError


#: Define a new "trait type" using BaseInstance. This is similar to the
#: way that Datetime and Time are defined.
Slice = BaseInstance(slice)


class HasSlices(HasStrictTraits):
    my_slice = Instance(slice)

    also_my_slice = Slice()

    none_explicitly_allowed = Instance(slice, allow_none=True)

    also_allow_none = Slice(allow_none=True)

    disallow_none = Instance(slice, allow_none=False)

    also_disallow_none = Slice(allow_none=False)


class TestInstance(unittest.TestCase):
    def test_explicitly_prohibit_none(self):
        obj = HasSlices(disallow_none=slice(2, 5))
        self.assertIsNotNone(obj.disallow_none)
        with self.assertRaises(TraitError):
            obj.disallow_none = None
        self.assertIsNotNone(obj.disallow_none)

        obj = HasSlices(also_disallow_none=slice(2, 5))
        self.assertIsNotNone(obj.also_disallow_none)
        with self.assertRaises(TraitError):
            obj.also_disallow_none = None
        self.assertIsNotNone(obj.also_disallow_none)

    def test_explicitly_allow_none(self):
        obj = HasSlices(none_explicitly_allowed=slice(2, 5))
        self.assertIsNotNone(obj.none_explicitly_allowed)
        obj.none_explicitly_allowed = None
        self.assertIsNone(obj.none_explicitly_allowed)

        obj = HasSlices(also_allow_none=slice(2, 5))
        self.assertIsNotNone(obj.also_allow_none)
        obj.also_allow_none = None
        self.assertIsNone(obj.also_allow_none)

    def test_allow_none_permitted_by_default(self):
        obj = HasSlices(my_slice=slice(2, 5))
        self.assertIsNotNone(obj.my_slice)
        obj.my_slice = None
        self.assertIsNone(obj.my_slice)

        obj = HasSlices(also_my_slice=slice(2, 5))
        self.assertIsNotNone(obj.also_my_slice)
        obj.my_slice = None
        self.assertIsNone(obj.my_slice)
