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
import unittest

from traits.testing.optional_dependencies import numpy, requires_numpy
from traits.trait_errors import TraitError
from traits.trait_list_object import (
    accept_anything,
    TraitList,
    TraitListObject,
)
from traits.trait_types import List


def int_item_validator(item):
    """
    An item_validator for TraitList that checks that the item is an integer.

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

    def test_deepcopy(self):
        tl = TraitList([1, 2, 3],
                       item_validator=int_item_validator,
                       notifiers=[self.notification_handler])

        tl_copy = copy.deepcopy(tl)

        for itm, itm_cpy in zip(tl, tl_copy):
            self.assertEqual(itm_cpy, itm)

        self.assertEqual(tl_copy.notifiers, [])
        self.assertEqual(tl_copy.item_validator, tl.item_validator)

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
