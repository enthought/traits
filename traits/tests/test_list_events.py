# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for List items_changed events.

"""
import unittest

from traits.api import HasTraits, Int, List


class MyClass(HasTraits):
    l = List(Int, [1, 2, 3])

    l_events = List

    def _l_items_changed(self, event):
        self.l_events.append(event)


class ListEventTestCase(unittest.TestCase):
    def test_initialization(self):
        # Just creating an instance of MyClass shouldn't cause
        # the items_changed handler to fire.
        foo = MyClass()
        self.assertEqual(foo.l, [1, 2, 3])
        self.assertEqual(len(foo.l_events), 0)

    def test_append(self):
        foo = MyClass()
        foo.l.append(4)
        self.assertEqual(foo.l, [1, 2, 3, 4])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [4])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 3)

    def test_extend(self):
        foo = MyClass()
        foo.l.extend([4, 5, 6])
        self.assertEqual(foo.l, [1, 2, 3, 4, 5, 6])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [4, 5, 6])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 3)

    def test_extend_via_inplace_addition(self):
        foo = MyClass()
        foo.l += [4, 5, 6]
        self.assertEqual(foo.l, [1, 2, 3, 4, 5, 6])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [4, 5, 6])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 3)

    def test_insert(self):
        foo = MyClass()
        foo.l.insert(1, 99)
        self.assertEqual(foo.l, [1, 99, 2, 3])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [99])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 1)

    def test_insert_with_negative_argument(self):
        foo = MyClass()
        foo.l.insert(-1, 99)
        self.assertEqual(foo.l, [1, 2, 99, 3])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [99])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 2)

    def test_insert_index_invariants(self):
        # Note that Python's list.insert allows indices outside
        # the range [-len(my_list), len(my_list)].
        for index in range(-10, 10):
            foo = MyClass()
            foo.l.insert(index, 1729)
            self.assertEqual(len(foo.l_events), 1)
            event = foo.l_events[0]
            self.assertEqual(event.added, [1729])
            self.assertEqual(event.removed, [])
            self.assertGreaterEqual(event.index, 0)
            self.assertEqual(foo.l[event.index], 1729)

    def test_pop_with_no_argument(self):
        foo = MyClass()
        item = foo.l.pop()
        self.assertEqual(item, 3)
        self.assertEqual(foo.l, [1, 2])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [])
        self.assertEqual(event.removed, [3])
        self.assertEqual(event.index, 2)

    def test_pop(self):
        foo = MyClass()
        item = foo.l.pop(0)
        self.assertEqual(item, 1)
        self.assertEqual(foo.l, [2, 3])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [])
        self.assertEqual(event.removed, [1])
        self.assertEqual(event.index, 0)

    def test_pop_with_negative_argument(self):
        foo = MyClass()
        item = foo.l.pop(-2)
        self.assertEqual(item, 2)
        self.assertEqual(foo.l, [1, 3])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [])
        self.assertEqual(event.removed, [2])
        self.assertEqual(event.index, 1)

    def test_pop_out_of_range(self):
        foo = MyClass()
        with self.assertRaises(IndexError):
            foo.l.pop(-4)
        with self.assertRaises(IndexError):
            foo.l.pop(3)
        self.assertEqual(foo.l, [1, 2, 3])
        self.assertEqual(len(foo.l_events), 0)

    def test_remove(self):
        foo = MyClass()
        foo.l.remove(2)
        self.assertEqual(foo.l, [1, 3])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [])
        self.assertEqual(event.removed, [2])
        self.assertEqual(event.index, 1)

    def test_remove_item_not_present(self):
        foo = MyClass()
        with self.assertRaises(ValueError):
            foo.l.remove(1729)
        self.assertEqual(foo.l, [1, 2, 3])
        self.assertEqual(len(foo.l_events), 0)

    def test_inplace_multiply(self):
        foo = MyClass()
        foo.l *= 2
        self.assertEqual(foo.l, [1, 2, 3, 1, 2, 3])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [1, 2, 3])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 3)

    def test_inplace_multiply_by_zero(self):
        foo = MyClass()
        foo.l *= 0
        self.assertEqual(foo.l, [])
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.added, [])
        self.assertEqual(event.removed, [1, 2, 3])
        self.assertEqual(event.index, 0)

    def test_remove_empty_slices(self):
        # Test that no events are produced when no items are deleted
        foo = MyClass()

        # Delete no items and get no events
        del foo.l[3:]
        self.assertEqual(foo.l, [1, 2, 3])
        self.assertEqual(len(foo.l_events), 0)

        # Delete all items and get an expected event
        del foo.l[:]
        self.assertEqual(foo.l, [])
        self.assertEqual(len(foo.l_events), 1)
        event, = foo.l_events
        self.assertEqual(event.added, [])
        self.assertEqual(event.removed, [1, 2, 3])
        self.assertEqual(event.index, 0)

        # Delete no items and get no new events
        del foo.l[:]
        self.assertEqual(foo.l, [])
        self.assertEqual(len(foo.l_events), 1)

    def test_remove_empty_slices_steps(self):
        foo = MyClass()

        # Delete no items and get no events
        del foo.l[3::2]
        self.assertEqual(foo.l, [1, 2, 3])
        self.assertEqual(len(foo.l_events), 0)

    def test_clear(self):
        foo = MyClass()
        foo.l.clear()
        self.assertEqual(len(foo.l_events), 1)
        event = foo.l_events[0]
        self.assertEqual(event.index, 0)
        self.assertEqual(event.removed, [1, 2, 3])
        self.assertEqual(event.added, [])

    def test_clear_empty_list(self):
        foo = MyClass()
        foo.l = []

        foo.l.clear()

        self.assertEqual(len(foo.l_events), 0)

    def test_delete_step_slice(self):
        foo = MyClass()
        foo.l = [0, 1, 2, 3, 4]

        del foo.l[0:5:2]

        self.assertEqual(len(foo.l_events), 1)
        event, = foo.l_events
        self.assertEqual(event.index, slice(0, 5, 2))
        self.assertEqual(event.removed, [0, 2, 4])
        self.assertEqual(event.added, [])

    def test_delete_step_slice_empty_list(self):
        foo = MyClass()
        foo.l = []

        del foo.l[::-1]

        # No items deleted, so no event fired
        self.assertEqual(len(foo.l_events), 0)

    def test_assignment_step_slice(self):
        foo = MyClass()
        foo.l = [1, 2, 3]

        foo.l[::2] = [3, 4]

        self.assertEqual(len(foo.l_events), 1)
        event, = foo.l_events
        self.assertEqual(event.index, slice(0, 3, 2))
        self.assertEqual(event.added, [3, 4])
        self.assertEqual(event.removed, [1, 3])
