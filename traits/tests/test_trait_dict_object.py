# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import copy
import pickle
import unittest

from traits.trait_errors import TraitError
from traits.trait_base import Undefined
from traits.trait_dict_object import TraitDict


def str_validator(value):
    if type(value) is str:
        return value
    else:
        raise TraitError


def int_validator(value):
    if type(value) is int:
        return value
    else:
        raise TraitError


class TestTraitList(unittest.TestCase):

    def setUp(self):
        self.added = None
        self.changed = None
        self.removed = None
        self.trait_list = None

    def notification_handler(self, trait_list, added, changed, removed):
        self.trait_list = trait_list
        self.added = added
        self.changed = changed
        self.removed = removed

    def test_init(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator)
        self.assertDictEqual(td, {"a": 1, "b": 2})
        self.assertEqual(td.notifiers, [])

    def test_notification(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])
        td["c"] = 5

        self.assertEqual(self.added, {"c": 5})
        self.assertEqual(self.changed, {})
        self.assertEqual(self.removed, {})

    def test_deepcopy(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])
        td_copy = copy.deepcopy(td)

        for itm, itm_cpy in zip(td.items(), td_copy.items()):
            self.assertTupleEqual(itm_cpy, itm)

        self.assertEqual(td_copy.notifiers, [])
        self.assertEqual(td_copy.value_validator, td.value_validator)
        self.assertEqual(td_copy.key_validator, td.key_validator)

    def test_setitem(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])
        td["a"] = 5

        self.assertEqual(self.added, {})
        self.assertEqual(self.changed, {"a": 1})
        self.assertEqual(self.removed, {})

        with self.assertRaises(TraitError):
            td[5] = "a"

    def test_delitem(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])
        del td["a"]

        self.assertEqual(self.added, {})
        self.assertEqual(self.changed, {})
        self.assertEqual(self.removed, {"a": 1})

    def test_update(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        td.update({"a": 2, "b": 4, "c": 5})

        self.assertEqual(self.added, {"c": 5})
        self.assertEqual(self.changed, {"a": 1, "b": 2})
        self.assertEqual(self.removed, {})

    def test_clear(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        td.clear()

        self.assertEqual(self.added, {})
        self.assertEqual(self.changed, {})
        self.assertEqual(self.removed, {"a": 1, "b": 2})

    def test_invalid_key(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            td[3] = "3"

    def test_invalid_value(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            td["3"] = True

    def test_setdefault(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        result = td.setdefault("c", 3)
        self.assertEqual(result, 3)

        self.assertEqual(td.setdefault("a", 5), 1)

    def test_pop(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        td.pop("b", "X")

        self.assertEqual(self.removed, {"b": 2})

        res = td.pop("x", "X")
        self.assertEqual(self.removed, {"b": 2})
        self.assertEqual(res, "X")

    def test_popitem(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        items_cpy = td.copy().items()

        itm = td.popitem()

        self.assertIn(itm, items_cpy)
        self.assertNotIn(itm, td.items())

        td = TraitDict({}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(KeyError):
            td.popitem()

    def test_pickle(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])
        pickle.loads(pickle.dumps(td))
