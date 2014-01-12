""" Unit tests for the Tuple trait type.
"""

from traits.testing.unittest_tools import unittest, UnittestTools

from traits.api import HasTraits, Tuple, TraitError

VALUES = ('value1', 33, None)


class E(HasTraits):

    t1 = Tuple(VALUES)

    t2 = Tuple(*VALUES)


class TupleTestCase(unittest.TestCase, UnittestTools):

    def test_default_values(self):
        # Check that the default values for t1 and t2 are correctly
        # derived from the VALUES tuple.

        e = E()
        self.assertEqual(e.t1, VALUES)
        self.assertEqual(e.t2, VALUES)

    def test_simple_assignment(self):
        # Check that we can assign different values of the correct type.

        e = E()
        with self.assertTraitChanges(e, 't1'):
            e.t1 = ('other value 1', 77, None)
        with self.assertTraitChanges(e, 't2'):
            e.t2 = ('other value 2', 99, None)

    def test_invalid_assignment_length(self):
        # Check that assigning a tuple of incorrect length
        # raises a TraitError.
        self._assign_invalid_values_length(('str', 44))
        self._assign_invalid_values_length(('str', 33, None, []))

    def test_type_checking(self):
        # Test that type checking is done for the 't1' attribute.
        e = E()
        other_tuple = ('other value', 75, True)
        with self.assertRaises(TraitError):
            e.t1 = other_tuple
        self.assertEqual(e.t1, VALUES)

        # Test that no type checking is done for the 't2' attribute.
        try:
            e.t2 = other_tuple
        except TraitError:
            self.fail('Unexpected TraitError when assigning to tuple.')
        self.assertEqual(e.t2, other_tuple)

    def _assign_invalid_values_length(self, values):

        e = E()
        with self.assertRaises(TraitError):
            e.t1 = values
        self.assertEqual(e.t1, VALUES)
        with self.assertRaises(TraitError):
            e.t2 = values
        self.assertEqual(e.t2, VALUES)
