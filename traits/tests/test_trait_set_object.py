# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.trait_errors import TraitError
from traits.trait_set_object import TraitSet, adapt_trait_validator
from traits.trait_types import _validate_int


def int_validator(current_set, value):
    return {_validate_int(v) for v in value}


def string_validator(current_set, value):
    ret = set()
    for v in value:
        if isinstance(v, str):
            ret.add(v)
        else:
            raise TraitError
    return ret


class TestTraitSet(unittest.TestCase):

    def setUp(self):
        self.added = None
        self.removed = None

    def notification_handler(self, removed, added):
        self.removed = removed
        self.added = added

    def test_init(self):
        ts = TraitSet({1, 2, 3})

        self.assertSetEqual(ts, {1, 2, 3})
        self.assertIsNone(ts.validator)
        self.assertEqual(ts.notifiers, [])

    def test_validator(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator)

        self.assertSetEqual(ts, {1, 2, 3})
        self.assertEqual(ts.validator, int_validator)
        self.assertEqual(ts.notifiers, [])

    def test_adapt_trait_validator(self):

        def bool_validator(object, name, value):
            if isinstance(value, bool):
                return value
            else:
                raise TraitError

        # Fail without adaptor
        with self.assertRaises(TypeError):
            TraitSet({}, validator=bool_validator)

        # Attach the adaptor
        list_bool_validator = adapt_trait_validator(bool_validator)

        # It now works!
        ts_2 = TraitSet({}, validator=list_bool_validator)
        ts_2.update([True, False, True])

        # Decorate with set adaptor
        @adapt_trait_validator
        def bool_validator(object, name, value):
            if isinstance(value, bool):
                return value
            else:
                raise TraitError

        # Still working
        ts = TraitSet({}, validator=bool_validator)
        ts.update([True, False, True])

        with self.assertRaises(TraitError):
            ts.update(["invalid"])

    def test_notification(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])

        self.assertSetEqual(ts, {1, 2, 3})
        self.assertEqual(ts.validator, int_validator)
        self.assertEqual(ts.notifiers, [self.notification_handler])

    def test_add(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.add(5)

        self.assertSetEqual(ts, {1, 2, 3, 5})
        self.assertEqual(set(), self.removed)
        self.assertEqual({5}, self.added)

        ts = TraitSet({"one", "two", "three"}, validator=string_validator,
                      notifiers=[self.notification_handler])
        ts.add("four")
        self.assertSetEqual(ts, {"one", "two", "three", "four"})
        self.assertEqual(set(), self.removed)
        self.assertEqual({"four"}, self.added)

    def test_remove(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.remove(3)

        self.assertSetEqual(ts, {1, 2})
        self.assertEqual({3}, self.removed)
        self.assertEqual(set(), self.added)

        with self.assertRaises(KeyError):
            ts.remove(3)

    def test_discard(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.discard(3)

        self.assertSetEqual(ts, {1, 2})
        self.assertEqual({3}, self.removed)
        self.assertEqual(set(), self.added)

        # No error is raised
        ts.discard(3)

    def test_pop(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        val = ts.pop()

        self.assertIn(val, {1, 2, 3})
        self.assertEqual({val}, self.removed)
        self.assertEqual(set(), self.added)

    def test_clear(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.clear()

        self.assertEqual({1, 2, 3}, self.removed)
        self.assertEqual(set(), self.added)

    def test_ior(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts |= {4, 5}

        self.assertEqual(set(), self.removed)
        self.assertEqual({4, 5}, self.added)

        ts2 = TraitSet({6, 7}, validator=int_validator,
                       notifiers=[self.notification_handler])

        ts |= ts2

        self.assertEqual(set(), self.removed)
        self.assertEqual({6, 7}, self.added)

    def test_iand(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts &= {1, 2, 3}

        # Event is not fired
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

        ts &= {1, 2}
        self.assertEqual({3}, self.removed)
        self.assertEqual(set(), self.added)

    def test_ixor(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts ^= {1, 2, 3, 5}

        self.assertEqual({1, 2, 3}, self.removed)
        self.assertEqual({5}, self.added)
        self.assertSetEqual({5}, ts)

    def test_isub(self):
        ts = TraitSet({1, 2, 3}, validator=int_validator,
                      notifiers=[self.notification_handler])
        ts -= {2, 3, 5}

        self.assertEqual({2, 3}, self.removed)
        self.assertEqual(set(), self.added)
        self.assertSetEqual({1}, ts)
