import gc
import unittest

import six

from ..weakiddict import WeakIDDict, WeakIDKeyDict


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
    if six.PY2:
        assertCountEqual = unittest.TestCase.assertItemsEqual

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
