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
import operator
import pickle
import unittest.mock

from traits.api import HasTraits, Int, List
from traits.testing.optional_dependencies import numpy, requires_numpy
from traits.trait_errors import TraitError
from traits.trait_list_object import (
    accept_anything,
    TraitList,
    TraitListEvent,
    TraitListObject,
)


def int_item_validator(item):
    """
    An item_validator for TraitList that checks that the item is an int
    or integer-like object (e.g., any object whose type provides __index__).

    Parameters
    ----------
    item : object
        Proposed item to add to the list.

    Returns
    -------
    validated_item : object
        Actual item to add to the list.

    Raises
    ------
    TraitError
        If the item is not valid.
    """
    try:
        return int(operator.index(item))
    except TypeError:
        raise TraitError("Value {} is not a valid integer".format(item))


def list_item_validator(item):
    """
    An item_validator for TraitList that checks that the item is a list.

    Parameters
    ----------
    item : object
        Proposed item to add to the list.

    Returns
    -------
    validated_item : object
        Actual item to add to the list.

    Raises
    ------
    TraitError
        If the item is not valid.
    """
    if isinstance(item, list):
        return item
    else:
        raise TraitError("Value {} is not a list instance".format(item))


class TestTraitListEvent(unittest.TestCase):
    def test_creation(self):
        event = TraitListEvent(2, [3], [4])
        self.assertEqual(event.index, 2)
        self.assertEqual(event.removed, [3])
        self.assertEqual(event.added, [4])

        event = TraitListEvent(index=2, removed=[3], added=[4])
        self.assertEqual(event.index, 2)
        self.assertEqual(event.removed, [3])
        self.assertEqual(event.added, [4])

    def test_defaults(self):
        event = TraitListEvent()
        self.assertEqual(event.index, 0)
        self.assertEqual(event.removed, [])
        self.assertEqual(event.added, [])


class TestTraitList(unittest.TestCase):

    def setUp(self):
        self.index = None
        self.added = None
        self.removed = None
        self.trait_list = None

    def notification_handler(self, trait_list, index, removed, added):
        self.trait_list = trait_list
        self.index = index
        self.removed = removed
        self.added = added

    def test_init(self):
        tl = TraitList([1, 2, 3])

        self.assertListEqual(tl, [1, 2, 3])
        self.assertIs(tl.item_validator, accept_anything)
        self.assertEqual(tl.notifiers, [])

    def test_init_no_value(self):
        tl = TraitList()

        self.assertEqual(tl, [])
        self.assertIs(tl.item_validator, accept_anything)
        self.assertEqual(tl.notifiers, [])

    def test_init_iterable(self):
        tl = TraitList("abcde")

        self.assertListEqual(tl, ['a', 'b', 'c', 'd', 'e'])
        self.assertIs(tl.item_validator, accept_anything)
        self.assertEqual(tl.notifiers, [])

    def test_init_iterable_without_length(self):
        tl = TraitList(x**2 for x in range(5))

        self.assertEqual(tl, [0, 1, 4, 9, 16])
        self.assertIs(tl.item_validator, accept_anything)
        self.assertEqual(tl.notifiers, [])

    def test_init_validates(self):
        with self.assertRaises(TraitError):
            TraitList([1, 2.0, 3], item_validator=int_item_validator)

    def test_init_converts(self):
        tl = TraitList([True, False], item_validator=int_item_validator)

        self.assertEqual(tl, [1, 0])
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )

    def test_validator(self):
        tl = TraitList([1, 2, 3], item_validator=int_item_validator)

        self.assertListEqual(tl, [1, 2, 3])
        self.assertEqual(tl.item_validator, int_item_validator)
        self.assertEqual(tl.notifiers, [])

    def test_notification(self):
        tl = TraitList([1, 2, 3], notifiers=[self.notification_handler])

        self.assertListEqual(tl, [1, 2, 3])
        self.assertIs(tl.item_validator, accept_anything)
        self.assertEqual(tl.notifiers, [self.notification_handler])

        tl[0] = 5

        self.assertListEqual(tl, [5, 2, 3])
        self.assertIs(self.trait_list, tl)
        self.assertEqual(self.index, 0)
        self.assertEqual(self.removed, [1])
        self.assertEqual(self.added, [5])

    def test_copy(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl_copy = copy.copy(tl)

        for itm, itm_cpy in zip(tl, tl_copy):
            self.assertEqual(itm_cpy, itm)

        self.assertEqual(tl_copy.notifiers, [])
        self.assertEqual(tl_copy.item_validator, tl.item_validator)

    def test_deepcopy(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl_copy = copy.deepcopy(tl)

        for itm, itm_cpy in zip(tl, tl_copy):
            self.assertEqual(itm_cpy, itm)

        self.assertEqual(tl_copy.notifiers, [])
        self.assertEqual(tl_copy.item_validator, tl.item_validator)

    def test_deepcopy_memoization(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])
        trait_lists_copy = copy.deepcopy([tl, tl])
        self.assertIs(trait_lists_copy[0], trait_lists_copy[1])

    def test_setitem(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl[1] = 5
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [2])
        self.assertEqual(self.added, [5])

        tl[:] = [1, 2, 3, 4, 5]
        self.assertEqual(self.index, slice(0, 3, None))
        self.assertEqual(self.removed, [1, 5, 3])
        self.assertEqual(self.added, [1, 2, 3, 4, 5])

    def test_setitem_converts(self):
        tl = TraitList([9, 8, 7],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl[1] = False
        self.assertEqual(tl, [9, 0, 7])
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [8])
        self.assertEqual(self.added, [0])
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )
        self.assertTrue(
            all(type(item) is int for item in self.added),
            msg="Event contains non-integers for int-only list",
        )

        tl[::2] = [True, True]
        self.assertEqual(tl, [1, 0, 1])
        self.assertEqual(self.index, slice(0, 3, 2))
        self.assertEqual(self.removed, [9, 7])
        self.assertEqual(self.added, [1, 1])
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )
        self.assertTrue(
            all(type(item) is int for item in self.added),
            msg="Event contains non-integers for int-only list",
        )

    def test_setitem_nochange(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl[3:] = []
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_setitem_iterable(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl[:] = (x**2 for x in range(4))
        self.assertEqual(tl, [0, 1, 4, 9])
        self.assertEqual(self.index, slice(0, 3))
        self.assertEqual(self.removed, [1, 2, 3])
        self.assertEqual(self.added, [0, 1, 4, 9])

    def test_setitem_indexerror(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(IndexError):
            tl[3] = 4
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_setitem_validation_error(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            tl[0] = 4.5
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

        with self.assertRaises(TraitError):
            tl[0:2] = [1, "a string"]
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

        with self.assertRaises(TraitError):
            tl[2:0:-1] = [1, "a string"]
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_setitem_negative_step(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl[::-2] = [10, 11, 12]
        self.assertEqual(tl, [12, 2, 11, 4, 10])
        self.assertEqual(self.index, slice(None, None, -2))
        self.assertEqual(self.removed, [5, 3, 1])
        self.assertEqual(self.added, [10, 11, 12])

    def test_setitem_index_and_validation_error(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        # Assigning an invalid value to an invalid index: the
        # TraitError from the invalid value wins.
        with self.assertRaises(TraitError):
            tl[3] = 4.5
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

        # Assigning to a slice with invalid r.h.s. length and
        # invalid contents: again, the TraitError wins.
        with self.assertRaises(TraitError):
            tl[::2] = [1, 2, 4.5]
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_setitem_item_conversion(self):
        tl = TraitList([2, 3, 4],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl[0] = True
        self.assertEqual(tl, [1, 3, 4])
        self.assertEqual(self.index, 0)
        self.assertEqual(self.removed, [2])
        self.assertEqual(self.added, [1])

        # Check that the True has been converted to an int.
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )
        self.assertTrue(
            all(type(item) is int for item in self.added),
            msg="Event contains non-integers for int-only list",
        )

    def test_setitem_corner_case(self):
        # A peculiar-looking corner case where it's easy to get the
        # implementation wrong (and CPython did so in the distance past).
        tl = TraitList(range(7), notifiers=[self.notification_handler])

        # Note: new items inserted at position 5, not position 2.
        tl[5:2] = [10, 11, 12]
        self.assertEqual(tl, [0, 1, 2, 3, 4, 10, 11, 12, 5, 6])
        self.assertEqual(self.index, slice(5, 2))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [10, 11, 12])

    def test_delitem(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        del tl[2]
        self.assertEqual(self.index, 2)
        self.assertEqual(self.removed, [3])
        self.assertEqual(self.added, [])

        del tl[:]
        self.assertEqual(self.index, slice(0, 2, None))
        self.assertEqual(self.removed, [1, 2])
        self.assertEqual(self.added, [])

        with self.assertRaises(IndexError):
            del tl[0]

    def test_delitem_nochange(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        del tl[3:]
        self.assertEqual(tl, [1, 2, 3])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_delitem_negative_step(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        del tl[::-2]
        self.assertEqual(tl, [2, 4])
        self.assertEqual(self.index, slice(None, None, -2))
        self.assertEqual(self.removed, [5, 3, 1])
        self.assertEqual(self.added, [])

    def test_iadd(self):
        tl = TraitList([4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl += [6, 7]
        self.assertEqual(self.index, slice(2, 4, None))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [6, 7])

    def test_iadd_validates(self):
        tl = TraitList([4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            tl += [6, 7, 8.0]
        self.assertEqual(tl, [4, 5])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_iadd_converts(self):
        tl = TraitList([4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl += [True, True]
        self.assertEqual(tl, [4, 5, 1, 1])
        self.assertEqual(self.index, slice(2, 4))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1, 1])
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )
        self.assertTrue(
            all(type(item) is int for item in self.added),
            msg="Event contains non-integers for int-only list",
        )

    def test_iadd_empty(self):
        tl = TraitList([4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl += []
        self.assertEqual(tl, [4, 5])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_iadd_iterable(self):
        tl = TraitList([4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl += (x**2 for x in range(3))
        self.assertEqual(tl, [4, 5, 0, 1, 4])
        self.assertEqual(self.index, slice(2, 5))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [0, 1, 4])

    def test_imul(self):
        tl = TraitList([1, 2],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl *= 1
        self.assertListEqual(tl, [1, 2])
        self.assertEqual(self.index, None)
        self.assertEqual(self.removed, None)
        self.assertEqual(self.added, None)

        tl *= 2
        self.assertEqual(self.index, slice(2, 4, None))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1, 2])

        with self.assertRaises(TypeError):
            tl *= "5"

        with self.assertRaises(TypeError):
            tl *= 2.5

        tl *= -1
        self.assertEqual(self.index, slice(0, 4, None))
        self.assertEqual(self.removed, [1, 2, 1, 2])
        self.assertEqual(self.added, [])

    def test_imul_no_notification_for_empty_list(self):
        for multiplier in [-1, 0, 1, 2]:
            with self.subTest(multiplier=multiplier):
                tl = TraitList(
                    [],
                    item_validator=int_item_validator,
                    notifiers=[self.notification_handler])

                tl *= multiplier
                self.assertEqual(tl, [])
                self.assertIsNone(self.index)
                self.assertIsNone(self.removed)
                self.assertIsNone(self.added)

    @requires_numpy
    def test_imul_integer_like(self):
        tl = TraitList([1, 2],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl *= numpy.int64(2)
        self.assertEqual(tl, [1, 2, 1, 2])
        self.assertEqual(self.index, slice(2, 4))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1, 2])

        tl *= numpy.int64(-1)
        self.assertEqual(tl, [])
        self.assertEqual(self.index, slice(0, 4))
        self.assertEqual(self.removed, [1, 2, 1, 2])
        self.assertEqual(self.added, [])

    def test_imul_does_not_revalidate(self):
        item_validator = unittest.mock.Mock(wraps=int_item_validator)
        tl = TraitList([1, 1], item_validator=item_validator)
        item_validator.reset_mock()

        tl *= 3

        item_validator.assert_not_called()

    def test_append(self):
        tl = TraitList([1],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.append(2)
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [2])

    def test_append_validates(self):
        tl = TraitList([1],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            tl.append(1.0)
        self.assertEqual(tl, [1])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_append_converts(self):
        tl = TraitList([2],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.append(False)
        self.assertEqual(tl, [2, 0])
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [0])
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )
        self.assertTrue(
            all(type(item) is int for item in self.added),
            msg="Event contains non-integers for int-only list",
        )

    def test_extend(self):
        tl = TraitList([1],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.extend([1, 2])
        self.assertEqual(self.index, slice(1, 3, None))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1, 2])

    def test_extend_validates(self):
        tl = TraitList([5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            tl.extend([2, 3, 4.0])
        self.assertEqual(tl, [5])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_extend_converts(self):
        tl = TraitList([4],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.extend([False, True])
        self.assertEqual(tl, [4, 0, 1])
        self.assertEqual(self.index, slice(1, 3))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [0, 1])
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )
        self.assertTrue(
            all(type(item) is int for item in self.added),
            msg="Event contains non-integers for int-only list",
        )

    def test_extend_empty(self):
        tl = TraitList([1],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.extend([])
        self.assertEqual(tl, [1])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_extend_iterable(self):
        tl = TraitList([1],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.extend(x**2 for x in range(10, 13))
        self.assertEqual(tl, [1, 100, 121, 144])
        self.assertEqual(self.index, slice(1, 4))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [100, 121, 144])

    def test_insert(self):
        tl = TraitList([2],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.insert(0, 1)  # [1,2]
        self.assertEqual(self.index, 0)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1])

        tl.insert(-1, 3)  # [1,3,2]
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [3])

    def test_insert_index_matches_python_interpretation(self):
        for insertion_index in range(-10, 10):
            with self.subTest(insertion_index=insertion_index):
                tl = TraitList([5, 6, 7])
                pl = [5, 6, 7]

                tl.insert(insertion_index, 1729)
                pl.insert(insertion_index, 1729)
                self.assertEqual(tl, pl)

    def test_insert_validates(self):
        tl = TraitList([2],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            tl.insert(0, 1.0)
        self.assertEqual(tl, [2])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_insert_converts(self):
        tl = TraitList([2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.insert(1, True)
        self.assertEqual(tl, [2, 1, 3])
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1])
        self.assertTrue(
            all(type(item) is int for item in tl),
            msg="Non-integers found in int-only list",
        )
        self.assertTrue(
            all(type(item) is int for item in self.added),
            msg="Event contains non-integers for int-only list",
        )

    def test_pop(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.pop()
        self.assertEqual(self.index, 4)
        self.assertEqual(self.removed, [5])
        self.assertEqual(self.added, [])

        tl.pop(0)
        self.assertEqual(self.index, 0)
        self.assertEqual(self.removed, [1])
        self.assertEqual(self.added, [])

        # tl is now [2,3,4]
        tl.pop(-2)
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [3])
        self.assertEqual(self.added, [])

    def test_remove(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.remove(3)
        self.assertEqual(self.index, 2)
        self.assertEqual(self.removed, [3])
        self.assertEqual(self.added, [])

        with self.assertRaises(ValueError):
            tl.remove(3)

        tl.remove(2.0)
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [2])
        self.assertIsInstance(self.removed[0], int)
        self.assertEqual(self.added, [])

    def test_clear(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])
        tl.clear()
        self.assertEqual(self.index, slice(0, 5, None))
        self.assertEqual(self.removed, [1, 2, 3, 4, 5])
        self.assertEqual(self.added, [])

    def test_clear_empty_list(self):
        tl = TraitList([],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.clear()
        self.assertEqual(tl, [])
        self.assertIsNone(self.index)
        self.assertIsNone(self.removed)
        self.assertIsNone(self.added)

    def test_sort(self):
        tl = TraitList([2, 3, 1, 4, 5, 0],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.sort()

        self.assertEqual(tl, [0, 1, 2, 3, 4, 5])
        self.assertEqual(self.index, slice(0, 6, None))
        self.assertEqual(self.removed, [2, 3, 1, 4, 5, 0])
        self.assertEqual(self.added, [0, 1, 2, 3, 4, 5])

    def test_reverse(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl.reverse()
        self.assertEqual(tl, [5, 4, 3, 2, 1])
        self.assertEqual(self.index, slice(0, 5, None))
        self.assertEqual(self.removed, [1, 2, 3, 4, 5])
        self.assertEqual(self.added, [5, 4, 3, 2, 1])

    def test_reverse_single_notification(self):
        # Regression test for double notification.
        notifier = unittest.mock.Mock()
        tl = TraitList([1, 2, 3, 4, 5],
                       notifiers=[notifier])
        notifier.assert_not_called()
        tl.reverse()
        self.assertEqual(notifier.call_count, 1)

    def test_pickle(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            serialized = pickle.dumps(tl, protocol=protocol)

            tl_unpickled = pickle.loads(serialized)

            self.assertIs(tl_unpickled.item_validator, tl.item_validator)
            self.assertEqual(tl_unpickled.notifiers, [])

            for i, j in zip(tl, tl_unpickled):
                self.assertIs(i, j)

    def test_invalid_entry(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TraitError):
            tl.append("A")

    def test_list_of_lists(self):
        tl = TraitList([[1]],
                       item_validator=list_item_validator,
                       notifiers=[self.notification_handler])

        tl.append([2])


def squares(n):
    """
    Generic iterable without a valid len, for testing purposes.

    Parameters
    ----------
    n : int
        Limit for computation.

    Returns
    -------
    squares : generator
        Generator yielding the first n squares.
    """
    return (x * x for x in range(n))


class HasLengthConstrainedLists(HasTraits):
    """
    Test class for testing list length validation.
    """
    at_least_two = List(Int, [3, 4], minlen=2)

    at_most_five = List(Int, maxlen=5)


class TestTraitListObject(unittest.TestCase):
    def test_list_of_lists_pickle_with_notifier(self):
        class Foo:
            pass

        tl = TraitListObject(
            trait=List(),
            object=Foo(),
            name="foo",
            value=(),
        )

        self.assertEqual(
            [tl.notifier],
            tl.notifiers
        )

        serialized = pickle.dumps(tl)

        tl_deserialized = pickle.loads(serialized)

        self.assertEqual(
            [tl_deserialized.notifier],
            tl_deserialized.notifiers
        )

    def test_init_too_small(self):
        with self.assertRaises(TraitError):
            HasLengthConstrainedLists(at_least_two=[1])

    def test_init_too_large(self):
        with self.assertRaises(TraitError):
            HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4, 5, 6])

    def test_init_from_iterable(self):
        class Foo:
            pass

        tl = TraitListObject(
            trait=List(),
            object=Foo(),
            name="foo",
            value=squares(5),
        )
        self.assertEqual(tl, list(squares(5)))

    def test_delitem(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 23])
        del foo.at_most_five[1]
        self.assertEqual(foo.at_most_five, [1])

    def test_delitem_single_too_small(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2])
        with self.assertRaises(TraitError):
            del foo.at_least_two[0]
        self.assertEqual(foo.at_least_two, [1, 2])

    def test_delitem_slice_too_small(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2])
        with self.assertRaises(TraitError):
            del foo.at_least_two[:]
        self.assertEqual(foo.at_least_two, [1, 2])

    def test_iadd(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2])
        foo.at_most_five += [6, 7, 8]
        self.assertEqual(foo.at_most_five, [1, 2, 6, 7, 8])

    def test_iadd_too_large(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_most_five += [6, 7, 8]
        self.assertEqual(foo.at_most_five, [1, 2, 3, 4])

    def test_iadd_from_iterable(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2])
        foo.at_most_five += squares(3)
        self.assertEqual(foo.at_most_five, [1, 2, 0, 1, 4])

    def test_imul(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3])
        foo.at_least_two *= 2
        self.assertEqual(foo.at_least_two, [1, 2, 3, 1, 2, 3])

    def test_imul_too_small(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_least_two *= 0
        self.assertEqual(foo.at_least_two, [1, 2, 3, 4])

    def test_imul_too_large(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_most_five *= 2
        self.assertEqual(foo.at_most_five, [1, 2, 3, 4])

    def test_setitem_index(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        foo.at_least_two[1] = 7
        self.assertEqual(foo.at_least_two, [1, 7, 3, 4])

    def test_setitem_slice(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        foo.at_least_two[1:] = [6, 7]
        self.assertEqual(foo.at_least_two, [1, 6, 7])

    def test_setitem_extended_slice(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        foo.at_least_two[1::2] = [6, 7]
        self.assertEqual(foo.at_least_two, [1, 6, 3, 7])

    def test_setitem_too_small(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_least_two[1:] = []
        self.assertEqual(foo.at_least_two, [1, 2, 3, 4])

    def test_setitem_too_large(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_most_five[2:] = [10, 11, 12, 13]
        self.assertEqual(foo.at_most_five, [1, 2, 3, 4])

    def test_setitem_from_iterable(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2])
        foo.at_most_five[:1] = squares(4)
        self.assertEqual(foo.at_most_five, [0, 1, 4, 9, 2])

    def test_setitem_extended_slice_bad_length(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        with self.assertRaises(ValueError):
            foo.at_least_two[1::2] = squares(3)
        self.assertEqual(foo.at_least_two, [1, 2, 3, 4])

    def test_setitem_item_validation_failure(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_least_two[2:] = [5.0, 6.0]
        self.assertEqual(foo.at_least_two, [1, 2, 3, 4])

    def test_append(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3])
        foo.at_most_five.append(6)
        self.assertEqual(foo.at_most_five, [1, 2, 3, 6])

    def test_append_too_large(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4, 5])
        with self.assertRaises(TraitError):
            foo.at_most_five.append(6)
        self.assertEqual(foo.at_most_five, [1, 2, 3, 4, 5])

    def test_clear(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4])
        foo.at_most_five.clear()
        self.assertEqual(foo.at_most_five, [])

    def test_clear_too_small(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_least_two.clear()
        self.assertEqual(foo.at_least_two, [1, 2, 3, 4])

    def test_extend(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        foo.at_least_two.extend([10, 11])
        self.assertEqual(foo.at_least_two, [1, 2, 3, 4, 10, 11])

    def test_extend_too_large(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4])
        with self.assertRaises(TraitError):
            foo.at_most_five.extend([10, 11, 12])
        self.assertEqual(foo.at_most_five, [1, 2, 3, 4])

    def test_extend_from_iterable(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2])
        foo.at_most_five.extend(squares(3))
        self.assertEqual(foo.at_most_five, [1, 2, 0, 1, 4])

    def test_insert(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 3, 4])
        foo.at_least_two.insert(3, 16)
        self.assertEqual(foo.at_least_two, [1, 2, 3, 16, 4])

    def test_insert_too_large(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4, 5])
        with self.assertRaises(TraitError):
            foo.at_most_five.insert(3, 16)
        with self.assertRaises(TraitError):
            foo.at_most_five.insert(-10, 16)
        with self.assertRaises(TraitError):
            foo.at_most_five.insert(10, 16)
        self.assertEqual(foo.at_most_five, [1, 2, 3, 4, 5])

    def test_pop(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 6])
        foo.at_least_two.pop()
        self.assertEqual(foo.at_least_two, [1, 2])

    def test_pop_too_small(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2])
        with self.assertRaises(TraitError):
            foo.at_least_two.pop()
        with self.assertRaises(TraitError):
            foo.at_least_two.pop(0)
        # TraitError takes precedence over the IndexError for a bad index.
        with self.assertRaises(TraitError):
            foo.at_least_two.pop(10)
        self.assertEqual(foo.at_least_two, [1, 2])

    def test_remove(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2, 6, 4])
        foo.at_least_two.remove(2)
        self.assertEqual(foo.at_least_two, [1, 6, 4])

    def test_remove_too_small(self):
        foo = HasLengthConstrainedLists(at_least_two=[1, 2])
        with self.assertRaises(TraitError):
            foo.at_least_two.remove(1)
        with self.assertRaises(TraitError):
            foo.at_least_two.remove(2.0)
        # TraitError from the length violation takes precedence over
        # the ValueError for the vad value.
        with self.assertRaises(TraitError):
            foo.at_least_two.remove(10)
        self.assertEqual(foo.at_least_two, [1, 2])

    def test_dead_object_reference(self):
        foo = HasLengthConstrainedLists(at_most_five=[1, 2, 3, 4])
        list_object = foo.at_most_five
        del foo

        list_object.append(5)
        self.assertEqual(list_object, [1, 2, 3, 4, 5])
        with self.assertRaises(TraitError):
            list_object.append(4)
