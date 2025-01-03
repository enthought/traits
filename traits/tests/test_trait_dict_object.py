# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
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
import sys
import unittest
from unittest import mock

from traits.api import DefaultValue, HasTraits, TraitType, ValidateTrait
from traits.trait_dict_object import TraitDict, TraitDictEvent, TraitDictObject
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


class RangeInstance(TraitType):
    """
    Dummy custom trait type for use in validation tests.
    """

    default_value_type = DefaultValue.constant

    default_value = range(10)

    fast_validate = ValidateTrait.coerce, range


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

    if sys.version_info >= (3, 9):
        # The |= operation on dictionaries was introduced in Python 3.9

        def test_ior(self):
            td = TraitDict(
                {"a": 1, "b": 2},
                key_validator=str_validator,
                value_validator=int_validator,
                notifiers=[self.notification_handler],
            )
            td |= {"a": 3, "d": 5}

            self.assertEqual(td, {"a": 3, "b": 2, "d": 5})
            self.assertEqual(self.added, {"d": 5})
            self.assertEqual(self.changed, {"a": 1})
            self.assertEqual(self.removed, {})

        def test_ior_is_quiet_if_no_change(self):
            td = TraitDict(
                {"a": 1, "b": 2},
                key_validator=str_validator,
                value_validator=int_validator,
                notifiers=[self.notification_handler],
            )

            td |= []

            self.assertEqual(td, {"a": 1, "b": 2})
            self.assertIsNone(self.added)
            self.assertIsNone(self.removed)
            self.assertIsNone(self.changed)

    else:
        # Python versions earlier than 3.9 should still raise TypeError.

        def test_ior(self):
            td = TraitDict(
                {"a": 1, "b": 2},
                key_validator=str_validator,
                value_validator=int_validator,
                notifiers=[self.notification_handler],
            )
            with self.assertRaises(TypeError):
                td |= {"a": 3, "d": 5}

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

    def test_update_with_transformation(self):
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

    def test_update_with_empty_argument(self):
        td = TraitDict(
            {"1": 1, "2": 2},
            key_validator=str,
            notifiers=[self.notification_handler],
        )

        # neither of these should cause a notification to be emitted
        td.update([])
        td.update({})
        self.assertEqual(td, {"1": 1, "2": 2})
        self.assertIsNone(self.added)
        self.assertIsNone(self.changed)
        self.assertIsNone(self.removed)

    def test_update_notifies_with_nonempty_argument(self):
        # Corner case: we don't want to get into the difficulties of
        # comparing values for equality, so we notify for a non-empty
        # argument even if the dictionary has not actually changed.
        td = TraitDict(
            {"1": 1, "2": 2},
            key_validator=str,
            notifiers=[self.notification_handler],
        )

        td.update({"1": 1})
        self.assertEqual(td, {"1": 1, "2": 2})
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

    def test_clear_empty_dictionary(self):
        # Clearing an empty dictionary should not notify.
        td = TraitDict(
            {},
            key_validator=str_validator,
            value_validator=int_validator,
            notifiers=[self.notification_handler],
        )

        td.clear()

        self.assertIsNone(self.added)
        self.assertIsNone(self.changed)
        self.assertIsNone(self.removed)

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

    def test_disconnected_dict(self):
        # Objects that are disconnected from their HasTraits "owner" can arise
        # as a result of clone_traits operations, or of serialization and
        # deserialization.
        disconnected = TraitDictObject(
            trait=Dict(Str, Str),
            object=None,
            name="foo",
            value={},
        )
        self.assertEqual(disconnected.object(), None)

    def test_key_validation_uses_ctrait(self):
        # Regression test for enthought/traits#1619

        class HasRanges(HasTraits):
            ranges = Dict(RangeInstance(), Int())

        obj = HasRanges()

        with self.assertRaises(TraitError):
            obj.ranges[3] = 27

        obj.ranges[range(10, 20)] = 3
        self.assertEqual(obj.ranges, {range(10, 20): 3})

    def test_value_validation_uses_ctrait(self):
        # Regression test for enthought/traits#1619

        class HasRanges(HasTraits):
            ranges = Dict(Int(), RangeInstance())

        obj = HasRanges()

        with self.assertRaises(TraitError):
            obj.ranges[3] = 27

        obj.ranges[3] = range(10, 20)
        self.assertEqual(obj.ranges, {3: range(10, 20)})


class TestTraitDictEvent(unittest.TestCase):

    def test_trait_dict_event_str_representation(self):
        """ Test string representation of the TraitDictEvent class. """
        desired_repr = "TraitDictEvent(removed={}, added={}, changed={})"
        trait_dict_event = TraitDictEvent()
        self.assertEqual(desired_repr, str(trait_dict_event))
        self.assertEqual(desired_repr, repr(trait_dict_event))

    def test_trait_dict_event_subclass_str_representation(self):
        """ Test string representation of a subclass of the TraitDictEvent
        class. """

        class DifferentName(TraitDictEvent):
            pass

        desired_repr = "DifferentName(removed={}, added={}, changed={})"
        differnt_name_subclass = DifferentName()
        self.assertEqual(desired_repr, str(differnt_name_subclass))
        self.assertEqual(desired_repr, repr(differnt_name_subclass))
