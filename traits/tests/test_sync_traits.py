""" Test that the `syn_traits` member function of the `HasTraits`
functions correctly.

"""

from __future__ import absolute_import

from traits.testing.unittest_tools import unittest, UnittestTools

from ..api import HasTraits, Int


class A(HasTraits):

    t = Int


class B(HasTraits):

    t = Int

    u = Int


class TestSyncTraits(unittest.TestCase, UnittestTools):

    def test_mutual_sync(self):
        """ Test that two traits can be mutually synchronized.
        """

        a = A()
        b = B()

        a.sync_trait('t', b)

        b.t = 10
        self.assertEqual(a.t, b.t)
        a.t = 20
        self.assertEqual(b.t, a.t)

        # Check that we can remove the synchronization
        a.sync_trait('t', b, remove=True)

        with self.assertTraitDoesNotChange(a, 't'):
            b.t = 5
        with self.assertTraitDoesNotChange(b, 't'):
            a.t = 7

    def test_sync_alias(self):
        """ Test synchronization of a trait with an aliased trait.
        """

        a = A()
        b = B()

        a.sync_trait('t', b, 'u')

        with self.assertTraitDoesNotChange(b, 't'):
            a.t = 5

        self.assertEqual(a.t, b.u)

        b.u = 7
        self.assertEqual(a.t, b.u)

    def test_one_way_sync(self):
        """ Test one-way synchronization of two traits.
        """

        a = A()
        b = B()

        a.sync_trait('t', b, mutual=False)

        a.t = 5
        self.assertEqual(b.t, a.t)

        with self.assertTraitDoesNotChange(a, 't'):
            b.t = 7

        # Remove synchronization
        a.sync_trait('t', b, remove=True)

        with self.assertTraitDoesNotChange(b, 't'):
            a.t = 12


if __name__ == '__main__':
    unittest.main()
