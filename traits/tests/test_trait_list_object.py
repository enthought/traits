#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

import unittest

from traits.trait_base import Undefined
from traits.trait_list_object import TraitList
from traits.trait_types import _validate_int


def int_validator(trait_list, index, removed, value):
    if isinstance(index, slice):
        return [_validate_int(item) for item in value]
    else:
        if value is Undefined:
            return Undefined
        return _validate_int(value)


class TestTraitList(unittest.TestCase):

    def notification_handler(self, trait_list, index, removed, added):
        self.trait_list = trait_list
        self.index = index
        self.removed = removed
        self.added = added

    def test_init(self):
        tl = TraitList([1, 2, 3])

        self.assertListEqual(tl, [1, 2, 3])
        self.assertIsNone(tl.validator)
        self.assertEqual(tl.notifiers, [])

    def test_validator(self):
        tl = TraitList([1, 2, 3], validator=int_validator)

        self.assertListEqual(tl, [1, 2, 3])
        self.assertEqual(tl.validator, int_validator)
        self.assertEqual(tl.notifiers, [])

    def test_notification(self):
        tl = TraitList([1, 2, 3], notifiers=[self.notification_handler])

        self.assertListEqual(tl, [1, 2, 3])
        self.assertIsNone(tl.validator)
        self.assertEqual(tl.notifiers, [self.notification_handler])

        tl[0] = 5

        self.assertListEqual(tl, [5, 2, 3])
        self.assertIs(self.trait_list, tl)
        self.assertEqual(self.index, 0)
        self.assertEqual(self.removed, 1)
        self.assertEqual(self.added, 5)
