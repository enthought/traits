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
from unittest import mock

from traits.api import HasTraits
from traits.trait_dict_object import TraitDict, TraitDictObject
from traits.trait_errors import TraitError
from traits.trait_types import Dict, Int, Str


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


class TestTraitDict(unittest.TestCase):

    def setUp(self):
        self.added = None
        self.changed = None
        self.removed = None
        self.trait_dict = None

    def notification_handler(self, trait_dict, removed, added, changed):
        self.trait_list = trait_dict
        self.removed = removed
        self.added = added
        self.changed = changed

    def test_init(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator)
        self.assertEqual(td, {"a": 1, "b": 2})
        self.assertEqual(td.notifiers, [])

    def test_init_iterable(self):
        td = TraitDict([("a", 1), ("b", 2)], key_validator=str_validator,
                       value_validator=int_validator)
        self.assertEqual(td, {"a": 1, "b": 2})
        self.assertEqual(td.notifiers, [])

        with self.assertRaises(ValueError):
            TraitDict(["a", "b"], key_validator=str_validator,
                      value_validator=int_validator)

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

        self.assertEqual(td, td_copy)
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

    def test_delitem_not_found(self):
        python_dict = dict()
        with self.assertRaises(KeyError) as python_e:
            del python_dict["x"]

        td = TraitDict()
        with self.assertRaises(KeyError) as trait_e:
            del td["x"]

        self.assertEqual(
            str(trait_e.exception),
            str(python_e.exception),
        )

    def test_update(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        td.update({"a": 2, "b": 4, "c": 5})

        self.assertEqual(self.added, {"c": 5})
        self.assertEqual(self.changed, {"a": 1, "b": 2})
        self.assertEqual(self.removed, {})

    def test_update_iterable(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        td.update([("a", 2), ("b", 4), ("c", 5)])

        self.assertEqual(self.added, {"c": 5})
        self.assertEqual(self.changed, {"a": 1, "b": 2})
        self.assertEqual(self.removed, {})

    def test_update_with_tranformation(self):
        td = TraitDict(
            {"1": 1, "2": 2},
            key_validator=str,
            notifiers=[self.notification_handler],
        )

        # when
        td.update({1: 2})

        # then
        self.assertEqual(td, {"1": 2, "2": 2})
        self.assertEqual(self.added, {})
        self.assertEqual(self.changed, {"1": 1})
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

    def test_setdefault_with_casting(self):
        # If the validator does transformation, the containment
        # is checked before the transformation. This is more
        # consistent with the description of setdefault, which is
        # effectively a short-hand for ``__getitem__``,
        # followed by ``__setitem__`` (if get fails), followed by
        # another ``__getitem__``.
        # The notification should be factual about the actual
        # mutation on the dict.
        notifier = mock.Mock()
        td = TraitDict(
            key_validator=str,
            value_validator=str,
            notifiers=[notifier, self.notification_handler],
        )

        td.setdefault(1, 2)
        self.assertEqual(td, {"1": "2"})
        self.assertEqual(notifier.call_count, 1)
        self.assertEqual(self.removed, {})
        self.assertEqual(self.added, {"1": "2"})
        self.assertEqual(self.changed, {})

        notifier.reset_mock()
        td.setdefault(1, 4)
        self.assertEqual(td, {"1": "4"})
        self.assertEqual(notifier.call_count, 1)

        self.assertEqual(self.removed, {})
        self.assertEqual(self.added, {})
        self.assertEqual(self.changed, {"1": "2"})

    def test_pop(self):
        td = TraitDict({"a": 1, "b": 2}, key_validator=str_validator,
                       value_validator=int_validator,
                       notifiers=[self.notification_handler])

        td.pop("b", "X")

        self.assertEqual(self.removed, {"b": 2})

        self.removed = None
        res = td.pop("x", "X")
        # Ensure no notification is fired.
        self.assertIsNone(self.removed)
        self.assertEqual(res, "X")

    def test_pop_key_error(self):
        python_dict = {}
        with self.assertRaises(KeyError) as python_e:
            python_dict.pop("a")

        td = TraitDict()
        with self.assertRaises(KeyError) as trait_e:
            td.pop("a")

        self.assertEqual(
            str(trait_e.exception),
            str(python_e.exception),
        )

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

        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            td_unpickled = pickle.loads(pickle.dumps(td, protocol=protocol))

            self.assertIs(td_unpickled.key_validator, str_validator)
            self.assertIs(td_unpickled.value_validator, int_validator)
            self.assertEqual(td_unpickled.notifiers, [])


class TestTraitDictObject(unittest.TestCase):
    """ Test TraitDictObject operations."""

    class TestClass(HasTraits):
        dict_1 = Dict(Str)
        dict_2 = Dict(Int, Str)

    def test_trait_dict_object_validate_key(self):
        obj = TestTraitDictObject.TestClass()
        trait_dict_obj = TraitDictObject(
            trait=obj.trait('dict_1').trait_type,
            object=obj,
            name="a",
            value={},
        )
        # This is okay
        trait_dict_obj.key_validator("1")

        # This fails.
        with self.assertRaises(TraitError):
            trait_dict_obj.key_validator(1)

    def test_trait_dict_object_validate_value(self):
        obj = TestTraitDictObject.TestClass()
        trait_dict_obj = TraitDictObject(
            trait=obj.trait('dict_2').trait_type,
            object=obj,
            name="a",
            value={},
        )
        # This is okay
        trait_dict_obj.value_validator("1")

        # This fails.
        with self.assertRaises(TraitError):
            trait_dict_obj.value_validator(1)

    def test_trait_dict_object_pickle(self):
        obj = TestTraitDictObject.TestClass()
        trait_dict_obj = TraitDictObject(
            trait=obj.trait('dict_2').trait_type,
            object=obj,
            name="a",
            value={},
        )

        tdo_unpickled = pickle.loads(pickle.dumps(trait_dict_obj))

        # Validation is disabled
        tdo_unpickled.value_validator("1")
        tdo_unpickled.value_validator(1)
        tdo_unpickled.value_validator(True)
