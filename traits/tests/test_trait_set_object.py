# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import pickle
import unittest
from unittest import mock

from traits.api import (
    DefaultValue,
    HasTraits,
    Set,
    Str,
    TraitType,
    ValidateTrait,
)
from traits.trait_base import _validate_everything
from traits.trait_errors import TraitError
from traits.trait_set_object import TraitSet, TraitSetEvent, TraitSetObject
from traits.trait_types import _validate_int


def int_validator(value):
    try:
        return _validate_int(value)
    except TypeError:
        raise TraitError("int_validator error")


def string_validator(value):
    if isinstance(value, str):
        return value
    else:
        raise TraitError("string_validator error")


class TestTraitSet(unittest.TestCase):

    def setUp(self):
        self.added = None
        self.removed = None
        self.validator_args = None
        self.trait_set = None

    def notification_handler(self, trait_set, removed, added):
        self.trait_set = trait_set
        self.removed = removed
        self.added = added

    def validator(self, added):
        self.validator_args = added
        return added

    def test_init(self):
        ts = TraitSet({1, 2, 3})

        self.assertEqual(ts, {1, 2, 3})
        self.assertIs(ts.item_validator, _validate_everything)
        self.assertEqual(ts.notifiers, [])

    def test_init_with_no_input(self):
        ts = TraitSet()

        self.assertEqual(ts, set())
        self.assertIs(ts.item_validator, _validate_everything)
        self.assertEqual(ts.notifiers, [])

    def test_validator(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator)

        self.assertEqual(ts, {1, 2, 3})
        self.assertEqual(ts.item_validator, int_validator)
        self.assertEqual(ts.notifiers, [])

    def test_notification(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])

        self.assertEqual(ts, {1, 2, 3})
        self.assertEqual(ts.item_validator, int_validator)
        self.assertEqual(ts.notifiers, [self.notification_handler])

        ts.add(5)

        self.assertEqual(ts, {1, 2, 3, 5})
        self.assertIs(self.trait_set, ts)
        self.assertEqual(self.removed, set())
        self.assertEqual(self.added, {5})

    def test_add(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.add(5)

        self.assertEqual(ts, {1, 2, 3, 5})
        self.assertEqual(self.removed, set())
        self.assertEqual(self.added, {5})

        ts = TraitSet({"one", "two", "three"}, item_validator=string_validator,
                      notifiers=[self.notification_handler])
        ts.add("four")
        self.assertEqual(ts, {"one", "two", "three", "four"})
        self.assertEqual(self.removed, set())
        self.assertEqual(self.added, {"four"})

    def test_add_iterable(self):
        python_set = set()
        iterable = (i for i in range(4))
        python_set.add(iterable)

        ts = TraitSet()
        ts.add(iterable)

        # iterable has not been exhausted
        next(iterable)
        self.assertEqual(ts, python_set)

    def test_add_unhashable(self):
        with self.assertRaises(TypeError) as python_e:
            set().add([])

        with self.assertRaises(TypeError) as trait_e:
            TraitSet().add([])

        self.assertEqual(
            str(trait_e.exception),
            str(python_e.exception),
        )

    def test_add_no_notification_for_no_op(self):
        # Test adding an existing item triggers no notifications
        notifier = mock.Mock()
        ts = TraitSet({1, 2}, notifiers=[notifier])

        # when
        ts.add(1)

        # then
        notifier.assert_not_called()

    def test_remove(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.remove(3)

        self.assertEqual(ts, {1, 2})
        self.assertEqual(self.removed, {3})
        self.assertEqual(self.added, set())

        with self.assertRaises(KeyError):
            ts.remove(3)

    def test_remove_iterable(self):
        iterable = (i for i in range(4))

        ts = TraitSet()
        ts.add(iterable)
        self.assertIn(iterable, ts)

        # when
        ts.remove(iterable)

        # then
        self.assertEqual(ts, set())

    def test_remove_does_not_call_validator(self):
        # Test validator should not be called with removed
        # items
        ts = TraitSet(item_validator=self.validator)
        ts.add("123")

        value, = ts

        # when
        self.validator_args = None
        ts.remove(value)

        # then
        # validator is not called.
        self.assertIsNone(self.validator_args)

    def test_update_with_non_iterable(self):
        python_set = set()
        with self.assertRaises(TypeError) as python_exc:
            python_set.update(None)

        ts = TraitSet()
        with self.assertRaises(TypeError) as trait_exc:
            ts.update(None)

        self.assertEqual(
            str(trait_exc.exception),
            str(python_exc.exception),
        )

    def test_update_varargs(self):
        ts = TraitSet(notifiers=[self.notification_handler])
        ts.update({1, 2}, {3, 4})
        self.assertEqual(self.added, {1, 2, 3, 4})
        self.assertEqual(self.removed, set())

    def test_update_with_nothing(self):
        notifier = mock.Mock()

        python_set = set()
        python_set.update()

        ts = TraitSet(notifiers=[notifier])

        # when
        ts.update()

        # then
        notifier.assert_not_called()
        self.assertEqual(ts, python_set)

    def test_discard(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.discard(3)

        self.assertEqual(ts, {1, 2})
        self.assertEqual(self.removed, {3})
        self.assertEqual(self.added, set())

        # No error is raised
        ts.discard(3)

    def test_pop(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        val = ts.pop()

        self.assertIn(val, {1, 2, 3})
        self.assertEqual(self.removed, {val})
        self.assertEqual(self.added, set())

    def test_clear(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts.clear()

        self.assertEqual(self.removed, {1, 2, 3})
        self.assertEqual(self.added, set())

    def test_clear_no_notifications_if_already_empty(self):
        # test no notifications are emitted if the set is already
        # empty.
        notifier = mock.Mock()
        ts = TraitSet(notifiers=[notifier])
        ts.clear()
        notifier.assert_not_called()

    def test_ior(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts |= {4, 5}

        self.assertEqual(self.removed, set())
        self.assertEqual(self.added, {4, 5})

        ts2 = TraitSet({6, 7}, item_validator=int_validator,
                       notifiers=[self.notification_handler])

        ts |= ts2

        self.assertEqual(self.removed, set())
        self.assertEqual(self.added, {6, 7})

        with self.assertRaises(TypeError):
            ts |= 8

    def test_iand(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts &= {1, 2, 3}

        # Event is not fired
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

        ts &= {1, 2}
        self.assertEqual(self.removed, {3})
        self.assertEqual(self.added, set())

        with self.assertRaises(TypeError):
            ts &= [3]

    def test_iand_does_not_call_validator(self):
        # Nothing are added, validator should not be called.
        ts = TraitSet({1, 2, 3}, item_validator=self.validator)
        values = list(ts)

        python_set = set(ts)
        python_set &= set(values[:2])

        # when
        self.validator_args = None
        ts &= set(values[:2])

        # then
        self.assertEqual(ts, python_set)
        self.assertIsNone(self.validator_args)

    def test_intersection_update_with_no_arguments(self):
        python_set = set([1, 2, 3])
        python_set.intersection_update()

        notifier = mock.Mock()
        ts = TraitSet([1, 2, 3], notifiers=[notifier])
        ts.intersection_update()

        self.assertEqual(ts, python_set)
        notifier.assert_not_called

    def test_intersection_update_varargs(self):
        python_set = set([1, 2, 3])
        python_set.intersection_update([2], [3])

        ts = TraitSet([1, 2, 3])
        ts.intersection_update([2], [3])

        self.assertEqual(ts, python_set)

    def test_intersection_update_with_iterable(self):
        python_set = set([1, 2, 3])
        python_set.intersection_update(i for i in [1, 2])

        ts = TraitSet([1, 2, 3])
        ts.intersection_update(i for i in [1, 2])
        self.assertEqual(ts, python_set)

    def test_ixor(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts ^= {1, 2, 3, 5}

        self.assertEqual(self.removed, {1, 2, 3})
        self.assertEqual(self.added, {5})
        self.assertEqual(ts, {5})

        with self.assertRaises(TypeError):
            ts ^= [5]

    def test_ixor_no_nofications_for_no_change(self):
        notifier = mock.Mock()
        ts_1 = TraitSet([1, 2], notifiers=[notifier])

        # when
        ts_1 ^= set()

        # then
        notifier.assert_not_called()

    def test_ixor_with_iterable_items(self):
        iterable = range(2)

        python_set = set([iterable])
        python_set ^= set([iterable])
        self.assertEqual(python_set, set())

        ts = TraitSet([iterable], item_validator=self.validator)
        self.validator_args = None
        ts ^= {iterable}
        self.assertEqual(ts, set())

        # No values are being added.
        self.assertIsNone(self.validator_args)

    def test_ixor_validator_args_with_added(self):
        # Check the values given to the validator
        # when symmetric_difference_update is called.

        validator = mock.Mock(wraps=str)
        ts = TraitSet(
            [1, 2, 3],
            item_validator=validator,
            notifiers=[self.notification_handler],
        )
        self.assertEqual(ts, set(["1", "2", "3"]))
        validator.reset_mock()

        # when
        ts ^= set(["2", 3, 4])

        # then
        validator_inputs = set(
            value for (value,), _ in validator.call_args_list)
        self.assertEqual(validator_inputs, set([3, 4]))
        self.assertEqual(ts, set(["1", "3", "4"]))
        self.assertEqual(self.added, set(["4"]))
        self.assertEqual(self.removed, set(["2"]))

    def test_isub(self):
        ts = TraitSet({1, 2, 3}, item_validator=int_validator,
                      notifiers=[self.notification_handler])
        ts -= {2, 3, 5}

        self.assertEqual(self.removed, {2, 3})
        self.assertEqual(self.added, set())
        self.assertEqual(ts, {1})

        with self.assertRaises(TypeError):
            ts -= [4, 5]

    def test_isub_validator_not_called(self):
        # isub never needs to add items, validator should not
        # be called.
        ts = TraitSet({1, 2, 3}, item_validator=self.validator)
        values = set(ts)

        # when
        self.validator_args = None

        ts -= values

        # then
        # Validator should not be called
        self.assertIsNone(self.validator_args)

    def test_isub_with_no_intersection(self):
        python_set = set([3, 4, 5])
        python_set -= set(i for i in range(2))

        notifier = mock.Mock()
        ts = TraitSet((3, 4, 5), notifiers=[notifier])

        # when
        ts -= set(i for i in range(2))

        # then
        self.assertEqual(ts, python_set)
        notifier.assert_not_called()

    def test_difference_update_with_no_arguments(self):
        python_set = set([1, 2, 3])
        python_set.difference_update()

        ts = TraitSet([1, 2, 3])
        ts.difference_update()

        self.assertEqual(ts, python_set)

    def test_difference_update_varargs(self):
        ts = TraitSet([1, 2, 3], notifiers=[self.notification_handler])
        ts.difference_update([2], [3])
        self.assertEqual(self.removed, {2, 3})

    def test_get_state(self):
        ts = TraitSet(notifiers=[self.notification_handler])

        states = ts.__getstate__()
        self.assertNotIn("notifiers", states)

    def test_set_state_exclude_notifiers(self):
        ts = TraitSet(notifiers=[])
        ts.__setstate__({"notifiers": [self.notification_handler]})

        self.assertEqual(ts.notifiers, [])


class Foo(HasTraits):
    values = Set()


def notifier(removed, added):
    pass


class TestTraitSetObject(unittest.TestCase):

    def test_get_state(self):
        foo = Foo(values={1, 2, 3})
        self.assertEqual(
            foo.values.notifiers, [foo.values.notifier])

        states = foo.values.__getstate__()
        self.assertNotIn("notifiers", states)

    def test_pickle_with_notifier(self):
        foo = Foo(values={1, 2, 3})
        foo.values.notifiers.append(notifier)

        protocols = range(pickle.HIGHEST_PROTOCOL + 1)

        for protocol in protocols:
            with self.subTest(protocol=protocol):
                serialized = pickle.dumps(
                    foo.values, protocol=protocol)
                deserialized = pickle.loads(serialized)

                # Transient notifiers are gone.
                self.assertEqual(
                    deserialized.notifiers,
                    [deserialized.notifier],
                )

    def test_validation(self):
        class TestSet(HasTraits):
            letters = Set(Str())

        TestSet(letters={"4"})
        with self.assertRaises(TraitError):
            TestSet(letters={4})

    def test_notification_silenced_if_has_items_if_false(self):
        class Foo(HasTraits):
            values = Set(items=False)

        foo = Foo(values=set())
        # name_items is a on_trait_change feature
        # Setting items to False effectively switches it off
        notifier = mock.Mock()
        foo.on_trait_change(lambda: notifier(), "values_items")

        # when
        foo.values.add(1)

        # then
        notifier.assert_not_called()

    def test_disconnected_set(self):
        # Objects that are disconnected from their HasTraits "owner" can arise
        # as a result of clone_traits operations, or of serialization and
        # deserialization.
        disconnected = TraitSetObject(
            trait=Set(Str),
            object=None,
            name="foo",
            value=set(),
        )
        self.assertEqual(disconnected.object(), None)

    def test_item_validation_uses_ctrait(self):
        # Regression test for enthought/traits#1619

        class RangeInstance(TraitType):
            default_value_type = DefaultValue.constant

            default_value = range(10)

            fast_validate = ValidateTrait.coerce, range

        class HasRanges(HasTraits):
            ranges = Set(RangeInstance())

        obj = HasRanges()

        with self.assertRaises(TraitError):
            obj.ranges.add(23)

        obj.ranges.add(range(10, 20))
        self.assertEqual(obj.ranges, {range(10, 20)})


class TestTraitSetEvent(unittest.TestCase):

    def test_trait_set_event_str_representation(self):
        """ Test string representation of the TraitSetEvent class. """
        desired_repr = "TraitSetEvent(removed=set(), added=set())"
        trait_set_event = TraitSetEvent()
        self.assertEqual(desired_repr, str(trait_set_event))
        self.assertEqual(desired_repr, repr(trait_set_event))

    def test_trait_set_event_subclass_str_representation(self):
        """ Test string representation of a subclass of the TraitSetEvent
        class. """

        class DifferentName(TraitSetEvent):
            pass

        desired_repr = "DifferentName(removed=set(), added=set())"
        different_name_subclass = DifferentName()
        self.assertEqual(desired_repr, str(different_name_subclass))
        self.assertEqual(desired_repr, repr(different_name_subclass))
