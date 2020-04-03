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
from traits.trait_list_object import (
    adapt_trait_validator,
    TraitList,
    TraitListObject,
)
from traits.trait_types import _validate_int, List


def int_validator(trait_list, index, removed, added):
    return [_validate_int(item) for item in added]


def list_validator(trait_list, index, removed, added):
    for itm in added:
        if not isinstance(itm, list):
            raise TraitError
    return added


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
        self.assertIsNone(tl.validator)
        self.assertEqual(tl.notifiers, [])

    def test_init_iterable(self):
        tl = TraitList("abcde")

        self.assertListEqual(tl, ['a', 'b', 'c', 'd', 'e'])
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
        self.assertEqual(self.removed, [1])
        self.assertEqual(self.added, [5])

    def test_deepcopy(self):
        tl = TraitList([1, 2, 3],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl_copy = copy.deepcopy(tl)

        for itm, itm_cpy in zip(tl, tl_copy):
            self.assertEqual(itm_cpy, itm)

        self.assertEqual(tl_copy.notifiers, [])
        self.assertEqual(tl_copy.validator, tl.validator)

    def test_setitem(self):
        tl = TraitList([1, 2, 3],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl[1] = 5
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [2])
        self.assertEqual(self.added, [5])

        tl[:] = [1, 2, 3, 4, 5]
        self.assertEqual(self.index, slice(0, 3, None))
        self.assertEqual(self.removed, [1, 5, 3])
        self.assertEqual(self.added, [1, 2, 3, 4, 5])

    def test_delitem(self):
        tl = TraitList([1, 2, 3],
                       validator=int_validator,
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

    def test_iadd(self):
        tl = TraitList([4, 5],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl += [6, 7]
        self.assertEqual(self.index, slice(2, 4, None))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [6, 7])

    def test_imul(self):
        tl = TraitList([1, 2],
                       validator=int_validator,
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

    def test_append(self):
        tl = TraitList([1],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl.append(2)
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [2])

    def test_extend(self):
        tl = TraitList([1],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl.extend([1, 2])
        self.assertEqual(self.index, slice(1, 3, None))
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1, 2])

    def test_insert(self):
        tl = TraitList([2],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl.insert(0, 1)  # [1,2]
        self.assertEqual(self.index, 0)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [1])

        tl.insert(-1, 3)  # [1,3,2]
        self.assertEqual(self.index, 1)
        self.assertEqual(self.removed, [])
        self.assertEqual(self.added, [3])

    def test_pop(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       validator=int_validator,
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
                       validator=int_validator,
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
                       validator=int_validator,
                       notifiers=[self.notification_handler])
        tl.clear()
        self.assertEqual(self.index, slice(0, 5, None))
        self.assertEqual(self.removed, [1, 2, 3, 4, 5])
        self.assertEqual(self.added, [])

    def test_sort(self):
        tl = TraitList([2, 3, 1, 4, 5, 0],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl.sort()

        self.assertEqual(tl, [0, 1, 2, 3, 4, 5])
        self.assertEqual(self.index, slice(0, 6, None))
        self.assertEqual(self.removed, [2, 3, 1, 4, 5, 0])
        self.assertEqual(self.added, [0, 1, 2, 3, 4, 5])

    def test_reverse(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        tl.reverse()
        self.assertEqual(tl, [5, 4, 3, 2, 1])
        self.assertEqual(self.index, slice(0, 5, None))
        self.assertEqual(self.removed, [1, 2, 3, 4, 5])
        self.assertEqual(self.added, [5, 4, 3, 2, 1])

    def test_pickle(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       validator=int_validator,
                       notifiers=[self.notification_handler])
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            serialized = pickle.dumps(tl, protocol=protocol)

            tl_unpickled = pickle.loads(serialized)

            self.assertIs(tl_unpickled.validator, tl.validator)
            self.assertEqual(tl_unpickled.notifiers, [])

            for i, j in zip(tl, tl_unpickled):
                self.assertIs(i, j)

    def test_invalid_entry(self):
        tl = TraitList([1, 2, 3, 4, 5],
                       validator=int_validator,
                       notifiers=[self.notification_handler])

        with self.assertRaises(TypeError):
            tl.append("A")

    def test_adapt_trait_validator(self):

        def bool_validator(object, name, value):
            if isinstance(value, bool):
                return value
            else:
                raise TraitError

        # Fail without adaptor
        with self.assertRaises(TypeError):
            tl = TraitList([], validator=bool_validator)

        # Attach the adaptor
        list_bool_validator = adapt_trait_validator(bool_validator)

        # It now works!
        tl_2 = TraitList([], validator=list_bool_validator)
        tl_2.extend([True, False, True])
        tl_2.insert(0, True)

        # Decorate with list adaptor
        @adapt_trait_validator
        def bool_validator(object, name, value):
            if isinstance(value, bool):
                return value
            else:
                raise TraitError

        # Still working
        tl = TraitList([], validator=bool_validator)
        tl.extend([True, False, True])

        with self.assertRaises(TraitError):
            tl.extend(["invalid"])

    def test_list_of_lists(self):
        tl = TraitList([[1]],
                       validator=list_validator,
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
