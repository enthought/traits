# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test that the `sync_trait` member function of `HasTraits` instances
functions correctly.

"""

import unittest

from traits.api import (
    HasTraits,
    Int,
    List,
    push_exception_handler,
    pop_exception_handler,
)
from traits.testing.unittest_tools import UnittestTools


class A(HasTraits):

    t = Int

    l = List(Int)


class B(HasTraits):

    t = Int

    u = Int

    l = List(Int)


class TestSyncTraits(unittest.TestCase, UnittestTools):
    def setUp(self):
        push_exception_handler(lambda *args: None, reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()

    def test_mutual_sync(self):
        """ Test that two traits can be mutually synchronized.
        """

        a = A()
        b = B()

        a.sync_trait("t", b)

        b.t = 10
        self.assertEqual(a.t, b.t)
        a.t = 20
        self.assertEqual(b.t, a.t)

        # Check that we can remove the synchronization
        a.sync_trait("t", b, remove=True)

        with self.assertTraitDoesNotChange(a, "t"):
            b.t = 5
        with self.assertTraitDoesNotChange(b, "t"):
            a.t = 7

    def test_sync_alias(self):
        """ Test synchronization of a trait with an aliased trait.
        """

        a = A()
        b = B()

        a.sync_trait("t", b, "u")

        with self.assertTraitDoesNotChange(b, "t"):
            a.t = 5

        self.assertEqual(a.t, b.u)

        b.u = 7
        self.assertEqual(a.t, b.u)

    def test_one_way_sync(self):
        """ Test one-way synchronization of two traits.
        """

        a = A(t=3)
        b = B(t=4)

        a.sync_trait("t", b, mutual=False)
        self.assertEqual(b.t, 3)

        a.t = 5
        self.assertEqual(b.t, a.t)

        with self.assertTraitDoesNotChange(a, "t"):
            b.t = 7

        # Remove synchronization
        a.sync_trait("t", b, remove=True)

        with self.assertTraitDoesNotChange(b, "t"):
            a.t = 12

    def test_sync_lists(self):
        """ Test synchronization of list traits.
        """

        a = A()
        b = B()

        a.sync_trait("l", b)

        # Change entire list.
        a.l = [1, 2, 3]
        self.assertEqual(a.l, b.l)
        b.l = [4, 5]
        self.assertEqual(a.l, b.l)

        # Change list items.
        a.l = [7, 8, 9]
        with self.assertTraitChanges(b, "l_items"):
            a.l[-1] = 20
        self.assertEqual(b.l, [7, 8, 20])

        # Remove synchronization
        a.sync_trait("l", b, remove=True)

        with self.assertTraitDoesNotChange(a, "l"):
            b.l = [7, 8]

    def test_sync_lists_partial_slice(self):
        """ Test synchronization of list traits when there is a partial slice.

        Regression test for enthought/traits#540
        """

        a = A()
        b = B()

        a.sync_trait("l", b)

        # Change entire list.
        a.l = [1, 2, 3]
        self.assertEqual(a.l, b.l)
        b.l = [4, 5]
        self.assertEqual(a.l, b.l)

        # Change list items with an empty slice.
        with self.assertTraitChanges(b, "l_items"):
            a.l[:] = [7]
        self.assertEqual(b.l, [7])

        # Change list items with a partial slice.
        with self.assertTraitChanges(b, "l_items"):
            a.l[:0] = [6]
        self.assertEqual(b.l, [6, 7])

    def test_sync_delete(self):
        """ Test that deleting a synchronized trait works.
        """

        a = A()
        b = B()

        a.sync_trait("t", b)

        a.t = 5
        del a

        try:
            # Updating `b.t` should not raise an exception due to remaining
            # listeners.
            b.t = 7
        except Exception:
            self.fail("Unexpected exception while setting sync trait.")

    def test_sync_delete_one_way(self):
        """ Test that deleting a one-way synchronized trait works.

        (Regression test for #131).

        """
        a = A()
        b = B()

        a.sync_trait("t", b, mutual=False)
        del b

        try:
            a.t = 42
        except Exception:
            self.fail("Unexpected exception while setting sync trait.")

    def test_sync_ref_cycle(self):
        """ Regression test for #69.
        """

        a = A()
        b = B()

        change_counter = [0]

        def _handle_change():
            change_counter[0] += 1

        b.on_trait_change(_handle_change, "t")

        a.sync_trait("t", b)
        a.t = 17
        self.assertEqual(change_counter, [1])

        # Delete b and check that no more changes to b.t are recorded.
        del b
        a.t = 42
        self.assertEqual(change_counter, [1])
