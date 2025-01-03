# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.util.weakiddict import WeakIDDict, WeakIDKeyDict


class AllTheSame(object):
    def __hash__(self):
        return 42

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __ne__(self, other):
        return not self.__eq__(other)


class WeakreffableInt(object):
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        else:
            return self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)


class TestWeakIDDict(unittest.TestCase):

    def test_weak_keys(self):
        wd = WeakIDKeyDict()

        keep = []
        dont_keep = []
        values = list(range(10))
        for n, i in enumerate(values, 1):
            key = AllTheSame()
            if not (i % 2):
                keep.append(key)
            else:
                dont_keep.append(key)
            wd[key] = i
            del key
            # No keys or values have been deleted, yet.
            self.assertEqual(len(wd), n)

        # Delete half of the keys.
        self.assertEqual(len(wd), 10)
        del dont_keep
        self.assertEqual(len(wd), 5)

        # Check the remaining values.
        self.assertCountEqual(list(wd.values()), list(range(0, 10, 2)))
        self.assertEqual([wd[k] for k in keep], list(range(0, 10, 2)))

        # Check the remaining keys.
        self.assertCountEqual([id(k) for k in wd.keys()], [id(k) for k in wd])
        self.assertCountEqual(
            [id(k) for k in wd.keys()], [id(k) for k in keep]
        )

    def test_weak_keys_values(self):
        wd = WeakIDDict()

        keep = []
        dont_keep = []
        values = list(map(WeakreffableInt, range(10)))
        for n, i in enumerate(values, 1):
            key = AllTheSame()
            if not (i.value % 2):
                keep.append(key)
            else:
                dont_keep.append(key)
            wd[key] = i
            del key
            # No keys or values have been deleted, yet.
            self.assertEqual(len(wd), n)

        # Delete half of the keys.
        self.assertEqual(len(wd), 10)
        del dont_keep
        self.assertEqual(len(wd), 5)

        # Check the remaining values.
        self.assertCountEqual(
            list(wd.values()), list(map(WeakreffableInt, [0, 2, 4, 6, 8]))
        )
        self.assertEqual(
            [wd[k] for k in keep], list(map(WeakreffableInt, [0, 2, 4, 6, 8]))
        )

        # Check the remaining keys.
        self.assertCountEqual([id(k) for k in wd.keys()], [id(k) for k in wd])
        self.assertCountEqual(
            [id(k) for k in wd.keys()], [id(k) for k in keep]
        )

        # Delete the weak values progressively and ensure that the
        # corresponding entries disappear.
        del values[0:2]
        self.assertEqual(len(wd), 4)
        del values[0:2]
        self.assertEqual(len(wd), 3)
        del values[0:2]
        self.assertEqual(len(wd), 2)
        del values[0:2]
        self.assertEqual(len(wd), 1)
        del values[0:2]
        self.assertEqual(len(wd), 0)

    def test_weak_id_dict_str_representation(self):
        """ test string representation of the WeakIDDict class. """
        weak_id_dict = WeakIDDict()
        desired_repr = "<WeakIDDict at 0x{0:x}>".format(id(weak_id_dict))
        self.assertEqual(desired_repr, str(weak_id_dict))
        self.assertEqual(desired_repr, repr(weak_id_dict))

    def test_weak_id_key_dict_str_representation(self):
        """ test string representation of the WeakIDKeyDict class. """
        weak_id_key_dict = WeakIDKeyDict()
        desired_repr = f"<WeakIDKeyDict at 0x{id(weak_id_key_dict):x}>"
        self.assertEqual(desired_repr, str(weak_id_key_dict))
        self.assertEqual(desired_repr, repr(weak_id_key_dict))
